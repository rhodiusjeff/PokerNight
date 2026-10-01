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
    def repository_fixture(self, kind='ad-hoc', minted=False):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder=pathlib.Path(temporary.name).resolve()
        repository=changes.helper('planning-repository')
        git=lambda *args: changes.git(folder,*args).decode().strip()
        git('init','--quiet','-b','main')
        git('config','user.name','Fixture')
        git('config','user.email','fixture@example.invalid')
        for relative,value in zip(repository.LEGACY,(capture.contract.empty_specification(),{'phases':{},'contracts':{}})):
            filename=folder/relative
            filename.parent.mkdir(parents=True,exist_ok=True)
            filename.write_bytes(changes.encoded(value))
        git('add','control-plane')
        git('commit','--quiet','-m','Empty operational fixture')
        document=proposal([add(record())],kind)
        document.update(status='complete',base=repository.reference(folder,'refs/heads/main'))
        home='control-plane/horizons' if kind == 'horizon' else 'control-plane/ad-hoc'
        filename=folder/home/document['id']/(document['id']+'-proposal.json')
        filename.parent.mkdir(parents=True)
        narrative=capture.narrative_path(filename)
        narrative.write_text('Operator fixture requirements\n')
        document['capture'].update(path=narrative.relative_to(folder).as_posix(),sha256=hashlib.sha256(narrative.read_bytes()).hexdigest())
        source=folder/'source.md'
        source.write_text('A player makes legal moves.\n')
        document['sources'][0]['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
        if kind == 'discovery':
            (folder/'contract.json').write_bytes(b'Exact originating contract\n')
            document['context']['origin']['contract']['sha256']=hashlib.sha256((folder/'contract.json').read_bytes()).hexdigest()
        if minted:
            issued=changes.identity_policy.mint(folder,kind,'fixture','fixture-create','Fixture',document['context'].get('origin'),True)
            document['id']=document['context']['id']=issued['id']
            bindings=[{'change_id':change['change_id'],'operation':change['operation'],'target':change['target'],
                       'kind':change['value']['kind']} for change in document['changes']]
            allocated=changes.identity_policy.reserve_records(folder,document['id'],'fixture-records',bindings,confirmed=True)
            document['identity']={'mint':{'operation_id':issued['operation_id'],'request_digest':issued['request_digest']},
                'allocation':allocated['state'],'aliases':{'contexts':[],'canon':{},'changes':{}}}
            for change in document['changes']:
                change['change_id']=allocated['mapping']['changes'][change['change_id']]
                change['target']['id']=change['value']['id']=allocated['mapping']['canon'][change['value']['id']]
            filename=folder/home/document['id']/(document['id']+'-proposal.json')
            filename.parent.mkdir(parents=True)
            new_narrative=capture.narrative_path(filename)
            new_narrative.write_bytes(narrative.read_bytes())
            narrative.unlink()
            narrative=new_narrative
            document['capture']['path']=narrative.relative_to(folder).as_posix()
        filename.write_bytes(changes.encoded(document))
        return folder,document,repository,filename

    def lifecycle_event(self, action='create', preimage=None):
        event={'operation_id':'fixture-'+action,'action':action,'actor':'Fixture Operator',
               'invocation_source':'operator-command','timestamp':'2026-09-30T12:00:00Z','preimage':preimage}
        if action in ('suspend','abandon','close'):
            event['reason']='Fixture disposition'
        if action == 'suspend':
            event['next_step']='Resume after inspection'
        return event

    def test_paired_save_across_all_scopes(self):
        for kind in ('ad-hoc','discovery','horizon'):
            with self.subTest(kind=kind):
                folder,document,repository,filename=self.repository_fixture(kind,minted=True)
                document.update(status='draft')
                document['context']['lifecycle']={'state':'planning','events':[self.lifecycle_event()]}
                filename.write_bytes(changes.encoded(document))
                before=filename.read_bytes()
                narrative=capture.narrative_path(filename).read_bytes()
                expected=hashlib.sha256(before).hexdigest()
                self.assertEqual(capture.resolve_document(folder,document['id']),filename)
                changed=copy.deepcopy(document)
                changed.update(status='draft',revision=2,title='Revised fixture')
                result=changes.save(folder,document['id'],changed,expected,'Operator requested a draft revision.')
                current=capture.read_capture(filename)
                self.assertTrue(result['updated'])
                self.assertEqual(current['context'],document['context'])
                self.assertEqual(current['identity'],document['identity'])
                self.assertEqual(current['sources'],document['sources'])
                self.assertEqual(capture.assets_path(folder,document['id']),filename.parent/'assets')
                self.assertEqual((capture.assets_path(folder,document['id'])/'history'/(expected+'-proposal.json')).read_bytes(),before)
                self.assertEqual((capture.assets_path(folder,document['id'])/'history'/(expected+'-capture.md')).read_bytes(),narrative)
                self.assertFalse(changes.save(folder,document['id'],changed,expected,'Operator requested a draft revision.')['updated'])
                completed=copy.deepcopy(current)
                completed.update(status='complete',revision=3)
                self.assertTrue(changes.save(folder,document['id'],completed,result['document_digest'],'Operator confirmed completion.',complete=True)['updated'])
                self.assertTrue(changes.validate(folder,capture.read_capture(filename))['base_verified'])

    def test_finalize_proposal_all_scopes_and_freshness(self):
        for kind in ('ad-hoc','discovery','horizon'):
            with self.subTest(kind=kind):
                folder,document,repository,filename=self.repository_fixture(kind,minted=True)
                document['status']='draft'
                filename.write_bytes(changes.encoded(document))
                before=filename.read_bytes()
                expected=hashlib.sha256(before).hexdigest()
                completed=copy.deepcopy(document)
                completed.update(status='complete',revision=2)
                unknown=copy.deepcopy(completed)
                unknown['base']=None
                with self.assertRaisesRegex(ValueError,'exact baseline'):
                    changes.finalize_proposal(folder,document['id'],unknown,expected,'Finalize supplied content')
                self.assertEqual(filename.read_bytes(),before)
                result=changes.finalize_proposal(folder,document['id'],completed,expected,'Finalize supplied content')
                self.assertTrue(result['updated'])
                self.assertFalse(changes.finalize_proposal(folder,document['id'],completed,expected,'Finalize supplied content')['updated'])
                changes.git(folder,'commit','--allow-empty','--quiet','-m','Target advanced')
                with self.assertRaisesRegex(ValueError,'baseline is stale'):
                    changes.finalize_proposal(folder,document['id'],completed,result['document_digest'],'Finalize supplied content')

    def test_planning_input_changes_invalidate_finalization(self):
        for kind in ('ad-hoc','discovery','horizon'):
            for field in ('meaning','source','decision','scope','base'):
                with self.subTest(kind=kind,field=field):
                    folder,document,repository,filename=self.repository_fixture(kind,minted=True)
                    before=filename.read_bytes()
                    narrative=capture.narrative_path(filename).read_bytes()
                    expected=hashlib.sha256(before).hexdigest()
                    changed=copy.deepcopy(document)
                    changed['revision']+=1
                    if field == 'meaning':
                        changed['changes'][0]['value']['content']['obligation']='Allow only validated legal moves'
                    elif field == 'source':
                        (folder/'additional.md').write_text('Additional planning source\n')
                        changed['sources'].append({'id':'source-2','path':'additional.md','sha256':hashlib.sha256((folder/'additional.md').read_bytes()).hexdigest()})
                    elif field == 'scope':
                        changed['unresolved']=[{'id':'scope-gap','explanation':'Operator must resolve scope','affects':[]}]
                    elif field == 'base':
                        changed['base']=None
                    result=changes.save(folder,document['id'],changed,expected,'Operator changed '+field)
                    current=capture.read_capture(filename)
                    self.assertEqual(current['status'],'draft')
                    self.assertEqual(current['context'],document['context'])
                    self.assertEqual(current['identity'],document['identity'])
                    history=filename.parent/'assets/history'
                    self.assertEqual((history/(expected+'-proposal.json')).read_bytes(),before)
                    self.assertEqual((history/(expected+'-capture.md')).read_bytes(),narrative)
                    with self.assertRaisesRegex(ValueError,'complete change set'):
                        changes.helper('planning-change-evidence').subject(folder,current)
                    self.assertFalse(changes.save(folder,document['id'],changed,result['document_digest'],'Operator changed '+field)['updated'])

    def test_finalize_cli_and_retired_complete_no_writes(self):
        folder,document,repository,filename=self.repository_fixture()
        executable=[sys.executable,str(root/'control-plane/framework/scripts/planning-change-set.py'),'--root',str(folder)]
        inventory=lambda: {item.relative_to(folder):item.read_bytes() for item in folder.rglob('*') if item.is_file()}
        before=inventory()
        for arguments in (['--complete'],['--context',document['id'],'complete','--request','missing']):
            result=subprocess.run([*executable,*arguments],capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('use finalize-proposal',result.stderr)
            self.assertEqual(inventory(),before)
        document['status']='draft'
        filename.write_bytes(changes.encoded(document))
        expected=hashlib.sha256(filename.read_bytes()).hexdigest()
        document.update(status='complete',revision=2)
        (folder/'request-note.md').write_text('Operator explicitly requested finalization')
        arguments=['--context',document['id'],'finalize-proposal','--request','-',
                   '--expected-digest',expected,'--record',str(folder/'request-note.md')]
        before=inventory()
        refused=subprocess.run([*executable,*arguments],input=json.dumps(document),capture_output=True,text=True)
        self.assertNotEqual(refused.returncode,0)
        self.assertEqual(inventory(),before)
        result=subprocess.run([*executable,*arguments,'--confirmed'],input=json.dumps(document),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['updated'])

    def test_finalization_validation_and_admission_edit_lock(self):
        for kind in ('ad-hoc','discovery','horizon'):
            with self.subTest(kind=kind):
                folder,document,repository,filename=self.repository_fixture(kind)
                document['status']='draft'
                filename.write_bytes(changes.encoded(document))
                expected=hashlib.sha256(filename.read_bytes()).hexdigest()
                inventory=lambda: {item.relative_to(filename.parent):item.read_bytes() for item in filename.parent.rglob('*') if item.is_file()}
                before=inventory()
                completed=copy.deepcopy(document)
                completed.update(status='complete',revision=2)
                for defect in ('work','unresolved','empty','source'):
                    invalid=copy.deepcopy(completed)
                    if defect == 'work': invalid['changes'].append(add(work(),'work_item'))
                    elif defect == 'unresolved': invalid['unresolved']=[{'id':'gap','explanation':'Unresolved decision','affects':[]}]
                    elif defect == 'empty': invalid['changes']=[]
                    else: invalid['sources'][0]['sha256']='0'*64
                    with self.subTest(defect=defect), self.assertRaises(ValueError):
                        changes.finalize_proposal(folder,document['id'],invalid,expected,'Explicit finalization')
                    self.assertEqual(inventory(),before)
                changes.validate(folder,document)
                (folder/'unrelated.md').write_text('Unrelated work')
                self.assertEqual(inventory(),before)
                publication=changes.helper('planning-publication')
                claim=folder/'control-plane/state/planning-local/publication/claims'/(document['id']+'.json')
                publication.immutable_json(folder,claim,{'attempt_id':'fixture-lock','bundle_id':'fixture'})
                directory=publication.attempt_directory(folder,'fixture-lock')
                publication.append_event(folder,directory,'published',{})
                for candidate,finish in (({**document,'revision':2,'title':'Changed'},False),(completed,True)):
                    with self.assertRaisesRegex(ValueError,'active publication'):
                        changes.save(folder,document['id'],candidate,expected,'Attempted edit',complete=finish)
                    self.assertEqual(inventory(),before)
                publication.append_event(folder,directory,'applied',{'application_verified':True})
                with self.assertRaisesRegex(ValueError,'post-application draft reset unavailable'):
                    changes.save(folder,document['id'],{**document,'revision':2,'changes':[]},expected,'Attempted blind reset')
                self.assertEqual(inventory(),before)

    def test_lifecycle_schema_and_legacy_default(self):
        changes.Draft202012Validator.check_schema(changes.canon.load_json(changes.SCHEMA_PATH))
        document=proposal()
        self.assertEqual(changes.lifecycle_state(document),'planning')
        self.assertNotIn('lifecycle',document['context'])
        preimage={'proposal':{'id':'previous-proposal','path':'assets/history/previous-proposal.json','sha256':'1'*64},
                  'capture':{'id':'previous-capture','path':'assets/history/previous-capture.md','sha256':'2'*64}}
        for state,action in [('planning','create'),('planning','resume'),('suspended','suspend'),('abandoned','abandon'),('closed','close')]:
            with self.subTest(state=state,action=action):
                lifecycle={'state':state,'events':[self.lifecycle_event(action,None if action == 'create' else preimage)]}
                if state == 'closed':
                    lifecycle['closure']={'applied':[{'proposal':preimage['proposal'],'attempt':preimage['capture'],'verification':preimage['capture']}],
                        'remaining_scope':[{'scope':'Remaining candidate','disposition':'deferred','evidence':preimage['capture']}]}
                document['context']['lifecycle']=lifecycle
                self.assertEqual(changes.lifecycle_state(document),state)
        invalids=[None,{}, {'state':'absorbed','events':[]},{'state':'suspended','events':[]},
                  {'state':'planning','events':[],'extra':True}, {'state':'planning','events':[],'closure':{}}]
        valid={'state':'planning','events':[self.lifecycle_event()]}
        for field,bad in [('timestamp','yesterday'),('actor',''),('invocation_source','inferred'),('preimage',preimage),('extra',True)]:
            malformed=copy.deepcopy(valid)
            malformed['events'][0][field]=bad
            invalids.append(malformed)
        invalids.append({'state':'planning','events':[self.lifecycle_event(),self.lifecycle_event()]})
        invalids.append({'state':'suspended','events':[self.lifecycle_event()]})
        invalids.append({'state':'closed','events':[self.lifecycle_event('close',preimage)]})
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                document['context']['lifecycle']=invalid
                with self.assertRaises(ValueError): changes.shape(document)

    def test_save_cannot_change_identity_origin_or_lifecycle(self):
        folder,document,repository,filename=self.repository_fixture('discovery',minted=True)
        document['context']['lifecycle']={'state':'planning','events':[]}
        filename.write_bytes(changes.encoded(document))
        before=filename.read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        for field in ('id','author','created_at','kind','origin','lifecycle'):
            changed=copy.deepcopy(document)
            changed.update(revision=2,status='draft')
            if field in ('kind','origin','lifecycle'):
                changed['context'].pop(field)
            else:
                changed[field]='Changed'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'immutable'):
                changes.save(folder,document['id'],changed,expected,'Attempted metadata rewrite')
            self.assertEqual(filename.read_bytes(),before)

    def test_pair_requires_exact_repository_relative_capture_path(self):
        for kind in ('ad-hoc','discovery','horizon'):
            with self.subTest(kind=kind):
                folder,document,repository,filename=self.repository_fixture(kind,minted=True)
                narrative=capture.narrative_path(filename)
                correct=document['capture']['path']
                self.assertEqual(capture.read_capture(filename),document)
                for wrong in (narrative.name,document['id']+'/'+narrative.name,'other/'+correct,
                              correct.replace('control-plane/',''),correct.replace('/'+document['id']+'/', '/other/')):
                    invalid=copy.deepcopy(document)
                    invalid['capture']['path']=wrong
                    filename.write_bytes(changes.encoded(invalid))
                    before=filename.read_bytes()
                    with self.subTest(path=wrong), self.assertRaisesRegex(ValueError,'companion file'):
                        capture.read_capture(capture.resolve_document(folder,document['id']))
                    self.assertEqual(filename.read_bytes(),before)
                filename.write_bytes(changes.encoded(document))
                self.assertEqual(capture.read_capture(filename),document)

    def test_rekey_refuses_lifecycle_without_changing_package(self):
        folder,document,repository,filename=self.repository_fixture()
        document['status']='draft'
        before=changes.encoded(document)
        filename.write_bytes(before)
        narrative=capture.narrative_path(filename).read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        history=filename.parent/'assets/history'
        preimage={'proposal':{'id':'prior-proposal','path':(history/(expected+'-proposal.json')).relative_to(folder).as_posix(),'sha256':expected},
                  'capture':{'id':'prior-capture','path':(history/(expected+'-capture.md')).relative_to(folder).as_posix(),
                             'sha256':hashlib.sha256(narrative).hexdigest()}}
        document['revision']+=1
        document['context']['lifecycle']={'state':'planning','events':[self.lifecycle_event('resume',preimage)]}
        with capture.local_writer(folder):
            changes._publish_pair(folder,filename,before,narrative,changes.encoded(document),narrative)
        inventory={item.relative_to(folder):item.read_bytes() for item in folder.rglob('*') if item.is_file()}
        with self.assertRaisesRegex(ValueError,'lifecycle-bearing rekey is unavailable'):
            changes.rekey_package(folder,document['id'],'rekey-review','review-rekey',hashlib.sha256(filename.read_bytes()).hexdigest(),True)
        self.assertEqual(inventory,{item.relative_to(folder):item.read_bytes() for item in folder.rglob('*') if item.is_file()})
        for reference in preimage.values(): changes.canon.verify_source(folder,reference)

    def test_strict_horizon_pair_and_legacy_dispatch(self):
        folder,document,repository,filename=self.repository_fixture('horizon',minted=True)
        raw=filename.read_bytes()
        narrative=capture.narrative_path(filename)
        original_narrative=narrative.read_bytes()
        for malformed in ({**document,'schema':'unknown'}, {**document,'unknown':True}, [],
                          {**document,'context':{**document['context'],'id':'H001'}}):
            filename.write_bytes(changes.encoded(malformed))
            with self.assertRaises(ValueError): capture.read_capture(capture.resolve_document(folder,document['id']))
        filename.write_bytes(raw.replace(b'"schema":',b'"schema":"duplicate", "schema":',1))
        with self.assertRaisesRegex(ValueError,'duplicate'): capture.read_capture(filename)
        filename.write_bytes(raw)
        narrative.write_bytes(b'Unpaired edit\r\n')
        self.assertEqual(capture.resolve_document(folder,document['id']),filename)
        with self.assertRaisesRegex(ValueError,'pair mismatch'): capture.read_capture(filename)
        narrative.unlink()
        with self.assertRaisesRegex(ValueError,'pair mismatch'): capture.read_capture(filename)
        narrative.write_bytes(original_narrative)
        legacy=filename.parent/'planning'/(document['id']+'.md')
        legacy.parent.mkdir()
        old={'schema':'cp-planning-capture-v1','id':document['id'],'kind':'horizon','title':'Old fixture','author':'Fixture',
             'created_at':'2026-09-30T00:00:00Z','sources':[capture.canonical_source(folder/'source.md',1)],'origin':None,
             'context':{'state':'absorbed'}}
        legacy.write_bytes(capture.render_legacy(old).encode())
        with self.assertRaisesRegex(ValueError,'mixed horizon'): capture.resolve_document(folder,document['id'])
        filename.unlink()
        narrative.unlink()
        self.assertEqual(capture.resolve_document(folder,document['id']),legacy)
        self.assertEqual(capture.read_capture(legacy),old)
        with self.assertRaisesRegex(ValueError,'read-only'):
            changes.save(folder,document['id'],document,hashlib.sha256(legacy.read_bytes()).hexdigest(),'No implicit conversion')
        self.assertEqual(capture.read_capture(legacy),old)
        self.assertFalse(filename.exists())

    def test_pair_publication_lifecycle_preimages_and_failure(self):
        folder,document,repository,filename=self.repository_fixture('horizon',minted=True)
        before=filename.read_bytes()
        narrative=capture.narrative_path(filename)
        old_narrative=narrative.read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        history=filename.parent/'assets/history'
        preimage={'proposal':{'id':'prior-proposal','path':(history/(expected+'-proposal.json')).relative_to(folder).as_posix(),'sha256':expected},
                  'capture':{'id':'prior-capture','path':(history/(expected+'-capture.md')).relative_to(folder).as_posix(),
                             'sha256':hashlib.sha256(old_narrative).hexdigest()}}
        changed=copy.deepcopy(document)
        changed['revision']=2
        changed['context']['lifecycle']={'state':'suspended','events':[self.lifecycle_event('suspend',preimage)]}
        content=changes.encoded(changed)
        original_replace=capture.replace_bytes
        def fail_proposal(destination,original,updated):
            if destination == filename:
                raise OSError('injected proposal publication failure')
            original_replace(destination,original,updated)
        real_helper=changes.helper
        with mock.patch.object(changes,'helper',side_effect=lambda name: capture if name == 'planning-capture' else real_helper(name)), \
             mock.patch.object(capture,'replace_bytes',side_effect=fail_proposal), capture.local_writer(folder):
            with self.assertRaisesRegex(OSError,'injected'):
                changes._publish_pair(folder,filename,before,old_narrative,content,old_narrative)
        self.assertEqual(filename.read_bytes(),before)
        self.assertEqual(narrative.read_bytes(),old_narrative)
        with capture.local_writer(folder):
            changes._publish_pair(folder,filename,before,old_narrative,content,old_narrative)
        self.assertEqual((history/(expected+'-proposal.json')).read_bytes(),before)
        self.assertEqual((history/(expected+'-capture.md')).read_bytes(),old_narrative)
        for source in preimage.values(): changes.canon.verify_source(folder,source)
        self.assertEqual(changes.lifecycle_state(capture.read_capture(filename)),'suspended')
        with self.assertRaisesRegex(ValueError,'not mutable planning'):
            changes.save(folder,document['id'],changed,hashlib.sha256(content).hexdigest(),'No implicit resume')

    def test_horizon_pair_recovery_preserves_metadata(self):
        folder,document,repository,filename=self.repository_fixture('horizon',minted=True)
        before=filename.read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        narrative=capture.narrative_path(filename)
        before_narrative=narrative.read_bytes()
        changed=copy.deepcopy(document)
        changed.update(revision=2,status='draft')
        changes.save(folder,document['id'],changed,expected,'Operator requested a new draft')
        narrative.write_bytes(b'Interrupted narrative update\r\n')
        result=capture.recover_pair(folder,document['id'],hashlib.sha256(filename.read_bytes()).hexdigest(),
            hashlib.sha256(narrative.read_bytes()).hexdigest(),expected,True)
        self.assertTrue(result['recovered'])
        self.assertEqual(filename.read_bytes(),before)
        self.assertEqual(narrative.read_bytes(),before_narrative)

    def test_current_pair_inventory_and_guarded_writers(self):
        folder,document,repository,filename=self.repository_fixture('horizon',minted=True)
        context=changes.helper('planning-context')
        before=filename.read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        binding=folder/'control-plane/state/planning-local/binding.json'
        self.assertEqual(context.inspect_context(folder,document['id'])['path'],str(filename))
        self.assertEqual(context.planning_status(folder)['count'],1)
        with self.assertRaisesRegex(ValueError,'confirmation'):
            context.activate(folder,document['id'],False)
        with self.assertRaisesRegex(ValueError,'operation token'):
            context.transition(folder,document['id'],'suspend',expected,'Fixture next step',True)
        with self.assertRaisesRegex(ValueError,'unavailable'):
            changes.helper('planning-admission').prepare(folder,document['id'],'no-decision',None,None,expected,True)
        self.assertEqual(filename.read_bytes(),before)
        self.assertFalse(binding.exists())
        self.assertFalse((filename.parent/'assets/admission').exists())

    def test_repository_admission_history_and_round_trip(self):
        folder,document,repository,filename=self.repository_fixture()
        selected=repository.snapshot(folder,document['base']['git_commit'])
        result=repository.compose(document,selected,'1'*64)
        self.assertEqual(result['canon']['records'][0]['authority_status'],'admitted')
        self.assertEqual(document['changes'][0]['value']['authority_status'],'proposed')
        self.assertEqual(repository.validate(json.loads(json.dumps(result))),result)
        self.assertEqual(result['tracker']['revision'],1)
        with self.assertRaisesRegex(ValueError,'already admitted'):
            repository.compose(document,{**selected,'state':result},'1'*64)
        original=copy.deepcopy(result['canon']['records'][0])
        updated=copy.deepcopy(document)
        updated['revision']=2
        updated['sources']=copy.deepcopy(result['canon']['sources'])
        updated['changes']=[{'change_id':'obsolete','operation':'obsolete','target':{'type':'canon_record','id':'req'},
            'expected':{'state':'present','revision':1,'digest':changes.digest(original)},'rationale':'Retire fixture obligation','sources':['source-1']}]
        updated['base']['revision']=1
        retired=repository.compose(updated,{**selected,'state':result},'2'*64)
        self.assertEqual(retired['canon']['records'][0],original)
        self.assertEqual(retired['canon']['records'][-1]['authority_status'],'retired')
        self.assertEqual(repository.latest_records(retired['canon'])['req']['revision'],2)

    def test_applied_target_cannot_be_blindly_reset_without_claim(self):
        folder,document,repository,filename=self.repository_fixture()
        result=repository.compose(document,repository.snapshot(folder,document['base']['git_commit']),'1'*64)
        for key,relative in repository.PATHS.items():
            destination=folder/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(changes.encoded(result[key]))
        for relative in repository.LEGACY: (folder/relative).unlink()
        changes.git(folder,'add','--',*repository.PATHS.values(),*repository.LEGACY)
        changes.git(folder,'commit','--quiet','-m','Applied target fixture')
        before=filename.read_bytes()
        reset=copy.deepcopy(document)
        reset.update(status='draft',revision=2,changes=[],base=repository.reference(folder,'refs/heads/main'))
        with self.assertRaisesRegex(ValueError,'post-application draft reset unavailable'):
            changes.save(folder,document['id'],reset,hashlib.sha256(before).hexdigest(),'Attempted blind reset')
        self.assertEqual(filename.read_bytes(),before)
        self.assertFalse((filename.parent/'assets/history').exists())

        changes.git(folder,'branch','-m','main','applied-target')
        reset['base']=repository.reference(folder,'refs/heads/applied-target')
        with self.assertRaisesRegex(ValueError,'post-application draft reset unavailable'):
            changes.save(folder,document['id'],reset,hashlib.sha256(before).hexdigest(),'Attempted reset through replacement target')
        self.assertEqual(filename.read_bytes(),before)
        document['base']=copy.deepcopy(reset['base'])
        filename.write_bytes(changes.encoded(document))
        before=filename.read_bytes()
        changes.git(folder,'branch','-m','applied-target','renamed-again')
        reset['base']=None
        with self.assertRaisesRegex(ValueError,'post-application draft reset unavailable'):
            changes.save(folder,document['id'],reset,hashlib.sha256(before).hexdigest(),'Attempted unknown-base reset of pinned application')
        self.assertEqual(filename.read_bytes(),before)
        self.assertFalse((filename.parent/'assets/history').exists())

    def test_draft_reconciliation_after_target_rename(self):
        for kind in ('ad-hoc','discovery','horizon'):
            for selected_base in ('replacement','unknown','retained'):
                with self.subTest(kind=kind,selected_base=selected_base):
                    folder,document,repository,filename=self.repository_fixture(kind)
                    changes.git(folder,'branch','replacement')
                    changes.git(folder,'symbolic-ref','HEAD','refs/heads/replacement')
                    changes.git(folder,'branch','-D','main')
                    before=filename.read_bytes()
                    expected=hashlib.sha256(before).hexdigest()
                    revised=copy.deepcopy(document)
                    revised.update(status='draft',revision=2,title='Reconciled draft')
                    if selected_base == 'replacement':
                        revised['base']=repository.reference(folder,'refs/heads/replacement')
                    elif selected_base == 'unknown':
                        revised['base']=None
                    changes.validate(folder,revised)
                    refs=changes.git(folder,'show-ref')
                    result=changes.save(folder,document['id'],revised,expected,'Operator reconciled the planning baseline')
                    self.assertTrue(result['updated'])
                    self.assertEqual(capture.read_capture(filename)['base'],revised['base'])
                    self.assertEqual(changes.git(folder,'show-ref'),refs)
                    self.assertEqual((filename.parent/'assets/history'/(expected+'-proposal.json')).read_bytes(),before)
                    self.assertFalse(changes.save(folder,document['id'],revised,expected,'Operator reconciled the planning baseline')['updated'])
                    if selected_base == 'replacement':
                        completed=capture.read_capture(filename)
                        completed.update(status='complete',revision=3)
                        self.assertTrue(changes.finalize_proposal(folder,document['id'],completed,result['document_digest'],'Finalize against replacement target')['updated'])

    def test_standalone_baseline_save_and_finalization(self):
        for kind in ('ad-hoc','discovery','horizon'):
            for baseline_kind in ('cp-plan-baseline-v1','cp-operational-specification-v1'):
                with self.subTest(kind=kind,baseline_kind=baseline_kind):
                    folder,document,repository,filename=self.repository_fixture(kind)
                    value=({'schema':baseline_kind,**changes.empty_base()} if baseline_kind == 'cp-plan-baseline-v1'
                           else capture.contract.empty_specification())
                    (folder/'baseline.json').write_bytes(changes.encoded(value))
                    for relative in repository.LEGACY: (folder/relative).unlink()
                    changes.git(folder,'add','--','baseline.json',*repository.LEGACY)
                    changes.git(folder,'commit','--quiet','-m','Standalone supported baseline')
                    document.update(status='draft',base={'target_ref':'refs/heads/main',
                        'git_commit':changes.git(folder,'rev-parse','HEAD').decode().strip(),'path':'baseline.json',
                        'revision':0,'sha256':hashlib.sha256((folder/'baseline.json').read_bytes()).hexdigest()})
                    filename.write_bytes(changes.encoded(document))
                    expected=hashlib.sha256(filename.read_bytes()).hexdigest()
                    revised=copy.deepcopy(document)
                    revised.update(revision=2,title='Revised standalone draft')
                    self.assertTrue(changes.validate(folder,revised)['base_verified'])
                    result=changes.save(folder,document['id'],revised,expected,'Operator revised standalone draft')
                    self.assertTrue(result['updated'])
                    completed=capture.read_capture(filename)
                    completed.update(status='complete',revision=3)
                    finalized=changes.finalize_proposal(folder,document['id'],completed,result['document_digest'],'Finalize standalone proposal')
                    self.assertTrue(finalized['updated'])
                    self.assertFalse(changes.finalize_proposal(folder,document['id'],completed,result['document_digest'],'Finalize standalone proposal')['updated'])
                    candidate=folder/repository.CANON
                    candidate.parent.mkdir(parents=True)
                    candidate.write_bytes(changes.encoded(repository.empty()['canon']))
                    changes.git(folder,'add','--',repository.CANON)
                    changes.git(folder,'commit','--quiet','-m','Malformed partial repository target')
                    before=filename.read_bytes()
                    revised=capture.read_capture(filename)
                    revised.update(status='draft',revision=4)
                    with self.assertRaisesRegex(ValueError,'incomplete repository'):
                        changes.save(folder,document['id'],revised,finalized['document_digest'],'Must not bypass malformed target')
                    self.assertEqual(filename.read_bytes(),before)

    def test_repository_partial_and_duplicate_authority_refuse(self):
        folder,document,repository,filename=self.repository_fixture()
        candidate=folder/repository.CANON
        candidate.parent.mkdir(parents=True)
        candidate.write_bytes(changes.encoded(repository.empty()['canon']))
        with self.assertRaisesRegex(ValueError,'competing master'):
            changes.helper('planning-execution').initialize(folder,True)
        changes.git(folder,'add',repository.CANON)
        changes.git(folder,'commit','--quiet','-m','Incomplete fixture state')
        commit=changes.git(folder,'rev-parse','HEAD').decode().strip()
        with self.assertRaisesRegex(ValueError,'incomplete repository'):
            repository.snapshot(folder,commit)

    def test_repository_archive_prerequisites_and_bound_contracts(self):
        folder,document,repository,filename=self.repository_fixture()
        for identity in ('finished','next'):
            item=work(identity)
            item.update(maturity='specified',specification={'execution_model':'Operator-selected','sizing_rationale':'Bounded',
                'validation_plan':['Run fixture'],'failure_discovery_route':'Capture scope','review_boundary':'self','closeout_basis':'Verified merge'})
            document['changes'].append(add(item,'work_item'))
        edge={'from':{'id':'finished','revision':1},'to':{'id':'next','revision':1},'rationale':'Prior work','sources':['source-1']}
        document['changes'].append(add(edge,'work_dependency','dependency'))
        selected=repository.snapshot(folder,document['base']['git_commit'])
        state=repository.compose(document,selected,'1'*64)
        completed=state['tracker']['nodes'].pop(0)
        completed['status']='done'
        completed['binding']={'work':copy.deepcopy(completed['work']),'canon':copy.deepcopy(state['canon'])}
        state['archive']['nodes'].append(completed)
        state['archive']['dependencies']=state['tracker']['dependencies']
        state['tracker']['dependencies']=[]
        for key,relative in repository.PATHS.items():
            destination=folder/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(changes.encoded(state[key]))
        for relative in repository.LEGACY:
            (folder/relative).unlink()
        changes.git(folder,'add','--',*repository.PATHS.values(),*repository.LEGACY)
        changes.git(folder,'commit','--quiet','-m','Applied fixture and completed archive')
        commit=changes.git(folder,'rev-parse','HEAD').decode().strip()
        resolved=repository.resolve(folder,'next',commit)
        self.assertEqual(resolved['dependency_statuses'],{'finished':'done'})
        self.assertEqual(resolved['blocked_dependencies'],[])
        self.assertTrue(repository.resolve(folder,'finished',commit)['archive_only'])
        amended=copy.deepcopy(document)
        amended.update(revision=2,base=repository.reference(folder,'refs/heads/main'),sources=copy.deepcopy(state['canon']['sources']))
        successor=record(revision=2)
        change=add(successor)
        change.update(operation='modify',expected={'state':'present','revision':1,'digest':changes.digest(state['canon']['records'][0])})
        amended['changes']=[change]
        current=repository.snapshot(folder,commit)
        with self.assertRaisesRegex(ValueError,'execution-impact'):
            repository.compose(amended,current,'2'*64)
        amended['execution_impact']=[{'work':{'id':'finished','revision':1},'disposition':'preserve-bound-contract','rationale':'Completed work keeps original meaning'}]
        result=repository.compose(amended,current,'2'*64)
        self.assertEqual(result['archive'],state['archive'])
        self.assertEqual(result['tracker']['nodes'],state['tracker']['nodes'])
        duplicate=copy.deepcopy(state)
        duplicate['tracker']['nodes'].append(completed)
        with self.assertRaisesRegex(ValueError,'duplicate phase'):
            repository.validate(duplicate)

    def test_change_review_and_exact_decision(self):
        folder,document,repository,filename=self.repository_fixture()
        evidence=changes.helper('planning-change-evidence')
        authority={'actor':'Operator','authority':'Fixture only','date':'2026-09-29','rationale':'Synthetic test','evidence':'fixture://confirmation'}
        (folder/'review.md').write_text('Independent fixture assessment of full Canon/work impact.\n')
        request={'request_id':'review-1','review_input':evidence.subject(folder,document),'report_path':'review.md','observations':[],
            'attestation':{**authority,'actor':'Independent Reviewer','independent':True,'scope':'Full change set and impact'}}
        evidence.apply(folder,document,'review',request,True)
        self.assertFalse(evidence.apply(folder,document,'review',request,True)['updated'])
        fields={'kind':'approval','actor':'Operator','authority':'Fixture only','date':'2026-09-29','scope':'Full fixture',
            'checklist':dict.fromkeys(capture.contract.CHECK_NAMES,True),'integration_assessment':'Reviewed exact candidate',
            'dag_assessment':'No work changes','findings_acknowledged':[],'conditions':[],'signoff':'Fixture approval','invocation_source':'operator-confirmation'}
        draft=evidence.apply(folder,document,'draft-decision',{'identity':'decision-1','review_ids':['review-1'],'fields':fields},True)
        decision=evidence.read_events(folder,document['id'])[-1]['decision']
        confirmation={**authority,'decision_digest':changes.digest(decision)}
        evidence.apply(folder,document,'finalize-decision',{'identity':'decision-1','expected_draft_digest':draft['evidence_result'],'confirmation':confirmation},True)
        final,reviews=evidence.selected(folder,document,'decision-1')
        self.assertEqual(final['decision'],decision)
        self.assertEqual(len(reviews),1)
        admission=changes.helper('planning-admission')
        prepared=admission.prepare(folder,document['id'],'decision-1',None,None,hashlib.sha256(filename.read_bytes()).hexdigest(),True)
        self.assertEqual(admission.validate_bundle(folder,prepared['bundle'])['result']['tracker']['revision'],1)
        self.assertFalse(admission.prepare(folder,document['id'],'decision-1',None,None,hashlib.sha256(filename.read_bytes()).hexdigest(),True)['created'])
        manifest,view,payload,validation=admission.verify_directory(folder,prepared['bundle'])
        header={'id':'fixture-attempt','offer':{'bundle':str(pathlib.Path(prepared['bundle']).relative_to(folder)),
            'bundle_id':prepared['bundle_id'],'base_digest':manifest['base_digest'],'decision_digest':manifest['decision_digest'],
            'proposal_digest':manifest['subjects']['proposal_digest']}}
        files,paths=evidence.expected_files(folder,header)
        self.assertIsNone(files[repository.LEGACY[0]])
        self.assertIsNone(files[repository.LEGACY[1]])
        self.assertIn(repository.CANON,files)
        self.assertIn(repository.TRACKER,files)
        self.assertIn(repository.ARCHIVE,files)
        source_path=validation['result']['canon']['sources'][0]['path']
        self.assertEqual(files[source_path],(folder/'source.md').read_bytes())
        changed=copy.deepcopy(document)
        changed['title']='Changed exact subject'
        with self.assertRaisesRegex(ValueError,'stale'):
            evidence.selected(folder,changed,'decision-1')
        request['attestation']['actor']=document['author']
        with self.assertRaisesRegex(ValueError,'not independent'):
            evidence.apply(folder,document,'review',request,True)
        evidence_before={item.relative_to(evidence.location(folder,document['id'])):item.read_bytes()
                         for item in evidence.location(folder,document['id']).rglob('*') if item.is_file()}
        revised=copy.deepcopy(document)
        revised['revision']+=1
        saved=changes.save(folder,document['id'],revised,hashlib.sha256(filename.read_bytes()).hexdigest(),'Operator changed a planning decision')
        revised=capture.read_capture(filename)
        self.assertEqual(revised['status'],'draft')
        with self.assertRaisesRegex(ValueError,'complete change set'):
            evidence.selected(folder,revised,'decision-1')
        revised.update(status='complete',revision=revised['revision']+1)
        changes.finalize_proposal(folder,document['id'],revised,saved['document_digest'],'Operator explicitly refinalized')
        document=capture.read_capture(filename)
        with self.assertRaisesRegex(ValueError,'stale'):
            evidence.selected(folder,document,'decision-1')
        with self.assertRaisesRegex(ValueError,'review input is stale'):
            evidence.review_records(evidence.read_events(folder,document['id']),document,['review-1'],changes.digest(evidence.subject(folder,document)))
        self.assertEqual(evidence_before,{item.relative_to(evidence.location(folder,document['id'])):item.read_bytes()
                         for item in evidence.location(folder,document['id']).rglob('*') if item.is_file()})
        retained={item.relative_to(pathlib.Path(prepared['bundle'])).as_posix():item.read_bytes()
                  for item in pathlib.Path(prepared['bundle']).rglob('*') if item.is_file()}
        before=filename.read_bytes()
        expected=hashlib.sha256(before).hexdigest()
        narrative=capture.narrative_path(filename).read_bytes()
        history=filename.parent/'assets/history'
        preimage={'proposal':{'id':'prior-proposal','path':(history/(expected+'-proposal.json')).relative_to(folder).as_posix(),'sha256':expected},
                  'capture':{'id':'prior-capture','path':(history/(expected+'-capture.md')).relative_to(folder).as_posix(),
                             'sha256':hashlib.sha256(narrative).hexdigest()}}
        changed=copy.deepcopy(document)
        changed['revision']+=1
        changed['context']['lifecycle']={'state':'suspended','events':[self.lifecycle_event('suspend',preimage)]}
        with capture.local_writer(folder):
            changes._publish_pair(folder,filename,before,narrative,changes.encoded(changed),narrative)
        self.assertEqual(admission.verify_directory(folder,prepared['bundle'])[0],manifest)
        self.assertEqual(retained,{item.relative_to(pathlib.Path(prepared['bundle'])).as_posix():item.read_bytes()
                                  for item in pathlib.Path(prepared['bundle']).rglob('*') if item.is_file()})
        self.assertEqual((history/(expected+'-proposal.json')).read_bytes(),before)
        with self.assertRaisesRegex(ValueError,'stale'):
            evidence.selected(folder,changed,'decision-1')
        with self.assertRaisesRegex(ValueError,'suspended'):
            evidence.apply(folder,changed,'review',request,True)

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
        self.assertEqual(result['canon']['records'][0],record())
        self.assertEqual(result['canon']['records'][1]['revision'],2)
        self.assertEqual(result['canon']['records'][1]['authority_status'],'retired')
        restored=copy.deepcopy(base)
        restored['canon']=json.loads(json.dumps(result['canon']))
        self.assertEqual(changes.compose(proposal(),restored)['result']['effective_record_refs'],[])
        with self.assertRaisesRegex(ValueError,'already exists'):
            changes.compose(proposal([add(record())]),restored)
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