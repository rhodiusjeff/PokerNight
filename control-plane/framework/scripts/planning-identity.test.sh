#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT" <<'PY'
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

repo = pathlib.Path(sys.argv.pop())
spec = importlib.util.spec_from_file_location('identity', repo/'control-plane/framework/scripts/planning-identity.py')
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)
capture = identity.load_helper('planning-capture')
changes = identity.load_helper('planning-change-set')


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()

    def mint(self, operation='one', kind='ad-hoc', slug='test-planning', **kwargs):
        return identity.mint(self.root,kind,slug,operation,'Fixture',confirmed=True,**kwargs)

    def test_forms_and_local_retry(self):
        with patch.object(identity.secrets,'token_hex',return_value='00af'):
            first=self.mint()
        self.assertEqual(first['id'],'ADHOC-test-planning-00af')
        with patch.object(identity.secrets,'token_hex',side_effect=AssertionError('retry reminted')):
            self.assertEqual(self.mint()['id'],first['id'])
        with self.assertRaisesRegex(ValueError,'different inputs'):
            self.mint(slug='different')
        self.assertTrue(identity.matches_kind(first['id'],'ad-hoc'))
        self.assertFalse(identity.matches_kind(first['id'],'discovery'))

    def test_collision_retry_limit_and_casefold(self):
        home=self.root/'control-plane/ad-hoc/ADHOC-test-planning-abcd'
        home.mkdir(parents=True)
        with patch.object(identity.secrets,'token_hex',side_effect=['abcd','0011']):
            self.assertTrue(self.mint()['id'].endswith('-0011'))
        with patch.object(identity.secrets,'token_hex',return_value='abcd'):
            with self.assertRaisesRegex(ValueError,'collision limit'):
                self.mint('two')

    def test_invalid_slugs_and_confirmation_do_not_allocate(self):
        for slug in ('../escape','Upper','a--b','a-','a'*49,'1-start'):
            with self.assertRaisesRegex(ValueError,'slug'):
                self.mint(slug=slug)
        with self.assertRaisesRegex(ValueError,'confirmation'):
            identity.mint(self.root,'ad-hoc','valid','one','Fixture')
        self.assertFalse((self.root/'control-plane').exists())

    def test_discovery_origin_required(self):
        with self.assertRaisesRegex(ValueError,'origin'):
            self.mint(kind='discovery')
        contract=self.root/'contract.json'
        contract.write_text('{}')
        origin={'phase':{'id':'PHASE-1','revision':1},'contract':{'id':'origin','path':'contract.json','sha256':hashlib.sha256(contract.read_bytes()).hexdigest()}}
        self.assertTrue(self.mint(kind='discovery',origin=origin)['id'].startswith('DISC-'))
        contract.write_text('changed')
        with self.assertRaisesRegex(ValueError,'digest'):
            self.mint('two',kind='discovery',origin=origin)

    def test_horizon_sequence_and_full_id_resolution(self):
        first=self.mint(kind='horizon')
        second=self.mint('two',kind='horizon')
        self.assertTrue(first['id'].startswith('H000-test-planning-'))
        self.assertTrue(second['id'].startswith('H001-test-planning-'))
        home=self.root/'control-plane/horizons'/first['id']/'planning'
        home.mkdir(parents=True)
        path=home/(first['id']+'.md')
        path.write_text('fixture')
        self.assertEqual(capture.resolve_document(self.root,first['id']),path)
        with self.assertRaisesRegex(ValueError,'missing or ambiguous'):
            capture.resolve_document(self.root,'H000')

    def test_horizon_legacy_highwater_and_exhaustion(self):
        (self.root/'control-plane/horizons/H007-old').mkdir(parents=True)
        self.assertTrue(self.mint(kind='horizon')['id'].startswith('H008-'))
        (self.root/'control-plane/horizons/H899-old').mkdir()
        with self.assertRaisesRegex(ValueError,'exhausted'):
            self.mint('two',kind='horizon')

    def test_ordinals_retry_and_no_reuse(self):
        context=self.mint()['id']
        bindings=[{'change_id':'old','operation':'add','target':{'type':'canon_record','id':'req'},'kind':'functional_requirement'}]
        first=identity.reserve_records(self.root,context,'allocate',bindings,confirmed=True)
        self.assertEqual(first['mapping']['changes']['old'],'CHG-0001')
        self.assertEqual(first['mapping']['canon']['req'],'CR-'+context+'-0001')
        self.assertEqual(identity.reserve_records(self.root,context,'allocate',bindings,confirmed=True),first)
        second=identity.reserve_records(self.root,context,'next',bindings,confirmed=True)
        self.assertEqual(second['mapping']['changes']['old'],'CHG-0002')
        self.assertEqual(second['mapping']['canon']['req'],'CR-'+context+'-0002')

    def test_rekey_package_uses_writer_maps_and_preserves_sources(self):
        source=self.root/'source.md'
        source.write_bytes(b'Original source\r\n')
        old_id='ADHOC-'+'a'*32
        capture.create_capture(SimpleNamespace(root=self.root,id=old_id,kind='ad-hoc',title='Fixture',author='Fixture',sources=[source],origin_phase=None,origin_specification=None,confirmed=True))
        path=capture.resolve_document(self.root,old_id)
        prior=capture.read_capture(path)
        value={'id':'req','revision':1,'kind':'functional_requirement','title':'Fixture','scope':'repository','authority_status':'proposed','sources':['source-1'],
               'selection_rationale':'Fixture','content':{'obligation':'Do the thing','rationale':'Needed','acceptance_direction':'Observe it'}}
        proposal={'schema':changes.FORMAT,'id':old_id,'revision':1,'title':'Fixture','author':'Fixture','created_at':prior['created_at'],'context':{'kind':'ad-hoc','id':old_id},
                  'status':'draft','capture':{'id':'capture','path':capture.narrative_path(path).relative_to(self.root).as_posix(),'sha256':prior['capture_sha256']},
                  'base':None,'sources':[{'id':'source-1','path':'source.md','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}],
                  'changes':[{'change_id':'add-req','operation':'add','target':{'type':'canon_record','id':'req'},'expected':{'state':'absent'},'value':value,'rationale':'Fixture','sources':['source-1']}],
                  'unresolved':[{'id':'gap','explanation':'Fixture gap','affects':['add-req']}]}
        migrated=changes.save(self.root,old_id,proposal,hashlib.sha256(path.read_bytes()).hexdigest(),'Confirmed fixture.',True)
        original=path.read_bytes()
        with patch.object(changes,'retire_rekey_source',side_effect=OSError('interrupted retirement')):
            with self.assertRaisesRegex(OSError,'interrupted retirement'):
                changes.rekey_package(self.root,old_id,'test-planning','rekey',migrated['document_digest'],True)
        self.assertTrue(path.parent.exists())
        result=changes.rekey_package(self.root,old_id,'test-planning','rekey',migrated['document_digest'],True)
        new_path=pathlib.Path(result['path'])
        current=capture.read_capture(new_path)
        for collection, missing in (('canon','CR-'+result['id']+'-9999'),('changes','CHG-9999')):
            invalid=copy.deepcopy(current)
            alias=next(iter(invalid['identity']['aliases'][collection]))
            invalid['identity']['aliases'][collection][alias]=missing
            with self.subTest(collection=collection):
                with self.assertRaisesRegex(ValueError,'alias targets unallocated'):
                    changes.validate(self.root,invalid)
        withdrawn=copy.deepcopy(current)
        withdrawn['changes']=[]
        withdrawn['unresolved']=[]
        changes.validate(self.root,withdrawn)
        self.assertFalse(path.parent.exists())
        self.assertEqual(capture.resolve_document(self.root,old_id),new_path)
        self.assertEqual(current['changes'][0]['change_id'],'CHG-0001')
        self.assertEqual(current['changes'][0]['target']['id'],'CR-'+result['id']+'-0001')
        self.assertEqual(current['changes'][0]['value']['content'],value['content'])
        self.assertEqual(current['unresolved'][0]['affects'],['CHG-0001'])
        self.assertEqual((new_path.parent/'assets/history'/('identity-'+old_id)/path.name).read_bytes(),original)
        self.assertEqual(source.read_bytes(),b'Original source\r\n')
        self.assertFalse(changes.rekey_package(self.root,old_id,'test-planning','rekey',migrated['document_digest'],True)['updated'])
        changed=copy.deepcopy(current)
        changed['changes'][0]['operation']='obsolete'
        del changed['changes'][0]['value']
        changed['changes'][0]['expected']={'state':'present','revision':1,'digest':'0'*64}
        with self.assertRaisesRegex(ValueError,'rebound'):
            changes.shape(changed)
        new_binding={'change_id':'next-request','operation':'add','target':{'type':'canon_record','id':'next-record'},'kind':'functional_requirement'}
        issued=identity.reserve_records(self.root,result['id'],'next-allocation',[new_binding],current['identity']['allocation'],True)
        candidate=copy.deepcopy(current)
        candidate['revision']+=1
        candidate['identity']['allocation']=issued['state']
        new_change=copy.deepcopy(candidate['changes'][0])
        new_change['change_id']=issued['mapping']['changes']['next-request']
        new_change['target']['id']=issued['mapping']['canon']['next-record']
        new_change['value']['id']=new_change['target']['id']
        candidate['changes'].append(new_change)
        saved=changes.save(self.root,result['id'],candidate,hashlib.sha256(new_path.read_bytes()).hexdigest(),'Confirmed additional fixture record.')
        self.assertTrue(saved['updated'])
        self.assertEqual(capture.read_capture(new_path)['changes'][-1]['change_id'],'CHG-0002')
        forged=copy.deepcopy(capture.read_capture(new_path))
        forged['revision']+=1
        forged['identity']['allocation']['next_change']=999
        with self.assertRaisesRegex(ValueError,'issued by the identity helper'):
            changes.save(self.root,result['id'],forged,saved['document_digest'],'Unissued allocation.')
        prior_capture=capture.narrative_path(new_path).read_bytes()
        prior_proposal=new_path.read_bytes()
        refreshed=changes.refresh_navigation(self.root,result['id'],saved['document_digest'],True)
        self.assertTrue(refreshed['updated'])
        refreshed_capture=capture.narrative_path(new_path).read_text()
        self.assertIn('[source.md](../../../source.md)',refreshed_capture)
        after=capture.read_capture(new_path)
        before_refresh=json.loads(prior_proposal)
        self.assertEqual(after['changes'],before_refresh['changes'])
        self.assertEqual(after['identity'],before_refresh['identity'])
        history=new_path.parent/'assets/history'
        self.assertEqual((history/(saved['document_digest']+'-capture.md')).read_bytes(),prior_capture)
        self.assertEqual((history/(saved['document_digest']+'-proposal.json')).read_bytes(),prior_proposal)
        self.assertFalse(changes.refresh_navigation(self.root,result['id'],refreshed['document_digest'],True)['updated'])
        with self.assertRaisesRegex(ValueError,'changed since navigation'):
            changes.refresh_navigation(self.root,result['id'],saved['document_digest'],True)

    def test_source_navigation_replaces_only_location_sections(self):
        source=self.root/'source.md'
        source.write_text('Fixture')
        document={'capture':{'path':'capture.md'},'sources':[{'id':'source-1','path':'source.md','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}
        original='Origin: old/source.md\n\n## Restored Source Locations\n\nobsolete alias\n\n## Source Filename Correction\n\nobsolete current path\n\n## Historical Command\n\nold/source.md\n'
        actual=changes.source_navigation(self.root,document,original)
        self.assertTrue(actual.startswith('Origin: old/source.md\n\n'))
        self.assertTrue(actual.endswith('## Historical Command\n\nold/source.md\n'))
        self.assertNotIn('obsolete',actual)
        self.assertEqual(actual.count('## Current Source Locations'),1)
        self.assertEqual(changes.source_navigation(self.root,document,actual),actual)


unittest.main(verbosity=2)
PY