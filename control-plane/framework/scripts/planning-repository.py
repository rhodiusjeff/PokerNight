#!/usr/bin/env python3
"""Repository state composition. LOCAL MOD - HARVEST TO CPB: coordinated admission storage."""

import copy
import hashlib
import importlib.util
import json
import pathlib

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def helper(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), pathlib.Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


changes = helper('planning-change-set')
canon = changes.canon
require = canon.require
digest = changes.digest
encoded = changes.encoded
CANON = 'control-plane/canon/CANON.json'
TRACKER = 'control-plane/tracker/TRACKER.json'
ARCHIVE = 'control-plane/tracker/TRACKER_ARCHIVE.json'
PATHS = {'canon': CANON, 'tracker': TRACKER, 'archive': ARCHIVE}
LEGACY = ('control-plane/operational/SPECIFICATION.json', 'control-plane/state/execution.json')
SCHEMA = canon.SCHEMA_PATH.with_name('repository-state.schema.json')


def empty():
    return {'canon': changes.empty_base()['canon'],
            'tracker': {'schema': 'cp-repository-tracker-v1', 'revision': 0, 'nodes': [], 'dependencies': [], 'admissions': []},
            'archive': {'schema': 'cp-repository-tracker-archive-v1', 'nodes': [], 'dependencies': []}}


def latest_records(payload):
    latest = {}
    for record in payload['records']:
        if record['id'] not in latest or latest[record['id']]['revision'] < record['revision']:
            latest[record['id']] = record
    return latest


def baseline(state):
    nodes = state['tracker']['nodes'] + state['archive']['nodes']
    return {'revision': state['tracker']['revision'], 'canon': copy.deepcopy(state['canon']),
            'work_items': [copy.deepcopy(node['work']) for node in nodes],
            'dependencies': copy.deepcopy(state['tracker']['dependencies'] + state['archive']['dependencies']),
            'bound_work': [{'id': node['work']['id'], 'revision': node['work']['revision']} for node in nodes if node['binding'] is not None],
            'obsolete_work': [{'id': node['work']['id'], 'revision': node['work']['revision']} for node in nodes if node['applicability'] == 'obsolete']}


def validate(state, root=None):
    resources = []
    for filename in (SCHEMA, changes.SCHEMA_PATH, canon.SCHEMA_PATH):
        schema = canon.load_json(filename)
        resource = Resource.from_contents(schema)
        resources.extend(((filename.name, resource), (schema['$id'], resource)))
    errors = list(Draft202012Validator(canon.load_json(SCHEMA), registry=Registry().with_resources(resources)).iter_errors(state))
    require(not errors, 'repository state schema: ' + (errors[0].message if errors else ''))
    canon.validate(state['canon'], root=root)
    require(all(record['authority_status'] in ('admitted', 'retired') for record in state['canon']['records']), 'repository Canon contains unadmitted records')
    nodes = state['tracker']['nodes'] + state['archive']['nodes']
    identities = [node['work']['id'] for node in nodes]
    require(len(identities) == len(set(identities)), 'duplicate phase across tracker/archive')
    for node in nodes:
        require(node['work']['maturity'] == 'specified', 'repository work is not specified')
        require(node['status'] == 'not-started' or node['binding'] is not None, 'started phase has no bound contract')
        revisions = [item['revision'] for item in node['history']] + [node['work']['revision']]
        require(revisions == list(range(1, node['work']['revision'] + 1)), 'work history revision gap')
        require(all(item['id'] == node['work']['id'] for item in node['history']), 'work history identity differs')
        if node['binding'] is not None:
            require(node['binding']['work'] == node['work'], 'bound work was changed')
            canon.validate(node['binding']['canon'], state['canon'], root=root)
            bound_keys = {canon.record_key(item) for item in node['binding']['canon']['records']}
            require(all(canon.record_key(item) in bound_keys for item in node['work']['canon_refs']), 'bound Canon revision missing')
        if root is not None:
            for source in node['evidence']:
                canon.verify_source(root, source)
    require(all(node['status'] == 'done' for node in state['archive']['nodes']), 'archive contains incomplete work')
    admissions = state['tracker']['admissions']
    require([item['revision'] for item in admissions] == list(range(1, state['tracker']['revision'] + 1)), 'admission history revision gap')
    require(len({item['id'] for item in admissions}) == len(admissions), 'duplicate admission identity')
    probe = {'schema': changes.FORMAT, 'id': 'ADHOC-' + '0' * 32, 'revision': 1, 'title': 'State validation',
             'author': 'Validator', 'created_at': '2026-09-29T00:00:00Z', 'context': {'kind': 'ad-hoc', 'id': 'ADHOC-' + '0' * 32},
             'status': 'draft', 'capture': {'id': 'capture', 'path': 'unused.md', 'sha256': '0' * 64},
             'base': None, 'sources': [], 'changes': [], 'unresolved': []}
    changes.compose(probe, baseline(state))
    return state


def blob(root, commit, relative):
    listing = changes.git(root, 'ls-tree', commit, '--', relative).decode().strip()
    if not listing:
        return None
    require(listing.startswith('100644 blob ') or listing.startswith('100755 blob '), 'state must be a regular Git blob')
    return changes.git(root, 'show', commit + ':' + relative)


def snapshot(root, commit):
    raw = {relative: blob(root, commit, relative) for relative in (*PATHS.values(), *LEGACY)}
    present = [raw[relative] is not None for relative in PATHS.values()]
    if any(present):
        require(all(present), 'incomplete repository Canon/tracker/archive set')
        require(all(raw[relative] is None for relative in LEGACY), 'competing legacy operational authority')
        state = {key: changes.helper('planning-evidence').load_bytes(raw[relative]) for key, relative in PATHS.items()}
    else:
        require(all(raw[relative] is not None for relative in LEGACY), 'missing baseline is not an empty repository')
        contract = changes.helper('planning-contract')
        require(json.loads(raw[LEGACY[0]]) == contract.empty_specification() and
                json.loads(raw[LEGACY[1]]) == {'phases': {}, 'contracts': {}}, 'populated legacy state requires explicit typed migration')
        state = empty()
    validate(state)
    return {'schema': 'cp-repository-snapshot-v1', 'commit': commit,
            'files': {relative: hashlib.sha256(content).hexdigest() if content is not None else None for relative, content in raw.items()},
            'state': state}


def reference(root, target_ref):
    commit = changes.git(root, 'rev-parse', '--verify', target_ref + '^{commit}').decode().strip()
    selected = snapshot(root, commit)
    primary = CANON if selected['files'][CANON] is not None else LEGACY[0]
    return {'target_ref': target_ref, 'git_commit': commit, 'path': primary,
            'revision': selected['state']['tracker']['revision'], 'sha256': selected['files'][primary], 'files': selected['files']}


def compose(proposal, selected, decision_digest):
    state = validate(copy.deepcopy(selected['state']))
    previous = state['tracker']['admissions']
    require(not any(item['proposal_id'] == proposal['id'] and item['proposal_revision'] == proposal['revision'] for item in previous), 'proposal revision already admitted')
    proposed_base = proposal['base']
    require(proposed_base is not None and proposed_base['git_commit'] == selected['commit'] and
            proposed_base['revision'] == state['tracker']['revision'], 'stale repository baseline')
    if 'files' in proposed_base:
        require(proposed_base['files'] == selected['files'], 'baseline file bindings differ')
    else:
        require(state == empty(), 'repository proposal must pin all three authority files')
    require(selected['files'].get(proposed_base['path']) == proposed_base['sha256'], 'baseline primary digest differs')
    require(proposal['status'] == 'complete', 'complete proposal required for admission')
    result = copy.deepcopy(changes.compose(proposal, baseline(state))['result'])
    original_keys = {canon.record_key(record) for record in state['canon']['records']}
    for record in result['canon']['records']:
        if canon.record_key(record) not in original_keys and record['authority_status'] == 'proposed':
            record['authority_status'] = 'admitted'
    state['canon'] = result['canon']
    active = {node['work']['id']: node for node in state['tracker']['nodes']}
    archived = {node['work']['id']: node for node in state['archive']['nodes']}
    for change in proposal['changes']:
        if change['target']['type'] != 'work_item':
            continue
        identity = change['target']['id']
        require(identity not in archived, 'archived phase cannot be amended or reused')
        node = active.get(identity)
        require(node is None or (node['status'] == 'not-started' and node['binding'] is None), 'started work requires a new revision phase')
        if change['operation'] == 'obsolete':
            node['applicability'] = 'obsolete'
        elif node is None:
            node = {'work': copy.deepcopy(change['value']), 'status': 'not-started', 'applicability': 'active',
                    'history': [], 'binding': None, 'evidence': []}
            state['tracker']['nodes'].append(node)
            active[identity] = node
        else:
            node['history'].append(node['work'])
            node['work'] = copy.deepcopy(change['value'])
            node['applicability'] = 'active'
    old_archived_edges = state['archive']['dependencies']
    require(all(edge in result['dependencies'] for edge in old_archived_edges), 'archive dependency history cannot be rewritten')
    state['tracker']['dependencies'] = [edge for edge in result['dependencies'] if edge not in old_archived_edges]
    admission_id = digest(proposal)
    old_sources = {source['id'] for source in selected['state']['canon']['sources']}
    for source in state['canon']['sources']:
        if source['id'] not in old_sources:
            source['path'] = f'control-plane/evidence/admissions/{admission_id}/sources/{source["sha256"]}.bin'
            source.pop('git_commit', None)
    state['tracker']['revision'] += 1
    state['tracker']['admissions'].append({'id': admission_id, 'proposal_id': proposal['id'], 'proposal_revision': proposal['revision'],
        'proposal_digest': digest(proposal), 'decision_digest': decision_digest, 'base_digest': digest(selected),
        'revision': state['tracker']['revision']})
    validate(state)
    return state


def resolve(root, phase_id, commit):
    state = snapshot(root, commit)['state']
    nodes = state['tracker']['nodes'] + state['archive']['nodes']
    found = [node for node in nodes if node['work']['id'] == phase_id]
    require(len(found) == 1, 'repository phase missing or ambiguous')
    node = found[0]
    dependencies = [edge['from']['id'] for edge in state['tracker']['dependencies'] + state['archive']['dependencies'] if edge['to']['id'] == phase_id]
    statuses = {item['work']['id']: item['status'] for item in nodes}
    return {'source': 'repository', 'phase_id': phase_id, 'phase_status': node['status'],
            'canon': CANON, 'tracker': TRACKER, 'archive': ARCHIVE, 'status_path': TRACKER if node in state['tracker']['nodes'] else ARCHIVE,
            'horizon': None, 'packet': None, 'ledgers': None, 'target_commit': commit,
            'operational_revision': state['tracker']['revision'], 'operational_digest': digest(state),
            'phase_contract': node['work'], 'contract_content': node['binding'] or {'work': node['work'], 'canon': state['canon']},
            'contract_source': 'retained-bound' if node['binding'] is not None else 'current',
            'dependencies': dependencies, 'dependency_statuses': {identity: statuses[identity] for identity in dependencies},
            'blocked_dependencies': [identity for identity in dependencies if statuses[identity] != 'done'],
            'archive_only': node in state['archive']['nodes'], 'applicability': node['applicability'], 'executable': False}