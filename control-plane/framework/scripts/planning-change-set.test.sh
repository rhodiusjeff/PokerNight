#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

root = pathlib.Path(sys.argv.pop())
spec = importlib.util.spec_from_file_location('change_set', root / 'control-plane/framework/scripts/planning-change-set.py')
changes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(changes)
capture = changes.helper('planning-capture')


def record(identity='req', revision=1):
    return {'id':identity,'revision':revision,'kind':'functional_requirement','title':'Legal move','scope':'repository',
            'authority_status':'proposed','sources':['source-1'],'selection_rationale':'Distinct behavior',
            'content':{'obligation':'Allow a legal move','rationale':'Enable play','acceptance_direction':'Reject occupied cells'}}


def add(value, target_type='canon_record', identity=None):
    target = {'type':target_type,'id':value['id']} if target_type in ('canon_record','work_item') else changes.edge_target(value,target_type)
    return {'change_id':identity or 'add-'+value['id'],'operation':'add','target':target,'expected':{'state':'absent'},
            'value':copy.deepcopy(value),'rationale':'Fixture addition','sources':['source-1']}


def proposal(items=None, kind='ad-hoc'):
    context = {'kind':kind,'id':'H001' if kind == 'horizon' else 'ADHOC-'+'a'*32}
    if kind == 'discovery':
        context['origin']={'phase':{'id':'PHASE-1','revision':1},'contract':{'id':'contract','path':'contract.json','sha256':'0'*64}}
    return {'schema':changes.FORMAT,'id':context['id'],'revision':1,'title':'Fixture','author':'Fixture',
            'created_at':'2026-09-29T00:00:00Z','context':context,'status':'draft',
            'capture':{'id':'capture','path':'capture.md','sha256':'0'*64},'base':None,
            'sources':[{'id':'source-1','path':'source.md','sha256':'0'*64}],'changes':items or [],'unresolved':[]}


def work(identity='work'):
    return {'id':identity,'revision':1,'maturity':'candidate','title':'Playable game','outcome':'Deliver game',
            'included':['Game'],'excluded':[],'canon_refs':[{'id':'req','revision':1}], 'acceptance':['Play works'],
            'tasks':[{'id':'implement','text':'Implement game','after':[]}],'risks':[],'sources':['source-1']}


class ChangeTests(unittest.TestCase):
    def test_all_planning_origins_share_schema(self):
        for kind in ('ad-hoc','horizon','discovery'):
            with self.subTest(kind=kind):
                self.assertEqual(changes.shape(proposal([add(record())],kind))['context']['kind'],kind)
        invalid=proposal(kind='discovery')
        del invalid['context']['origin']
        with self.assertRaises(ValueError): changes.shape(invalid)

    def test_empty_and_unknown_base_differ(self):
        value=proposal([add(record())])
        self.assertIsNone(changes.compose(value,None)['result'])
        result=changes.compose(value,changes.empty_base())
        self.assertEqual(len(result['result']['canon']['records']),1)
        self.assertNotIn('result',value)

    def test_no_base64_or_result_snapshot(self):
        for key,value in [('result',{}),('workflow',{})]:
            document=proposal()
            document[key]=value
            with self.assertRaises(ValueError): changes.shape(document)
        document=proposal()
        document['sources'][0]['bytes_base64']='eA=='
        with self.assertRaises(ValueError): changes.shape(document)

    def test_add_requires_absence_and_revision_one(self):
        base=changes.empty_base()
        base['canon']['sources']=proposal()['sources']
        base['canon']['records']=[record()]
        with self.assertRaisesRegex(ValueError,'already exists'): changes.compose(proposal([add(record())]),base)
        with self.assertRaisesRegex(ValueError,'revision 1'): changes.compose(proposal([add(record(revision=2))]),changes.empty_base())

    def test_modify_full_successor_and_exact_preconditions(self):
        original=record()
        base=changes.empty_base()
        base['canon'].update(sources=proposal()['sources'],records=[original])
        changed=add(record(revision=2))
        changed.update(operation='modify',expected={'state':'present','revision':1,'digest':changes.digest(original)})
        result=changes.compose(proposal([changed]),base)['result']
        self.assertEqual([item['revision'] for item in result['canon']['records']],[1,2])
        self.assertEqual(result['effective_record_refs'],[{'id':'req','revision':2}])
        changed['expected']['digest']='0'*64
        with self.assertRaisesRegex(ValueError,'stale'): changes.compose(proposal([changed]),base)
        del changed['value']['content']['obligation']
        with self.assertRaisesRegex(ValueError,'schema'): changes.compose(proposal([changed]),base)

    def test_conflicting_changes_and_unresolved_ids_refuse(self):
        first=add(record())
        second={**copy.deepcopy(first),'change_id':'another'}
        with self.assertRaisesRegex(ValueError,'conflicting'): changes.compose(proposal([first,second]),changes.empty_base())
        value=proposal([first])
        value['unresolved']=[{'id':'gap','explanation':'Unknown','affects':['missing']}]
        with self.assertRaisesRegex(ValueError,'unresolved'): changes.compose(value,changes.empty_base())

    def test_edge_can_precede_its_added_endpoints(self):
        definition={'id':'term','revision':1,'kind':'definition','title':'Mark','scope':'repository','authority_status':'proposed',
                    'sources':['source-1'],'selection_rationale':'Term is reused','content':{'term':'mark','meaning':'X or O','applies_to':'Game','aliases':[]}}
        edge={'kind':'defines','from':{'id':'term','revision':1},'to':{'id':'req','revision':1},'rationale':'Term used by requirement','sources':['source-1']}
        value=proposal([add(edge,'canon_relationship','edge'),add(record()),add(definition)])
        self.assertEqual(len(changes.compose(value,changes.empty_base())['result']['canon']['relationships']),1)
        value['changes'][0]['value']['to']['revision']=9
        with self.assertRaisesRegex(ValueError,'edge mismatch'): changes.compose(value,changes.empty_base())

    def test_relationship_replace_is_remove_add(self):
        first,second=record('first'),record('second')
        edge={'kind':'refines','from':{'id':'first','revision':1},'to':{'id':'second','revision':1},'rationale':'Original rationale','sources':['source-1']}
        base=changes.empty_base()
        base['canon'].update(sources=proposal()['sources'],records=[first,second],relationships=[edge])
        new={**edge,'rationale':'Revised rationale'}
        added=add(new,'canon_relationship','replacement')
        removed={key:value for key,value in added.items() if key!='value'}
        removed.update(change_id='remove-old',operation='remove',expected={'state':'present','digest':changes.digest(edge)})
        self.assertEqual(changes.compose(proposal([added,removed]),base)['result']['canon']['relationships'],[new])
        added['operation']='modify'
        with self.assertRaisesRegex(ValueError,'schema'): changes.shape(proposal([added]))

    def test_obsolete_retains_history_and_rejects_live_references(self):
        base=changes.empty_base()
        base['canon'].update(sources=proposal()['sources'],records=[record()])
        deletion={'change_id':'obsolete','operation':'obsolete','target':{'type':'canon_record','id':'req'},
                  'expected':{'state':'present','revision':1,'digest':changes.digest(record())},'rationale':'No longer applicable','sources':['source-1']}
        result=changes.compose(proposal([deletion]),base)['result']
        self.assertEqual(result['effective_record_refs'],[])
        self.assertEqual(result['canon']['records'],[record()])
        base['work_items']=[work()]
        with self.assertRaisesRegex(ValueError,'unavailable Canon'): changes.compose(proposal([deletion]),base)

    def test_work_dependencies_and_task_cycles(self):
        first,second=work('first'),work('second')
        edge={'from':{'id':'first','revision':1},'to':{'id':'second','revision':1},'rationale':'Prerequisite','sources':['source-1']}
        value=proposal([add(record()),add(first,'work_item'),add(second,'work_item'),add(edge,'work_dependency','dep')])
        self.assertEqual(len(changes.compose(value,changes.empty_base())['result']['dependencies']),1)
        reverse={**edge,'from':edge['to'],'to':edge['from']}
        value['changes'].append(add(reverse,'work_dependency','reverse'))
        with self.assertRaisesRegex(ValueError,'cycle'): changes.compose(value,changes.empty_base())
        first['tasks'][0]['after']=['implement']
        with self.assertRaisesRegex(ValueError,'task dependency'): changes.compose(proposal([add(record()),add(first,'work_item')]),changes.empty_base())

    def test_complete_requires_base_no_gaps_and_specified_work(self):
        value=proposal([add(record()),add(work(),'work_item')])
        value['status']='complete'
        with self.assertRaisesRegex(ValueError,'schema'): changes.shape(value)
        value['base']={'path':'base.json','sha256':'0'*64,'revision':0,'target_ref':'refs/heads/main','git_commit':'0'*40}
        with self.assertRaisesRegex(ValueError,'incomplete work'): changes.compose(value,changes.empty_base())
        value['changes'].pop()
        self.assertTrue(changes.compose(value,changes.empty_base())['base_verified'])

    def test_migrate_save_sources_and_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=pathlib.Path(temporary).resolve()
            source=folder/'source.md'
            source.write_bytes(b'Exact source\r\n')
            identity='ADHOC-'+'a'*32
            capture.create_capture(SimpleNamespace(root=folder,id=identity,kind='ad-hoc',title='Fixture',author='Fixture',
                sources=[source],origin_phase=None,origin_specification=None,confirmed=True))
            filename=capture.resolve_document(folder,identity)
            before=filename.read_bytes()
            old=capture.read_capture(filename)
            document=proposal([add(record())])
            document['created_at']=old['created_at']
            document['sources'][0]['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
            document['capture']['path']=capture.narrative_path(filename).relative_to(folder).as_posix()
            result=changes.save(folder,identity,document,hashlib.sha256(before).hexdigest(),'Operator confirmed fixture migration.',True)
            current=capture.read_capture(filename)
            self.assertEqual(current['schema'],changes.FORMAT)
            self.assertNotIn('bytes_base64',filename.read_text())
            self.assertEqual(next((filename.parent/'assets/history').glob('*-proposal.json')).read_bytes(),before)
            self.assertFalse(changes.save(folder,identity,current,result['document_digest'],'Retry')['updated'])
            with self.assertRaisesRegex(ValueError,'change-set proposal'):
                capture.require_mutable(current)
            updated=copy.deepcopy(current)
            updated['revision']=2
            updated['title']='Changed title'
            with self.assertRaisesRegex(ValueError,'changed since'):
                changes.save(folder,identity,updated,'0'*64,'Operator confirmed change.')
            next_result=changes.save(folder,identity,updated,result['document_digest'],'Operator confirmed title change.')
            self.assertEqual(capture.read_capture(filename)['revision'],2)
            self.assertTrue(next_result['updated'])
            retry=changes.save(folder,identity,updated,result['document_digest'],'Operator confirmed title change.')
            self.assertFalse(retry['updated'])
            completed=copy.deepcopy(capture.read_capture(filename))
            completed.update(status='complete',revision=3)
            with self.assertRaisesRegex(ValueError,'explicit complete'):
                changes.save(folder,identity,completed,next_result['document_digest'],'Attempted status-only completion.')
            current_digest=hashlib.sha256(filename.read_bytes()).hexdigest()
            current_md=hashlib.sha256(capture.narrative_path(filename).read_bytes()).hexdigest()
            capture.recover_pair(folder,identity,current_digest,current_md,result['document_digest'],True)
            self.assertEqual(capture.read_capture(filename)['revision'],1)
            source.write_text('Changed source')
            with self.assertRaisesRegex(ValueError,'digest mismatch'):
                changes.validate(folder,capture.read_capture(filename))

    def test_pinned_empty_legacy_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=pathlib.Path(temporary).resolve()
            def git(*args):
                return changes.git(folder,*args).decode().strip()
            git('init','--quiet','-b','main')
            git('config','user.name','Fixture')
            git('config','user.email','fixture@example.invalid')
            baseline=folder/'base.json'
            baseline.write_bytes(changes.encoded(changes.helper('planning-contract').empty_specification()))
            git('add','base.json')
            git('commit','--quiet','-m','Empty fixture base')
            reference={'target_ref':'refs/heads/main','git_commit':git('rev-parse','HEAD'),'path':'base.json','revision':0,
                       'sha256':hashlib.sha256(baseline.read_bytes()).hexdigest()}
            self.assertEqual(changes.baseline(folder,reference),changes.empty_base())
            reference['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'digest mismatch'): changes.baseline(folder,reference)

    def test_work_specification_fields_and_missing_content_refuse(self):
        value=work()
        value['maturity']='specified'
        with self.assertRaisesRegex(ValueError,'schema'):
            changes.shape(proposal([add(value,'work_item')]))
        value['specification']={'execution_model':'Operator-selected','sizing_rationale':'One bounded result',
            'validation_plan':['Run behavior suite'],'failure_discovery_route':'Capture new scope before acting',
            'review_boundary':'self','closeout_basis':'Verified tests and reviewed delivery'}
        self.assertTrue(changes.shape(proposal([add(value,'work_item')])))

    def test_schema_links_in_entry_points(self):
        paths=['.github/prompts/plan-work.prompt.md','.github/agents/project-planning-design.agent.md',
               '.github/skills/planning-workflow/SKILL.md','.github/skills/canon-consolidation/SKILL.md',
               '.github/skills/work-plan-shaping/SKILL.md','.github/skills/guided-admission/SKILL.md']
        for relative in paths:
            self.assertIn('plan-change-set.policy.md',(root/relative).read_text(),relative)


unittest.main(verbosity=2)
PY