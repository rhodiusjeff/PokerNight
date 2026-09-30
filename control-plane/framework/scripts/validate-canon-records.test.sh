#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
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

from jsonschema import Draft202012Validator

repository = pathlib.Path(sys.argv.pop())
script = repository / 'control-plane/framework/scripts/validate-canon-records.py'
spec = importlib.util.spec_from_file_location('canon_records', script)
canon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canon)
schema = canon.load_json(canon.SCHEMA_PATH)

CONTENT = {
    'outcome': {'intent': 'Playable game', 'success_posture': 'Players complete a game'},
    'functional_requirement': {'obligation': 'Choose a mark', 'rationale': 'Player preference', 'acceptance_direction': 'Both marks selectable'},
    'constraint': {'constraint': 'Use port 3630', 'applies_to': 'Local serving', 'rationale': 'Operator requirement'},
    'story': {'actor': 'Player', 'desired_outcome': 'Play as O', 'benefit': 'Choose the preferred mark'},
    'acceptance_scenario': {'given_context': 'Human selected O', 'when_action': 'Start is pressed', 'then_observable_result': 'AI opens as X after its delay', 'limitations': []},
    'risk': {'statement': 'Old timer applies a move', 'impact': 'Wrong game state', 'likelihood_posture': 'Unmeasured scheduling risk', 'mitigation_direction': 'Invalidate old callbacks'},
    'assumption': {'statement': 'Local phone testing is available', 'confidence': 'Unverified fixture premise', 'validation_or_expiry_condition': 'Confirm before acceptance'},
    'open_question': {'question': 'Which library is suitable?', 'owner_role': 'Implementation planner', 'decision_due_boundary': 'Dependency selection'},
    'decision': {'decision': 'Keep game state in browser', 'rationale': 'Local scope', 'alternatives': ['Server-held state'], 'decision_authority': 'Proposed for Operator decision'},
    'scope_disposition': {'posture': 'excluded', 'subject': 'Online multiplayer', 'rationale': 'Local-only feature', 'destination_or_reopen_condition': None},
    'definition': {'term': 'Unbeatable', 'meaning': 'Never loses; draws allowed', 'applies_to': 'Fresh legal tic-tac-toe games', 'aliases': []},
}


def record(kind, identity=None, revision=1):
    return {'id': identity or kind, 'revision': revision, 'kind': kind, 'title': kind.replace('_', ' '),
            'scope': 'repository', 'authority_status': 'proposed', 'sources': ['brief'],
            'selection_rationale': 'Fixture has distinct source-backed meaning of this kind.', 'content': copy.deepcopy(CONTENT[kind])}


def edge(kind, start, end):
    return {'kind': kind, 'from': {key: start[key] for key in ('id', 'revision')},
            'to': {key: end[key] for key in ('id', 'revision')}, 'rationale': 'Fixture relationship', 'sources': ['brief']}


def payload(records=None, relationships=None):
    return {'schema': 'cp-canon-records-v1', 'sources': [{'id': 'brief', 'path': 'brief.md', 'sha256': '0' * 64}],
            'records': records or [], 'relationships': relationships or []}


class CanonTests(unittest.TestCase):
    def test_planning_entry_points_load_policy(self):
        paths = ['.github/agents/project-planning-design.agent.md', '.github/prompts/plan-work.prompt.md',
                 '.github/skills/planning-workflow/SKILL.md', '.github/skills/canon-consolidation/SKILL.md',
                 '.github/skills/work-plan-shaping/SKILL.md', '.github/skills/proposal-assessment/SKILL.md']
        for relative in paths:
            filename = repository / relative
            text = filename.read_text()
            self.assertIn('canon-records.policy.md', text, relative)
            for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', text):
                if 'canon-records' in target:
                    self.assertTrue((filename.parent / target).is_file(), (relative, target))

    def test_schema_and_catalogue_consistency(self):
        Draft202012Validator.check_schema(schema)
        self.assertEqual(set(CONTENT), set(schema['$defs']['kind']['enum']))
        self.assertEqual(set(schema['x-relationships']), set(schema['$defs']['relationship']['properties']['kind']['enum']))
        for rule in schema['x-relationships'].values():
            self.assertTrue(rule['meaning'])
            self.assertTrue(set(rule['from'] + rule['to']) <= {*CONTENT, '*'})

    def test_all_eleven_families_and_only_selected_records(self):
        for kind in CONTENT:
            with self.subTest(kind=kind):
                self.assertEqual(canon.validate(payload([record(kind)]))['records'], 1)
        self.assertEqual(canon.validate(payload())['records'], 0)
        self.assertEqual(canon.validate(payload([record(kind) for kind in CONTENT]))['records'], 11)

    def test_missing_typed_fields_and_unknown_fields_refuse(self):
        for kind, content in CONTENT.items():
            for field in content:
                with self.subTest(kind=kind, field=field):
                    selected = record(kind)
                    del selected['content'][field]
                    with self.assertRaisesRegex(ValueError, 'schema'):
                        canon.validate(payload([selected]))
            selected = record(kind)
            selected['content']['invented'] = 'Uncatalogued field'
            with self.assertRaisesRegex(ValueError, 'schema'):
                canon.validate(payload([selected]))

    def test_selection_rationale_required(self):
        selected = record('definition')
        selected['selection_rationale'] = ' '
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(payload([selected]))

    def test_no_embedded_source_payload(self):
        selected = payload([record('outcome')])
        selected['sources'][0]['bytes_base64'] = 'ZW1iZWRkZWQ='
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(selected)

    def test_each_relationship_accepts_and_refuses_endpoint_kinds(self):
        for name, rule in schema['x-relationships'].items():
            source_kind = 'outcome' if '*' in rule['from'] else rule['from'][0]
            target_kind = source_kind if rule.get('same_kind') else ('story' if '*' in rule['to'] else rule['to'][0])
            start, end = record(source_kind, 'start'), record(target_kind, 'end')
            with self.subTest(relationship=name):
                self.assertTrue(canon.validate(payload([start, end], [edge(name, start, end)]))['valid'])
                if rule.get('same_kind'):
                    end = record('risk' if source_kind != 'risk' else 'story', 'end')
                else:
                    invalid_kind = next(kind for kind in CONTENT if kind not in rule['from'])
                    start = record(invalid_kind, 'start')
                with self.assertRaisesRegex(ValueError, 'kind'):
                    canon.validate(payload([start, end], [edge(name, start, end)]))

    def test_unknown_relationship_alias_refuses(self):
        start, end = record('outcome'), record('story')
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(payload([start, end], [edge('related_to', start, end)]))

    def test_unresolved_and_unpinned_references_refuse(self):
        start, end = record('outcome'), record('story')
        relationship = edge('drives', start, end)
        relationship['to']['revision'] = 2
        with self.assertRaisesRegex(ValueError, 'unresolved record revision'):
            canon.validate(payload([start, end], [relationship]))
        del relationship['to']['revision']
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(payload([start, end], [relationship]))
        start['sources'] = ['missing']
        with self.assertRaisesRegex(ValueError, 'unresolved source'):
            canon.validate(payload([start]))

    def test_duplicate_id_revision_and_edges_refuse(self):
        start, end = record('outcome'), record('story')
        with self.assertRaisesRegex(ValueError, 'duplicate record revision'):
            canon.validate(payload([start, start]))
        first = edge('drives', start, end)
        second = {**first, 'rationale': 'Different explanation does not create a different edge'}
        with self.assertRaisesRegex(ValueError, 'duplicate relationship'):
            canon.validate(payload([start, end], [first, second]))

    def test_reference_set_resolves_pinned_revision_without_copy(self):
        start, end = record('outcome'), record('story')
        result = canon.validate(payload([end], [edge('drives', start, end)]), payload([start]))
        self.assertEqual(result['records'], 1)
        changed = copy.deepcopy(start)
        changed['content']['intent'] = 'Changed preserved meaning'
        with self.assertRaisesRegex(ValueError, 'preserved revision'):
            canon.validate(payload([changed]), payload([start]))
        retyped = record('story', start['id'], 2)
        with self.assertRaisesRegex(ValueError, 'kind/scope'):
            canon.validate(payload([retyped]), payload([start]))

    def test_ordering_cycles_include_reference_edges(self):
        first, second, third = [record('outcome', identity) for identity in ('first', 'second', 'third')]
        reference = payload([first, second, third], [edge('refines', first, second), edge('supersedes', second, third)])
        with self.assertRaisesRegex(ValueError, 'cycle'):
            canon.validate(payload([], [edge('refines', third, first)]), reference)

    def test_nonordering_cycle_is_not_blanket_rejected(self):
        first, second = record('definition', 'first'), record('definition', 'second')
        self.assertTrue(canon.validate(payload([first, second], [edge('defines', first, second), edge('defines', second, first)]))['valid'])

    def test_self_edges_and_reversed_successor_refuse(self):
        first, second = record('outcome', 'same', 1), record('outcome', 'same', 2)
        for name in ('supersedes', 'refines'):
            with self.assertRaisesRegex(ValueError, 'self'):
                canon.validate(payload([first], [edge(name, first, first)]))
        with self.assertRaisesRegex(ValueError, 'newer to older'):
            canon.validate(payload([first, second], [edge('supersedes', first, second)]))
        self.assertTrue(canon.validate(payload([first, second], [edge('supersedes', second, first)]))['valid'])
        with self.assertRaisesRegex(ValueError, 'distinct'):
            canon.validate(payload([first, second], [edge('refines', second, first)]))

    def test_scope_and_deferment(self):
        selected = record('scope_disposition')
        selected['content']['posture'] = 'deferred'
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(payload([selected]))
        selected['content']['destination_or_reopen_condition'] = 'Reopen when remote play is requested'
        self.assertTrue(canon.validate(payload([selected]))['valid'])
        selected['scope'] = 'horizon'
        with self.assertRaisesRegex(ValueError, 'schema'):
            canon.validate(payload([selected]))

    def test_file_sources_hashes_symlinks_and_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary).resolve()
            source = root / 'brief.md'
            source.write_bytes(b'Original source\r\n')
            selected = payload([record('definition')])
            selected['sources'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(canon.validate(selected, root=root)['source_verification'], 'checked')
            source.write_bytes(b'Changed source')
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                canon.validate(selected, root=root)
            source.unlink()
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                canon.validate(selected, root=root)
            (root / 'original.md').write_bytes(b'Original source\r\n')
            source.symlink_to(root / 'original.md')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                canon.validate(selected, root=root)
            for invalid in ('../brief.md', '/brief.md', '.git/config', 'folder//brief.md'):
                selected['sources'][0]['path'] = invalid
                with self.assertRaises(ValueError):
                    canon.validate(selected, root=root)

    def test_git_source_uses_exact_committed_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary).resolve()
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout.decode().strip()
            git('init', '--quiet')
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            source = root / 'brief.md'
            source.write_bytes(b'Frozen source\n')
            selected = payload([record('definition')])
            selected['sources'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
            git('add', 'brief.md')
            git('commit', '--quiet', '-m', 'Fixture source')
            selected['sources'][0]['git_commit'] = git('rev-parse', 'HEAD')
            source.unlink()
            self.assertTrue(canon.validate(selected, root=root)['valid'])
            selected['sources'][0]['git_commit'] = '0' * 40
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                canon.validate(selected, root=root)

    def test_duplicate_json_keys_and_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            filename = root / 'canon.json'
            filename.write_text('{"schema":1,"schema":2}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
                canon.load_json(filename)
            filename.write_text(json.dumps({'schema':'cp-canon-records-v1','sources':[],'records':[],'relationships':[]}))
            result = subprocess.run([sys.executable, str(script), str(filename), '--root', str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['admission'], 'not-assessed')
            self.assertEqual(list(root.iterdir()), [filename])


unittest.main(verbosity=2)
PY