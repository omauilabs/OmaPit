#!/usr/bin/env python3
"""Local, aggregate-only hardware reports. Network is used only by `submit`."""
import argparse
import datetime as dt
import hashlib
import json
import math
import platform
import re
import sqlite3
import subprocess
from pathlib import Path

CHECKS = ('temperature_comparison', 'ambient', 'battery', 'wake_dock', 'reconnect', 'restart', 'recording', 'alarms', 'long_cook', 'multiple_probes')
PRIVATE = re.compile(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|@|https?://|[/\\]|token|password|secret', re.I)
STATS = ('samples', 'valid_food_samples', 'valid_ambient_samples', 'valid_battery_samples', 'duration_seconds', 'max_gap_seconds')
REPO = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}')

def text(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 80 or PRIVATE.search(value) or not re.fullmatch(r'[A-Za-z0-9 ._+()\-]+', value):
        raise ValueError('Metadata must be short plain model/version text, without identifiers, paths, URLs or credentials')
    return value

def exact(obj, keys):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError('Unexpected or missing report fields')

def validate(r):
    exact(r, ('schema_version','app_version','device','environment','evidence','observations','checks'))
    if type(r['schema_version']) is not int or r['schema_version'] != 1: raise ValueError('Unsupported schema')
    text(r['app_version'])
    exact(r['device'], ('manufacturer','model','firmware','protocol','adapter_version','transport'))
    for key, value in r['device'].items(): text(value)
    if r['device']['transport'] not in ('ble','bridge','import','manual'): raise ValueError('Unknown transport')
    exact(r['environment'], ('os','architecture','python'))
    for value in r['environment'].values(): text(value)
    if r['evidence'] not in ('not-tested','live-observation','real-capture-replay','synthetic-replay'): raise ValueError('Invalid evidence')
    exact(r['observations'], STATS)
    for key, value in r['observations'].items():
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1_000_000_000: raise ValueError('Invalid aggregate')
        if key.endswith('samples') and type(value) is not int: raise ValueError('Sample counts must be integers')
    o=r['observations']
    if any(o[k]>o['samples'] for k in STATS if k.startswith('valid_')): raise ValueError('Impossible sample counts')
    if o['max_gap_seconds']>o['duration_seconds']: raise ValueError('Impossible gap')
    exact(r['checks'], CHECKS)
    if any(v not in ('not-run','pass','fail') for v in r['checks'].values()): raise ValueError('Invalid check outcome')
    if r['evidence'] != 'live-observation' and any(v != 'not-run' for v in r['checks'].values()): raise ValueError('Replay cannot certify physical checks')
    if r['evidence']=='live-observation' and o['samples']==0: raise ValueError('Live evidence needs samples')
    if r['evidence']=='not-tested' and any(o.values()): raise ValueError('Untested evidence cannot contain observations')
    return r

def template(model='unknown', transport='ble'):
    return dict(schema_version=1,app_version=json.loads((Path(__file__).resolve().parent.parent/'manifest.json').read_text()).get('version','unknown'),device=dict(manufacturer='unknown',model=model,firmware='unknown',protocol='unknown',adapter_version='unknown',transport=transport),environment=dict(os=platform.system() or 'unknown',architecture=platform.machine() or 'unknown',python=platform.python_version()),evidence='not-tested',observations={k:0 for k in STATS},checks={k:'not-run' for k in CHECKS})

def collect(db, device, model):
    # Read-only database, one explicitly selected local device. Never copy identities or raw readings.
    con=sqlite3.connect(Path(db).resolve().as_uri()+'?mode=ro',uri=True)
    con.row_factory=sqlite3.Row
    try:
        d=con.execute('SELECT model,protocol,source,adapter_version FROM devices WHERE id=?',(device,)).fetchone()
        if d is None: raise ValueError('Selected device not found')
        rows=con.execute('SELECT at,role,quality,source FROM samples WHERE device=? ORDER BY at',(device,)).fetchall()
    finally: con.close()
    if not rows: raise ValueError('No stored samples for selected device')
    if any(row['source'] != d['source'] for row in rows): raise ValueError('Mixed sources cannot establish a live benchmark')
    if d['source'] not in ('ble','bridge','replay'): raise ValueError('Unsupported source for collection')
    r=template(model or d['model'], 'ble' if d['source']=='replay' else d['source'])
    r['device']['protocol']=d['protocol'] or 'unknown'
    r['device']['adapter_version']=str(d['adapter_version'] or 'unknown')
    # Replays are conservatively synthetic unless a reviewer supplies actual capture provenance.
    r['evidence']='synthetic-replay' if d['source']=='replay' else 'live-observation'
    times=sorted(set(float(row['at']) for row in rows))
    r['observations'].update(samples=len(rows),duration_seconds=round(times[-1]-times[0],3),max_gap_seconds=round(max((b-a for a,b in zip(times,times[1:])),default=0),3))
    for role in ('food','ambient','battery'):
        r['observations']['valid_'+role+'_samples']=sum(row['role']==role and row['quality']=='valid' for row in rows)
    return validate(r)

def save(path, value):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2)+'\n')

def fingerprint(r): return hashlib.sha256(json.dumps(validate(r),sort_keys=True,separators=(',',':')).encode()).hexdigest()[:20]

def body(r):
    key=fingerprint(r)
    return ('## Aggregate hardware benchmark\n\nReport fingerprint: `omapit-benchmark-'+key+'`\n\n'
            'Owner-contributed evidence, pending maintainer review. Check outcomes are owner attestations, not independently certified. No addresses, raw packets, temperatures, timestamps or journal content are included.\n\n```json\n'+json.dumps(r,indent=2)+'\n```\n')

def gh(args):
    result=subprocess.run(['gh',*args],capture_output=True,text=True,check=False)
    if result.returncode: raise ValueError('GitHub command failed. Check gh authentication and repository permissions; no report was marked as submitted.')
    return result.stdout.strip()

def submit(path, config_path):
    r=validate(json.loads(Path(path).read_text()))
    c=json.loads(Path(config_path).read_text())
    exact(c,('repository','allow_automatic_submission','report_schema_version'))
    if c['allow_automatic_submission'] is not True or c['report_schema_version']!=1 or not REPO.fullmatch(c['repository']): raise ValueError('Explicit destination-specific opt-in required')
    repo=c['repository']; key=fingerprint(r)
    found=json.loads(gh(['issue','list','--repo',repo,'--state','all','--search','"omapit-benchmark-'+key+'" in:body','--json','url']))
    if found: return 'Already submitted: '+found[0]['url']
    # Use a sibling file for review/reproducibility; no command-string interpolation.
    review=Path(path).with_suffix('.submission.md'); review.write_text(body(r))
    return gh(['issue','create','--repo',repo,'--title','Hardware benchmark: '+r['device']['model']+' ('+r['device']['protocol']+')','--body-file',str(review)])

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('template'); q.add_argument('--model',default='unknown'); q.add_argument('--out',required=True)
    q=sub.add_parser('collect'); q.add_argument('--db',required=True); q.add_argument('--device',required=True); q.add_argument('--model'); q.add_argument('--out',required=True)
    q=sub.add_parser('validate'); q.add_argument('report')
    q=sub.add_parser('review'); q.add_argument('report'); q.add_argument('--out',required=True)
    q=sub.add_parser('configure'); q.add_argument('--repo',required=True); q.add_argument('--config',required=True); q.add_argument('--allow-auto-submit',action='store_true',help='Owner opt-in: publish schema-v1 model/version, OS/architecture/Python, aggregate sample counts/gaps, evidence and check outcomes to this named GitHub repository')
    q=sub.add_parser('submit'); q.add_argument('report'); q.add_argument('--config',required=True)
    q=sub.add_parser('disable'); q.add_argument('--config',required=True)
    a=p.parse_args()
    try:
        if a.action=='template': save(a.out,validate(template(a.model))); print('Local template written. No hardware test or upload performed.')
        elif a.action=='collect': save(a.out,collect(a.db,a.device,a.model)); print('Local aggregate report written. All physical checks remain not-run. No upload performed.')
        elif a.action=='validate': validate(json.loads(Path(a.report).read_text())); print('Report schema/privacy checks passed. This does not certify hardware.')
        elif a.action=='review': Path(a.out).write_text(body(json.loads(Path(a.report).read_text()))); print('Local submission preview written.')
        elif a.action=='configure':
            if not REPO.fullmatch(a.repo) or not a.allow_auto_submit: raise ValueError('Provide a valid owner/repository and explicit --allow-auto-submit opt-in')
            save(a.config,dict(repository=a.repo,allow_automatic_submission=True,report_schema_version=1)); print('Automatic submission enabled only for '+a.repo+'. No report sent.')
        elif a.action=='disable':
            c=json.loads(Path(a.config).read_text()); c['allow_automatic_submission']=False; save(a.config,c); print('Automatic submission disabled.')
        else: print(submit(a.report,a.config))
    except (ValueError,OSError,sqlite3.Error,KeyError,TypeError) as e: p.exit(1,str(e)+'\n')
if __name__=='__main__': main()
