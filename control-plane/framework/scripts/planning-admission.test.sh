#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export SCRIPT_DIR
python3 - <<'PY'
import copy
import hashlib
import importlib.util
import os
import pathlib
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location('admission', pathlib.Path(os.environ['SCRIPT_DIR']) / 'planning-admission.py')
admission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admission)
evidence = admission.evidence
capture = admission.capture
contract = admission.contract


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()
        self.identity = 'ADHOC-' + 'c' * 32
        source = self.root / 'input.txt'
        source.write_bytes(b'Exact fixture source\r\n\x00')
        capture.create_capture(SimpleNamespace(root=self.root, id=self.identity, confirmed=True, sources=[source],
            kind='ad-hoc', origin_phase=None, origin_specification=None, title='Admission fixture', author='Fixture Author'))
        self.path = capture.resolve_document(self.root, self.identity)
        self.document = capture.read_capture(self.path)
        self.base = contract.empty_specification()
        content = copy.deepcopy(self.base['content'])
        canon = {'kind': 'requirement', 'text': 'Fixture requirement', 'status': 'active', 'sources': ['source-1']}
        phase = {'title': 'Fixture phase', 'specification': 'Fixture-only contract', 'status': 'active',
                 'canon_ids': ['REQ-1'], 'acceptance': ['Fixture test passes']}
        content['canon']['REQ-1'] = canon
        content['phases']['PHASE-1'] = phase
        content['dag']['order'] = ['PHASE-1']
        self.document['proposal'] = {'schema': 'cp-plan-proposal-v1', 'id': self.identity, 'revision': 1,
            'author': 'Fixture Author', 'base_revision': 0, 'base_digest': self.base['content_digest'],
            'sources': self.document['sources'], 'changes': [
                {'collection': 'canon', 'id': 'REQ-1', 'operation': 'add', 'before_digest': None, 'value': canon},
                {'collection': 'phases', 'id': 'PHASE-1', 'operation': 'add', 'before_digest': None, 'value': phase}],
            'result': content, 'execution_expectations': {'PHASE-1': {
                'state_digest': contract.digest({'status': 'not-started'}), 'disposition': 'unstarted'}}}
        self.document['workflow'] = {'other_lane': {'preserve': True}}
        self.authority = {'actor': 'Fixture Operator', 'authority': 'fixture only', 'date': '2026-09-29',
                          'rationale': 'Synthetic test authority', 'evidence': 'fixture://confirmation'}
        evidence.record_round(self.document, 'SCRUB', 'scrub', 'Unresolved source issue', [{
            'summary': 'Open fixture concern', 'severity': 'high', 'consequence': 'Fixture risk', 'scope': 'All',
            'recommendation': 'Investigate', 'locations': ['input.txt']}], 'Fixture Reviewer', '2026-09-29')
        self.finalize()
        self.save()
        self.base_path = self.root / admission.SPECIFICATION_PATH
        self.base_path.parent.mkdir(parents=True)
        self.base_path.write_bytes(evidence.encoded(self.base))
        self.execution_path = self.root / admission.EXECUTION_PATH
        self.execution_path.parent.mkdir(parents=True, exist_ok=True)
        self.execution_path.write_bytes(evidence.encoded({'phases': {}, 'contracts': {}}))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(capture.render(self.document))

    def finalize(self, identity='decision-1', supersedes=None):
        reviewer = {**self.authority, 'actor': 'Independent Fixture Reviewer', 'scope': 'Complete fixture', 'independent': True}
        review_id = evidence.record_review(self.document, identity + '-review', evidence.subject(self.document),
                                            b'Independent fixture report\r\n', [], reviewer, True)
        fields = {'kind': 'approval', 'actor': self.authority['actor'], 'authority': self.authority['authority'],
            'date': '2026-09-29', 'scope': 'Complete fixture', 'checklist': dict.fromkeys(contract.CHECK_NAMES, True),
            'integration_assessment': 'Isolated fixture only', 'dag_assessment': 'Valid single node',
            'findings_acknowledged': [item['id'] for item in evidence.warnings(self.document)], 'conditions': [],
            'signoff': 'Explicit synthetic fixture signoff', 'invocation_source': 'operator-confirmation'}
        digest = evidence.draft_decision(self.document, identity, [review_id], fields)
        decision = self.document['workflow']['decision']['drafts'][-1]['decision']
        evidence.finalize_decision(self.document, identity, digest,
                                  {**self.authority, 'decision_digest': contract.digest(decision)}, True, supersedes)

    def prepare(self):
        return admission.prepare(self.root, self.identity, 'decision-1', self.base_path, self.execution_path,
                                 hashlib.sha256(self.path.read_bytes()).hexdigest(), True)

    def bundle(self):
        return pathlib.Path(self.prepare()['bundle'])


class AdmissionTests(Fixture):
    def test_first_admission_multipart_single_increment_and_open_warnings(self):
        before = self.base_path.read_bytes()
        prepared = self.prepare()
        result = admission.validate_bundle(self.root, prepared['bundle'], self.base_path, self.execution_path)
        self.assertEqual(result['result']['revision'], 1)
        self.assertEqual(len(result['result']['admissions']), 1)
        self.assertEqual(result['warnings'][0]['id'], 'SCRUB01-F01')
        self.assertEqual(self.base_path.read_bytes(), before)
        self.assertFalse(result['live_admission'])

    def test_snapshot_exact_bytes_and_idempotent_retry(self):
        raw = self.path.read_bytes()
        first, second = self.prepare(), self.prepare()
        self.assertEqual(pathlib.Path(first['bundle']), self.path.parent / 'assets/admission' / first['bundle_id'])
        self.assertEqual(first['bundle_id'], second['bundle_id'])
        self.assertFalse(second['created'])
        self.assertEqual((pathlib.Path(first['bundle']) / 'capture.md').read_bytes(), raw)
        self.assertEqual((pathlib.Path(first['bundle']) / 'base.json').read_bytes(), self.base_path.read_bytes())

    def test_tampered_result_and_manifest_refuse(self):
        bundle = self.bundle()
        (bundle / 'result.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'tampered'):
            admission.validate_bundle(self.root, bundle)

    def test_undeclared_inventory_and_symlink_refuse(self):
        bundle = self.bundle()
        extra = bundle / 'unexpected.py'
        extra.write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            admission.validate_bundle(self.root, bundle)
        extra.unlink()
        (bundle / 'result.json').unlink()
        (bundle / 'result.json').symlink_to(self.base_path)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            admission.validate_bundle(self.root, bundle)

    def test_stale_current_subject_and_finding_posture(self):
        bundle = self.bundle()
        evidence.disposition(self.document, 'SCRUB', 'SCRUB01-F01', 'defer', 'deferred',
                             {**self.authority, 'revisit': 'Next fixture'}, True)
        self.save()
        with self.assertRaisesRegex(ValueError, 'findings'):
            admission.validate_bundle(self.root, bundle)

    def test_already_applied_safe_and_identity_reuse_refused(self):
        bundle = self.bundle()
        self.base_path.write_bytes((bundle / 'result.json').read_bytes())
        result = admission.validate_bundle(self.root, bundle, self.base_path, self.execution_path)
        self.assertEqual(result['already_applied_revision'], 1)
        self.assertIsNone(result['result'])
        self.assertEqual(self.prepare()['status'], 'already-applied')
        self.document['proposal']['revision'] += 1
        self.finalize('decision-2', 'decision-1')
        self.save()
        with self.assertRaisesRegex(ValueError, 'identity reused'):
            admission.prepare(self.root, self.identity, 'decision-2', self.base_path, self.execution_path,
                              hashlib.sha256(self.path.read_bytes()).hexdigest(), True)

    def test_transfer_and_terminal_source_refuse(self):
        bundle = self.bundle()
        self.document['context'] = {'state': 'planning', 'transfer_pending': 'transfer-1'}
        self.save()
        with self.assertRaisesRegex(ValueError, 'transferred'):
            admission.validate_bundle(self.root, bundle)
        self.document['context'] = {'state': 'absorbed'}
        self.save()
        with self.assertRaisesRegex(ValueError, 'terminal'):
            admission.validate_bundle(self.root, bundle)

    def test_execution_race_refuse(self):
        bundle = self.bundle()
        execution = {'phases': {'PHASE-1': {'status': 'in-progress', 'contract_digest': self.base['content_digest'],
                     'specification_revision': 0}}, 'contracts': {}}
        self.execution_path.write_bytes(evidence.encoded(execution))
        with self.assertRaisesRegex(ValueError, 'execution state changed'):
            admission.validate_bundle(self.root, bundle, self.base_path, self.execution_path)

    def test_writer_contention_and_stale_capture_refuse(self):
        with capture.local_writer(self.root):
            with self.assertRaisesRegex(ValueError, 'another local'):
                self.prepare()
        with self.assertRaisesRegex(ValueError, 'capture changed'):
            admission.prepare(self.root, self.identity, 'decision-1', self.base_path, self.execution_path, '0' * 64, True)

    def test_noop_refuses(self):
        proposal = copy.deepcopy(self.document['proposal'])
        proposal['changes'] = []
        proposal['result'] = self.base['content']
        with self.assertRaisesRegex(ValueError, 'no-op'):
            contract.apply_changes(self.base, proposal)


if os.environ.get('PLANNING_TEST_PUBLICATION'):
    publication = evidence.load_module('planning-publication')
    git = publication.planning_git.git

    class PublicationTests(Fixture):
        def setUp(self):
            super().setUp()
            git(self.root, 'init', '--quiet', '-b', 'integration')
            git(self.root, 'config', 'user.name', 'Local Fixture')
            git(self.root, 'config', 'user.email', 'fixture@example.invalid')
            git(self.root, 'add', '--', admission.SPECIFICATION_PATH, admission.EXECUTION_PATH)
            git(self.root, 'commit', '--quiet', '-m', 'Fixture integration baseline')
            self.target = publication.planning_git.resolve_commit(self.root, 'refs/heads/integration')
            git(self.root, 'switch', '--quiet', '-c', 'parent-implementation')
            (self.root / 'parent-code.py').write_text('unmerged parent implementation\n')
            git(self.root, 'add', '--', 'parent-code.py')
            git(self.root, 'commit', '--quiet', '-m', 'Fixture unmerged parent')
            (self.root / 'parent-code.py').write_text('dirty parent implementation\n')
            self.parent = publication.planning_git.resolve_commit(self.root, 'HEAD')
            self.bundle_path = self.bundle()

        def create(self, identity='attempt-1'):
            offered = publication.offer(self.root, self.bundle_path, 'refs/heads/integration')
            publication.create_attempt(self.root, offered, identity,
                {**self.authority, 'offer_digest': offered['offer_digest']}, True)
            return identity

        def test_isolation_actual_candidate_and_idempotent_retry(self):
            identity = self.create()
            first = publication.resume(self.root, identity, True)
            second = publication.resume(self.root, identity, True)
            self.assertEqual(first, second)
            self.assertEqual(first['state'], 'authorized-for-merge')
            root, directory, header = publication.load_attempt(self.root, identity)
            checked = publication.check_candidate(root, directory, header, first['commit'])
            self.assertNotIn('parent-code.py', checked['whole_candidate_inventory'])
            self.assertEqual(publication.planning_git.resolve_commit(self.root, 'HEAD'), self.parent)
            self.assertEqual(publication.planning_git.resolve_commit(self.root, 'refs/heads/integration'), self.target)
            self.assertEqual((self.root / 'parent-code.py').read_text(), 'dirty parent implementation\n')
            current = capture.read_capture(self.path)
            self.assertEqual(len(current['workflow']['admission']['history']), 1)
            self.assertTrue(current['workflow']['other_lane']['preserve'])
            self.assertFalse(first['live_admission'])
            retried = self.prepare()
            self.assertEqual(retried['bundle'], str(self.bundle_path))
            self.assertFalse(retried['created'])

        def test_push_reply_loss_retries_without_duplicate(self):
            identity = self.create()
            with self.assertRaisesRegex(ValueError, 'injected'):
                publication.resume(self.root, identity, True, 'after-push')
            directory = publication.attempt_directory(self.root, identity)
            pushed = (directory / 'mock/push.json').read_bytes()
            result = publication.resume(self.root, identity, True)
            self.assertEqual(result['state'], 'authorized-for-merge')
            self.assertEqual((directory / 'mock/push.json').read_bytes(), pushed)

        def test_request_reply_loss_retries_same_request(self):
            identity = self.create()
            with self.assertRaisesRegex(ValueError, 'injected'):
                publication.resume(self.root, identity, True, 'after-request')
            directory = publication.attempt_directory(self.root, identity)
            request = (directory / 'mock/request.json').read_bytes()
            publication.resume(self.root, identity, True)
            self.assertEqual((directory / 'mock/request.json').read_bytes(), request)

        def test_authorization_reply_loss_recovers_without_second_history(self):
            identity = self.create()
            with self.assertRaisesRegex(ValueError, 'injected'):
                publication.resume(self.root, identity, True, 'after-authorization')
            publication.resume(self.root, identity, True)
            self.assertEqual(len(capture.read_capture(self.path)['workflow']['admission']['history']), 1)

        def test_withdrawal_unlocks_capture_and_old_attempt_stays_dead(self):
            identity = self.create()
            publication.resume(self.root, identity, True)
            result = publication.withdraw(self.root, identity, self.authority, True)
            self.assertEqual(result['state'], 'withdrawn')
            self.assertEqual(capture.read_capture(self.path)['workflow']['admission']['status'], 'withdrawn')
            with self.assertRaisesRegex(ValueError, 'withdrawn'):
                publication.resume(self.root, identity, True)
            publication.withdraw(self.root, identity, self.authority, True)
            self.assertEqual(len(capture.read_capture(self.path)['workflow']['admission']['history']), 2)

        def test_closed_unmerged_does_not_change_context_state(self):
            identity = self.create()
            publication.resume(self.root, identity, True)
            before = self.path.read_bytes()
            publication.close_request(self.root, identity, self.authority, True)
            self.assertEqual(publication.inspect(self.root, identity)['state'], 'closed-unmerged')
            self.assertEqual(publication.resume(self.root, identity, True)['state'], 'closed-unmerged')
            self.assertEqual(self.path.read_bytes(), before)

        def test_competing_attempt_refuses(self):
            self.create()
            with self.assertRaisesRegex(ValueError, 'competing'):
                self.create('attempt-2')

        def test_target_movement_invalidates_attempt_not_unchanged_proposal(self):
            identity = self.create()
            tree = git(self.root, 'rev-parse', self.target + '^{tree}').stdout.decode().strip()
            moved = git(self.root, 'commit-tree', tree, '-p', self.target, '-m', 'Unrelated target progress').stdout.decode().strip()
            git(self.root, 'update-ref', 'refs/heads/integration', moved, self.target)
            with self.assertRaisesRegex(ValueError, 'target moved'):
                publication.resume(self.root, identity, True)
            fresh = publication.offer(self.root, self.bundle_path, 'refs/heads/integration')
            self.assertEqual(fresh['offer']['target_commit'], moved)
            self.assertEqual(fresh['offer']['proposal_digest'], contract.digest(self.document['proposal']))

        def test_candidate_checker_tampering_and_extra_code_refuse(self):
            identity = self.create()
            root, directory, header = publication.load_attempt(self.root, identity)
            commit = publication.candidate(root, directory, header)
            sandbox = directory / 'repository'
            git(sandbox, 'read-tree', commit)
            extra = sandbox / 'checker.py'
            extra.write_text('weakened checker\n')
            blob = git(sandbox, 'hash-object', '-w', '--no-filters', '--', 'checker.py').stdout.decode().strip()
            git(sandbox, 'update-index', '--add', '--cacheinfo', '100644,' + blob + ',checker.py')
            tree = git(sandbox, 'write-tree').stdout.decode().strip()
            bad = git(sandbox, 'commit-tree', tree, '-p', self.target, '-m', 'Undeclared checker').stdout.decode().strip()
            with self.assertRaisesRegex(ValueError, 'inventory'):
                publication.check_candidate(root, directory, header, bad)

        def test_source_transfer_and_attempt_lock_refuse(self):
            identity = self.create()
            directory = publication.attempt_directory(self.root, identity)
            with publication.attempt_lock(self.root, directory):
                with self.assertRaisesRegex(ValueError, 'another writer'):
                    publication.resume(self.root, identity, True)
            self.document['context'] = {'state': 'planning', 'transfer_pending': 'transfer-1'}
            self.save()
            with self.assertRaisesRegex(ValueError, 'transferred'):
                publication.resume(self.root, identity, True)

        def test_partial_candidate_resumes_exact_owned_bytes(self):
            identity = self.create()
            root, directory, header = publication.load_attempt(self.root, identity)
            sandbox = directory / 'repository'
            git(directory, 'clone', '--quiet', '--no-checkout', '--local', '--no-hardlinks', str(root), str(sandbox))
            files, paths = publication.expected_files(root, header)
            relative, content = next(iter(files.items()))
            filename = sandbox / relative
            filename.parent.mkdir(parents=True)
            filename.write_bytes(content)
            result = publication.resume(root, identity, True)
            self.assertEqual(result['state'], 'authorized-for-merge')
            self.assertEqual(filename.read_bytes(), content)

        def test_changed_attempt_inputs_and_symlink_refuse(self):
            identity = self.create()
            root, directory, header = publication.load_attempt(self.root, identity)
            header['offer']['decision_digest'] = '0' * 64
            (directory / 'attempt.json').write_bytes(evidence.encoded(header))
            with self.assertRaisesRegex(ValueError, 'changed'):
                publication.resume(root, identity, True)
            with self.assertRaises(ValueError):
                publication.attempt_directory(root, '../other')

        def test_withdrawn_id_not_reused_and_fresh_attempt_allowed(self):
            identity = self.create()
            publication.resume(self.root, identity, True)
            publication.withdraw(self.root, identity, self.authority, True)
            with self.assertRaisesRegex(ValueError, 'withdrawn'):
                self.create(identity)
            next_id = self.create('attempt-2')
            publication.resume(self.root, next_id, True)
            self.assertEqual(capture.read_capture(self.path)['workflow']['admission']['attempt_id'], next_id)

        def test_two_revision_42_candidates_only_one_cas_winner(self):
            admitted = admission.validate_bundle(self.root, self.bundle_path)['result']
            base = copy.deepcopy(admitted)
            base.update(revision=42, previous_revision=41)
            base['admissions'] = [{**copy.deepcopy(admitted['admissions'][0]), 'proposal_id': 'fixture-history-' + str(index),
                                   'revision': index} for index in range(1, 43)]
            contract.validate_specification(base)
            self.base_path.write_bytes(evidence.encoded(base))
            git(self.root, 'read-tree', self.target)
            git(self.root, 'add', '--', admission.SPECIFICATION_PATH)
            tree = git(self.root, 'write-tree').stdout.decode().strip()
            target42 = git(self.root, 'commit-tree', tree, '-p', self.target, '-m', 'Synthetic revision 42 fixture').stdout.decode().strip()
            git(self.root, 'update-ref', 'refs/heads/integration', target42, self.target)
            candidates = []
            for suffix, change_text in (('d', 'Proposal D'), ('e', 'Proposal E')):
                self.identity = 'ADHOC-' + suffix * 32
                self.document['id'] = self.identity
                self.document['workflow'] = {'other_lane': {'preserve': True}}
                self.path = capture.resolve_document(self.root, self.identity)
                proposal = self.document['proposal']
                proposal['id'] = self.identity
                proposal['base_revision'] = 42
                proposal['base_digest'] = base['content_digest']
                proposal['result'] = copy.deepcopy(base['content'])
                proposal['result']['canon']['REQ-1']['text'] = change_text
                proposal['changes'] = [{'collection': 'canon', 'id': 'REQ-1', 'operation': 'modify',
                    'before_digest': contract.digest(base['content']['canon']['REQ-1']),
                    'value': copy.deepcopy(proposal['result']['canon']['REQ-1'])}]
                self.finalize()
                self.save()
                self.bundle_path = self.bundle()
                identity = self.create('attempt-' + suffix)
                result = publication.resume(self.root, identity, True)
                root, directory, header = publication.load_attempt(self.root, identity)
                checked = publication.check_candidate(root, directory, header, result['commit'])
                self.assertEqual(checked['revision'], 43)
                git(self.root, 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head',
                    str(directory / 'repository'), 'refs/heads/cp-admission/' + identity)
                candidates.append((result['commit'], header, directory))
            barrier = threading.Barrier(2)
            def compare_and_swap(candidate):
                barrier.wait(timeout=5)
                return git(self.root, 'update-ref', 'refs/heads/integration', candidate[0], target42, check=False).returncode
            with ThreadPoolExecutor(max_workers=2) as workers:
                outcomes = list(workers.map(compare_and_swap, candidates))
            self.assertEqual(outcomes.count(0), 1)
            current = publication.planning_git.resolve_commit(self.root, 'refs/heads/integration')
            operational = publication.planning_git.blob_json(self.root, current, admission.SPECIFICATION_PATH)
            self.assertEqual(operational['revision'], 43)
            self.assertEqual(len(operational['admissions']), 43)
            self.assertEqual(operational['admissions'][:42], base['admissions'])
            loser = candidates[outcomes.index(next(value for value in outcomes if value != 0))]
            with self.assertRaisesRegex(ValueError, 'target moved'):
                publication.check_candidate(self.root, loser[2], loser[1], loser[0])
            payload = admission.verify_directory(self.root, evidence.confined(self.root, loser[1]['offer']['bundle']))[2]
            with self.assertRaisesRegex(ValueError, 'base is stale'):
                contract.validate_admission(operational, evidence.load_bytes(payload['proposal.json']),
                    evidence.load_bytes(payload['reviews.json']), evidence.load_bytes(payload['decision.json']),
                    evidence.load_bytes(payload['execution.json']))
            winner = candidates[outcomes.index(0)]
            winner_capture = capture.resolve_document(self.root, winner[1]['offer']['context_id'])
            prior = winner_capture.read_bytes()
            observed = publication.resume(self.root, winner[1]['id'], True)
            self.assertEqual(observed['state'], 'already-applied')
            self.assertEqual(observed['revision'], 43)
            self.assertEqual(winner_capture.read_bytes(), prior)
            with self.assertRaisesRegex(ValueError, 'already integrated'):
                publication.withdraw(self.root, winner[1]['id'], self.authority, True)

    unittest.main(defaultTest=os.environ.get('PLANNING_TEST_FILTER', 'PublicationTests'), verbosity=2)
else:
    unittest.main(defaultTest=os.environ.get('PLANNING_TEST_FILTER', 'AdmissionTests'), verbosity=2)
PY