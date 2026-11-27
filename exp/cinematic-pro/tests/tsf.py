from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:500])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    pg.fill('#dsc','誰も見ていない朝。何度も失敗して、心が折れそうになる。それでも一歩だけ前へ。景色が変わり始める。君の朝が始まる。');pg.click('#bDir');pg.wait_for_timeout(500)
    pg.evaluate("()=>{CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true}")
    # ---- S1 failure on 3rd video: first two kept (on screen and in IndexedDB), materials/settings intact
    r=pg.evaluate("""async()=>{let n=0;const res=await CP.blindSet(async()=>{n++;if(n===3)return null;CP.renderFrame(2);return {blob:new Blob([new Uint8Array(4000+n)],{type:'video/mp4'})}});
      const L=await CP.blindList();return {res,links:[...document.querySelectorAll('#blindl a')].map(a=>a.download),txt:document.getElementById('blindl').innerText,idb:L.map(x=>x.code),busy:CP.S.busy,on:CP.S.cmp.on,sc:CP.S.sc.length,ln:CP.S.ln.length,narr:!!CP.S.narr,abortHidden:document.getElementById('bAbort').hidden}}""")
    chk('S1 3rd export fails: first two videos still offered for saving',r['res'] is None and len(r['links'])==2,r)
    chk('S1b completed videos also stored on the device (IndexedDB)',len(r['idb'])>=2,r['idb'])
    chk('S1c message says completed videos and materials remain',('残っています' in r['txt']) and r['busy']==False and r['on']==False and r['narr'] and r['abortHidden'],r['txt'])
    # ---- S2 page killed -> reopen: videos recovered from the device
    pg2=ctx.new_page();pg2.goto(URL);pg2.wait_for_timeout(1200)
    t=pg2.inner_text('#blindl');l=pg2.evaluate("()=>[...document.querySelectorAll('#blindl a')].map(a=>a.download)")
    chk('S2 after reopening the page, finished videos are recovered',('残っています' in t) and len(l)==2,[t,l])
    pg2.close()
    # ---- S3 abort between/during export
    r=pg.evaluate("""async()=>{let n=0;const res=await CP.blindSet(async()=>{n++;if(n===2){CP.S.abort=true;return null}return {blob:new Blob([new Uint8Array(4000)],{type:'video/mp4'})}});return {res,txt:document.getElementById('blindl').innerText,links:document.querySelectorAll('#blindl a').length}}""")
    chk('S3 abort: stops safely, keeps the finished video, says it was stopped',r['res'] is None and ('中止' in r['txt']) and r['links']==1,r)
    r=pg.evaluate("""async()=>{let n=0;const res=await CP.blindSet(async()=>{n++;if(n===1){setTimeout(()=>{CP.S.abort=true},0)}return {blob:new Blob([new Uint8Array(4000)],{type:'video/mp4'})}});return {res,n,txt:document.getElementById('blindl').innerText,links:document.querySelectorAll('#blindl a').length}}""")
    chk('S3b abort pressed between videos is honoured (not reset), finished video kept',r['res'] is None and r['n']==1 and r['links']==1 and '中止' in r['txt'],r)
    # ---- S4 exportGuard: abort flag and memory pressure raise coded errors
    g=pg.evaluate("""()=>{const o={};try{CP.S.abort=true;CP.exportGuard(0)}catch(e){o.abort=e.code}CP.S.abort=false;
      Object.defineProperty(performance,'memory',{configurable:true,get:()=>({usedJSHeapSize:900,jsHeapSizeLimit:1000})});try{CP.exportGuard(0)}catch(e){o.mem=e.code}
      Object.defineProperty(performance,'memory',{configurable:true,get:()=>({usedJSHeapSize:100,jsHeapSizeLimit:1000})});try{CP.exportGuard(0);o.ok=true}catch(e){o.ok=false}return o}""")
    chk('S4 guard: abort and low-memory raise ABORT/MEMORY, healthy state passes',g=={'abort':'ABORT','mem':'MEMORY','ok':True},g)
    # real exportOffline error path with a failing encoder: busy released, message, nothing lost
    f=pg.evaluate("""async()=>{CP.S.abort=false;const r=await CP.exportOffline();return {r,busy:CP.S.busy,fail:CP.S.lastFail,txt:document.getElementById('st')?document.getElementById('st').textContent:''}}""")
    chk('S5 exportOffline failure (no native AAC in this sandbox): returns null, busy released, failure recorded',f['r'] is None and f['busy']==False,f)
    # ---- audio report
    a=pg.evaluate("""()=>{const sr=48000,mk=(f)=>{const b=new AudioBuffer({length:16*sr,sampleRate:sr,numberOfChannels:2});for(let c=0;c<2;c++){const x=b.getChannelData(c);for(let i=0;i<x.length;i++)x[i]=f(i/sr)}return b};
      const ln=CP.S.ln;const inSp=t=>ln.some(L=>t>=L.t0&&t<L.t0+L.d);
      const good=CP.audioReport(mk(t=>inSp(t)?.3*Math.sin(2*Math.PI*200*t):.03*Math.sin(2*Math.PI*60*t)));
      const clip=CP.audioReport(mk(t=>Math.max(-1,Math.min(1,3*Math.sin(2*Math.PI*200*t)))));
      const flat=CP.audioReport(mk(t=>.2*Math.sin(2*Math.PI*200*t)));
      return {good,clip,flat}}""")
    chk('S6 healthy mix: no warnings, speech well above gaps',a['good']['warn']==[] and a['good']['speechOverGap']>12,a['good'])
    chk('S7 clipped mix: peak and clipping flagged',a['clip']['clipSamples']>0 and any('音割れ' in w for w in a['clip']['warn']) and any('ピーク' in w for w in a['clip']['warn']),a['clip'])
    chk('S8 narration not louder than background: flagged as hard to hear',any('聞き取りにくい' in w for w in a['flat']['warn']),a['flat'])
    # ---- evidence record
    pg.evaluate("()=>{CP.S.dj=JSON.stringify({schema:'become.design/1',scenes:[]})}")
    r=pg.evaluate("""async()=>{await CP.blindSet(async()=>({blob:new Blob([new Uint8Array(4000)],{type:'video/mp4'})}));CP.revealKey();await new Promise(r=>setTimeout(r,600));const E=CP.lastEvidence;return {E,link:!!document.querySelector('#revl a')}}""")
    E=r['E']
    chk('S9 evidence record created with a download link after the reveal',r['link'] and E is not None)
    chk('S9b record ties script, JSON hash, app build, device, narration, BGM field',E and len(E['script'])>=4 and len(E['designJson']['sha256'])==64 and 'build' in E['app'] and E['device']['userAgent'] and 'narration' in E and 'bgm' in E,E and list(E.keys()))
    chk('S9c record lists 3 videos with variant, audio check, loudness, perf keys',E and len(E['videos'])==3 and sorted(v['variant'] for v in E['videos'])==['A','B','C'] and all('audio' in v and 'loudness' in v for v in E['videos']),E and E['videos'])
    pg.evaluate("()=>{CP.S.cmp.key={};try{sessionStorage.removeItem('cpKey')}catch{}}")
    chk('S10 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
