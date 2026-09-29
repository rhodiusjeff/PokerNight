#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
python3 - "$ROOT" <<'PY'
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

import yaml

repository = pathlib.Path(sys.argv.pop())
script = repository / 'control-plane/framework/scripts/planning-work.py'
module_spec = importlib.util.spec_from_file_location('planning_work', script)
work = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(work)
capture, contract = work.capture, work.contract


def load_helper(name):
    specification = importlib.util.spec_from_file_location(name.replace('-', '_'), script.with_name(name + '.py'))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve()
        self.identity = 'ADHOC-' + 'a' * 32
        self.source = self.root / 'source.txt'
        self.source.write_bytes(b'Exact input\r\nDefinition: scope and exceptions remain unresolved.\n')
        capture.create_capture(SimpleNamespace(root=self.root, id=self.identity, confirmed=True,
            sources=[self.source], kind='ad-hoc', origin_phase=None, origin_specification=None,
            title='Workflow fixture', author='Fixture Author'))
        self.path = capture.resolve_document(self.root, self.identity)
        self.base = contract.empty_specification()
        self.execution = {'phases': {}, 'contracts': {}}
        self.request = {'request_id': 'draft-1', 'text': 'Definition with clauses; work remains unresolved.',
                        'source_ids': ['source-1'], 'questions': ['Which exception applies?'],
                        'schema_expansions': ['Structured clauses are not represented by the kernel.']}

    def digest(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def full_request(self):
        result = copy.deepcopy(self.base['content'])
        result['canon']['DEF-1'] = {'kind': 'definition', 'text': self.request['text'],
                                    'status': 'active', 'sources': ['source-1']}
        result['phases']['PHASE-1'] = {'title': 'Fixture work', 'specification': 'Complete fixture contract',
            'status': 'active', 'canon_ids': ['DEF-1'], 'acceptance': ['Fixture check passes']}
        result['dag']['order'] = ['PHASE-1']
        return {'result': result, 'started_dispositions': {}}

    def test_partial_draft_preserves_other_keys_and_no_fake_work(self):
        reserved = {'findings': {}, 'reviews': [], 'decision': {'drafts': []}, 'admission': {}}
        capture.mutate_capture(self.root, self.identity, self.digest(),
            lambda document: {**document, 'workflow': copy.deepcopy(reserved)}, True)
        original = self.path.read_bytes()
        result = work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)
        snapshot = self.path.parent / 'assets/history' / (hashlib.sha256(original).hexdigest() + '-proposal.json')
        self.assertEqual(pathlib.Path(result['previous_snapshot']), snapshot)
        self.assertEqual(snapshot.read_bytes(), original)
        self.assertFalse((self.path.parent / 'assets' / self.identity).exists())
        document = capture.read_capture(self.path)
        self.assertNotIn('proposal', document)
        self.assertEqual(document['workflow']['planning']['current']['canon']['content']['summary'], self.request['text'])
        self.assertEqual(document['workflow']['planning']['status'], 'draft')
        self.assertEqual({key: document['workflow'][key] for key in reserved}, reserved)
        self.assertFalse((self.root / 'control-plane/operational').exists())

    def test_stale_digest_and_confirmation_refuse(self):
        original = self.path.read_bytes()
        for expected, confirmed in [('0' * 64, True), (self.digest(), False)]:
            with self.assertRaises(ValueError):
                work.draft(self.root, self.identity, 'work', self.request, expected, confirmed)
        self.assertEqual(self.path.read_bytes(), original)

    def test_draft_retry_and_changed_identity(self):
        work.draft(self.root, self.identity, 'work', self.request, self.digest(), True)
        result = work.draft(self.root, self.identity, 'work', self.request, self.digest(), True)
        self.assertFalse(result['updated'])
        with self.assertRaisesRegex(ValueError, 'identity reused'):
            work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)

    def test_current_sections_replace_without_losing_other_section(self):
        work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)
        work_request = {**self.request, 'request_id': 'work-1', 'text': 'Current work'}
        work.draft(self.root, self.identity, 'work', work_request, self.digest(), True)
        revised = {key: value for key, value in self.request.items() if key != 'text'}
        revised.update(request_id='canon-2', content={'requirements': [{'id': 'candidate-1', 'text': 'Current requirement'}]})
        work.draft(self.root, self.identity, 'canon', revised, self.digest(), True)
        planning = capture.read_capture(self.path)['workflow']['planning']
        self.assertEqual(set(planning['current']), {'canon', 'work'})
        self.assertEqual(planning['current']['work']['content']['summary'], 'Current work')
        self.assertEqual(planning['current']['canon']['content'], revised['content'])
        self.assertNotIn('drafts', planning)
        retry = work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)
        self.assertFalse(retry['updated'])
        self.assertEqual(capture.read_capture(self.path)['workflow']['planning'], planning)

    def test_markdown_request_refused_without_writes(self):
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'not Markdown'):
            work.draft(self.root, self.identity, 'canon', {**self.request, 'text': '# Mixed format'}, self.digest(), True)
        self.assertEqual(self.path.read_bytes(), before)

    def test_stdin_request_needs_no_permanent_request_file(self):
        result = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--context', self.identity,
            'draft', '--section', 'canon', '--request', '-', '--expected-digest', self.digest(), '--confirmed'],
            input=json.dumps(self.request), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.path.parent / 'assets/requests').exists())

    def test_source_draft_proposal_clean_export_cli(self):
        def command(name, *arguments):
            result = subprocess.run([sys.executable, str(script), '--root', str(self.root),
                '--context', self.identity, name, *arguments], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

        inputs = {'draft': self.request, 'complete': self.full_request(), 'base': self.base, 'execution': self.execution}
        for name, value in inputs.items():
            (self.root / (name + '.json')).write_text(json.dumps(value))
        command('draft', '--section', 'canon', '--request', str(self.root / 'draft.json'),
                '--expected-digest', self.digest(), '--confirmed')
        original = self.path.read_bytes()
        arguments = ['--request', str(self.root / 'complete.json'), '--base', str(self.root / 'base.json'),
                     '--execution', str(self.root / 'execution.json'), '--expected-digest', self.digest()]
        proposal = command('compose', *arguments)
        self.assertEqual(self.path.read_bytes(), original)
        command('propose', *arguments, '--confirmed')
        self.assertEqual(capture.read_capture(self.path)['proposal'], proposal)
        exported = subprocess.run([sys.executable, str(script.with_name('planning-evidence.py')),
            '--root', str(self.root), '--context', self.identity, 'export-review'], capture_output=True, text=True)
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertNotIn('previous_findings', json.loads(exported.stdout))
        self.assertEqual(proposal['sources'], capture.read_capture(self.path)['sources'])
        self.assertEqual(proposal['author'], 'Fixture Author')
        self.assertEqual(proposal['revision'], 1)
        self.assertFalse((self.root / 'control-plane/operational').exists())

    def test_horizon_uses_same_writer_without_adhoc_substitute(self):
        document = capture.read_capture(self.path)
        document.update(id='H007', kind='horizon')
        destination = self.root / 'control-plane/horizons/H007-fixture/planning/H007.md'
        destination.parent.mkdir(parents=True)
        destination.write_text(capture.render(document))
        original = self.path.read_bytes()
        expected = hashlib.sha256(destination.read_bytes()).hexdigest()
        work.draft(self.root, 'H007', 'work', self.request, expected, True)
        expected = hashlib.sha256(destination.read_bytes()).hexdigest()
        work.propose(self.root, 'H007', self.base, self.execution, self.full_request(), expected, True)
        self.assertEqual(capture.read_capture(destination)['proposal']['id'], 'H007')
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse((destination.parent.parent / 'TRACKER.json').exists())

    def test_uncaptured_source_and_reserved_request_fields_refuse(self):
        original = self.path.read_bytes()
        for request in ({**self.request, 'source_ids': ['missing']}, {**self.request, 'decision': 'approval'}):
            with self.assertRaises(ValueError):
                work.draft(self.root, self.identity, 'canon', request, self.digest(), True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_authorized_context_blocks_planning_even_workflow_only(self):
        capture.mutate_capture(self.root, self.identity, self.digest(), lambda document: {
            **document, 'workflow': {'admission': {'status': 'authorized-for-merge'}}}, True)
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'withdrawal'):
            work.draft(self.root, self.identity, 'work', self.request, self.digest(), True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_complete_retry_next_revision_and_stale_digest(self):
        request = self.full_request()
        old_digest = self.digest()
        work.propose(self.root, self.identity, self.base, self.execution, request, old_digest, True)
        with self.assertRaisesRegex(ValueError, 'capture changed'):
            work.propose(self.root, self.identity, self.base, self.execution, request, old_digest, True)
        repeated = work.propose(self.root, self.identity, self.base, self.execution, request, self.digest(), True)
        self.assertFalse(repeated['updated'])
        request['result']['canon']['DEF-1']['text'] += ' Explicitly resolved exception.'
        work.propose(self.root, self.identity, self.base, self.execution, request, self.digest(), True)
        self.assertEqual(capture.read_capture(self.path)['proposal']['revision'], 2)

    def test_noop_and_tampered_base_refuse_without_writes(self):
        original = self.path.read_bytes()
        request = {'result': self.base['content'], 'started_dispositions': {}}
        with self.assertRaisesRegex(ValueError, 'no-op'):
            work.propose(self.root, self.identity, self.base, self.execution, request, self.digest(), True)
        base = {**self.base, 'content_digest': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            work.compose(self.root, self.identity, base, self.execution, self.full_request(), self.digest())
        self.assertEqual(self.path.read_bytes(), original)

    def admitted_base(self):
        content = self.full_request()['result']
        digest = contract.digest(content)
        return {'schema': 'cp-operational-specification-v1', 'revision': 1, 'previous_revision': 0,
                'content': content, 'content_digest': digest, 'admissions': [{
                    'proposal_id': 'synthetic-prior', 'proposal_revision': 1, 'subject_digest': 'a' * 64,
                    'decision_digest': 'b' * 64, 'revision': 1, 'content_digest': digest}]}

    def test_explicit_modify_obsolete_and_no_deletion(self):
        base = self.admitted_base()
        result = copy.deepcopy(base['content'])
        result['canon']['DEF-1']['text'] += ' Revised definition.'
        proposal = work.build_proposal(capture.read_capture(self.path), base, self.execution,
                                       {'result': result, 'started_dispositions': {}})
        self.assertEqual(proposal['changes'][0]['operation'], 'modify')
        self.assertEqual(proposal['changes'][0]['before_digest'], contract.digest(base['content']['canon']['DEF-1']))
        result = copy.deepcopy(base['content'])
        result['canon']['DEF-1']['status'] = 'obsolete'
        result['phases']['PHASE-1']['status'] = 'obsolete'
        result['dag']['order'] = []
        proposal = work.build_proposal(capture.read_capture(self.path), base, self.execution,
                                       {'result': result, 'started_dispositions': {}})
        self.assertEqual([change['operation'] for change in proposal['changes']], ['obsolete', 'obsolete'])
        result['canon']['DEF-1']['text'] += ' Not a valid obsoletion.'
        with self.assertRaisesRegex(ValueError, 'obsoletion must preserve'):
            work.build_proposal(capture.read_capture(self.path), base, self.execution,
                                {'result': result, 'started_dispositions': {}})
        with self.assertRaisesRegex(ValueError, 'cannot disappear'):
            work.build_proposal(capture.read_capture(self.path), base, self.execution,
                                {'result': self.base['content'], 'started_dispositions': {}})

    def test_started_work_requires_explicit_retained_contract_disposition(self):
        base = self.admitted_base()
        digest = base['content_digest']
        execution = {'phases': {'PHASE-1': {'status': 'done', 'contract_digest': digest, 'specification_revision': 1}},
                     'contracts': {digest: copy.deepcopy(base['content'])}}
        original = copy.deepcopy(execution)
        result = copy.deepcopy(base['content'])
        result['canon']['DEF-1']['text'] += ' New obligation.'
        request = {'result': result, 'started_dispositions': {}}
        with self.assertRaisesRegex(ValueError, 'explicit bound-contract'):
            work.build_proposal(capture.read_capture(self.path), base, execution, request)
        request['started_dispositions']['PHASE-1'] = 'preserve-bound-contract'
        proposal = work.build_proposal(capture.read_capture(self.path), base, execution, request)
        self.assertEqual(proposal['execution_expectations']['PHASE-1']['disposition'], 'preserve-bound-contract')
        self.assertEqual(execution, original)
        execution['contracts'] = {}
        with self.assertRaisesRegex(ValueError, 'not retained'):
            work.build_proposal(capture.read_capture(self.path), base, execution, request)

    def test_invalid_traceability_cycle_and_obsolete_dependency(self):
        request = self.full_request()
        request['result']['phases']['PHASE-1']['canon_ids'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'missing Canon'):
            work.compose(self.root, self.identity, self.base, self.execution, request, self.digest())
        request = self.full_request()
        request['result']['canon']['DEF-1']['sources'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'captured sources'):
            work.compose(self.root, self.identity, self.base, self.execution, request, self.digest())
        request = self.full_request()
        request['result']['phases']['PHASE-2'] = copy.deepcopy(request['result']['phases']['PHASE-1'])
        request['result']['dag'] = {'order': ['PHASE-1', 'PHASE-2'], 'edges': [
            {'from': 'PHASE-1', 'to': 'PHASE-2', 'type': 'requires'},
            {'from': 'PHASE-2', 'to': 'PHASE-1', 'type': 'requires'}]}
        with self.assertRaisesRegex(ValueError, 'cycle'):
            work.compose(self.root, self.identity, self.base, self.execution, request, self.digest())
        request['result']['phases']['PHASE-2']['status'] = 'obsolete'
        request['result']['dag']['order'] = ['PHASE-1']
        with self.assertRaisesRegex(ValueError, 'obsolete phase'):
            work.compose(self.root, self.identity, self.base, self.execution, request, self.digest())

    def test_family_is_not_implicit_dependency(self):
        base = self.admitted_base()
        result = copy.deepcopy(base['content'])
        result['phases']['PHASE-2'] = {**result['phases']['PHASE-1'], 'family': 'PHASE-1'}
        result['dag']['order'].append('PHASE-2')
        proposal = work.build_proposal(capture.read_capture(self.path), base, self.execution,
                                       {'result': result, 'started_dispositions': {}})
        self.assertEqual(proposal['result']['dag']['edges'], [])
        self.assertEqual(set(proposal['execution_expectations']), {'PHASE-2'})

    def test_deferred_selection_preserves_declined_and_discloses_associations(self):
        deferred = load_helper('planning-deferred')
        for identity in ('DEFER-SELECTED', 'DEFER-DECLINED'):
            item = {'id': identity, 'title': identity, 'origin': 'Synthetic original note',
                    'intent': 'Preserve scope', 'guardrail': 'Keep original evidence', 'reopen': 'Explicit choice'}
            deferred.capture_item(self.root, item, deferred.list_items(self.root)['register_digest'], True)
        before = copy.deepcopy(deferred.read_register(self.root)[0]['items']['DEFER-DECLINED'])
        offer = deferred.offer_inclusion(self.root, ['DEFER-SELECTED'], self.identity)
        deferred.include(self.root, offer, True)
        self.assertEqual(deferred.read_register(self.root)[0]['items']['DEFER-DECLINED'], before)
        repeated = deferred.offer_inclusion(self.root, ['DEFER-SELECTED'], self.identity)
        self.assertEqual(repeated['selected'][0]['existing_associations'][0]['context_id'], self.identity)
        work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)
        work.propose(self.root, self.identity, self.base, self.execution, self.full_request(), self.digest(), True)
        proposal = capture.read_capture(self.path)['proposal']
        self.assertEqual([source['id'] for source in proposal['sources']], ['source-1', 'DEFER-SELECTED@1'])
        self.assertEqual(deferred.read_register(self.root)[0]['items']['DEFER-DECLINED'], before)

    def test_full_cli_review_decision_mock_retry_and_withdrawal(self):
        publication = load_helper('planning-publication')
        evidence = publication.evidence

        def command(helper, *arguments):
            transport = ['--transport', 'local-mock'] if helper == 'planning-publication' else []
            completed = subprocess.run([sys.executable, str(script.with_name(helper + '.py')),
                '--root', str(self.root), *transport, *arguments], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(completed.stdout)

        def request_file(name, value):
            destination = self.root / (name + '.json')
            destination.write_text(json.dumps(value))
            return str(destination)

        def record(operation, request):
            return command('planning-evidence', '--context', self.identity, operation, '--request',
                           request_file(operation, request), '--expected-digest', self.digest(), '--confirmed')

        work.draft(self.root, self.identity, 'canon', self.request, self.digest(), True)
        work.propose(self.root, self.identity, self.base, self.execution, self.full_request(), self.digest(), True)
        original_planning = capture.read_capture(self.path)['workflow']['planning']
        authority = {'actor': 'Synthetic Operator', 'authority': 'Temporary fixture only',
            'date': '2026-09-29', 'rationale': 'Synthetic test decision', 'evidence': 'fixture://explicit-confirmation'}
        observation = {'summary': 'Synthetic unresolved concern', 'severity': 'low', 'consequence': 'Fixture risk',
                       'scope': 'Fixture', 'recommendation': 'Inspect', 'locations': ['source.txt']}
        record('round', {'kind': 'SCRUB', 'request_id': 'scrub-1', 'report': 'Synthetic source assessment',
                         'observations': [observation], 'actor': 'Synthetic Assessor', 'recorded_at': '2026-09-29'})
        exported = command('planning-evidence', '--context', self.identity, 'export-review')
        self.assertNotIn('workflow', exported['input']['capture'])
        (self.root / 'report.txt').write_bytes(b'Synthetic independent fixture review only.\r\n')
        reviewed = record('review', {'request_id': 'review-1', 'review_input': exported['input'],
            'report_path': 'report.txt', 'observations': [],
            'attestation': {**authority, 'actor': 'Synthetic Independent Reviewer', 'scope': 'Fixture', 'independent': True}})
        fields = {'kind': 'approval', 'actor': authority['actor'], 'authority': authority['authority'],
            'date': authority['date'], 'scope': 'Fixture', 'checklist': dict.fromkeys(contract.CHECK_NAMES, True),
            'integration_assessment': 'Local fixture only', 'dag_assessment': 'Single fixture node',
            'findings_acknowledged': ['SCRUB01-F01'], 'conditions': [], 'signoff': 'Synthetic fixture signoff',
            'invocation_source': 'operator-confirmation'}
        drafted = record('draft-decision', {'identity': 'decision-1', 'review_ids': [reviewed['evidence_result']], 'fields': fields})
        decision = capture.read_capture(self.path)['workflow']['decision']['drafts'][-1]['decision']
        record('finalize-decision', {'identity': 'decision-1', 'expected_draft_digest': drafted['evidence_result'],
               'confirmation': {**authority, 'decision_digest': contract.digest(decision)}})
        base_path = self.root / publication.admission.SPECIFICATION_PATH
        execution_path = self.root / publication.admission.EXECUTION_PATH
        for destination, value in ((base_path, self.base), (execution_path, self.execution)):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(evidence.encoded(value))
        git = publication.planning_git.git
        git(self.root, 'init', '--quiet', '-b', 'integration')
        git(self.root, 'config', 'user.name', 'Synthetic Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        git(self.root, 'add', '--', publication.admission.SPECIFICATION_PATH, publication.admission.EXECUTION_PATH)
        git(self.root, 'commit', '--quiet', '-m', 'Synthetic fixture baseline')
        original_head = git(self.root, 'rev-parse', 'HEAD').stdout
        original_base, original_execution = base_path.read_bytes(), execution_path.read_bytes()
        prepared = command('planning-admission', 'prepare', '--context', self.identity, '--decision', 'decision-1',
            '--expected-digest', self.digest(), '--base', str(base_path), '--execution', str(execution_path), '--confirmed')
        offered = command('planning-publication', 'offer', '--bundle', prepared['bundle'], '--target', 'refs/heads/integration')
        confirmation = request_file('confirmation', {**authority, 'offer_digest': offered['offer_digest']})
        command('planning-publication', 'create', '--attempt', 'workflow-attempt', '--offer',
                request_file('offer', offered), '--confirmation', confirmation, '--confirmed')
        first = command('planning-publication', 'resume', '--attempt', 'workflow-attempt', '--confirmed')
        second = command('planning-publication', 'resume', '--attempt', 'workflow-attempt', '--confirmed')
        self.assertEqual(first, second)
        self.assertFalse(first['live_admission'])
        self.assertEqual(first['transport'], 'local-mock')
        self.assertEqual(first['state'], 'authorized-for-merge')
        with self.assertRaisesRegex(ValueError, 'withdrawal'):
            work.draft(self.root, self.identity, 'work', self.request, self.digest(), True)
        command('planning-publication', 'close-mock', '--attempt', 'workflow-attempt', '--confirmation', confirmation, '--confirmed')
        withdrawn = command('planning-publication', 'withdraw', '--attempt', 'workflow-attempt', '--confirmation', confirmation, '--confirmed')
        self.assertEqual(withdrawn['state'], 'withdrawn')
        self.assertEqual(capture.read_capture(self.path)['workflow']['planning'], original_planning)
        work.draft(self.root, self.identity, 'work', {**self.request, 'request_id': 'draft-after-withdrawal'}, self.digest(), True)
        self.assertEqual(git(self.root, 'rev-parse', 'HEAD').stdout, original_head)
        self.assertEqual(base_path.read_bytes(), original_base)
        self.assertEqual(execution_path.read_bytes(), original_execution)

    def test_customization_yaml_links_and_caller_contracts(self):
        for name in ('planning-workflow', 'guided-admission', 'canon-consolidation', 'work-plan-shaping',
                     'proposal-assessment', 'inception-scrub', 'diagram-checkpoint'):
            filename = repository / '.github/skills' / name / 'SKILL.md'
            text = filename.read_text()
            self.assertEqual(yaml.safe_load(text.split('---', 2)[1])['name'], name)
            for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', text):
                self.assertTrue((filename.parent / target).exists(), (filename, target))
        for name in ('horizon', 'plan-work', 'admit-plan'):
            metadata = yaml.safe_load((repository / '.github/prompts' / (name + '.prompt.md')).read_text().split('---', 2)[1])
            self.assertTrue(metadata['description'])
            self.assertNotIn('agent', metadata)
        for name in ('plan-work', 'admit-horizon'):
            text = (repository / '.github/prompts' / (name + '.prompt.md')).read_text()
            self.assertNotIn('LOCAL/MOCK', text)
        for name in ('inception-facilitator', 'project-planning-design', 'project-codegen'):
            text = (repository / '.github/agents' / (name + '.agent.md')).read_text()
            self.assertIn('## Named Scope: Shared File-Backed Planning', text)
            self.assertIn('## Admission Conflict Recovery', text)
            self.assertIn('.github/skills/guided-admission/SKILL.md', text)

    def test_documented_builder_help_and_duplicate_json(self):
        for name in ('deep-discovery-classify', 'deep-discovery-run', 'deep-discovery-closeout', 'review-canon'):
            self.assertFalse((repository / '.github/prompts' / (name + '.prompt.md')).exists())
            self.assertFalse((repository / '.claude/commands' / (name + '.md')).exists())
        glossary = (repository / 'control-plane/framework/docs/GLOSSARY.md').read_text()
        self.assertNotIn('unit of parallel execution', glossary)
        self.assertNotIn("embedded in the horizon's `TRACKER.json`", glossary)
        governance = (repository / 'control-plane/framework/governance/README.md').read_text()
        self.assertNotIn('There is no single tracker shared', governance)
        skill = (repository / '.github/skills/guided-admission/SKILL.md').read_text()
        self.assertNotIn('forge-cli-trial', skill)
        self.assertNotIn('## Legacy Trial Compatibility', skill)
        for name in ('closeout-prompt', 'complete-phase', 'publish-review-unit'):
            text = (repository / '.github/prompts' / (name + '.prompt.md')).read_text()
            self.assertIn('source: operational', text)
            self.assertIn('0.8.2', text)
        for operation in ('draft', 'compose', 'propose'):
            completed = subprocess.run([sys.executable, str(script), '--context', self.identity, operation, '--help'],
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('--expected-digest', completed.stdout)
            self.assertIn('--request', completed.stdout)
        filename = self.root / 'invalid.json'
        filename.write_text('{"request_id":"one","request_id":"two"}')
        completed = subprocess.run([sys.executable, str(script), '--root', str(self.root), '--context', self.identity,
            'draft', '--section', 'canon', '--request', str(filename), '--expected-digest', self.digest(), '--confirmed'],
            capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('duplicate JSON key', completed.stderr)


unittest.main()
PY