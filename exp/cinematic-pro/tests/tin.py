import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:500])
S2=open((REPO+'/exp/design/sample2.design.json')).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    def load(t):
        pg.fill('#dj',t);pg.click('#bDJ');pg.wait_for_timeout(400);return pg.inner_text('#djr'),pg.evaluate("()=>CP.lastIntake")
    txt,r=load(S2)
    chk('I1 report appears for valid JSON',('【取り込み報告】' in txt and '適合' in txt),txt[:200])
    chk('I2 requested vs applied listed per scene (sample2 keeps its effects)',len(r['scenes'])==6 and any('mask:iris' in s['applied'] for s in r['scenes']) and any('matchCut' in s['applied'] for s in r['scenes']),r['scenes'])
    chk('I3 render check ran on all scenes and all drew an image',len(r['render'])==6 and all(x['ok'] for x in r['render']),r['render'])
    # unsupported + conflict + adjustment
    d=json.loads(S2);d['scenes'][1]['fx']=['live-anim-fusion'];d['scenes'][2]['matchCut']=True;d['scenes'][2]['mask']={"type":"slit","dur":.6}
    txt,r=load(json.dumps(d))
    chk('I4 unsupported effect named with scene',any('場面2' in u and 'live-anim-fusion' in u for u in r['unsupported']),r['unsupported'])
    chk('I5 conflict named with reason',any('S3' in c for c in r['conflicts']),r['conflicts'])
    chk('I6 report text says what was lost (指定→反映)',('外れた: mask:slit' in txt),txt)
    # invalid JSON: no report of success, state unchanged
    pg.fill('#dj','{"schema":"x"}');pg.click('#bDJ');pg.wait_for_timeout(300)
    chk('I7 invalid JSON rejected; old report is labelled as the previous one',('取り込めません' in pg.inner_text('#djs')) and ('直前に取り込んだJSONの報告' in pg.inner_text('#djr')) and ('【取り込み報告】' in pg.inner_text('#djr')),pg.inner_text('#djr')[:120])
    chk('I8 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
