#!/usr/bin/env python3
"""Exact change-set evidence. LOCAL MOD - HARVEST TO CPB: no embedded source copies."""

import copy
import hashlib
import pathlib
import tempfile
import os

import importlib.util


def helper(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), pathlib.Path(__file__).with_name(name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


repository = helper('planning-repository')
changes = repository.changes
capture = helper('planning-capture')
contract = capture.contract
require = contract.require
digest = contract.digest
encoded = changes.encoded


def location(root, identity):
    return capture.assets_path(root, identity) / 'admission' / 'evidence'


def read_events(root, identity):
    home = location(root, identity)
    events = []
    previous = None
    if not home.exists():
        return events
    for ordinal, folder in enumerate(sorted(home.iterdir()), 1):
        folder = capture.safe_path(root, folder)
        require(folder.is_dir(), 'unexpected evidence entry')
        event = contract.load_json(folder / 'event.json')
        require(folder.name == f'{ordinal:06d}-' + digest(event) and event['previous'] == previous, 'evidence chain differs')
        for name, expected in event['files'].items():
            filename = capture.safe_path(root, folder / name)
            require(filename.is_file() and hashlib.sha256(filename.read_bytes()).hexdigest() == expected, 'evidence file digest mismatch')
        require(digest(contract.load_json(folder / 'input.json')) == event['subject_digest'], 'review input binding differs')
        require({item.name for item in folder.iterdir()} == {'event.json', *event['files']}, 'unexpected evidence files')
        events.append(event)
        previous = digest(event)
    return events


def subject(root, proposal):
    changes.validate(root, proposal)
    require(proposal['status'] == 'complete', 'independent admission review requires a complete change set')
    selected = repository.snapshot(root, proposal['base']['git_commit'])
    result = repository.compose(proposal, selected, '0' * 64)
    return {'schema': 'cp-change-review-input-v1', 'proposal': copy.deepcopy(proposal),
            'base': selected, 'result_template': result}


def subjects(root, proposal):
    current = subject(root, proposal)
    return {'capture_digest': proposal['capture']['sha256'], 'sources_digest': digest(proposal['sources']),
            'proposal_digest': digest(proposal), 'input_digest': digest(current)}


def warnings(events):
    findings = {}
    for event in events:
        request = event['request']
        if event['operation'] in ('round', 'review'):
            kind = request.get('kind', 'REVIEW')
            for ordinal, observation in enumerate(request.get('observations', []), 1):
                identity = observation.get('id', f'{kind}{event["sequence"]:02d}-F{ordinal:02d}')
                findings[identity] = {'id': identity, 'register': kind, 'status': 'open',
                                      'summary': observation['summary'], 'subject_digest': event['subject_digest']}
        elif event['operation'] == 'disposition':
            identity = request['identity']
            require(identity in findings, 'unknown finding disposition')
            findings[identity].update(status=request['status'], subject_digest=event['subject_digest'])
    return list(findings.values())


def review_records(events, proposal, selected_ids, input_digest):
    require(isinstance(selected_ids, list) and selected_ids and len(selected_ids) == len(set(selected_ids)), 'select distinct independent reviews')
    result = []
    for identity in selected_ids:
        found = [event for event in events if event['operation'] == 'review' and event['request']['request_id'] == identity]
        require(len(found) == 1, 'review identity missing or ambiguous')
        event = found[0]
        require(event['subject_digest'] == input_digest, 'review input is stale')
        request = event['request']
        attestation = request['attestation']
        helper('planning-evidence').attribution(attestation)
        require(attestation.get('independent') is True and attestation['actor'].strip().casefold() != proposal['author'].strip().casefold(), 'proposal author is not an independent reviewer')
        result.append({'id': identity, 'subject_digest': digest(proposal), 'reviewer': attestation['actor'],
                       'independent': True, 'scope': attestation['scope'], 'report': f'evidence/{event["sequence"]:06d}-{digest(event)}/report.md',
                       'findings': [{'id': item['id'], 'status': item['status'] if item['subject_digest'] == input_digest else 'open',
                                    'summary': item['summary']} for item in warnings(events)]})
    return result


def selected(root, proposal, identity, events=None, current_subject=None):
    events = read_events(root, proposal['id']) if events is None else events
    current_subject = subject(root, proposal) if current_subject is None else current_subject
    input_digest = digest(current_subject)
    finals = [event for event in events if event['operation'] == 'finalize-decision']
    require(finals and finals[-1]['request']['identity'] == identity, 'decision is not the current finalized selection')
    final = finals[-1]
    drafts = [event for event in events if event['operation'] == 'draft-decision' and event['request']['identity'] == identity]
    require(len(drafts) == 1, 'decision draft missing or ambiguous')
    draft = drafts[0]
    require(draft['subject_digest'] == final['subject_digest'] == input_digest, 'decision input is stale')
    require(final['request']['expected_draft_digest'] == digest(draft), 'decision draft digest differs')
    before_draft = events[:draft['sequence'] - 1]
    before_final = events[:final['sequence'] - 1]
    require(warnings(before_draft) == warnings(before_final) == warnings(events), 'finding posture changed; refresh decision')
    decision = copy.deepcopy(draft['decision'])
    reviews = review_records(events, proposal, draft['request']['review_ids'], input_digest)
    confirmation = final['request']['confirmation']
    helper('planning-evidence').attribution(confirmation)
    require(confirmation.get('decision_digest') == digest(decision) and confirmation['actor'] == decision['actor'] and
            confirmation['authority'] == decision['authority'], 'decision confirmation differs')
    contract.validate_evidence(proposal, reviews, decision)
    return {'id': identity, 'decision': decision, 'confirmation': confirmation, 'input_digest': input_digest}, reviews


def apply(root, proposal, operation, request, confirmed):
    require(confirmed, 'evidence operation requires actual confirmation')
    root = pathlib.Path(root).resolve()
    assert_mutable(root, proposal['id'])
    current = subject(root, proposal)
    events = read_events(root, proposal['id'])
    identity = request.get('request_id', request.get('identity'))
    require(isinstance(identity, str) and identity.strip(), 'evidence request identity required')
    request = copy.deepcopy(request)
    payload = {'input.json': encoded(current)}
    if operation == 'review':
        require(request['review_input'] == current, 'independent review input is stale')
        report = capture.safe_path(root, root / request['report_path']).read_bytes()
        require(report.decode('utf-8').strip(), 'independent review report required')
        payload['report.md'] = report
        request['report_path'] = 'report.md'
        attestation = request['attestation']
        helper('planning-evidence').attribution(attestation)
        require(attestation.get('independent') is True and attestation['actor'].strip().casefold() != proposal['author'].strip().casefold(), 'proposal author is not independent')
        require(attestation.get('scope'), 'review scope required')
        del request['review_input']
    elif operation == 'round':
        require(request['kind'] in ('SCRUB', 'REVIEW'), 'unknown finding register')
        payload['report.md'] = request.pop('report').encode('utf-8')
        require(payload['report.md'].strip(), 'finding report required')
    elif operation == 'disposition':
        evidence = request['evidence']
        helper('planning-evidence').attribution(evidence)
        require(request['kind'] in ('SCRUB', 'REVIEW') and request['status'] in helper('planning-evidence').STATUSES, 'invalid disposition')
        require(any(item['id'] == request['identity'] and item['register'] == request['kind'] for item in warnings(events)), 'finding does not exist in register')
        needed = {'resolved': 'verification', 'deferred': 'revisit', 'superseded': 'successor'}.get(request['status'])
        require(needed is None or evidence.get(needed), 'disposition evidence incomplete')
    elif operation not in ('draft-decision', 'finalize-decision'):
        raise ValueError('unsupported evidence operation')
    for observation in request.get('observations', []):
        require(all(observation.get(key) for key in ('summary', 'severity', 'consequence', 'scope', 'recommendation', 'locations')), 'finding detail missing')
    event = {'sequence': len(events) + 1, 'previous': digest(events[-1]) if events else None,
             'operation': operation, 'subject_digest': digest(current), 'request': request,
             'files': {name: hashlib.sha256(raw).hexdigest() for name, raw in payload.items()}}
    for previous in events:
        if previous['operation'] == operation and previous['request'].get('request_id', previous['request'].get('identity')) == identity:
            require(previous['request'] == request and previous['subject_digest'] == event['subject_digest'] and previous['files'] == event['files'], 'evidence identity reused with changed subject')
            return {'evidence_result': digest(previous), 'updated': False}
    if operation == 'draft-decision':
        reviews = review_records(events, proposal, request['review_ids'], digest(current))
        require(set(request['fields']) <= set(contract.DECISION['properties']), 'unknown decision field')
        decision = {**request['fields'], 'schema': 'cp-plan-decision-v1', 'subject_digest': digest(proposal), 'reviews_digest': digest(reviews)}
        require(all(key not in request['fields'] or request['fields'][key] == decision[key] for key in ('schema', 'subject_digest', 'reviews_digest')), 'decision binding differs')
        event['decision'] = decision
    elif operation == 'finalize-decision':
        finals = [entry for entry in events if entry['operation'] == operation]
        require(request.get('supersedes') == (finals[-1]['request']['identity'] if finals else None), 'explicit decision supersession required')
        selected(root, proposal, identity, [*events, event], current)
    folder = location(root, proposal['id']) / (f'{event["sequence"]:06d}-' + digest(event))
    capture.ensure_directory(root, folder.parent)
    with tempfile.TemporaryDirectory(prefix='.evidence-', dir=folder.parent.parent) as temporary:
        staged = pathlib.Path(temporary) / 'event'
        staged.mkdir()
        for name, raw in {**payload, 'event.json': encoded(event)}.items():
            capture.publish_new_bytes(staged / name, raw)
        os.rename(staged, folder)
    read_events(root, proposal['id'])
    return {'evidence_result': digest(event), 'review_id': identity if operation == 'review' else None, 'updated': True}


def cli(args):
    filename = capture.resolve_document(args.root, args.context)
    proposal = capture.read_capture(filename)
    current = subjects(args.root, proposal)
    if args.command == 'export-review':
        return {'input': subject(args.root, proposal), 'subjects': current}
    if args.command == 'previous-findings':
        return {'context_id': proposal['id'], 'previous_findings': warnings(read_events(args.root, proposal['id']))}
    if args.command == 'inspect':
        return {**current, 'document_digest': hashlib.sha256(filename.read_bytes()).hexdigest(), 'warnings': warnings(read_events(args.root, proposal['id']))}
    require(hashlib.sha256(filename.read_bytes()).hexdigest() == args.expected_digest, 'proposal changed since evidence offer')
    request = json_load_stdin() if str(args.request) == '-' else contract.load_json(capture.safe_path(args.root, pathlib.Path(args.root) / args.request))
    with capture.local_writer(args.root):
        require(hashlib.sha256(filename.read_bytes()).hexdigest() == args.expected_digest, 'proposal changed during evidence write')
        return {**apply(args.root, proposal, args.command, request, args.confirmed), 'document_digest': args.expected_digest}


def json_load_stdin():
    import json
    import sys
    return json.load(sys.stdin)


def assert_mutable(root, identity):
    home = pathlib.Path(root) / 'control-plane/state/planning-local/publication'
    claim = capture.safe_path(root, home / 'claims' / (identity + '.json'))
    if claim.exists():
        publication = helper('planning-publication')
        selected = contract.load_json(claim)
        events = publication.journal(root, publication.attempt_directory(root, selected['attempt_id']))
        require(any(event['state'] in ('applied', 'retired', 'withdrawn') for event in events),
                'active publication freezes proposal/evidence; close and retire the exact attempt first')


def read_view(root, identity):
    filename = capture.resolve_document(root, identity)
    proposal = capture.read_capture(filename)
    require(proposal['schema'] == changes.FORMAT, 'change-set proposal required')
    return filename, {'schema': 'cp-change-review-state-v1', 'id': proposal['id'], 'proposal': proposal,
                      '_root': str(root), 'workflow': {}}


def source_bytes(root, source, proposal):
    source = changes.source_at_base(source, changes.baseline(root, proposal['base']), proposal['base'])
    changes.canon.verify_source(root, source)
    if source.get('git_commit'):
        return repository.blob(root, source['git_commit'], source['path'])
    return capture.safe_path(root, pathlib.Path(root) / source['path']).read_bytes()


def bundle(root, proposal, decision_id, events, clean, raw_proposal, narrative, source_payload, evidence_payload):
    final, reviews = selected(root, proposal, decision_id, events, clean)
    require(clean['proposal'] == proposal, 'bundle review proposal differs')
    require(clean['result_template'] == repository.compose(proposal, clean['base'], '0' * 64), 'reviewed result differs')
    require(helper('planning-evidence').load_bytes(raw_proposal) == proposal and
            hashlib.sha256(narrative).hexdigest() == proposal['capture']['sha256'], 'bundle capture/proposal differs')
    for source in proposal['sources']:
        raw = source_payload['sources/' + source['sha256'] + '.bin']
        require(hashlib.sha256(raw).hexdigest() == source['sha256'], 'bundled source differs')
    result = repository.compose(proposal, clean['base'], digest(final['decision']))
    payload = {'base.json': encoded(clean['base']), 'proposal.json': encoded(proposal),
               'reviews.json': encoded(reviews), 'decision.json': encoded(final['decision']),
               'result.json': encoded(result), 'review-input.json': encoded(clean),
               'events.json': encoded(events), 'capture-proposal.json': raw_proposal,
               'capture-narrative.md': narrative, **source_payload, **evidence_payload}
    manifest = {'schema': 'cp-change-admission-bundle-v1', 'context_id': proposal['id'], 'decision_id': decision_id,
                'admission_id': digest(proposal), 'subjects': {'proposal_digest': digest(proposal),
                'input_digest': digest(clean), 'capture_digest': proposal['capture']['sha256'], 'sources_digest': digest(proposal['sources'])},
                'finalized_decision_digest': digest(final), 'base_digest': digest(clean['base']), 'decision_digest': digest(final['decision']),
                'files': {name: hashlib.sha256(raw).hexdigest() for name, raw in payload.items()}}
    payload['manifest.json'] = encoded(manifest)
    return payload, {'result': result, 'already_applied_revision': None, 'warnings': warnings(events)}


def prepare(root, identity, decision_id, expected_digest, confirmed):
    require(confirmed, 'bundle preparation requires actual confirmation')
    root = pathlib.Path(root).resolve()
    with capture.local_writer(root):
        filename = capture.resolve_document(root, identity)
        raw = filename.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected_digest, 'proposal changed since bundle preparation')
        proposal = capture.read_capture(filename)
        clean = subject(root, proposal)
        events = read_events(root, identity)
        sources = {'sources/' + source['sha256'] + '.bin': source_bytes(root, source, proposal) for source in proposal['sources']}
        evidence_files = {}
        home = location(root, identity)
        if home.exists():
            for item in home.rglob('*'):
                item = capture.safe_path(root, item)
                if item.is_file():
                    evidence_files['evidence/' + item.relative_to(home).as_posix()] = item.read_bytes()
        payload, validation = bundle(root, proposal, decision_id, events, clean, raw,
            capture.narrative_path(filename).read_bytes(), sources, evidence_files)
        manifest = helper('planning-evidence').load_bytes(payload['manifest.json'])
        destination = capture.assets_path(root, identity) / 'admission' / digest(manifest)
        created = not destination.exists()
        if created:
            capture.ensure_directory(root, destination.parent)
            with tempfile.TemporaryDirectory(prefix='.bundle-', dir=destination.parent) as temporary:
                staged = pathlib.Path(temporary) / 'bundle'
                staged.mkdir()
                for name, content in payload.items():
                    capture.ensure_directory(root, (staged / name).parent)
                    capture.publish_new_bytes(staged / name, content)
                os.rename(staged, destination)
        verify(root, destination)
        return {'status': 'prepared-local', 'bundle': str(destination), 'bundle_id': destination.name,
                'created': created, 'revision': validation['result']['tracker']['revision'], 'live_admission': False}


def verify(root, directory, expected_identity=None):
    root = pathlib.Path(root).resolve()
    directory = capture.safe_path(root, pathlib.Path(directory))
    manifest = contract.load_json(directory / 'manifest.json')
    require(manifest['schema'] == 'cp-change-admission-bundle-v1' and digest(manifest) == (expected_identity or directory.name), 'bundle manifest identity differs')
    actual = set()
    for item in directory.rglob('*'):
        item = capture.safe_path(root, item)
        if item.is_file():
            actual.add(item.relative_to(directory).as_posix())
    require(actual == {*manifest['files'], 'manifest.json'}, 'unexpected or missing bundle files')
    payload = {}
    for name, expected in manifest['files'].items():
        filename = capture.safe_path(root, directory / name)
        require(filename.is_relative_to(directory), 'bundle path escapes directory')
        payload[name] = filename.read_bytes()
        require(hashlib.sha256(payload[name]).hexdigest() == expected, 'bundle file digest differs')
    load = helper('planning-evidence').load_bytes
    proposal, events, clean = (load(payload[name]) for name in ('proposal.json', 'events.json', 'review-input.json'))
    previous = None
    for ordinal, event in enumerate(events, 1):
        require(event['sequence'] == ordinal and event['previous'] == previous, 'bundled evidence chain differs')
        prefix = f'evidence/{ordinal:06d}-{digest(event)}/'
        require(load(payload[prefix + 'event.json']) == event, 'bundled event differs')
        for name, expected in event['files'].items():
            require(hashlib.sha256(payload[prefix + name]).hexdigest() == expected, 'bundled review file differs')
        require(digest(load(payload[prefix + 'input.json'])) == event['subject_digest'], 'bundled review input differs')
        previous = digest(event)
    rebuilt, validation = bundle(root, proposal, manifest['decision_id'], events, clean,
        payload['capture-proposal.json'], payload['capture-narrative.md'],
        {name: raw for name, raw in payload.items() if name.startswith('sources/')},
        {name: raw for name, raw in payload.items() if name.startswith('evidence/')})
    require(rebuilt == {**payload, 'manifest.json': (directory / 'manifest.json').read_bytes()}, 'bundle differs from reconstructed approved result')
    view = {'schema': 'cp-change-review-state-v1', 'id': proposal['id'], 'proposal': proposal, '_root': str(root), 'workflow': {}}
    return manifest, view, rebuilt, validation


def validate_bundle(root, directory, check_current=True):
    manifest, view, payload, validation = verify(root, directory)
    if check_current:
        filename, current = read_view(root, view['id'])
        require(current['proposal'] == view['proposal'], 'bundle proposal is stale')
        final, reviews = selected(root, current['proposal'], manifest['decision_id'])
        require(digest(final) == manifest['finalized_decision_digest'] and
                encoded(reviews) == payload['reviews.json'], 'bundle evidence selection is stale')
    return {'status': 'bundle-valid-local', 'bundle_id': digest(manifest), 'manifest': manifest, **validation}


def expected_files(root, header):
    offer = header['offer']
    manifest, view, payload, validation = verify(root, pathlib.Path(root) / offer['bundle'], offer['bundle_id'])
    require(all(offer[key] == manifest[key] for key in ('base_digest', 'decision_digest')) and
            offer['proposal_digest'] == manifest['subjects']['proposal_digest'], 'offer differs from bundle')
    prefix = 'control-plane/evidence/admissions/' + manifest['admission_id']
    files = {prefix + '/' + name: raw for name, raw in payload.items()}
    files[prefix + '/publication.json'] = encoded(header)
    selected = helper('planning-evidence').load_bytes(payload['base.json'])
    result = validation['result']
    for key, relative in repository.PATHS.items():
        if result[key] != selected['state'][key] or selected['files'][relative] is None:
            files[relative] = encoded(result[key])
    for relative in repository.LEGACY:
        if selected['files'][relative] is not None:
            files[relative] = None
    return files, {'canon': repository.CANON, 'tracker': repository.TRACKER, 'archive': repository.ARCHIVE,
                   'prefix': prefix, 'schema': 'cp-change-admission-bundle-v1'}