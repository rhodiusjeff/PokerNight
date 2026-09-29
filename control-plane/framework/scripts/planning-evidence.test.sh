#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export SCRIPT_DIR
python3 - <<'PY'
import copy
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location('evidence', pathlib.Path(os.environ['SCRIPT_DIR']) / 'planning-evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.document = {'id': 'ADHOC-' + 'a' * 32, 'sources': [], 'title': 'Fixture', 'proposal': {'author': 'Author'}}
        self.finding = {'summary': 'Source conflict', 'severity': 'high', 'consequence': 'Wrong plan',
                        'scope': 'Fixture', 'recommendation': 'Ask authority', 'locations': ['source-1']}
        self.authority = {'actor': 'Fixture Operator', 'authority': 'fixture only', 'date': '2026-09-29',
                          'rationale': 'Test disposition', 'evidence': 'fixture://decision'}

    def round(self, kind='SCRUB', request='first', observations=None):
        return evidence.record_round(self.document, kind, request, 'Actual fixture report',
            [self.finding] if observations is None else observations, 'Fixture Reviewer', '2026-09-29')

    def test_report_append_does_not_change_subject(self):
        before = evidence.subjects(self.document)
        self.round()
        self.assertEqual(before, evidence.subjects(self.document))
        exported = evidence.export_review_input(self.document)
        self.assertNotIn('workflow', exported['input']['capture'])
        self.assertTrue(exported['previous_findings']['SCRUB']['items'])

    def test_repeat_and_omission_preserve_identity(self):
        self.assertEqual(self.round(), self.round())
        self.round(request='second')
        self.round(request='third', observations=[])
        register = evidence.registers(self.document)['SCRUB']
        self.assertEqual(len(register['items']), 1)
        self.assertEqual(len(register['rounds']), 3)
        self.assertEqual(len(evidence.warnings(self.document)), 1)

    def test_resolution_and_reopening_require_evidence(self):
        self.round()
        with self.assertRaises(ValueError):
            evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'resolve', 'resolved', self.authority, True)
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'resolve', 'resolved',
                             {**self.authority, 'verification': 'fixture://test-pass'}, True)
        self.assertEqual(evidence.warnings(self.document), [])
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'reopen', 'open', self.authority, True)
        self.assertEqual(len(evidence.warnings(self.document)), 1)

    def test_minted_identity_skips_resolved_imported_future_identity(self):
        for kind in evidence.KINDS:
            with self.subTest(kind=kind):
                imported = kind + '02-F01'
                self.round(kind, observations=[{**self.finding, 'id': imported}])
                evidence.disposition(self.document, kind, imported, 'resolve', 'resolved',
                                     {**self.authority, 'verification': 'fixture://test-pass'}, True)
                register = evidence.registers(self.document)[kind]
                previous = copy.deepcopy(register['items'][imported])
                new_finding = {**self.finding, 'summary': 'Distinct new issue'}
                self.round(kind, request='second', observations=[new_finding])
                minted = register['rounds'][-1]['findings'][0]
                self.assertNotEqual(minted, imported)
                self.assertEqual(register['items'][imported], previous)
                self.assertEqual(register['items'][minted]['status'], 'open')
                self.assertEqual(register['items'][minted]['summary'], new_finding['summary'])
                self.assertIn(minted, [item['id'] for item in evidence.warnings(self.document)])
                self.round(kind, request='third', observations=[new_finding])
                self.assertEqual(register['rounds'][-1]['findings'], [minted])
                self.round(kind, request='fourth', observations=[{'id': imported, 'summary': 'Explicit revisit'}])
                self.assertEqual(register['rounds'][-1]['findings'], [imported])
                self.assertEqual(len(register['items']), 2)

    def test_cross_links_do_not_close_other_register(self):
        self.round()
        self.finding['links'] = ['SCRUB01-F01']
        self.round('REVIEW')
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'resolve', 'resolved',
                             {**self.authority, 'verification': 'fixture://test-pass'}, True)
        self.assertEqual([item['id'] for item in evidence.warnings(self.document)], ['REVIEW01-F01'])

    def test_changed_source_invalidates_disposition(self):
        self.round()
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'dismiss', 'dismissed', self.authority, True)
        self.document['sources'].append({'changed': True})
        self.assertTrue(evidence.warnings(self.document)[0]['stale_disposition'])

    def test_original_semantics_preserved(self):
        before = copy.deepcopy(evidence.subject(self.document))
        self.round()
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'agree', 'open', self.authority, True)
        self.assertEqual(before, evidence.subject(self.document))

    def test_reserved_disposition_fields_cannot_override_authority(self):
        self.round()
        with self.assertRaisesRegex(ValueError, 'reserved'):
            evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'override', 'open',
                                 {**self.authority, 'status': 'resolved'}, True)

    def test_origin_qualified_and_legacy_finding_identities_preserved(self):
        self.round(observations=[{**self.finding, 'id': 'H007:SCRUB01-F01'},
                                 {**self.finding, 'id': 'S03-F07'}])
        self.round(request='next', observations=[{'id': 'H007:SCRUB01-F01', 'summary': 'Same imported issue'}])
        self.assertEqual(set(evidence.registers(self.document)['SCRUB']['items']), {'H007:SCRUB01-F01', 'S03-F07'})


class ReviewDecisionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        source = self.root / 'source.txt'
        source.write_bytes(b'Original\r\nsource\x00')
        self.identity = 'ADHOC-' + 'b' * 32
        evidence.capture.create_capture(SimpleNamespace(root=self.root, id=self.identity, confirmed=True,
            sources=[source], kind='ad-hoc', origin_phase=None, origin_specification=None, title='Fixture', author='Author'))
        self.path = evidence.capture.resolve_document(self.root, self.identity)
        self.document = evidence.capture.read_capture(self.path)
        base = evidence.contract.empty_specification()
        content = copy.deepcopy(base['content'])
        canon = {'kind': 'requirement', 'text': 'Fixture requirement', 'status': 'active', 'sources': ['source-1']}
        content['canon']['REQ-1'] = canon
        self.document['proposal'] = {'schema': 'cp-plan-proposal-v1', 'id': self.identity, 'revision': 1,
            'author': 'Author', 'base_revision': 0, 'base_digest': base['content_digest'],
            'sources': self.document['sources'], 'changes': [{'collection': 'canon', 'id': 'REQ-1', 'operation': 'add',
            'before_digest': None, 'value': canon}], 'result': content, 'execution_expectations': {}}
        self.document['workflow'] = {'other_lane': {'keep': True}}
        self.path.write_text(evidence.capture.render(self.document))
        self.attestation = {'actor': 'Independent Fixture Reviewer', 'authority': 'fixture only', 'date': '2026-09-29',
                            'rationale': 'Independent fixture assessment', 'evidence': 'fixture://review',
                            'scope': 'All fixture inputs', 'independent': True}

    def review(self):
        return evidence.record_review(self.document, 'review-1', evidence.subject(self.document), b'Actual report\r\n',
                                      [], self.attestation, True)

    def draft(self, kind='approval', identity='decision-1', **extra):
        self.review()
        fields = {'kind': kind, 'actor': 'Fixture Operator', 'authority': 'fixture only', 'date': '2026-09-29',
            'scope': 'Complete fixture', 'checklist': dict.fromkeys(evidence.contract.CHECK_NAMES, True),
            'integration_assessment': 'Fixture only', 'dag_assessment': 'Empty DAG checked', 'findings_acknowledged': [],
            'conditions': [], 'signoff': 'Fixture explicit signoff', 'invocation_source': 'operator-confirmation', **extra}
        return evidence.draft_decision(self.document, identity, ['REVIEW01'], fields)

    def confirmation(self, identity='decision-1'):
        draft = next(item for item in self.document['workflow']['decision']['drafts'] if item['id'] == identity)
        return {'actor': 'Fixture Operator', 'authority': 'fixture only', 'date': '2026-09-29',
                'rationale': 'Fixture confirmation', 'evidence': 'fixture://confirmation',
                'decision_digest': evidence.contract.digest(draft['decision'])}

    def test_exact_review_retention_and_retry(self):
        before = evidence.subjects(self.document)
        self.assertEqual(self.review(), self.review())
        record = self.document['workflow']['reviews'][0]
        self.assertEqual(evidence.retained_bytes(record['report']), b'Actual report\r\n')
        self.assertEqual(evidence.retained_bytes(record['input']), evidence.encoded(evidence.subject(self.document)))
        self.assertEqual(before, evidence.subjects(self.document))
        evidence.validate_workflow(self.document)

    def test_independent_cli_export_and_linear_review_retention(self):
        self.review()
        evidence.record_review(self.document, 'review-2', evidence.subject(self.document), b'Second independent report',
                               [], self.attestation, True)
        retained = evidence.decode_document(evidence.retained_bytes(self.document['workflow']['reviews'][-1]['capture_bytes']))
        self.assertNotIn('workflow', retained)
        self.path.write_text(evidence.capture.render(self.document))
        command = [sys.executable, str(pathlib.Path(os.environ['SCRIPT_DIR']) / 'planning-evidence.py'),
                   '--root', str(self.root), '--context', self.identity]
        clean = evidence.load_bytes(subprocess.check_output([*command, 'export-review']))
        prior = evidence.load_bytes(subprocess.check_output([*command, 'previous-findings']))
        self.assertNotIn('previous_findings', clean)
        self.assertNotIn('workflow', clean['input']['capture'])
        self.assertTrue(prior['previous_findings']['REVIEW']['rounds'])

    def test_independence_and_stale_review_refuse(self):
        with self.assertRaisesRegex(ValueError, 'attestation'):
            evidence.record_review(self.document, 'bad', evidence.subject(self.document), b'report', [],
                                   {**self.attestation, 'independent': False}, True)
        with self.assertRaises(ValueError):
            evidence.record_review(self.document, 'bad', evidence.subject(self.document), b'report', [],
                                   {**self.attestation, 'actor': ' AUTHOR '}, True)
        self.review()
        self.document['proposal']['revision'] += 1
        with self.assertRaisesRegex(ValueError, 'stale'):
            evidence.select_reviews(self.document, ['REVIEW01'])

    def test_draft_not_evidence_and_confirmation_required(self):
        digest = self.draft()
        with self.assertRaises(ValueError):
            evidence.selected_decision(self.document, 'decision-1')
        with self.assertRaises(ValueError):
            evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), False)
        evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        final, reviews = evidence.selected_decision(self.document, 'decision-1')
        self.assertEqual(final['status'], 'finalized')
        self.assertEqual(len(reviews), 1)
        evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        self.assertEqual(len(self.document['workflow']['decision']['finalized']), 1)

    def test_waiver_requires_rationale_and_actual_alternative(self):
        digest = self.draft(kind='waiver')
        with self.assertRaisesRegex(ValueError, 'waiver'):
            evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        digest = self.draft(kind='waiver', identity='decision-2', waiver_reason='Solo fixture', alternative_review='Independent fixture review')
        evidence.finalize_decision(self.document, 'decision-2', digest, self.confirmation('decision-2'), True)

    def test_unsatisfied_condition_and_ambiguous_decision(self):
        digest = self.draft(conditions=[{'description': 'Fixture check', 'satisfied': False, 'evidence': 'not run'}])
        with self.assertRaises(ValueError):
            evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        digest = self.draft(identity='decision-2')
        evidence.finalize_decision(self.document, 'decision-2', digest, self.confirmation('decision-2'), True)
        digest = self.draft(identity='decision-3')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            evidence.finalize_decision(self.document, 'decision-3', digest, self.confirmation('decision-3'), True)

    def test_capture_writer_preserves_metadata_and_preimage(self):
        before = self.path.read_bytes()
        def update(document):
            document['workflow']['findings'] = {'SCRUB': {'rounds': [], 'items': {}}, 'REVIEW': {'rounds': [], 'items': {}}}
            return document
        result = evidence.mutate(self.root, self.identity, evidence.retain(before)['sha256'], update, True)
        self.assertEqual(pathlib.Path(result['previous_snapshot']).read_bytes(), before)
        self.assertTrue(evidence.capture.read_capture(self.path)['workflow']['other_lane']['keep'])
        with self.assertRaisesRegex(ValueError, 'changed'):
            evidence.mutate(self.root, self.identity, evidence.retain(before)['sha256'], update, True)

    def test_symlink_and_traversal_refuse(self):
        (self.root / 'link').symlink_to(self.path)
        for filename in ('link', '../escape'):
            with self.assertRaises(ValueError):
                evidence.confined(self.root, filename)

    def test_authorization_blocks_evidence_before_superseding_decision(self):
        digest = self.draft()
        evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        next_digest = self.draft(identity='decision-2')
        confirmation = self.confirmation('decision-2')
        self.document['workflow']['admission'] = {'status': 'authorized-for-merge', 'attempt_id': 'attempt-1'}
        self.path.write_text(evidence.capture.render(self.document))
        before = self.path.read_bytes()
        with evidence.capture.local_writer(self.root):
            pass
        before_files = {str(filename.relative_to(self.root)): filename.read_bytes()
                        for filename in self.root.rglob('*') if filename.is_file()}
        called = []

        def update(document):
            called.append(True)
            evidence.finalize_decision(document, 'decision-2', next_digest, confirmation, True, 'decision-1')
            return document

        with self.assertRaisesRegex(ValueError, 'withdrawal'):
            evidence.mutate(self.root, self.identity, evidence.retain(before)['sha256'], update, True)
        self.assertEqual(called, [])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual({str(filename.relative_to(self.root)): filename.read_bytes()
                          for filename in self.root.rglob('*') if filename.is_file()}, before_files)

    def test_horizon_identity_uses_same_capture_api_without_adhoc_fabrication(self):
        self.identity = 'H007'
        self.document.update(id=self.identity, kind='horizon')
        self.document['proposal']['id'] = self.identity
        packet = self.root / 'control-plane/horizons/H007-fixture/planning'
        packet.mkdir(parents=True)
        self.path = packet / 'H007.md'
        self.path.write_text(evidence.capture.render(self.document))
        before = self.path.read_bytes()
        def update(document):
            evidence.record_review(document, 'horizon-review', evidence.subject(document), b'Independent horizon fixture review',
                                   [], self.attestation, True)
            return document
        result = evidence.mutate(self.root, self.identity, evidence.retain(before)['sha256'], update, True)
        self.assertTrue(result['updated'])
        filename, current = evidence.read_document(self.root, 'H007')
        self.assertEqual(current['id'], 'H007')
        self.assertEqual(current['proposal']['id'], 'H007')

    def test_tampered_finalized_draft_refuses(self):
        digest = self.draft()
        evidence.finalize_decision(self.document, 'decision-1', digest, self.confirmation(), True)
        self.document['workflow']['decision']['drafts'][0]['decision']['scope'] = 'Altered scope'
        with self.assertRaisesRegex(ValueError, 'confirmed draft'):
            evidence.validate_workflow(self.document)


unittest.main(verbosity=2)
PY