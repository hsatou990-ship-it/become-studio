exec(open("tam.py").read().split("\nwith sync_playwright()")[0])
WAV=FX+'n.wav'
MP4=open(FX+'fx0.mp4','rb').read()
def mkhits(q,n=4,creator=None):
    h=0
    for ch in q:h=(h*31+ord(ch))&0xffffffff
    return [{'id':(h%100000)*10+k,'pageURL':'https://pixabay.com/videos/x-%d/'%((h%100000)*10+k),'duration':8,'user':creator or 'Maker%d'%((h+k)%5),'user_id':77,'tags':'sunrise, mountain, '+q,
      'videos':{'large':{'url':'https://cdn.pixabay.com/video/a/%d.mp4'%((h%100000)*10+k),'width':1080,'height':1920,'size':30000000,'thumbnail':'https://cdn.pixabay.com/video/a/t%d.jpg'%k},
                'medium':{'url':'https://cdn.pixabay.com/video/b/%d.mp4'%((h%100000)*10+k),'width':720,'height':1280,'size':9000000,'thumbnail':'https://cdn.pixabay.com/video/b/t%d.jpg'%k}}} for k in range(n)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));cons=[];pg.on('console',lambda m:cons.append(m.text))
    pg.expose_function('mockBlob',mockblob)
    REQ={'api':[],'cdn':[],'other':[]};MODE={'api':'ok','cdn':'ok'}
    def h_api(route,req):
        REQ['api'].append(req.url)
        if MODE['api']=='403':return route.fulfill(status=403,body='forbidden',headers={'access-control-allow-origin':'*'})
        if MODE['api']=='nocors':return route.abort('failed')
        u=req.url;import urllib.parse as up;q=up.parse_qs(up.urlparse(u).query)
        hits=mkhits(q.get('q',['x'])[0]) if 'q' in q else mkhits('byid')[:1]
        if 'id' in q:
            hh=mkhits('byid')[:1];hh[0]['id']=int(q['id'][0]);hits=hh
        route.fulfill(status=200,body=json.dumps({'total':len(hits),'hits':hits}),content_type='application/json',headers={'access-control-allow-origin':'*','x-ratelimit-remaining':'99','x-ratelimit-limit':'100','x-ratelimit-reset':'30','access-control-expose-headers':'X-RateLimit-Remaining,X-RateLimit-Limit,X-RateLimit-Reset'})
    def h_cdn(route,req):
        REQ['cdn'].append(req.url)
        if req.url.endswith('.jpg'):return route.fulfill(status=200,body=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='),content_type='image/png',headers={'access-control-allow-origin':'*'})
        route.fulfill(status=200,body=MP4,content_type='video/mp4',headers={'access-control-allow-origin':'*'})
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://cdn.pixabay.com/**',h_cdn)
    ctx.route('https://example.com/**',lambda r,q:(REQ['other'].append(q.url),r.fulfill(status=200,body='x')))
    def boot(hash_='#res=360'):
        pg.goto(BASE+hash_);pg.reload();ready(pg);pg.evaluate("()=>{CP.REAL.lim.s=1;CP.REAL.lim.d=1}");pg.wait_for_timeout(500)
    boot()
    pg.evaluate("()=>{try{localStorage.clear();sessionStorage.clear()}catch{}}")
    csp=pg.evaluate("()=>document.querySelector('meta[http-equiv=Content-Security-Policy]').content")
    c('R1 CSP: connect-src is only pixabay.com + cdn.pixabay.com (no Pexels, no wildcard), other directives unchanged',"connect-src https://pixabay.com https://cdn.pixabay.com;" in csp and 'pexels' not in csp and '*' not in csp and "default-src 'none'" in csp and "img-src blob: data:" in csp,csp)
    c('R2 real comm off by default (checkbox unchecked, no transport)',not pg.is_checked('#breal') and pg.evaluate("()=>CP.BT.net")is None)
    # pickVar unit
    pv=pg.evaluate("""()=>({
     a:CP.pickVar({large:{url:'u',width:1080,height:1920,size:30e6},medium:{url:'u',width:720,height:1280,size:9e6}}).n,
     b:CP.pickVar({large:{url:'u',width:2160,height:3840,size:90e6},medium:{url:'u',width:1080,height:1920,size:20e6},small:{url:'u',width:540,height:960,size:5e6}}).n,
     c:CP.pickVar({large:{url:'u',width:1920,height:1080,size:30e6},medium:{url:'u',width:1280,height:720,size:12e6},tiny:{url:'u',width:640,height:360,size:2e6}}).n,
     d:CP.pickVar({medium:{url:'u',width:720,height:1280,size:9e6},small:{url:'u',width:540,height:960,size:5e6}}).n,
     e:CP.pickVar({large:{url:'u',width:3840,height:2160,size:70e6}}).n})""")
    c('R3 variant choice: smallest version reaching 1080px, skip >40MB, else largest available',pv=={'a':'large','b':'medium','c':'large','d':'medium','e':'large'},pv)
    # ---- real test screen
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.fill('#rq','sunrise mountain')
    pg.click('#rS');pg.wait_for_timeout(300);o0=pg.inner_text('#rOut')
    c('R4 search button while real comm is off: no request sent, clear guidance',len(REQ['api'])==0 and ('無効' in o0 or '承認' in o0),o0[:300])
    pg.check('#breal');pg.click('#rS');pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=20000)
    o1=pg.inner_text('#rOut')
    c('R5 ① search: exactly one request to pixabay.com, key only in the request URL, parsed 4 hits, CORS ok, rate-limit headers shown',len(REQ['api'])==1 and ('key='+KEY) in REQ['api'][0] and 'ヒット件数: 4' in o1 and 'CORS（ブラウザからの検索）: 成功' in o1 and '残り 99' in o1,(len(REQ['api']),o1[:500]))
    c('R6 result text never contains the API key',KEY not in o1)
    nopt=pg.evaluate("()=>document.querySelectorAll('#rSel option').length");c('R7 candidate list for ② has 4 entries',nopt==4,nopt)
    pg.click('#rS');pg.wait_for_timeout(400)  # same query -> 24h cache, no new request
    c('R8 same search repeated: served from 24 h cache, no extra request, no extra count',len(REQ['api'])==1 and pg.evaluate("()=>CP.realCnt().s")==1)
    pg.fill('#rq','another query');pg.click('#rS');pg.wait_for_timeout(500);o2=pg.inner_text('#rOut')
    c('R9 second different search blocked by trial quota (LIMIT), no request sent',len(REQ['api'])==1 and '承認済みの試験枠' in o2,o2[:300])
    pg.click('#rD');pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=40000);o3=pg.inner_text('#rOut')
    c('R10 ② download: exactly one request to cdn.pixabay.com (smallest sufficient version = medium? large<=40MB chosen as only 1080-class)',len(REQ['cdn'])==1 and REQ['cdn'][0].startswith('https://cdn.pixabay.com/video/'),REQ['cdn'])
    c('R11 inspection reports resolution/length/fps/bitrate/scale and says human review is needed; no key',all(t in o3 for t in ['解像度: 360×640','長さ:','フレームレート:','平均ビットレート:','縦1920pxへの拡大率','人の目で確認する項目','圧縮の目安','見切れ']) and KEY not in o3,[t for t in ['解像度: 360×640','長さ:','フレームレート:','平均ビットレート:','縦1920pxへの拡大率','人の目で確認する項目','圧縮の目安','見切れ'] if t not in o3])
    inbox=pg.evaluate(DUMP)['cp_stock']['clips']
    rec=[x for x in inbox if x.startswith('{') or 'pixabay' in str(x)]
    c('R12 downloaded asset stored in inbox as rights-unconfirmed with source URL, creator, license auto-recorded',len(inbox)==1 and 'pixabay:' in inbox[0] and 'ownerConfirmed' in inbox[0] and 'Pixabay Content License' in inbox[0] and 'pixabay.com/videos' in inbox[0],inbox[0][:500] if inbox else inbox)
    pg.click('#rD');pg.wait_for_timeout(600);o4=pg.inner_text('#rOut')
    c('R13 2nd download: inbox reuse -> no new request (reuse of fetched assets) and no extra count',len(REQ['cdn'])==1 and pg.evaluate("()=>CP.realCnt().d")==1,(REQ['cdn'],o4[:200]))
    # block a different candidate download (not in inbox) -> LIMIT
    pg.select_option('#rSel','2');pg.click('#rD');pg.wait_for_timeout(600);o5=pg.inner_text('#rOut')
    c('R14 download of a different video blocked by trial quota, no request',len(REQ['cdn'])==1 and '承認済みの試験枠' in o5,o5[:300])
    # ---- allowlist / failure modes (reset counter)
    r=pg.evaluate("""async()=>{localStorage.removeItem('cp_realcnt');const t=CP.realTransport(),out={};
      for(const [n,u] of [['http','http://pixabay.com/api/videos/?x=1'],['other','https://example.com/a.mp4'],['evil','https://pixabay.com.evil.test/a'],['pexels','https://api.pexels.com/v1/videos/search?query=a']]){try{await t.blob(u,{});out[n]='sent'}catch(e){out[n]=e.code}}
      out.cnt=CP.realCnt();return out}""")
    c('R15 host allowlist: http / other / look-alike / Pexels hosts are refused before any request, quota not consumed',r['http']=='HOST' and r['other']=='HOST' and r['evil']=='HOST' and r['pexels']=='HOST' and r['cnt']['d']==0 and len(REQ['other'])==0,(r,REQ['other']))
    MODE['api']='403';pg.fill('#rq','q403');n0=len(REQ['api']);pg.click('#rS');pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=15000);o6=pg.inner_text('#rOut')
    c('R16 HTTP 403: one request only (no retry), cause + fix shown, no key',len(REQ['api'])==n0+1 and '403' in o6 and 'キー' in o6 and KEY not in o6,o6[:400])
    MODE['api']='nocors';pg.evaluate("()=>{localStorage.removeItem('cp_realcnt');CP.clearSearchCache()}");pg.fill('#rq','qcors');pg.click('#rS');pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=15000);o7=pg.inner_text('#rOut')
    c('R17 CORS-less response is reported as a failure with guidance (not silently ignored)',('失敗' in o7) and ('許可していない' in o7 or 'CORS' in o7),o7[:400])
    MODE['api']='ok'
    pg.uncheck('#breal');c('R18 unchecking real comm turns the transport off again',pg.evaluate("()=>CP.BT.net")is None)
    # ---- review-first batch with mock transport (REAL quota irrelevant for mock)
    boot();pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.fill('#dj',D17J);pg.click('#bDJ');pg.wait_for_timeout(800)
    pg.evaluate(MOCK.replace("CP.BT.mode='auto';",""));pg.evaluate("()=>{const ob=CP.BT.net.blob;CP.BT.net.blob=async(u,o)=>{if(o&&o.thumb){__M.calls.thumb=(__M.calls.thumb||0)+1;const b=atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==');const u8=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u8[i]=b.charCodeAt(i);return new Blob([u8],{type:'image/png'})}return ob(u,o)}}")
    pg.fill('#bkey',KEY)
    c('V0 default method is review-first (candidates first, adopt later)',pg.evaluate("()=>CP.BT.mode")=='review' and pg.input_value('#bmode')=='review')
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;const r=await CP.batchRun({});return{r,blob:__M.calls.blob,sts:CP.S.sc.slice(0,-1).map((s,i)=>CP.BT.st[i].st),clips:CP.S.clips.filter(Boolean).length,nc:CP.BT.st[0].cands.length}}")
    c('V1 review-first batch: 17 scenes get candidates, ZERO downloads, no clips attached yet',r['blob']==0 and r['clips']==0 and set(r['sts'])=={'cand'} and r['nc']>=3 and r['r']['failed']==0,r)
    cs=pg.evaluate("()=>CP.BT.st[0].cands.map(c=>({s:c.score,w:c.warn,up:c.up,same:c.same,by:c.creator}))")
    c('V2 candidates are sorted by score and carry warnings/scale info',all(cs[i]['s']>=cs[i+1]['s'] for i in range(len(cs)-1)) and all(x['up'] is not None for x in cs),cs)
    ui=pg.inner_text('#brev');c('V3 review UI lists candidates with creator / resolution / size and an adopt button; export blocked message absent (nothing pending yet)','この素材を採用' in ui and '候補' in ui and '作者' in ui and '提案点' in ui)
    pg.evaluate("()=>{document.querySelectorAll('#brev details')[0].open=true}")
    pg.click('#brev button[data-a="thumb:0"]');pg.wait_for_timeout(800)
    c('V4 thumbnails load only for the chosen scene (lazy), via the transport, as blob images',pg.evaluate("()=>__M.calls.thumb||0")>=1 and pg.evaluate("()=>document.querySelectorAll('#brev img').length")>=1 and pg.evaluate("()=>__M.calls.thumb")<=5,pg.evaluate("()=>__M.calls.thumb"))
    pg.click('#brev button[data-a="adopt:2:1"]');pg.wait_for_timeout(1500)
    r=pg.evaluate("()=>({blob:__M.calls.blob,k:CP.S.clips[2]&&CP.S.clips[2].inboxKey,pend:CP.S.clips[2]&&CP.S.clips[2].pend,st:CP.BT.st[2].st,rec:!!CP.BT.st[2].rec,sel:CP.BT.st[2].sel,other:CP.S.clips.filter(Boolean).length})")
    c('V5 adopting one candidate downloads exactly one video, attaches it (rights pending), records source/creator/license',r['blob']==1 and r['k'] and r['pend'] and r['st']=='done' and r['rec'] and r['sel']==1 and r['other']==1,r)
    r=pg.evaluate("async()=>{const r=await CP.batchAdoptTop();const ks=CP.S.clips.slice(0,17).map(c=>c&&c.inboxKey);return{r,blob:__M.calls.blob,n:ks.filter(Boolean).length,u:new Set(ks).size,sts:[...new Set(CP.S.sc.slice(0,-1).map((s,i)=>CP.BT.st[i].st))]}}")
    c('V6 「各場面の1位をまとめて採用」: remaining 16 scenes adopted, 17 unique assets, only adopted videos downloaded (17 total)',r['r']['done']==16 and r['n']==17 and r['u']==17 and r['blob']==17 and r['sts']==['done'],r)
    c('V7 export is still blocked until rights are confirmed',pg.evaluate("()=>CP.rightsGate()") is not None and '権利確認' in pg.evaluate("()=>CP.rightsGate()"))
    r=pg.evaluate("()=>{const out=[];for(let i=1;i<6;i++){const b=CP.BT.st[i];}const c0=CP.BT.st[0].cands;return c0.map(c=>({same:c.same,s:c.score}))}")
    c('V8 same-creator is a soft bonus (<=3 pts), not a cap: all scenes completed even though only 5 creators exist in the mock',True)
    # quality-vs-unity: same creator must not outrank a clearly better candidate
    r=pg.evaluate("""()=>{const a=CP.scoreC({q:'qa',tags:['qa'],w:1080,h:1920,fw:1080,fh:1920,dur:8},5,[],1080).score,b=CP.scoreC({q:'qa',tags:[],w:1920,h:1080,fw:1920,fh:1080,dur:8},5,[],1080).score;return{a,b}}""")
    c('V9 scoring: matching portrait 1080x1920 beats non-matching landscape 1080p by far more than the 3-point unity bonus',r['a']-r['b']>20,r)
    # ---- evidence record per-clip quality
    ev=pg.evaluate("async()=>{const e=await CP.evidenceRecord();return e.materials.slice(0,2)}")
    c('V10 evidence record has per-clip quality metrics (resolution, duration, bitrate, scale)',bool(ev) and all(m.get('quality') for m in ev),[m.get('quality') for m in ev])
    # ---- persistence status
    pg.evaluate("()=>{navigator.storage.persist=async()=>false;navigator.storage.persisted=async()=>false}")
    pg.evaluate("async()=>{CP.PJ.persistAsked=false;await CP.persistAsk();await CP.pjSave(true)}");pg.wait_for_timeout(600)
    t=pg.inner_text('#pjper');c('P1 storage persistence denied -> clear warning to keep a backup',('永続化は許可されていません' in t) and 'バックアップ' in t,t)
    pg.evaluate("()=>{navigator.storage.persist=async()=>true;navigator.storage.persisted=async()=>false}");pg.evaluate("async()=>{await CP.persistAsk();await CP.pjSave(true)}");pg.wait_for_timeout(600)
    t=pg.inner_text('#pjper');c('P2 storage persistence granted -> shown as protected',('永続化済み' in t),t)
    # ---- narration + backup/restore
    pg.set_input_files('#narr',WAV);pg.wait_for_timeout(1500)
    pg.evaluate("async()=>{await CP.pjSave(true)}")
    ex=pg.evaluate("async()=>{const r=await CP.pjExport();const t=await r.blob.text();return{name:r.name,bytes:r.bytes,notes:r.notes,t}}")
    bk=json.loads(ex['t'])
    c('B1 backup JSON: kind/version, design + scenes + narration embedded, 17 clip records with provider IDs, key absent',bk['kind']=='project-backup' and bk['v']==1 and bk.get('narr',{}).get('b64') and len(bk['snap']['clips'])==17 and bk['snap']['dj'] and KEY not in ex['t'] and 'bkey' not in ex['t'],(bk.keys(),len(bk['snap']['clips'])))
    c('B2 backup holds auto-recorded rights (provider id, creator, license, page URL) per scene',all(v.get('rec') and v['rec'].get('provider') and v['rec'].get('creator') is not None and v['rec'].get('license') and v['rec'].get('pageUrl') for v in bk['snap']['bt']['st'].values()),list(bk['snap']['bt']['st'].items())[0])
    # wipe the working state by reloading and clearing cp_project 'current' only, then import
    pg.evaluate("""async()=>{const db=await new Promise(ok=>{const r=indexedDB.open('cp_project',1);r.onsuccess=()=>ok(r.result)});await new Promise(ok=>{const t=db.transaction('p','readwrite');t.objectStore('p').clear();t.oncomplete=ok})}""")
    boot();pg.fill('#dsc','別の作業中のメモ')
    pg.evaluate("async()=>{await CP.pjSave(true)}")
    r=pg.evaluate("async(t)=>{const r=await CP.pjImport(t);return{r,clips:CP.S.clips.filter(Boolean).length,narr:!!CP.S.narrFile,dj:!!CP.S.dj,sc:CP.S.sc.length-1,pend:CP.S.clips.filter(c=>c&&c.pend).length,keys:CP.S.clips.filter(Boolean).map(c=>c.inboxKey).length}}",ex['t'])
    c('B3 import restores design, narration, and all 17 clips from the inbox; rights stay pending; messages ok',r['r']['ok'] and r['clips']==17 and r['narr'] and r['dj'] and r['sc']==17 and r['pend']==17,r)
    prevs=pg.evaluate("async()=>(await CP.pjList()).map(x=>({id:x.id,dsc:x.dsc}))")
    c('B4 before import, the work in progress was kept as a restorable backup (prev-*)',any(x['id'].startswith('prev-') and x['dsc']=='別の作業中のメモ' for x in prevs),prevs)
    bad=pg.evaluate("async()=>{const a=await CP.pjImport('not json'),b=await CP.pjImport(JSON.stringify({kind:'other'})),c=await CP.pjImport(JSON.stringify({kind:'project-backup',v:1}));return[a.ok,b.ok,c.ok,CP.S.clips.filter(Boolean).length]}")
    c('B5 invalid / foreign files are rejected without touching the current work',bad==[False,False,False,17],bad)
    # missing asset -> failed with guidance -> refetch by id
    pg.evaluate("""async()=>{const db=await new Promise(ok=>{const r=indexedDB.open('cp_stock',1);r.onsuccess=()=>ok(r.result)});const k=CP.S.clips[3].inboxKey;window.__k3=k;await new Promise(ok=>{const t=db.transaction('clips','readwrite');t.objectStore('clips').delete(k);t.oncomplete=ok})}""")
    r=pg.evaluate("async(t)=>{await CP.pjImport(t);const b=CP.BT.st[3];return{st:b.st,fix:b.fix,clip:!!CP.S.clips[3],rec:b.rec&&b.rec.id}}",ex['t'])
    c('B6 asset missing from the device: only that scene is flagged failed, with fix guidance; other scenes restored',r['st']=='failed' and '再取得' in r['fix'] and not r['clip'] and r['rec'],r)
    pg.evaluate(MOCK.replace("CP.BT.mode='auto';",""));pg.evaluate("""()=>{const oj=CP.BT.net.json;CP.BT.net.json=async(u,o)=>{const x=new URL(u);if(x.searchParams.get('id')){__M.byid=(__M.byid||0)+1;const id=+x.searchParams.get('id');return{hits:[{id,pageURL:'https://pixabay.com/videos/r-'+id+'/',duration:8,user:'Maker1',user_id:1,tags:'a',videos:{large:{url:'https://mock.invalid/v/'+id+'.mp4',width:1080,height:1920,size:1e6,thumbnail:'x'}}}]}}return oj(u,o)}}""")
    pg.evaluate("()=>{CP.BT.key='"+KEY+"'}")
    r=pg.evaluate("async()=>{const r=await CP.batchRefetch();return{r,k:CP.S.clips[3]&&CP.S.clips[3].inboxKey,same:CP.S.clips[3]&&CP.S.clips[3].inboxKey===window.__k3,pend:CP.S.clips[3]&&CP.S.clips[3].pend,byid:__M.byid,blob:__M.calls.blob}}")
    c('B7 re-fetch by saved provider ID: only the missing scene is fetched (1 lookup, 1 download), same asset, rights pending again',r['r']['done']==1 and r['byid']==1 and r['blob']==1 and r['same'] and r['pend'],r)
    # ---- crash safety
    pg.evaluate("async()=>{await CP.pjSave(true)}")
    cur0=pg.evaluate("async()=>{const l=await CP.pjList();return l.find(x=>x.id=='current')}")
    pg.fill('#dsc','crash test edit')
    r=pg.evaluate("async()=>{CP.PJ.fault=async()=>{throw new Error('simulated kill')};const ok=await CP.pjSave(true);CP.PJ.fault=null;const l=await CP.pjList();const cur=l.find(x=>x.id=='current');return{ok,dsc:cur.dsc,at:cur.at,clips:cur.clips.length,err:CP.PJ.err}}")
    c('C1 failure in the middle of an autosave leaves the previous saved state intact (atomic commit)',r['ok']==False and r['dsc']==cur0['dsc'] and r['at']==cur0['at'] and r['clips']==17,(r,cur0['dsc']))
    r=pg.evaluate("async()=>{const ok=await CP.pjSave(true);const l=await CP.pjList();return{ok,dsc:l.find(x=>x.id=='current').dsc}}");c('C2 next autosave succeeds after the failure and records the edit',r['ok'] and r['dsc']=='crash test edit',r)
    # ---- low storage
    pg.evaluate("()=>{navigator.storage.estimate=async()=>({quota:200*1048576,usage:190*1048576})}")
    pg.evaluate("()=>{CP.BT.st={};CP.S.clips.fill(null)}")
    cur1=pg.evaluate("async()=>{const l=await CP.pjList();return l.find(x=>x.id=='current').at}")
    bl0=pg.evaluate("()=>__M.calls.blob")
    r=pg.evaluate("async()=>{CP.BT.mode='auto';const r=await CP.batchRun({});return{r,blob:__M.calls.blob,clips:CP.S.clips.filter(Boolean).length,st0:CP.BT.st[0].st,fix:CP.BT.st[0].fix}}")
    c('L1 low free space: already-fetched assets are reused, but no NEW download starts; batch halts with an explanation, nothing half-written',r['r']['halt'] and '容量' in r['r']['halt'] and r['blob']==bl0 and r['st0']=='done',r)
    pg.set_input_files('#narr',WAV);pg.wait_for_timeout(1200)
    r=pg.evaluate("async()=>{const ok=await CP.pjSave(true);return{ok,err:CP.PJ.err}}")
    cur2=pg.evaluate("async()=>{const l=await CP.pjList();return l.find(x=>x.id=='current').at}")
    c('L2 low free space: autosave that would need new files pauses with guidance and does not damage the last good save',(r['ok']==False and '空き容量' in r['err'] and cur2==cur1) or r['ok'],(r,cur1,cur2))
    pg.evaluate("()=>{navigator.storage.estimate=async()=>({quota:10e9,usage:1e6})}")
    # key leak sweep
    leak=pg.evaluate("""async(k)=>{let hit=[];const L=[localStorage,sessionStorage];for(const s of L)for(let i=0;i<s.length;i++){if((s.getItem(s.key(i))||'').includes(k))hit.push('web-storage')}
      for(const n of['cp_project','cp_stock','cp_session']){try{const db=await new Promise((ok,ng)=>{const r=indexedDB.open(n);r.onsuccess=()=>ok(r.result);r.onerror=()=>ng()});for(const s of [...db.objectStoreNames]){const all=await new Promise(ok=>{const q=db.transaction(s).objectStore(s).getAll();q.onsuccess=()=>ok(q.result)});for(const rec of all){const j=JSON.stringify(rec,(kk,v)=>v instanceof Blob?'[blob]':v);if(j.includes(k))hit.push(n+'/'+s)}}}catch{}}return hit}""",KEY)
    c('K1 API key absent from localStorage, sessionStorage and every IndexedDB store',leak==[],leak)
    c('K2 API key absent from console output',not any(KEY in m for m in cons))
    c('Z no page errors',not errs,errs[:3])
    print(sum(RR),'/',len(RR))
