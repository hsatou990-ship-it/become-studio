from playwright.sync_api import sync_playwright
import json, base64
exec(open('tns.py').read().split("with sync_playwright()")[0])
R3=[]
def c3(n,c,d=''):R3.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:500])
wav=base64.b64encode(open(D+'a.wav','rb').read()).decode()
PUT="""([wav,dj,extra])=>new Promise((ok,ng)=>{const bin=atob(wav),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);const r=indexedDB.open('cp_session',1);r.onupgradeneeded=()=>r.result.createObjectStore('s',{keyPath:'k'});r.onsuccess=()=>{const t=r.result.transaction('s','readwrite');t.objectStore('s').put(Object.assign({k:'last',at:Date.now(),dsc:'x',plan:false,dj:dj,dv:0,font:null,narr:new Blob([u],{type:'audio/wav'}),bgm:null,mockNarr:false,clips:[]},extra));t.oncomplete=ok;t.onerror=()=>ng(1)}})"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE+'#res=360');ready(pg)
    pg.evaluate("()=>{localStorage.removeItem('cp_voice');localStorage.removeItem('cp_syncmode');localStorage.removeItem('cp_bgmmode')}")
    # session saved by the previous version: no voice / manual / syncMode fields
    pg.evaluate(PUT,[wav,json.dumps(J,ensure_ascii=False),{}])
    pg.goto(BASE+'#res=360&restore=1');pg.reload();ready(pg);pg.wait_for_timeout(2500)
    st=pg.evaluate("()=>({voice:CP.S.voice||'orig',mode:CP.S.syncMode||'keep',ok:CP.S.sync&&CP.S.sync.ok,aligned:CP.S.aligned,narr:!!CP.S.narr,D:CP.S.sync&&CP.S.sync.D})")
    c3('S1 previous-version session (no voice/manual/syncMode) restores: original voice, default sync, narration aligned',st['voice']=='orig' and st['mode']=='keep' and st['ok'] and st['aligned'] and st['narr'],st)
    c3('S2 UI controls reflect defaults',pg.evaluate("()=>document.querySelector('input[name=voice]:checked').value")=='orig' and pg.evaluate("()=>document.getElementById('syncm').value")=='keep')
    # new-version session with legacy sync + beta + manual
    pg.evaluate(PUT,[wav,json.dumps(J,ensure_ascii=False),{'voice':'beta','syncMode':'legacy','manual':[{'s':.3,'e':1.9},{'s':2.5,'e':4.0},{'s':4.6,'e':6.3},{'s':6.9,'e':8.0}]}])
    pg.goto(BASE+'#res=360&restore=1');pg.reload();ready(pg);pg.wait_for_timeout(2500)
    st=pg.evaluate("()=>({voice:CP.S.voice,mode:CP.S.syncMode,man:!!CP.S.manual,sm:CP.S.sync&&CP.S.sync.mode,man2:CP.S.sync&&CP.S.sync.manual,D:CP.S.sync&&CP.S.sync.D,sel:document.getElementById('syncm').value})")
    c3('S3 new session restores voice=beta, sync=legacy, manual spans',st['voice']=='beta' and st['mode']=='legacy' and st['man'] and st['sm']=='legacy' and st['man2'] and st['sel']=='legacy',st)
    # plain reload: localStorage persistence of mode and voice
    pg.evaluate("()=>{CP.setVoice('orig');CP.setSyncMode('fit')}");pg.goto(BASE+'#res=360');pg.reload();ready(pg)
    c3('S4 plain reload keeps sync mode (fit) and voice (orig) via localStorage',pg.evaluate("()=>CP.S.syncMode")=='fit' and pg.evaluate("()=>document.getElementById('syncm').value")=='fit' and (pg.evaluate("()=>CP.S.voice")in('orig',None)))
    pg.evaluate("()=>{CP.setSyncMode('keep')}")
    # corrupt localStorage values fall back safely
    pg.evaluate("()=>{localStorage.setItem('cp_voice','zzz');localStorage.setItem('cp_syncmode','zzz')}");pg.goto(BASE+'#res=360');pg.reload();ready(pg)
    c3('S5 corrupt stored values fall back to defaults (no error)',(pg.evaluate("()=>CP.S.voice")in('orig',None)) and pg.evaluate("()=>CP.S.syncMode")=='keep' and not errs,errs)
    # export path unaffected: run existing offline export test separately (tev/tk/tj) – here just that mix builds without narration & with each mode
    pg.evaluate("()=>{localStorage.clear()}");pg.goto(BASE+'#res=360');ready(pg);pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(500)
    okm=pg.evaluate("""async()=>{const r=[];for(const m of['keep','fit','legacy']){CP.setSyncMode(m);for(const v of['orig','beta']){CP.setVoice(v);const x=await CP.buildAudio();r.push(x.length>0)}}return r}""")
    c3('S6 no narration: all 6 mode/voice combinations build',all(okm),okm)
    b.close()
print(sum(R3),'/',len(R3))
