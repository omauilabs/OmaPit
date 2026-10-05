import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import benchmark as b

class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def report(self):
        r=b.template('CQ60'); r['device']['manufacturer']='CHEF iQ'; return r
    def write(self,name,data):
        p=self.root/name; p.write_text(json.dumps(data)); return p
    def consent(self,enabled=True): return self.write('config.json',dict(repository='owner/omapit',allow_automatic_submission=enabled,report_schema_version=1))
    def test_template_does_not_claim_hardware(self):
        r=b.validate(self.report()); self.assertEqual(r['evidence'],'not-tested'); self.assertTrue(all(v=='not-run' for v in r['checks'].values()))
    def test_extra_fields_rejected_at_each_level(self):
        for target in ('root','device','environment','observations','checks'):
            r=self.report(); (r if target=='root' else r[target])['private']='hidden'
            with self.assertRaises(ValueError): b.validate(r)
    def test_identity_and_credential_patterns_rejected(self):
        for value in ('AA:BB:CC:DD:EE:FF','019d1234-1234-1234-1234-123456789abc','person@example.com','/Users/name','https://host','password123','token abc'):
            r=self.report(); r['device']['model']=value
            with self.assertRaises(ValueError): b.validate(r)
    def test_nonfinite_boolean_negative_and_fractional_counts_rejected(self):
        for value in (float('nan'),float('inf'),True,-1,2.5):
            r=self.report();r['observations']['samples']=value
            with self.assertRaises(ValueError):b.validate(r)
    def test_impossible_counts_and_gap_rejected(self):
        for key,value in (('valid_food_samples',1),('max_gap_seconds',1)):
            r=self.report();r['observations'][key]=value
            with self.assertRaises(ValueError):b.validate(r)
    def test_replay_cannot_pass_physical_checks(self):
        r=self.report();r['evidence']='synthetic-replay';r['checks']['reconnect']='pass'
        with self.assertRaises(ValueError): b.validate(r)
    def test_live_evidence_requires_samples(self):
        r=self.report();r['evidence']='live-observation'
        with self.assertRaises(ValueError):b.validate(r)
    def test_collect_readonly_selected_device_aggregate_only(self):
        path=self.root/'test.sqlite3';con=sqlite3.connect(path)
        con.executescript('CREATE TABLE devices(id TEXT,model TEXT,protocol TEXT,source TEXT,adapter_version TEXT);CREATE TABLE samples(device TEXT,at REAL,role TEXT,quality TEXT,source TEXT);')
        con.execute('INSERT INTO devices VALUES(?,?,?,?,?)',('private-identity','CQ60','4.0.0','ble','0.2.0'))
        con.executemany('INSERT INTO samples VALUES(?,?,?,?,?)',[('private-identity',100,'food','valid','ble'),('private-identity',100,'ambient','invalid','ble'),('private-identity',105,'food','valid','ble'),('other-device',1000,'food','valid','ble')]);con.commit();con.close()
        before=path.read_bytes();r=b.collect(path,'private-identity',None)
        self.assertEqual(path.read_bytes(),before);self.assertEqual(r['observations']['samples'],3);self.assertEqual(r['observations']['valid_food_samples'],2);self.assertEqual(r['observations']['valid_ambient_samples'],0);self.assertEqual(r['observations']['max_gap_seconds'],5)
        self.assertNotIn('private-identity',json.dumps(r));self.assertNotIn('other-device',json.dumps(r));self.assertEqual(r['checks']['recording'],'not-run')
    def test_mixed_sample_sources_rejected(self):
        path=self.root/'mixed.sqlite3';con=sqlite3.connect(path)
        con.executescript('CREATE TABLE devices(id TEXT,model TEXT,protocol TEXT,source TEXT,adapter_version TEXT);CREATE TABLE samples(device TEXT,at REAL,role TEXT,quality TEXT,source TEXT);')
        con.execute('INSERT INTO devices VALUES(?,?,?,?,?)',('local','CQ60','4.0.0','ble','0.2.0'));con.execute('INSERT INTO samples VALUES(?,?,?,?,?)',('local',100,'food','valid','replay'));con.commit();con.close()
        with self.assertRaises(ValueError): b.collect(path,'local',None)
    def test_no_submission_without_opt_in(self):
        report=self.write('report.json',self.report())
        with patch.object(b,'gh') as gh:
            with self.assertRaises(ValueError): b.submit(report,self.consent(False))
            gh.assert_not_called()
    def test_report_cannot_change_destination(self):
        r=self.report();r['repository']='attacker/repo';report=self.write('report.json',r)
        with patch.object(b,'gh') as gh:
            with self.assertRaises(ValueError):b.submit(report,self.consent())
            gh.assert_not_called()
    def test_submit_preview_and_named_destination(self):
        r=self.report();report=self.write('report.json',r)
        with patch.object(b,'gh',side_effect=['[]','https://github.com/owner/omapit/issues/1']) as gh:
            self.assertIn('/issues/1',b.submit(report,self.consent()))
            args=gh.call_args_list[1].args[0];self.assertEqual(args[args.index('--repo')+1],'owner/omapit');self.assertIn('--body-file',args)
            self.assertIn('not-run',report.with_suffix('.submission.md').read_text())
    def test_existing_fingerprint_skips_creation(self):
        report=self.write('report.json',self.report())
        with patch.object(b,'gh',return_value='[{"url":"https://github.com/owner/omapit/issues/1"}]') as gh:
            self.assertIn('Already submitted',b.submit(report,self.consent()));self.assertEqual(gh.call_count,1)
    def test_fingerprint_stable_but_distinguishes_evidence(self):
        r=self.report();self.assertEqual(b.fingerprint(r),b.fingerprint(copy.deepcopy(r)));r['device']['protocol']='4.0.0';self.assertNotEqual(b.fingerprint(r),b.fingerprint(self.report()))
if __name__=='__main__': unittest.main()
