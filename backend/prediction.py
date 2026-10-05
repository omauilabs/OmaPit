"""Experimental local trend ranges; conservative abstention, no safety assessment."""
import argparse,json,math,statistics,time

def estimate(rows,target,now=None):
    now=time.time() if now is None else now
    rows=[r for r in rows if r.get('source') in ('manual','ble','bridge') and isinstance(r.get('value_f'),(int,float)) and math.isfinite(r['value_f']) and isinstance(r.get('at'),(int,float)) and math.isfinite(r['at']) and r['at']<=now]
    rows=sorted({r['at']:r for r in rows}.values(),key=lambda r:r['at'])[-20:]
    def abstain(reason):return {'status':'insufficient','reason':reason,'method':'local-trend-v1','validated':False}
    if not rows:return abstain('No eligible temperature history.')
    latest=rows[-1];fresh=300 if latest['source']=='manual' else 30
    if now-latest['at']>fresh:return abstain('Latest reading is stale.')
    if latest['value_f']>=target:return {'status':'target_reached','reason':'The latest reading meets your personal target. Confirm doneness independently.','method':'local-trend-v1','validated':False}
    if len(rows)<8 or rows[-1]['at']-rows[0]['at']<300:return abstain('Need at least eight readings spanning five minutes.')
    gaps=[b['at']-a['at'] for a,b in zip(rows,rows[1:])]
    if max(gaps)>max(120,statistics.median(gaps)*3):return abstain('History has a substantial sampling gap.')
    slopes=[(b['value_f']-a['value_f'])/((b['at']-a['at'])/60) for i,a in enumerate(rows) for b in rows[i+1:] if b['at']-a['at']>=60]
    rate=statistics.median(slopes)
    if rate<=.03:return {'status':'stall_or_cooling','reason':'Temperature is flat or falling. A reliable finish estimate is unavailable.','rate_f_per_minute':round(rate,3),'method':'local-trend-v1','validated':False}
    adjacent=[(b['value_f']-a['value_f'])/((b['at']-a['at'])/60) for a,b in zip(rows,rows[1:])]
    half=len(adjacent)//2
    earlier=statistics.median(adjacent[:half]);recent=statistics.median(adjacent[half:])
    if abs(recent-earlier)/max(.03,abs(earlier))>.15:return abstain('Heating rate is changing. Wait for a stable trend.')
    positive=sorted(slopes);qlo=positive[int((len(positive)-1)*.1)];qhi=positive[int((len(positive)-1)*.9)]
    if qlo<=0 or (qhi-qlo)/rate>1:return abstain('Heating rate is too variable for a useful range.')
    delta=target-latest['value_f'];seconds=delta/rate*60
    if delta>40 or seconds>7200:return abstain('Target is too far away for a short-term trend estimate.')
    low_rate=max(.03,min(qlo,rate*.75));high_rate=max(qhi,rate*1.25)
    early=now+delta/high_rate*60;late=now+delta/low_rate*60
    return {'status':'estimate','earliest':early,'latest':late,'remaining_seconds':seconds,'rate_f_per_minute':round(rate,3),'samples':len(rows),'window_seconds':rows[-1]['at']-rows[0]['at'],'method':'local-trend-v1','validated':False,'reason':'Experimental range from recent heating rates. Assumes conditions continue; does not predict stall, carryover or resting.'}

def snapshot(db,foods):
    return {f['id']:estimate([dict(r) for r in db.execute('SELECT * FROM food_readings WHERE food=? ORDER BY at',(f['id'],))],f['target_f']) for f in foods if f['finished'] is None}

def evaluate(sessions):
    # Each held-out suffix is unseen by the predictor. An abstention is counted, never discarded from coverage reporting.
    results=[]
    for session in sessions:
        rows=sorted([r for r in session['readings'] if r.get('source') in ('manual','ble','bridge') and math.isfinite(r.get('at',float('nan'))) and math.isfinite(r.get('value_f',float('nan')))],key=lambda r:r['at']);target=session['target_f']
        if len(rows)<10:results.append({'id':session['id'],'category':session.get('category','unknown'),'status':'insufficient'});continue
        cut=max(8,int(len(rows)*.7));prefix=rows[:cut];suffix=rows[cut:]
        prediction=estimate(prefix,target,now=prefix[-1]['at'])
        crossing=next((r['at'] for r in suffix if r['value_f']>=target),None)
        item={'id':session['id'],'category':session.get('category','unknown'),'status':prediction['status']}
        if prediction['status']=='estimate' and crossing is not None:
            center=prefix[-1]['at']+prediction['remaining_seconds'];item.update(error_minutes=abs(center-crossing)/60,covered=prediction['earliest']<=crossing<=prediction['latest'])
        results.append(item)
    scored=[r for r in results if 'error_minutes' in r]
    groups={}
    for category in sorted({r['category'] for r in results}):
        allrows=[r for r in results if r['category']==category];eligible=[r for r in allrows if 'error_minutes' in r]
        groups[category]={'sessions':len(allrows),'scored':len(eligible),'mean_absolute_error_minutes':statistics.mean(r['error_minutes'] for r in eligible) if eligible else None,'range_coverage':statistics.mean(r['covered'] for r in eligible) if eligible else None}
    return {'method':'local-trend-v1','split':'First 70% prefix; held-out suffix, one estimate per session','sessions':len(results),'scored':len(scored),'abstained':sum(r['status']!='estimate' for r in results),'unscored_estimates':sum(r['status']=='estimate' and 'error_minutes' not in r for r in results),'mean_absolute_error_minutes':statistics.mean(r['error_minutes'] for r in scored) if scored else None,'range_coverage':statistics.mean(r['covered'] for r in scored) if scored else None,'by_category':groups,'results':results,'limitations':'Diagnostic benchmark, not a calibrated probability interval or field validation. Source/cook comparability needs owner review.'}

def journal_evaluation(db):
    sessions=[{**dict(f),'target_f':f['target_f'],'readings':[dict(r) for r in db.execute("SELECT * FROM food_readings WHERE food=? AND source IN ('manual','ble','bridge') ORDER BY at",(f['id'],))]} for f in db.execute("SELECT f.* FROM foods f JOIN cooks c ON c.id=f.cook WHERE f.finished IS NOT NULL AND c.source!='demo'")]
    return evaluate(sessions)

def main():
    p=argparse.ArgumentParser();p.add_argument('path',help='JSON array of sessions with target_f and timestamped value_f readings');args=p.parse_args()
    from pathlib import Path
    print(json.dumps(evaluate(json.loads(Path(args.path).read_text())),indent=2))
if __name__=='__main__':main()
