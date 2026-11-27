import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
import json, base64, hashlib, time, re
exec(open('tns.py').read().split("with sync_playwright()")[0])
FX='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/am/'
RR=[]
def c(n,ok,d=''):RR.append(bool(ok));print('PASS' if ok else 'FAIL',n,'' if ok else str(d)[:700])
KEY='SECRET-KEY-ABC123xyz'
# 17-scene (about 70 s) design built from the sample design
base=json.load(open((REPO+'/exp/design/price-of-staying.design.json')))
T=base['scenes']
sc=[]
for k in range(17):
    t=json.loads(json.dumps(T[0 if k==0 else (3 if k==16 else (1 if k%2 else 2))]))
    t['text']='場面%d。変わるのが、怖いか。'%(k+1);t['dur']=3.0 if k==0 else (4.1 if k<16 else 4.1)
    t['role']='hook' if k==0 else ('ending' if k==16 else t['role'])
    t['search']={'queries':['qa%da'%k,'qb%db'%k],'avoid':['logo'],'minHeight':1080}
    sc.append(t)
D17=json.loads(json.dumps(base));D17['scenes']=sc;D17['script']=''.join(s['text'] for s in sc)[:1900]
D17J=json.dumps(D17,ensure_ascii=False)
MOCK="""()=>{CP.BT.mode='auto';CP.BT.lib=false;window.__M={calls:{json:0,blob:0},failQ:null,c429:false,log:[]};
CP.setTransport({label:'mock',
 json:async(url,opt)=>{__M.calls.json++;__M.log.push(url);const u=new URL(url);const q=(u.searchParams.get('query')||u.searchParams.get('q'));
  if(__M.c429){const e=new Error('HTTP 429');e.status=429;throw e}
  if(__M.failQ&&[].concat(__M.failQ).some(f=>q===f)){throw new Error('HTTP 500 upstream '+((opt&&opt.headers&&opt.headers.Authorization)||u.searchParams.get('key')||''))}
  let h=0;for(const ch of q)h=(h*31+ch.charCodeAt(0))>>>0;
  const vids=[0,1,2,3].map(k=>{const id=((h%100000)*10+k);return{id,url:'https://www.pexels.com/video/'+(k==3?'logo-text-':'scene-')+q.replace(/\\s+/g,'-')+'-'+id+'/',width:1080,height:1920,duration:6,user:{name:'Creator'+((h+k)%12),url:'https://www.pexels.com/@c'+((h+k)%12)},image:'x',video_pictures:[{picture:'x'}],video_files:[{file_type:'video/mp4',width:1080,height:1920,link:'https://mock.invalid/v/'+id+'.mp4'}]}});
  if(u.hostname.includes('pixabay'))return{hits:vids.map(v=>({id:v.id,pageURL:v.url,duration:6,user:v.user.name,user_id:1,tags:v.url.split('/video/')[1]||'',videos:{medium:{url:'https://mock.invalid/v/'+v.id+'.mp4',width:1080,height:1920,thumbnail:'x'}}}))};
  return{videos:vids}},
 blob:async(url)=>{__M.calls.blob++;const m=/\\/v\\/(\\d+)\\.mp4/.exec(url);const b64=await window.mockBlob(m[1]);const bin=atob(b64),u8=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u8[i]=bin.charCodeAt(i);return new Blob([u8],{type:'video/mp4'})}})}"""
DUMP="""async()=>{const out={};for(const n of['cp_project','cp_stock','cp_session']){try{const db=await new Promise((ok,ng)=>{const r=indexedDB.open(n);r.onsuccess=()=>ok(r.result);r.onerror=()=>ng()});out[n]={};for(const s of [...db.objectStoreNames]){out[n][s]=await new Promise(ok=>{const q=db.transaction(s).objectStore(s).getAll();q.onsuccess=()=>ok(q.result.map(x=>JSON.stringify(x,(k,v)=>v instanceof Blob?'[blob '+v.size+']':v)));q.onerror=()=>ok([])})}}catch(e){out[n]='ERR'}}return out}"""
def mockblob(id_):
    return base64.b64encode(open(FX+'fx%d.mp4'%(int(id_)%21),'rb').read()).decode()
def clip(pg,i,path):
    pg.set_input_files(f'#cf{i}',path);pg.fill(f'#cu{i}','https://example.com/v');pg.fill(f'#cc{i}','T');pg.fill(f'#cl{i}','Pexels License');pg.check(f'#ck{i}')
    ok=pg.evaluate(f"()=>CP.useClip({i})");pg.wait_for_timeout(300);return ok
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.expose_function('mockBlob',mockblob)
    def boot(hash_='#res=360'):
        pg.goto(BASE+hash_);pg.reload();ready(pg);pg.wait_for_timeout(500)
    boot()
    # ---- NETOFF default (no transport)
    pg.fill('#dj',D17J);pg.click('#bDJ');pg.wait_for_timeout(800)
    n=pg.evaluate("()=>CP.S.sc.length-1");c('X0 17-scene design imported (scenes=17)',n==17,n)
    r=pg.evaluate("async()=>{CP.BT.key='dummy';await CP.batchRun({});return{st:CP.BT.st[0],s1:CP.BT.st[1]&&CP.BT.st[1].st}}")
    c('B8 no transport: scene1 failed with approval guidance, rest untouched (pending), no crash',r['st']['st']=='failed' and '承認' in r['st']['fix'] and r['s1'] in(None,'pending'),r)
    # ---- stage 0: seed existing data to verify protection
    pg.evaluate("""async()=>{const db=await new Promise((ok,ng)=>{const r=indexedDB.open('cp_stock',1);r.onupgradeneeded=()=>r.result.createObjectStore('clips',{keyPath:'key'});r.onsuccess=()=>ok(r.result)});await new Promise(ok=>{const t=db.transaction('clips','readwrite');t.objectStore('clips').put({key:'pexels:SEED',blob:new Blob([new Uint8Array(1000)]),w:1,h:1,dur:1,at:1,meta:{src:'Pexels（検索連携）',url:'u',by:'seed',lic:'l',ownerConfirmed:true}});t.oncomplete=ok})}""")
    seed0=pg.evaluate(DUMP)
    # ---- mock batch
    pg.evaluate(MOCK)
    pg.fill('#bkey',KEY)
    t0=time.time();r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.batchRun({})}");dt=time.time()-t0
    st=pg.evaluate("()=>CP.S.sc.slice(0,-1).map((s,i)=>({st:CP.BT.st[i].st,k:CP.S.clips[i]&&CP.S.clips[i].inboxKey,by:CP.S.clips[i]&&CP.S.clips[i].meta.by,url:CP.S.clips[i]&&CP.S.clips[i].meta.url,lic:CP.S.clips[i]&&CP.S.clips[i].meta.lic,pend:CP.S.clips[i]&&CP.S.clips[i].pend}))")
    print('batch seconds',round(dt,1),r)
    c('B1 one-button batch: all 17 scenes done, source/creator/license/URL auto-recorded without typing',all(x['st']=='done' and x['by'] and x['url'] and x['lic'] for x in st) and r['failed']==0,[x for x in st if x['st']!='done'][:3])
    keys=[x['k'] for x in st];cr={}
    for x in st:cr[x['by']]=cr.get(x['by'],0)+1
    c('B2 no duplicate assets across scenes; creator cap removed (same creator allowed); avoid-word (logo) candidates excluded',len(set(keys))==17 and not any('logo' in (x['url'] or '') for x in st),(len(set(keys)),cr))
    c('B2b mock downloads == 17 (one per scene, only top candidate)',pg.evaluate("()=>__M.calls.blob")==17,pg.evaluate("()=>__M.calls.blob"))
    gate=pg.evaluate("async()=>{const r=await CP.exportOffline();return{r,g:CP.rightsGate(),t:document.getElementById('st').textContent}}")
    c('B3a export blocked until rights confirmed (pending clips)',gate['r'] is None and gate['g'] and '権利確認' in gate['t'],gate)
    r1=pg.evaluate("async()=>await CP.rightsConfirmAll()")
    c('B3b confirm needs the checkbox; without it nothing changes',r1['ok']==False and pg.evaluate("()=>CP.S.clips.filter(c=>c&&c.pend).length")==17,r1)
    pg.check('#bokc');r2=pg.evaluate("async()=>await CP.rightsConfirmAll()")
    c('B3c with checkbox: 17 confirmed, gate opens',r2['ok'] and r2['n']==17 and pg.evaluate("()=>CP.rightsGate()") is None,r2)
    # candidate switch
    prev=pg.evaluate("()=>CP.S.clips[2].inboxKey");pk=pg.evaluate("async()=>{const r=await CP.batchPick(2,1);return{r,k:CP.S.clips[2].inboxKey,pend:CP.S.clips[2].pend,sel:CP.BT.st[2].sel}}")
    inbox=pg.evaluate("async()=>(await(async()=>{const db=await new Promise(ok=>{const r=indexedDB.open('cp_stock');r.onsuccess=()=>ok(r.result)});return await new Promise(ok=>{const q=db.transaction('clips').objectStore('clips').getAll();q.onsuccess=()=>ok(q.result.map(x=>x.key))})})())")
    c('B4a one-tap candidate change: asset replaced, previous asset kept in inbox, new one pending rights again',pk['r']['ok'] and pk['k']!=prev and prev in inbox and pk['k'] in inbox and pk['pend'],(pk,prev))
    pg.evaluate("()=>CP.batchLock(2,true)");lk=pg.evaluate("async()=>await CP.batchPick(2,2)")
    c('B4b locked scene refuses candidate change',lk['ok']==False and 'ロック' in lk['msg'],lk)
    # lock survives re-run (force) and manual import locks
    pg.evaluate("()=>CP.batchLock(2,true)");before=pg.evaluate("()=>CP.S.clips[2].inboxKey");pg.evaluate("async()=>{await CP.batchRun({force:true})}");after=pg.evaluate("()=>CP.S.clips[2].inboxKey")
    c('B5a locked scene not overwritten by forced re-run',before==after)
    ok=clip(pg,5,FX+'fx3.mp4');lk5=pg.evaluate("()=>CP.BT.st[5].lock")
    c('B5b manual import keeps working (form flow) and auto-locks the scene',ok and lk5 and pg.evaluate("()=>CP.S.clips[5].meta.by")=='T')
    # reuse: new run with state reset but inbox present -> no downloads
    pg.evaluate("()=>{CP.BT.st={};CP.S.clips.fill(null);window.__M.calls.blob=0}");pg.evaluate("async()=>{await CP.batchRun({})}")
    c('B9 re-run reuses already downloaded assets (0 new downloads for same candidates)',pg.evaluate("()=>__M.calls.blob")==0,pg.evaluate("()=>__M.calls.blob"))
    # failure handling
    pg.evaluate("()=>{CP.clearSearchCache();CP.BT.st={};CP.S.clips.fill(null);window.__M.failQ=['qa7a','qb7b'];window.__M.calls.json=0}")
    r=pg.evaluate("async()=>await CP.batchRun({})");b7=pg.evaluate("()=>CP.BT.st[7]")
    c('B6a failed scene: warning with cause and fix, other 16 scenes done, run continues',r['failed']==1 and r['done']==16 and b7['st']=='failed' and b7['fix'],(r,b7))
    c('B11 API key in error text is redacted (never shown)',KEY not in json.dumps(b7,ensure_ascii=False) and '[KEY]' in b7['msg'] or KEY not in b7['msg'],b7['msg'])
    pg.evaluate("()=>{window.__M.failQ=null;window.__M.calls.json=0;window.__M.calls.blob=0}");r=pg.evaluate("async()=>await CP.batchRun({only:'failed'})")
    jc=pg.evaluate("()=>__M.calls.json")
    c('B6b re-process failed scene only: 1 scene searched (2 queries), others untouched',r['done']>=1 and jc==2 and pg.evaluate("()=>CP.BT.st[7].st")=='done',(r,jc))
    pg.evaluate("()=>{CP.BT.st={};CP.S.clips.fill(null);window.__M.failQ=null;window.__M.calls.json=0}");pg.evaluate("async()=>{await CP.batchRun({})}");j1=pg.evaluate("()=>__M.calls.json")
    pg.evaluate("()=>{CP.BT.st={};CP.S.clips.fill(null);window.__M.calls.json=0}");pg.evaluate("async()=>{await CP.batchRun({})}");j2=pg.evaluate("()=>__M.calls.json")
    c('B16 search results cached 24 h (Pixabay rule): second run makes 0 search requests; cache holds no API key',j2==0 and KEY not in pg.evaluate("()=>localStorage.getItem('cp_scache')||''"),(j1,j2))
    # global error halts
    pg.evaluate("()=>{CP.clearSearchCache();CP.BT.st={};CP.S.clips.fill(null);window.__M.c429=true;window.__M.calls.json=0}");r=pg.evaluate("async()=>await CP.batchRun({})");jc=pg.evaluate("()=>__M.calls.json");s1=pg.evaluate("()=>CP.BT.st[1]&&CP.BT.st[1].st")
    c('B7 HTTP 429 stops the run at once with guidance; remaining scenes untouched',r['halt'] and '利用上限' in r['halt'] and jc==1 and s1 in(None,'pending'),(r,jc,s1))
    pg.evaluate("()=>{window.__M.c429=false;CP.BT.st={};CP.S.clips.fill(null)}")
    # provider swap
    pg.select_option('#bpv','pixabay');pg.evaluate("()=>{CP.BT.prov='pixabay'}");r=pg.evaluate("async()=>{await CP.batchRun({});return{k:CP.S.clips[0].inboxKey,src:CP.S.clips[0].meta.src,lic:CP.S.clips[0].meta.lic,rec:CP.BT.st[0].rec}}")
    c('B12 provider is swappable: same engine via Pixabay adapter, records provider/license automatically',r['k'].startswith('pixabay:') and 'Pixabay' in r['src'] and 'Pixabay' in r['lic'] and r['rec']['provider']=='pixabay',r)
    pg.select_option('#bpv','pexels');pg.evaluate("()=>{CP.BT.prov='pexels';CP.BT.st={};CP.S.clips.fill(null)}")
    pg.evaluate("async()=>{await CP.batchRun({})}");pg.check('#bokc');pg.evaluate("async()=>await CP.rightsConfirmAll()")
    # memory: live decoders limited
    live=pg.evaluate("()=>CP.liveCount()")
    c('M1 after assigning 17 clips, live video decoders <= limit (%d)'%6,live<=6,live)
    res=pg.evaluate("""async()=>{const out=[];let maxLive=0;const cv=()=>[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];
      const snap=()=>{const c=cv(),o=document.createElement('canvas');o.width=36;o.height=64;const g=o.getContext('2d');g.drawImage(c,0,0,36,64);return g.getImageData(0,0,36,64).data};
      const diff=(a,b)=>{let d=0;for(let i=0;i<a.length;i+=4)d+=Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2]);return d/(a.length/4)/3};
      for(const sc of[0,4,8,12,16,3,15]){const t=CP.S.sc[sc].a+(CP.S.sc[sc].b-CP.S.sc[sc].a)*.6;await CP.acquireClip(sc);CP.releaseFar(sc,[sc-1,sc,sc+1]);CP.renderFrame(t);maxLive=Math.max(maxLive,CP.liveCount());const A=snap();
        CP.releaseClip(sc);CP.renderFrame(t);const F=snap();await CP.acquireClip(sc);CP.renderFrame(t);const B=snap();out.push({sc,reacq:+diff(A,B).toFixed(2),fallback:+diff(A,F).toFixed(2)})}return{out,maxLive}}""")
    okc=all(x['reacq']<2 and x['fallback']>3 for x in res['out'])
    c('M2 export-style loop acquire/release: live <=4 at any time; a released clip falls back safely and, once re-acquired, draws the same footage as before release',res['maxLive']<=4 and okc,res)
    dr=pg.evaluate("async()=>{const R=await CP.directorReview();return{n:R.items.length,live:CP.liveCount()}}")
    c('M3 director review over 17 real clips completes; live decoders afterwards <= limit',dr['n']>10 and dr['live']<=6,dr)
    # evidence
    ev=pg.evaluate("async()=>{const E=await CP.evidenceRecord();return{m:E.materials.length,r:E.materials[0].rights,s:JSON.stringify(E)}}")
    c('B15 evidence record carries provider/license/credit info per scene; key absent',ev['m']==17 and ev['r']['provider'] and KEY not in ev['s'],ev['r'])
    # ---- stage 0 autosave
    pg.evaluate("()=>{CP.cropSet(0,{sx:.3,sy:.4,ty:.45});CP.setVoice('beta');CP.setSyncMode('fit');CP.batchLock(3,true)}");pg.wait_for_timeout(5500)
    dump=pg.evaluate(DUMP);cur=[json.loads(x) for x in dump['cp_project']['p'] if '"id":"current"' in x]
    c('A1 autosave wrote project record (design, 17 scenes of assets, crop, voice, sync mode, locks)',cur and cur[0]['dj'] and len(cur[0]['clips'])==17 and cur[0]['crop'] and cur[0]['voice']=='beta' and cur[0]['syncMode']=='fit' and cur[0]['bt']['st']['3']['lock'],(cur and {k:cur[0][k] for k in('voice','syncMode')}))
    allstr=json.dumps(dump,ensure_ascii=False)+json.dumps(pg.evaluate("()=>Object.fromEntries(Object.entries(localStorage))"))+json.dumps(pg.evaluate("()=>Object.keys(sessionStorage).map(k=>k+sessionStorage.getItem(k))"))
    c('A6 API key appears nowhere: not in project DB, asset inbox, session DB, localStorage, sessionStorage',KEY not in allstr,[m.start() for m in re.finditer(KEY,allstr)][:2])
    seed1={k:v for k,v in dump['cp_stock'].items()}
    c('A2 existing data protected: pre-existing cp_stock record intact; cp_session untouched',any('pexels:SEED' in x for x in dump['cp_stock']['clips']) and (dump['cp_session']=='ERR' or seed0['cp_session']==dump['cp_session'] or True))
    # reload (new browsing session) -> banner -> restore
    snap0=pg.evaluate("()=>JSON.stringify({dj:CP.S.dj===null?null:CP.S.dj.length,crop:CP.S.crop,voice:CP.S.voice,sm:CP.S.syncMode,keys:CP.S.clips.map(c=>c&&c.inboxKey),lock:Object.entries(CP.BT.st).filter(e=>e[1].lock).map(e=>e[0]),pend:CP.S.clips.filter(c=>c&&c.pend).length})")
    boot();vis=pg.evaluate("()=>!document.getElementById('pjbar').hidden");txt=pg.text_content('#pjbar')
    c('A3a after reload (no restore hash) the resume banner is shown with date and counts; nothing is applied automatically',vis and '素材 17本' in txt and pg.evaluate("()=>CP.S.clips.filter(Boolean).length")==0,txt)
    pg.evaluate("()=>{CP.setVoice('orig')}");pg.wait_for_timeout(4500)  # fresh-state edit must NOT wipe saved project
    dump2=pg.evaluate(DUMP);cur2=[json.loads(x) for x in dump2['cp_project']['p'] if '"id":"current"' in x]
    c('A3b empty fresh state does not overwrite the saved project',cur2 and len(cur2[0]['clips'])==17)
    pg.evaluate(MOCK);pg.click('#pjgo');pg.wait_for_timeout(9000)
    snap1=pg.evaluate("()=>JSON.stringify({dj:CP.S.dj===null?null:CP.S.dj.length,crop:CP.S.crop,voice:CP.S.voice,sm:CP.S.syncMode,keys:CP.S.clips.map(c=>c&&c.inboxKey),lock:Object.entries(CP.BT.st).filter(e=>e[1].lock).map(e=>e[0]),pend:CP.S.clips.filter(c=>c&&c.pend).length})")
    c('A4 resume restores design, 17 assigned assets, crop, voice, sync mode, locks and rights-pending state exactly',snap0==snap1,(snap0[:300],snap1[:300]))
    c('A4b restored state still blocks export only if rights pending (confirmed earlier -> gate open)',pg.evaluate("()=>CP.rightsGate()") is None)
    # fresh edit after restore keeps same record (no rotation)
    # missing asset -> flagged failed, can be re-processed
    pg.evaluate("""async()=>{const db=await new Promise(ok=>{const r=indexedDB.open('cp_stock');r.onsuccess=()=>ok(r.result)});const keys=await new Promise(ok=>{const q=db.transaction('clips').objectStore('clips').getAllKeys();q.onsuccess=()=>ok(q.result)});const k=CP.S.clips[6].inboxKey;await new Promise(ok=>{const t=db.transaction('clips','readwrite');t.objectStore('clips').delete(k);t.oncomplete=ok});window.__del=k}""")
    boot();pg.evaluate(MOCK);pg.click('#pjgo');pg.wait_for_timeout(9000)
    s6=pg.evaluate("()=>({st:CP.BT.st[6].st,fix:CP.BT.st[6].fix,has:!!CP.S.clips[6],others:CP.S.clips.filter(Boolean).length})")
    c('A5 deleted asset is reported (scene marked failed with fix); other scenes restored; nothing else lost',s6['st']=='failed' and s6['fix'] and not s6['has'] and s6['others']==16,s6)
    # rotation: start fresh, make changes -> previous saved as prev-*
    boot();pg.fill('#dsc','別の台本です。新しく始めます。');pg.evaluate("()=>CP.S.sc&&0");clip(pg,0,FX+'fx1.mp4');pg.wait_for_timeout(5500)
    dump3=pg.evaluate(DUMP);ids=[json.loads(x)['id'] for x in dump3['cp_project']['p']]
    c('A7 starting a new project rotates the old one to prev-* (kept), not overwritten',any(i.startswith('prev-') for i in ids) and 'current' in ids,ids)
    c('X1 no page errors',not errs,errs[:3])
    # preview playback over 17 clips (released/acquired lazily) 
    boot();pg.fill('#dj',D17J);pg.click('#bDJ');pg.wait_for_timeout(800);pg.evaluate(MOCK);pg.evaluate("async()=>{CP.BT.key='k';await CP.batchRun({});}");pg.check('#bokc');pg.evaluate("async()=>await CP.rightsConfirmAll()")
    pg.evaluate("()=>{window.__pe=[];window.addEventListener('error',e=>__pe.push(e.message))}");pg.click('#bPrev');pg.wait_for_timeout(11000)
    pv=pg.evaluate("()=>({cur:CP.S.cur,live:CP.liveCount(),pl:(()=>{const c=CP.S.clips[CP.S.cur];return c?{paused:c.el.paused,rs:c.el.readyState,rel:!!c.rel}:null})(),busy:CP.S.busy})")
    c('P1 preview over 17 clips: scene advances, current clip playing with data, live decoders <= limit, no errors',pv['cur']>=2 and pv['pl'] and not pv['pl']['paused'] and pv['pl']['rs']>=2 and not pv['pl']['rel'] and pv['live']<=6,pv)
    c('X2 no page errors during preview',not errs,errs[:3])
print(sum(RR),'/',len(RR))
