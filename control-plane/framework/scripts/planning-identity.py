#!/usr/bin/env python3
"""Mint local planning identities without Git-tag reservations or admission effects.

LOCAL MOD - HARVEST TO CPB: Operator-approved slug/hex context and ordinal record IDs.
"""

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import secrets
import subprocess
import sys
from contextlib import nullcontext


SLUG = r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*'
ADHOC_PATTERN = rf'(?:ADHOC-[0-9a-f]{{32}}|(?:ADHOC|DISC)-{SLUG}-[0-9a-f]{{4}})'
HORIZON_PATTERN = rf'H[0-8][0-9]{{2}}(?:-{SLUG}-[0-9a-f]{{4}})?'
CONTEXT_PATTERN = rf'(?:{ADHOC_PATTERN}|{HORIZON_PATTERN})'
TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}\Z')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_helper(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), pathlib.Path(__file__).with_name(name + '.py'))
    if spec is None or spec.loader is None:
        raise ValueError('helper unavailable: ' + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def parse(identity):
    require(isinstance(identity, str) and re.fullmatch(CONTEXT_PATTERN, identity), 'invalid planning context ID')
    if re.fullmatch(r'ADHOC-[0-9a-f]{32}|H[0-8][0-9]{2}', identity):
        return {'kind': 'horizon' if identity.startswith('H') else 'ad-hoc', 'legacy': True, 'slug': None}
    prefix, remainder = identity.split('-', 1)
    slug, suffix = remainder.rsplit('-', 1)
    require(len(slug) <= 48, 'planning slug exceeds 48 characters')
    return {'kind': 'horizon' if prefix.startswith('H') else 'discovery' if prefix == 'DISC' else 'ad-hoc',
            'legacy': False, 'slug': slug, 'suffix': suffix}


def matches_kind(identity, kind):
    try:
        value = parse(identity)
        return value['kind'] == kind or (value['legacy'] and value['kind'] == 'ad-hoc' and kind == 'discovery')
    except ValueError:
        return False


def local_state(root, capture):
    filename = capture.safe_path(root, root / 'control-plane/state/planning-local/identities.json')
    if filename.exists():
        state = capture.contract.load_json(filename)
        require(state.get('schema') == 'cp-planning-identities-v1', 'invalid identity allocation state')
        return filename, state, filename.read_bytes()
    return filename, {'schema': 'cp-planning-identities-v1', 'contexts': {}, 'records': {}, 'aliases': {}}, None


def persist(root, filename, state, before, capture):
    capture.ensure_directory(root, filename.parent)
    raw = (json.dumps(state, indent=2, ensure_ascii=False) + '\n').encode()
    if before is None:
        capture.publish_new_bytes(filename, raw)
    elif raw != before:
        capture.replace_bytes(filename, before, raw)


def known_ids(root, state):
    known = {item['id'] for item in state['contexts'].values()} | set(state['aliases']) | set(state['aliases'].values())
    for directory in ('ad-hoc', 'horizons'):
        home = root / 'control-plane' / directory
        if home.is_dir():
            known.update(item.name for item in home.iterdir())
    if (root / '.git').exists():
        for arguments in (['log', '--all', '--format=', '--name-only', '--', 'control-plane/ad-hoc', 'control-plane/horizons'],
                          ['for-each-ref', '--format=%(refname)', 'refs/tags/horizon']):
            result = subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, text=True)
            require(result.returncode == 0, 'cannot inspect local planning identity history')
            for line in result.stdout.splitlines():
                known.update(part for part in line.split('/') if part.startswith(('ADHOC-', 'DISC-', 'H')))
    return known


def mint(root, kind, slug, operation_id, author, origin=None, confirmed=False, locked=False):
    require(confirmed, 'identity minting requires explicit confirmation')
    require(kind in ('ad-hoc', 'discovery', 'horizon'), 'unsupported planning kind')
    require(bool(re.fullmatch(SLUG, slug)) and len(slug) <= 48, 'invalid planning slug')
    require(bool(TOKEN.fullmatch(operation_id)) and bool(author.strip()), 'operation identity and author required')
    require((kind == 'discovery') == (origin is not None), 'discovery requires exact origin; other kinds have no execution origin')
    root = pathlib.Path(root).resolve()
    capture = load_helper('planning-capture')
    if origin is not None:
        require(set(origin) == {'phase', 'contract'}, 'invalid discovery origin')
        require(isinstance(origin['phase'].get('revision'), int) and origin['phase']['revision'] > 0 and origin['phase'].get('id'), 'invalid discovery phase revision')
        load_helper('validate-canon-records').verify_source(root, origin['contract'])
    request = {'kind': kind, 'slug': slug, 'author': author, 'origin': origin}
    with nullcontext() if locked else capture.local_writer(root):
        filename, state, before = local_state(root, capture)
        if operation_id in state['contexts']:
            existing = state['contexts'][operation_id]
            require(existing['request'] == request, 'mint operation reused with different inputs')
            return {**existing, 'created': False}
        known = known_ids(root, state)
        prefix = 'ADHOC' if kind == 'ad-hoc' else 'DISC'
        if kind == 'horizon':
            numbers = [int(match.group(1)) for identity in known if (match := re.match(r'H([0-8][0-9]{2})(?:-|$)', identity))]
            number = max(numbers, default=-1) + 1
            require(number <= 899, 'production horizon sequence exhausted')
            prefix = f'H{number:03d}'
        for attempt in range(10):
            suffix = secrets.token_hex(2)
            require(bool(re.fullmatch(r'[0-9a-f]{4}', suffix)), 'invalid random suffix')
            identity = f'{prefix}-{slug}-{suffix}'
            if identity.casefold() not in {value.casefold() for value in known}:
                break
        else:
            raise ValueError('planning identity collision limit reached')
        entry = {'id': identity, 'operation_id': operation_id, 'request_digest': digest(request), 'request': request}
        state['contexts'][operation_id] = entry
        persist(root, filename, state, before, capture)
        return {**entry, 'created': True}


def reserve_records(root, context_id, operation_id, bindings, prior=None, confirmed=False, locked=False):
    require(confirmed and TOKEN.fullmatch(operation_id), 'record allocation requires explicit operation confirmation')
    require(not parse(context_id)['legacy'], 'record allocation requires a minted full context ID')
    root = pathlib.Path(root).resolve()
    capture = load_helper('planning-capture')
    request = {'context_id': context_id, 'bindings': bindings, 'prior': prior}
    with nullcontext() if locked else capture.local_writer(root):
        filename, state, before = local_state(root, capture)
        key = context_id + ':' + operation_id
        if key in state['records']:
            existing = state['records'][key]
            require(existing['request_digest'] == digest(request), 'record allocation operation reused with changed inputs')
            return {'state': copy.deepcopy(existing['allocation']), 'mapping': copy.deepcopy(existing['mapping'])}
        allocation = copy.deepcopy(prior or {'next_change': 1, 'next_canon': 1, 'changes': {}, 'canon': {}})
        for entry in state['records'].values():
            if entry['context_id'] == context_id:
                allocation['next_change'] = max(allocation['next_change'], entry['allocation']['next_change'])
                allocation['next_canon'] = max(allocation['next_canon'], entry['allocation']['next_canon'])
                for collection in ('changes', 'canon'):
                    retained = entry['allocation'][collection]
                    compatible = all(issued_id not in allocation[collection] or allocation[collection][issued_id] == binding for issued_id, binding in retained.items())
                    require(compatible, 'conflicting retained allocation')
                    allocation[collection].update(copy.deepcopy(retained))
        mapping = {'changes': {}, 'canon': {}}
        for binding in bindings:
            alias = binding['change_id']
            require(alias not in mapping['changes'], 'duplicate allocation input change ID')
            change_id = f"CHG-{allocation['next_change']:04d}"
            allocation['next_change'] += 1
            mapping['changes'][alias] = change_id
            if binding['target']['type'] == 'canon_record' and binding['operation'] == 'add':
                old_id = binding['target']['id']
                require(old_id not in mapping['canon'], 'duplicate new Canon identity')
                record_id = f"CR-{context_id}-{allocation['next_canon']:04d}"
                allocation['next_canon'] += 1
                mapping['canon'][old_id] = record_id
                allocation['canon'][record_id] = binding['kind']
        for binding in bindings:
            target = copy.deepcopy(binding['target'])
            if target['type'] == 'canon_record':
                target['id'] = mapping['canon'].get(target['id'], target['id'])
            elif target['type'] == 'canon_relationship':
                for endpoint in ('from', 'to'):
                    target[endpoint]['id'] = mapping['canon'].get(target[endpoint]['id'], target[endpoint]['id'])
            allocation['changes'][mapping['changes'][binding['change_id']]] = {'operation': binding['operation'], 'target_digest': digest(target)}
        result = {'state': allocation, 'mapping': mapping}
        state['records'][key] = {'context_id': context_id, 'request_digest': digest(request), 'allocation': allocation, 'mapping': mapping}
        persist(root, filename, state, before, capture)
        return result


def validate_allocation(document):
    if parse(document['context']['id'])['legacy']:
        return
    require('identity' in document, 'minted proposal requires allocation metadata')
    identity = document['context']['id']
    allocation = document['identity']['allocation']
    for collection in ('canon', 'changes'):
        targets = set(document['identity']['aliases'][collection].values())
        require(targets <= allocation[collection].keys(), 'alias targets unallocated ' + collection + ' identity')
    for change_id, binding in allocation['changes'].items():
        match = re.fullmatch(r'CHG-([0-9]{4,})', change_id)
        require(match is not None, 'invalid change allocation ID')
        number = int(match.group(1))
        require(0 < number < allocation['next_change'] and change_id == f'CHG-{number:04d}', 'invalid change high-water mark')
    for record_id in allocation['canon']:
        match = re.fullmatch(re.escape('CR-' + identity + '-') + r'([0-9]{4,})', record_id)
        require(match is not None, 'Canon allocation belongs to a different context')
        number = int(match.group(1))
        require(0 < number < allocation['next_canon'] and record_id == f'CR-{identity}-{number:04d}', 'invalid Canon high-water mark')
    for change in document['changes']:
        binding = allocation['changes'].get(change['change_id'])
        require(binding == {'operation': change['operation'], 'target_digest': digest(change['target'])}, 'change identity is unallocated or rebound')
        if change['target']['type'] == 'canon_record' and change['operation'] == 'add':
            require(allocation['canon'].get(change['value']['id']) == change['value']['kind'], 'new Canon identity is unallocated or retyped')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=pathlib.Path, default=pathlib.Path.cwd())
    commands = parser.add_subparsers(dest='command', required=True)
    mint_parser = commands.add_parser('mint')
    for name in ('kind', 'slug', 'operation-id', 'author'):
        mint_parser.add_argument('--' + name, required=True)
    mint_parser.add_argument('--origin', type=pathlib.Path)
    mint_parser.add_argument('--confirmed', action='store_true')
    records = commands.add_parser('records', help='reserve ordinals against an exact proposal subject; returns mappings for the save request')
    for name in ('context', 'operation-id', 'expected-digest'):
        records.add_argument('--' + name, required=True)
    records.add_argument('--bindings', type=pathlib.Path, required=True)
    records.add_argument('--confirmed', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'records':
            require(args.confirmed, 'record allocation requires explicit confirmation')
            capture = load_helper('planning-capture')
            with capture.local_writer(args.root.resolve()):
                filename = capture.resolve_document(args.root, args.context)
                require(hashlib.sha256(filename.read_bytes()).hexdigest() == args.expected_digest, 'proposal changed since allocation was offered')
                document = capture.read_capture(filename)
                require(document['id'] == args.context, 'allocate against the full current context ID')
                bindings = json.load(sys.stdin) if str(args.bindings) == '-' else json.loads(args.bindings.read_bytes())
                result = reserve_records(args.root, args.context, args.operation_id, bindings, document['identity']['allocation'], True, locked=True)
            print(json.dumps(result, indent=2))
            return 0
        origin = json.loads(args.origin.read_bytes()) if args.origin else None
        print(json.dumps(mint(args.root, args.kind, args.slug, args.operation_id, args.author, origin, args.confirmed), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('Planning identity refused: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())