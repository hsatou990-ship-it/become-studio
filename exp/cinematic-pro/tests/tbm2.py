import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8765/exp/cinematic-pro/index.html'
J=open((REPO+'/exp/design/price-of-staying.design.json')).read()
KICK='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/cp/vid/kick8.wav'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:500])
RMS="""(b,a,z)=>{const x=b.getChannelData(0),sr=b.sampleRate;let q=0,n=0;for(let i=Math.floor(a*sr);i<Math.floor(z*sr)&&i<x.length;i++){q+=x[i]*x[i];n++}return 10*Math.log10(Math.max(q/Math.max(n,1),1e-14))}"""
def ready(pg):
    pg.wait_for_function("()=>window.CP&&CP.S&&CP.S.sc&&CP.S.sc.length>0",timeout=20000);pg.wait_for_timeout(600)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE+'#res=360');ready(pg)
    chk('P0 fresh browser: default built-in, nothing saved',pg.evaluate("()=>CP.bgmEff()")=='builtin' and pg.evaluate("()=>localStorage.getItem('cp_bgmmode')")is None)
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500)
    pg.check('input[name=bgmm][value=none]');pg.wait_for_timeout(200)
    chk('P1 selection saved',pg.evaluate("()=>localStorage.getItem('cp_bgmmode')")=='none')
    pg.reload();ready(pg)
    chk('P2 plain reload keeps none (mode + radio)',pg.evaluate("()=>CP.bgmEff()")=='none' and pg.evaluate("()=>document.querySelector('input[name=bgmm]:checked').value")=='none')
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500)
    a=pg.evaluate("()=>CP.S.sc.find(o=>o.id==='S3').a")
    chk('P2b import after reload with none: beat snap stays off (S3=6.5)',abs(a-6.5)<.01,a)
    m=pg.evaluate("""async(RMS)=>{const f=eval(RMS);CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true;const m=await CP.buildAudio();const h=CP.S.sc.find(o=>o.id==='S3');return {nar:f(m,CP.S.ln[0].t0,CP.S.ln[0].t0+CP.S.ln[0].d),early:CP.S.ln[0].t0>2.4?f(m,.5,2.4):-999}}""",RMS)
    chk('P2c after reload: narration kept, no drone',m['nar']>-40,m)
    # res switch with none
    pg.select_option('#resSel','1080');pg.wait_for_load_state();ready(pg);pg.wait_for_timeout(1500)
    chk('P3 720->1080 switch keeps none',pg.evaluate("()=>CP.bgmEff()")=='none' and '1080' in pg.inner_text('#rs'),(pg.evaluate("()=>CP.bgmEff()"),pg.inner_text('#rs')))
    pg.select_option('#resSel','720');pg.wait_for_load_state();ready(pg);pg.wait_for_timeout(1500)
    chk('P3b 1080->720 switch keeps none',pg.evaluate("()=>CP.bgmEff()")=='none' and '720' in pg.inner_text('#rs'))
    # external + file, switch res
    pg.check('input[name=bgmm][value=external]')
    pg.set_input_files('#bgf',KICK);pg.fill('#bgs','synthetic test');pg.fill('#bgl','test only');pg.check('#bgk');pg.click('#bBgm');pg.wait_for_timeout(1500)
    chk('P4 external with file effective ext',pg.evaluate("()=>CP.bgmEff()")=='ext')
    pg.select_option('#resSel','1080');pg.wait_for_load_state();ready(pg);pg.wait_for_timeout(2500)
    chk('P5 res switch keeps external + restores imported file',pg.evaluate("()=>CP.bgmEff()")=='ext' and pg.evaluate("()=>!!CP.S.bgm"),(pg.evaluate("()=>[CP.bgmEff(),CP.S.bgmMode,!!CP.S.bgm]")))
    # reload with external file gone -> silent not built-in
    pg.reload();ready(pg)
    st=pg.evaluate("()=>[CP.S.bgmMode,CP.bgmEff(),!!CP.S.bgm]")
    chk('P6 reload with external (file not re-registered): mode external, effective silent (no built-in)',st==['external','none',False],st)
    chk('P6b warning shown',('未取込' in pg.inner_text('#bgmst')),pg.inner_text('#bgmst'))
    mm=pg.evaluate("""async(RMS)=>{const f=eval(RMS);CP.S.narr=null;const m=await CP.buildAudio();return f(m,.5,2.4)}""",RMS)
    chk('P6c audio really silent in drone window',mm<-100,mm)
    # switch to builtin and back
    pg.check('input[name=bgmm][value=builtin]');pg.wait_for_timeout(200)
    chk('P7 built-in restored by choice',pg.evaluate("()=>CP.bgmEff()")=='builtin' and pg.evaluate("()=>localStorage.getItem('cp_bgmmode')")=='builtin')
    # legacy session without bgmMode
    pg.evaluate("()=>localStorage.removeItem('cp_bgmmode')")
    pg.evaluate("""()=>new Promise((ok,ng)=>{const r=indexedDB.open('cp_session',1);r.onupgradeneeded=()=>r.result.createObjectStore('s',{keyPath:'k'});r.onsuccess=()=>{const t=r.result.transaction('s','readwrite');t.objectStore('s').put({k:'last',at:Date.now(),dsc:'誰も見ていない朝。それでも一歩だけ前へ。',plan:false,dj:null,dv:0,font:null,narr:null,bgm:null,mockNarr:false,clips:[]});t.oncomplete=ok;t.onerror=()=>ng(1)}})""")
    pg.goto(BASE+'#res=360&restore=1');pg.reload();ready(pg);pg.wait_for_timeout(1500)
    st=pg.evaluate("()=>[CP.S.bgmMode===undefined?'undef':CP.S.bgmMode,CP.bgmEff(),document.getElementById('dsc').value.slice(0,6)]")
    chk('P8 legacy session (no bgmMode) restores, behaves as before (built-in)',st[1]=='builtin' and st[2]=='誰も見ていな',st)
    chk('P9 no page errors',not errs,errs)
    b.close()
print(sum(R),'/',len(R))
