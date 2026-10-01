#!/usr/bin/env python3
"""Validate, preview and save planning change sets; never admit or execute them.

LOCAL MOD - HARVEST TO CPB: shared change-set proposal contract and paired-file writer.
"""

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


def helper(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), pathlib.Path(__file__).with_name(name + '.py'))
    if spec is None or spec.loader is None:
        raise ValueError('missing helper: ' + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


canon = helper('validate-canon-records')
identity_policy = helper('planning-identity')
require = canon.require
SCHEMA_PATH = canon.SCHEMA_PATH.with_name('plan-change-set.schema.json')
FORMAT = 'cp-plan-change-set-v1'


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def schema_validator():
    schema, canon_schema = canon.load_json(SCHEMA_PATH), canon.load_json(canon.SCHEMA_PATH)
    registry = Registry().with_resources([
        (SCHEMA_PATH.as_uri(), Resource.from_contents(schema)),
        (canon.SCHEMA_PATH.as_uri(), Resource.from_contents(canon_schema)),
        (schema['$id'], Resource.from_contents(schema)),
        (canon_schema['$id'], Resource.from_contents(canon_schema)),
        ('canon-records.schema.json', Resource.from_contents(canon_schema)),
    ])
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def shape(document):
    validator = schema_validator()
    errors = list(validator.iter_errors(document))
    require(not errors, 'change-set schema: ' + (errors[0].message if errors else ''))
    context = document['context']
    require(document['id'] == context['id'], 'proposal/context identity mismatch')
    require(identity_policy.matches_kind(context['id'], context['kind']), 'planning context kind/identity mismatch')
    identity_policy.validate_allocation(document)
    lifecycle = context.get('lifecycle')
    if lifecycle is not None:
        events = lifecycle['events']
        require(len({event['operation_id'] for event in events}) == len(events), 'duplicate lifecycle operation identity')
        timestamps = [datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) for event in events]
        require(timestamps == sorted(timestamps), 'lifecycle events are not time ordered')
        require(all(event['action'] != 'create' or index == 0 for index, event in enumerate(events)), 'create must be the first lifecycle event')
        if events:
            states = {'create': 'planning', 'resume': 'planning', 'suspend': 'suspended', 'abandon': 'abandoned', 'close': 'closed'}
            require(lifecycle['state'] == states[events[-1]['action']], 'lifecycle state differs from last event')
    return document


def lifecycle_state(document):
    shape(document)
    return document['context'].get('lifecycle', {}).get('state', 'planning')


def git(root, *arguments):
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(root), *arguments], capture_output=True)
    require(result.returncode == 0, 'baseline Git read failed: ' + result.stderr.decode(errors='replace').strip())
    return result.stdout


def empty_base():
    return {'revision': 0, 'canon': {'schema': 'cp-canon-records-v1', 'sources': [], 'records': [], 'relationships': []},
            'work_items': [], 'dependencies': [], 'bound_work': []}


def baseline(root, reference):
    if reference is None:
        return None
    if 'files' in reference:
        repository = helper('planning-repository')
        selected = repository.snapshot(root, reference['git_commit'])
        require(reference['files'] == selected['files'] and
                reference['sha256'] == selected['files'].get(reference['path']) and
                reference['revision'] == selected['state']['tracker']['revision'], 'repository baseline bindings differ')
        return repository.baseline(selected['state'])
    source = {'id': 'baseline', 'path': reference['path'], 'sha256': reference['sha256'], 'git_commit': reference['git_commit']}
    canon.verify_source(root, source)
    raw = git(root, 'show', reference['git_commit'] + ':' + reference['path'])
    value = json.loads(raw)
    if value.get('schema') == 'cp-operational-specification-v1':
        contract = helper('planning-contract')
        contract.validate_specification(value)
        require(value == contract.empty_specification(), 'populated legacy baseline needs explicit Canon/work migration')
        resolved = empty_base()
    else:
        errors = list(schema_validator().evolve(schema={'$ref': SCHEMA_PATH.as_uri() + '#/$defs/baseline'}).iter_errors(value))
        require(not errors, 'baseline schema: ' + (errors[0].message if errors else ''))
        require(value.get('schema') == 'cp-plan-baseline-v1' and set(value) ==
                {'schema', 'revision', 'canon', 'work_items', 'dependencies', 'bound_work'}, 'unsupported baseline schema')
        resolved = {key: content for key, content in value.items() if key != 'schema'}
    require(resolved['revision'] == reference['revision'], 'baseline revision mismatch')
    return resolved


def target_key(target):
    kind = target['type']
    if kind in ('canon_record', 'work_item'):
        return kind, target['id']
    start, end = canon.record_key(target['from']), canon.record_key(target['to'])
    return (kind, target['kind'], start, end) if kind == 'canon_relationship' else (kind, start, end)


def edge_target(value, kind):
    return {'type': kind, **{name: value[name] for name in (('kind', 'from', 'to') if kind == 'canon_relationship' else ('from', 'to'))}}


def compose(document, base):
    shape(document)
    require(base is not None or document['status'] == 'draft', 'complete proposal needs an exact baseline')
    known_base = base is not None
    base = copy.deepcopy(base if known_base else empty_base())
    require(set(base) - {'obsolete_work'} == {'revision', 'canon', 'work_items', 'dependencies', 'bound_work'}, 'invalid baseline fields')
    errors = list(schema_validator().evolve(schema={'$ref': SCHEMA_PATH.as_uri() + '#/$defs/baseline'}).iter_errors({'schema': 'cp-plan-baseline-v1', **base}))
    require(not errors, 'baseline schema: ' + (errors[0].message if errors else ''))
    canon.validate(base['canon'])
    sources = {source['id']: source for source in base['canon']['sources']}
    incoming = set()
    for source in document['sources']:
        require(source['id'] not in incoming, 'duplicate proposal source ID')
        incoming.add(source['id'])
        require(source['id'] not in sources or sources[source['id']] == source, 'source identity has conflicting versions')
        sources[source['id']] = source
    existing = {}
    all_revisions = {}
    for item in base['canon']['records']:
        all_revisions[canon.record_key(item)] = item
        key = ('canon_record', item['id'])
        if key not in existing or item['revision'] > existing[key]['revision']:
            existing[key] = item
    for item in base['work_items']:
        key = ('work_item', item['id'])
        require(key not in existing, 'duplicate baseline work identity')
        existing[key] = item
    for kind, values in (('canon_relationship', base['canon']['relationships']), ('work_dependency', base['dependencies'])):
        for item in values:
            key = target_key(edge_target(item, kind))
            require(key not in existing, 'duplicate baseline edge')
            existing[key] = item
    changes, ids, unknown = {}, set(), []
    for change in document['changes']:
        require(change['change_id'] not in ids, 'duplicate change ID')
        ids.add(change['change_id'])
        require(set(change['sources']) <= incoming, 'change cites undeclared source')
        key = target_key(change['target'])
        changes.setdefault(key, []).append(change)
        previous = existing.get(key)
        operation = change['operation']
        if not known_base and operation != 'add':
            unknown.append(change['change_id'])
        elif operation == 'add':
            replacement = key[0] in ('canon_relationship', 'work_dependency') and any(
                other['operation'] == 'remove' and target_key(other['target']) == key for other in document['changes'])
            require(previous is None or replacement, 'add target already exists in baseline')
        else:
            require(previous is not None, 'change target missing from baseline')
            require(change['expected']['digest'] == digest(previous), 'stale expected target digest')
            if key[0] in ('canon_record', 'work_item'):
                require(change['expected']['revision'] == previous['revision'], 'stale expected target revision')
        if 'value' in change:
            value = change['value']
            require(set(value['sources']) <= incoming, 'proposed value cites undeclared source')
            if key[0] in ('canon_record', 'work_item'):
                require(value['id'] == key[1], 'target/value identity mismatch')
                if operation == 'add':
                    require(value['revision'] == 1, 'new record must start at revision 1')
                else:
                    require(value['revision'] == change['expected']['revision'] + 1, 'modification must provide next complete revision')
                    if previous is not None and key[0] == 'canon_record':
                        require((value['kind'], value['scope']) == (previous['kind'], previous['scope']), 'record kind/scope change requires a new identity')
            else:
                require(target_key(edge_target(value, key[0])) == key, 'target/value edge mismatch')
            if document['status'] == 'complete' and key[0] == 'work_item':
                require(value['maturity'] == 'specified', 'complete proposal contains an incomplete work candidate')
    for key, selected in changes.items():
        operations = sorted(change['operation'] for change in selected)
        require(len(selected) == 1 or (key[0] in ('canon_relationship', 'work_dependency') and operations == ['add', 'remove']),
                'conflicting changes target the same identity')
    gaps = set()
    for gap in document['unresolved']:
        require(gap['id'] not in gaps and set(gap['affects']) <= ids, 'invalid unresolved-item identity or affected change')
        gaps.add(gap['id'])
    if not known_base:
        return {'base_verified': False, 'preconditions': 'not-checked', 'unresolved_existing_targets': unknown, 'result': None}
    effective = copy.deepcopy(existing)
    for reference in base.get('obsolete_work', []):
        require(('work_item', reference['id']) in existing, 'obsolete work is missing')
        effective.pop(('work_item', reference['id']), None)
    bound_keys = {canon.record_key(reference) for reference in base['bound_work']}
    retired = {value['id'] for key, value in existing.items() if key[0] == 'canon_record' and value['authority_status'] in ('retired', 'superseded', 'rejected', 'deferred')}
    for identity in retired:
        effective.pop(('canon_record', identity), None)
    for change in document['changes']:
        key = target_key(change['target'])
        if change['operation'] in ('remove', 'obsolete'):
            effective.pop(key, None)
            if key[0] == 'canon_record':
                retired.add(key[1])
                tombstone = copy.deepcopy(existing[key])
                tombstone['revision'] += 1
                tombstone['authority_status'] = 'retired'
                tombstone['sources'] = copy.deepcopy(change['sources'])
                require(canon.record_key(tombstone) not in all_revisions, 'retirement revision already exists')
                all_revisions[canon.record_key(tombstone)] = tombstone
    for change in document['changes']:
        if 'value' in change:
            key = target_key(change['target'])
            effective[key] = copy.deepcopy(change['value'])
            if key[0] == 'canon_record':
                value = change['value']
                require(canon.record_key(value) not in all_revisions, 'proposed revision already exists')
                all_revisions[canon.record_key(value)] = value
                retired.discard(key[1])
    canon_result = {'schema': 'cp-canon-records-v1', 'sources': list(sources.values()),
                    'records': list(all_revisions.values()),
                    'relationships': [value for key, value in effective.items() if key[0] == 'canon_relationship']}
    canon.validate(canon_result)
    for relationship in canon_result['relationships']:
        require(relationship['from']['id'] not in retired and relationship['to']['id'] not in retired,
                'obsoletion leaves an effective Canon relationship')
    work_items = [value for key, value in effective.items() if key[0] == 'work_item']
    work_keys = {canon.record_key(item) for item in work_items}
    for item in work_items:
        require(set(item['sources']) <= sources.keys(), 'work cites unresolved source')
        for reference in item['canon_refs']:
            require(canon.record_key(reference) in all_revisions and
                    (reference['id'] not in retired or canon.record_key(item) in bound_keys), 'work refers to unavailable Canon revision')
        task_ids = [task['id'] for task in item['tasks']]
        require(len(task_ids) == len(set(task_ids)), 'duplicate task identity')
        task_edges = []
        for task in item['tasks']:
            require(set(task['after']) <= set(task_ids) and task['id'] not in task['after'], 'invalid internal task dependency')
            task_edges.extend((prior, task['id']) for prior in task['after'])
        canon.reject_cycles(task_edges, 'internal tasks')
    dependencies = [value for key, value in effective.items() if key[0] == 'work_dependency']
    for dependency in dependencies:
        start, end = canon.record_key(dependency['from']), canon.record_key(dependency['to'])
        require(start in work_keys and end in work_keys and start != end, 'invalid work dependency endpoint')
        require(set(dependency['sources']) <= sources.keys(), 'dependency cites unresolved source')
    canon.reject_cycles([(canon.record_key(item['from']), canon.record_key(item['to'])) for item in dependencies], 'work dependencies')
    if base['bound_work'] and document['changes']:
        preserved = [canon.record_key(item['work']) for item in document.get('execution_impact', [])]
        require(len(preserved) == len(set(preserved)), 'duplicate execution-impact disposition')
        require(document['status'] == 'draft' or set(preserved) == bound_keys,
            'bound work needs explicit execution-impact preservation before completion')
        for change in document['changes']:
            require(not (change['target']['type'] == 'work_item' and
                 change['target']['id'] in {identity for identity, revision in bound_keys}), 'bound work cannot be rewritten')
    return {'base_verified': True, 'preconditions': 'checked', 'result': {'canon': canon_result,
            'effective_record_refs': [dict(id=value['id'], revision=value['revision']) for key, value in effective.items() if key[0] == 'canon_record'],
            'work_items': work_items, 'dependencies': dependencies}, 'admission': 'not-assessed'}


def source_at_base(source, base, reference):
    if base is not None and reference is not None and source in base['canon']['sources'] and 'git_commit' not in source:
        return {**source, 'git_commit': reference['git_commit']}
    return source


def validate(root, document, capture_bytes=None):
    root = pathlib.Path(root).resolve()
    shape(document)
    if capture_bytes is None:
        canon.verify_source(root, document['capture'])
    else:
        require(hashlib.sha256(capture_bytes).hexdigest() == document['capture']['sha256'], 'capture/proposal pair mismatch')
    selected_base = baseline(root, document['base'])
    for source in document['sources']:
        canon.verify_source(root, source_at_base(source, selected_base, document['base']))
    if document['context']['kind'] == 'discovery':
        canon.verify_source(root, document['context']['origin']['contract'])
    result = compose(document, selected_base)
    if result['result'] is not None:
        checked = copy.deepcopy(result['result']['canon'])
        checked['sources'] = [source_at_base(source, selected_base, document['base']) for source in checked['sources']]
        canon.validate(checked, root=root)
    result['target_freshness'] = 'not-checked; baseline is an exact committed snapshot'
    return result


def source_navigation(root, document, narrative):
    capture_home = (root / document['capture']['path']).parent
    lines = ['## Current Source Locations', '',
             'Live source references from the current proposal catalogue. Earlier relocation lists are superseded; original paths and commands remain historical evidence.', '']
    for source in document['sources']:
        require('git_commit' not in source, 'navigation refresh currently requires local source files')
        canon.verify_source(root, source)
        relative = pathlib.Path(os.path.relpath(root / source['path'], capture_home)).as_posix()
        require(not any(character in relative for character in '()[]\n\r'), 'source path cannot be represented as a navigation link')
        lines.append(f"- {source['id']}: [{pathlib.PurePosixPath(source['path']).name}]({relative.replace(' ', '%20')})")
    section = '\n'.join(lines) + '\n\n'
    pattern = re.compile(r'^## (?:Restored Source Locations|Source Filename Correction|Current Source Locations)\n.*?(?=^## |\Z)', re.MULTILINE | re.DOTALL)
    matches = list(pattern.finditer(narrative))
    if not matches:
        return narrative.rstrip() + '\n\n' + section
    first = matches[0].start()
    return pattern.sub(lambda match: section if match.start() == first else '', narrative)


def refresh_navigation(root, context_id, expected_digest, confirmed=False):
    require(confirmed, 'navigation refresh requires explicit confirmation')
    root = pathlib.Path(root).resolve()
    capture = helper('planning-capture')
    document = capture.read_capture(capture.resolve_document(root, context_id))
    require(document['schema'] == FORMAT and document['status'] == 'draft', 'navigation refresh requires a draft change set')
    document['revision'] += 1
    record = '## Navigation Correction\n\nOperator authorized fixing the referential-integrity findings. Refreshed current source links from the proposal catalogue; preserved original source bytes, historical commands and prior subjects. No Canon/work meaning or identity changed.'
    return save(root, context_id, document, expected_digest, record, navigation_only=True)


def finalize_proposal(root, context_id, document, expected_digest, record):
    require(document.get('status') == 'complete', 'finalize-proposal requires supplied complete content')
    return save(root, context_id, document, expected_digest, record, complete=True)


def assert_unapplied_baselines(root, context_id, references):
    repository = helper('planning-repository')
    commits = {}
    for reference in references:
        if reference is None:
            continue
        baseline(root, reference)
        selected = [reference['git_commit']]
        observed = subprocess.run(['git', '--no-replace-objects', '-C', str(root), 'show-ref',
                                   '--verify', '--quiet', reference['target_ref']], capture_output=True)
        require(observed.returncode in (0, 1), 'baseline target inspection failed: ' + observed.stderr.decode(errors='replace').strip())
        if observed.returncode == 0:
            selected.append(git(root, 'rev-parse', '--verify', reference['target_ref'] + '^{commit}').decode().strip())
        for commit in selected:
            commits[commit] = commits.get(commit, False) or 'files' in reference
    for commit, requires_repository in commits.items():
        present = git(root, 'ls-tree', '--name-only', commit, '--', *repository.PATHS.values(), *repository.LEGACY).strip()
        if requires_repository or present:
            current = repository.snapshot(root, commit)
            require(not any(entry['proposal_id'] == context_id for entry in current['state']['tracker']['admissions']),
                    'post-application draft reset unavailable until HR-06 verifies application and the new baseline; prior changes are preserved')


def save(root, context_id, document, expected_digest, record, migrate=False, complete=False, navigation_only=False):
    root = pathlib.Path(root).resolve()
    capture = helper('planning-capture')
    with capture.local_writer(root):
        destination = capture.resolve_document(root, context_id)
        before = destination.read_bytes()
        previous = capture.read_capture(destination)
        if previous['schema'] == FORMAT:
            require(lifecycle_state(previous) == 'planning', 'context is not mutable planning; explicit lifecycle handling required')
        if complete:
            require(document.get('base') is not None, 'finalize-proposal requires an exact baseline')
            require(git(root, 'rev-parse', '--verify', document['base']['target_ref'] + '^{commit}').decode().strip() == document['base']['git_commit'],
                    'finalize-proposal baseline is stale; reconcile against the current target')
        old_narrative_path = capture.narrative_path(destination) if destination.suffix == '.json' else None
        require(old_narrative_path is not None, 'legacy horizon capture is read-only here; explicit migration required')
        old_narrative = old_narrative_path.read_bytes()
        navigation = old_narrative
        if navigation_only:
            require(document == {**previous, 'revision': previous['revision'] + 1} and previous['status'] == 'draft', 'navigation refresh cannot change proposal meaning')
            require(hashlib.sha256(before).hexdigest() == expected_digest, 'proposal changed since navigation refresh was offered')
            validate(root, previous)
            navigation = source_navigation(root, previous, old_narrative.decode()).encode()
            if navigation == old_narrative:
                return {'updated': False, 'document_digest': expected_digest, 'admitted': False}
        normalized = copy.deepcopy(document)
        if previous['schema'] == FORMAT and 'capture' in normalized:
            normalized['capture']['sha256'] = previous['capture']['sha256']
            if not complete:
                normalized['status'] = 'draft'
            if normalized == previous:
                current_digest = hashlib.sha256(before).hexdigest()
                if expected_digest != current_digest:
                    require(bool(re.fullmatch(r'[0-9a-f]{64}', expected_digest)), 'invalid expected digest')
                    prior = capture.safe_path(root, capture.assets_path(root, context_id) / 'history' / (expected_digest + '-proposal.json'))
                    require(prior.is_file() and hashlib.sha256(prior.read_bytes()).hexdigest() == expected_digest and
                            old_narrative.endswith(b'\n' + record.rstrip().encode() + b'\n'), 'proposal changed since save was offered')
                validate(root, previous)
                return {'updated': False, 'document_digest': current_digest, 'admitted': False}
        document = copy.deepcopy(document)
        if not complete and previous['schema'] == FORMAT and previous['status'] == 'complete':
            document['status'] = 'draft'
        require(hashlib.sha256(before).hexdigest() == expected_digest, 'proposal changed since save was offered')
        helper('planning-change-evidence').assert_mutable(root, context_id)
        claim = capture.safe_path(root, root / 'control-plane/state/planning-local/publication/claims' / (context_id + '.json'))
        if claim.exists():
            publication = helper('planning-publication')
            attempt = canon.load_json(claim)['attempt_id']
            events = publication.journal(root, publication.attempt_directory(root, attempt))
            require(not any(event['state'] in ('applied', 'applied-trial') for event in events),
                'post-application draft reset unavailable until HR-06 verifies application and the new baseline; prior changes are preserved')
        if previous['schema'] == FORMAT:
            assert_unapplied_baselines(root, context_id, (previous['base'], document['base']))
        require(document['context']['id'] == context_id, 'save context mismatch')
        require(document['status'] != 'complete' or complete, 'complete proposal requires explicit complete operation')
        require(not complete or document['status'] == 'complete', 'complete operation requires complete status')
        if previous['schema'] == FORMAT:
            for key in ('id', 'author', 'created_at', 'context'):
                require(document[key] == previous[key], 'proposal identity/provenance is immutable')
            require(document['revision'] == previous['revision'] + 1, 'changed proposal requires next revision')
            if 'identity' in previous:
                old_identity = previous['identity']
                new_identity = document['identity']
                require(new_identity['mint'] == old_identity['mint'] and new_identity['aliases'] == old_identity['aliases'], 'identity provenance is immutable')
                if new_identity['allocation'] != old_identity['allocation']:
                    allocation = new_identity['allocation']
                    for collection in ('changes', 'canon'):
                        require(all(allocation[collection].get(key) == value for key, value in old_identity['allocation'][collection].items()),
                                'issued allocation bindings cannot be removed or changed')
                    require(all(allocation[key] >= old_identity['allocation'][key] for key in ('next_change', 'next_canon')), 'allocation high-water marks cannot decrease')
                    _, allocations, _ = identity_policy.local_state(root, capture)
                    require(any(entry['context_id'] == context_id and entry['allocation'] == allocation for entry in allocations['records'].values()),
                            'allocation extension must be issued by the identity helper in this workspace')
        else:
            require(migrate and 'proposal' not in previous and not any(previous.get('workflow', {}).get(key)
                    for key in ('reviews', 'decision', 'admission', 'findings')), 'migration requires an unreviewed draft with no complete proposal')
            capture.require_mutable(previous)
            require(document['id'] == previous['id'] and document['revision'] == 1 and document['status'] == 'draft', 'migration must create revision-1 draft')
            require(document['author'] == previous['author'] and document['created_at'] == previous['created_at'], 'migration must preserve attribution')
            require({(source['id'], source['sha256']) for source in document['sources']} ==
                    {(source['id'], source['sha256']) for source in previous['sources']}, 'migration source coverage differs')
        require(record and record.strip(), 'actual request/confirmation narrative is required')
        require(not re.search(r'(?im)^\s*(?:```|~~~)json\b', record), 'narrative record must not contain JSON blocks')
        after_narrative = navigation + b'\n' + record.rstrip().encode() + b'\n'
        if navigation_only:
            after_narrative = navigation.rstrip(b'\n') + b'\n\n' + record.rstrip().encode() + b'\n'
        changed = copy.deepcopy(document)
        require(changed['capture']['path'] == old_narrative_path.relative_to(root).as_posix() and 'git_commit' not in changed['capture'], 'working capture reference must identify its companion file')
        changed['capture']['sha256'] = hashlib.sha256(after_narrative).hexdigest()
        validate(root, changed, after_narrative)
        if complete:
            require(git(root, 'rev-parse', '--verify', changed['base']['target_ref'] + '^{commit}').decode().strip() == changed['base']['git_commit'],
                'finalize-proposal baseline changed during validation')
        content = encoded(changed)
        _publish_pair(root, destination, before, old_narrative, content, after_narrative)
        return {'updated': True, 'document_digest': hashlib.sha256(content).hexdigest(), 'revision': changed['revision'], 'admitted': False}


def _publish_pair(root, destination, before, old_narrative, content, after_narrative):
    capture = helper('planning-capture')
    previous = capture.decode_capture(before, capture.document_identity(destination))
    changed = capture.decode_capture(content, previous['id'])
    require(changed['schema'] == FORMAT, 'paired publication requires change-set format')
    old_capture_digest = previous['capture']['sha256'] if previous['schema'] == FORMAT else previous['capture_sha256']
    require(hashlib.sha256(old_narrative).hexdigest() == old_capture_digest, 'preimage capture/proposal pair mismatch')
    if previous['schema'] == FORMAT:
        require(all(changed[key] == previous[key] for key in ('id', 'author', 'created_at')), 'proposal identity/provenance is immutable')
        require({key: value for key, value in changed['context'].items() if key != 'lifecycle'} ==
                {key: value for key, value in previous['context'].items() if key != 'lifecycle'}, 'context identity/origin is immutable')
    narrative = capture.safe_path(root, capture.narrative_path(destination))
    require(changed['capture']['path'] == narrative.relative_to(root).as_posix() and 'git_commit' not in changed['capture'],
            'working capture reference must identify its companion file')
    require(hashlib.sha256(after_narrative).hexdigest() == changed['capture']['sha256'], 'capture/proposal pair mismatch')
    require(destination.read_bytes() == before and narrative.read_bytes() == old_narrative, 'pair changed before publication')
    if content == before and after_narrative == old_narrative:
        return
    expected_digest = hashlib.sha256(before).hexdigest()
    history = capture.assets_path(root, previous['id']) / 'history'
    capture.ensure_directory(root, history)
    for suffix, raw in (('proposal.json', before), ('capture.md', old_narrative)):
        snapshot = capture.safe_path(root, history / (expected_digest + '-' + suffix))
        if snapshot.exists():
            require(snapshot.read_bytes() == raw, 'history snapshot conflict')
        else:
            capture.publish_new_bytes(snapshot, raw)
    capture.replace_bytes(narrative, old_narrative, after_narrative)
    try:
        capture.replace_bytes(destination, before, content)
    except BaseException:
        if destination.read_bytes() == before:
            capture.replace_bytes(narrative, after_narrative, old_narrative)
        raise


def retire_rekey_source(root, home, inventory):
    capture = helper('planning-capture')
    if not home.exists():
        return
    current = {}
    for filename in home.rglob('*'):
        capture.safe_path(root, filename)
        if filename.is_file():
            current[filename.relative_to(home).as_posix()] = hashlib.sha256(filename.read_bytes()).hexdigest()
    require(current == inventory, 'original package changed before retirement; preserve both and reconcile')
    shutil.rmtree(home)
    capture.sync_directory(home.parent)


def rekey_package(root, context_id, slug, operation_id, expected_digest, confirmed=False):
    require(confirmed, 'package identity migration requires explicit confirmation')
    root = pathlib.Path(root).resolve()
    capture = helper('planning-capture')
    with capture.local_writer(root):
        journal_path, state, state_before = identity_policy.local_state(root, capture)
        if context_id in state['aliases']:
            new_id = state['aliases'][context_id]
            mint_record = state['contexts'].get(operation_id)
            matches_allocation = mint_record is not None and mint_record['id'] == new_id and mint_record['request']['slug'] == slug
            require(matches_allocation, 'identity migration retry differs from original allocation')
            migration = state.get('rekeys', {}).get(operation_id)
            matches_subject = migration is not None and migration['from'] == context_id and migration['before'] == expected_digest
            require(matches_subject, 'identity migration retry differs from original subject')
            current_path = capture.resolve_document(root, new_id)
            current = capture.read_capture(current_path)
            require('lifecycle' not in current['context'], 'lifecycle-bearing rekey is unavailable; preserve the package for supported migration')
            validate(root, current)
            old_home = capture.safe_path(root, root / 'control-plane/ad-hoc' / context_id)
            retire_rekey_source(root, old_home, migration['inventory'])
            return {'id': new_id, 'previous_id': context_id, 'updated': False, 'path': str(current_path), 'admitted': False}
        original_path = capture.resolve_document(root, context_id)
        before = original_path.read_bytes()
        require(hashlib.sha256(before).hexdigest() == expected_digest, 'proposal changed since identity migration was offered')
        previous = capture.read_capture(original_path)
        require(previous['schema'] == FORMAT and previous['status'] == 'draft' and 'identity' not in previous,
                'rekey requires an unallocated draft change set')
        require(previous['context']['kind'] in ('ad-hoc', 'discovery'), 'package rekey currently supports ad hoc/discovery only')
        require('lifecycle' not in previous['context'], 'lifecycle-bearing rekey is unavailable; preserve the package for supported migration')
        validate(root, previous)
        minted = identity_policy.mint(root, previous['context']['kind'], slug, operation_id, previous['author'],
                                     previous['context'].get('origin'), True, locked=True)
        new_id = minted['id']
        bindings = [{'change_id': change['change_id'], 'operation': change['operation'], 'target': change['target'],
                     'kind': change.get('value', {}).get('kind')} for change in previous['changes']]
        issued = identity_policy.reserve_records(root, new_id, operation_id, bindings, confirmed=True, locked=True)
        mapping = issued['mapping']
        document = copy.deepcopy(previous)
        document.update(id=new_id, revision=previous['revision'] + 1)
        document['context']['id'] = new_id
        document['identity'] = {'mint': {'operation_id': operation_id, 'request_digest': minted['request_digest']},
                                'allocation': issued['state'],
                                'aliases': {'contexts': [context_id], 'canon': mapping['canon'], 'changes': mapping['changes']}}
        def remap_ref(reference):
            reference['id'] = mapping['canon'].get(reference['id'], reference['id'])
        for change in document['changes']:
            change['change_id'] = mapping['changes'][change['change_id']]
            if change['target']['type'] == 'canon_record':
                change['target']['id'] = mapping['canon'].get(change['target']['id'], change['target']['id'])
                if 'value' in change:
                    change['value']['id'] = change['target']['id']
            elif change['target']['type'] == 'canon_relationship':
                for endpoint in ('from', 'to'):
                    remap_ref(change['target'][endpoint])
                    if 'value' in change:
                        remap_ref(change['value'][endpoint])
            elif change['target']['type'] == 'work_item' and 'value' in change:
                for reference in change['value']['canon_refs']:
                    remap_ref(reference)
        for gap in document['unresolved']:
            gap['affects'] = [mapping['changes'][identity] for identity in gap['affects']]
        old_home = original_path.parent
        new_home = capture.safe_path(root, old_home.parent / new_id)
        old_relative = old_home.relative_to(root).as_posix()
        new_relative = new_home.relative_to(root).as_posix()
        for source in document['sources']:
            if 'git_commit' not in source and source['path'].startswith(old_relative + '/'):
                source['path'] = new_relative + source['path'][len(old_relative):]
        narrative_path = capture.narrative_path(original_path)
        original_narrative = narrative_path.read_bytes()
        narrative = original_narrative.replace(f'\nContext: {context_id}\n'.encode(), f'\nContext: {new_id}\n'.encode(), 1)
        narrative += (f'\n## Planning Identity Migration\n\nOperator authorized the policy and a writer-owned ad hoc package rebuild.\n\nCurrent context: {new_id}\nPrevious context: {context_id}\n\nThe helper minted the context suffix, change IDs and Canon IDs; no Git-tag reservation was used. Canon/work meaning is unchanged. Exact prior subjects are retained in history; old names in historical prose denote the prior identity. The proposal identity metadata maps all old record/change IDs to their current IDs.\n').encode()
        document['capture']['path'] = new_relative + '/' + new_id + '-capture.md'
        document['capture']['sha256'] = hashlib.sha256(narrative).hexdigest()
        shape(document)
        compose(document, baseline(root, document['base']))
        inventory = {}
        for filename in old_home.rglob('*'):
            capture.safe_path(root, filename)
            if filename.is_file():
                inventory[filename.relative_to(old_home).as_posix()] = filename.read_bytes()
        with tempfile.TemporaryDirectory(prefix='.identity-rebuild-', dir=old_home.parent) as temporary:
            staged = pathlib.Path(temporary) / new_id
            shutil.copytree(old_home, staged)
            (staged / original_path.name).unlink()
            (staged / narrative_path.name).unlink()
            retained = staged / 'assets/history' / ('identity-' + context_id)
            retained.mkdir(parents=True)
            capture.publish_new_bytes(retained / original_path.name, before)
            capture.publish_new_bytes(retained / narrative_path.name, original_narrative)
            capture.publish_new_bytes(staged / (new_id + '-proposal.json'), encoded(document))
            capture.publish_new_bytes(staged / (new_id + '-capture.md'), narrative)
            for source in document['sources']:
                if 'git_commit' not in source and source['path'].startswith(new_relative + '/'):
                    source_file = staged / source['path'][len(new_relative) + 1:]
                    require(hashlib.sha256(source_file.read_bytes()).hexdigest() == source['sha256'], 'staged source digest mismatch')
            for relative, raw in inventory.items():
                if relative not in (original_path.name, narrative_path.name):
                    require((staged / relative).read_bytes() == raw, 'history changed during rebuild')
            require({filename.relative_to(old_home).as_posix(): filename.read_bytes() for filename in old_home.rglob('*') if filename.is_file()} == inventory,
                    'package changed during identity rebuild')
            created = not new_home.exists()
            if created:
                os.rename(staged, new_home)
            else:
                for filename in new_home.rglob('*'):
                    capture.safe_path(root, filename)
                actual = {filename.relative_to(new_home).as_posix(): filename.read_bytes() for filename in new_home.rglob('*') if filename.is_file()}
                expected = {filename.relative_to(staged).as_posix(): filename.read_bytes() for filename in staged.rglob('*') if filename.is_file()}
                require(actual == expected, 'existing destination differs from exact rekey result; reconcile without overwrite')
            try:
                validate(root, capture.read_capture(new_home / (new_id + '-proposal.json')))
                journal_path, state, state_before = identity_policy.local_state(root, capture)
                state['aliases'][context_id] = new_id
                hashes = {relative: hashlib.sha256(raw).hexdigest() for relative, raw in inventory.items()}
                state.setdefault('rekeys', {})[operation_id] = {'from': context_id, 'to': new_id, 'before': expected_digest, 'inventory': hashes}
                identity_policy.persist(root, journal_path, state, state_before, capture)
            except BaseException:
                if created:
                    shutil.rmtree(new_home)
                raise
            retire_rekey_source(root, old_home, hashes)
        return {'id': new_id, 'previous_id': context_id, 'updated': True, 'path': str(new_home / (new_id + '-proposal.json')),
                'canon_ids': len(mapping['canon']), 'change_ids': len(mapping['changes']), 'admitted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument('--context')
    commands = parser.add_subparsers(dest='command', required=True)
    baseline_command = commands.add_parser('baseline', help='read an exact repository Canon/tracker/archive baseline')
    baseline_command.add_argument('--target-ref', required=True)
    navigation = commands.add_parser('refresh-navigation', help='refresh local source links without changing proposal meaning')
    navigation.add_argument('--expected-digest', required=True)
    navigation.add_argument('--confirmed', action='store_true')
    rekey = commands.add_parser('rekey')
    rekey.add_argument('--slug', required=True)
    rekey.add_argument('--operation-id', required=True)
    rekey.add_argument('--expected-digest', required=True)
    rekey.add_argument('--confirmed', action='store_true')
    commands.add_parser('complete', help='retired user-facing name; use finalize-proposal')
    parser.add_argument('--complete', action='store_true', help='retired; use finalize-proposal')
    for name in ('validate', 'preview', 'save', 'migrate', 'finalize-proposal'):
        command = commands.add_parser(name)
        command.add_argument('--request', type=pathlib.Path, required=True)
        if name in ('save', 'migrate', 'finalize-proposal'):
            command.add_argument('--expected-digest', required=True)
            command.add_argument('--record', type=pathlib.Path, required=True)
            command.add_argument('--confirmed', action='store_true')
    if '--complete' in sys.argv[1:]:
        print('Change set refused: --complete is retired; use finalize-proposal (/plan-work --finalize-proposal). No files changed.', file=sys.stderr)
        return 1
    args, unknown = parser.parse_known_args()
    if args.command == 'complete':
        print('Change set refused: complete is retired; use finalize-proposal (/plan-work --finalize-proposal). No files changed.', file=sys.stderr)
        return 1
    if unknown:
        parser.error('unrecognized arguments: ' + ' '.join(unknown))
    try:
        if args.command == 'baseline':
            require(args.target_ref.startswith('refs/heads/'), 'baseline target must be a full heads ref')
            git(args.root, 'check-ref-format', args.target_ref)
            print(json.dumps(helper('planning-repository').reference(args.root, args.target_ref), indent=2))
            return 0
        if args.command == 'refresh-navigation':
            require(args.context, 'exact current context required')
            print(json.dumps(refresh_navigation(args.root, args.context, args.expected_digest, args.confirmed), indent=2))
            return 0
        if args.command == 'rekey':
            require(args.context, 'exact source context required')
            print(json.dumps(rekey_package(args.root, args.context, args.slug, args.operation_id, args.expected_digest, args.confirmed), indent=2))
            return 0
        document = json.load(sys.stdin) if str(args.request) == '-' else canon.load_json(args.request)
        if args.command in ('save', 'migrate', 'finalize-proposal'):
            require(args.confirmed and args.context, 'save requires exact context and explicit confirmation')
            if args.command == 'finalize-proposal':
                result = finalize_proposal(args.root, args.context, document, args.expected_digest, args.record.read_text())
            else:
                result = save(args.root, args.context, document, args.expected_digest, args.record.read_text(), args.command == 'migrate')
        else:
            result = validate(args.root, document)
            if args.command == 'validate':
                result.pop('result', None)
                result.update(valid=True, changes=len(document['changes']), status=document['status'])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('Change set refused: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())