import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tam2.py").read().split("\nwith sync_playwright()")[0])
import subprocess
D4=json.loads(json.dumps(base));sc4=[]
for k in range(4):
    t=json.loads(json.dumps(T[min(k,len(T)-1)]));t['text']='場面%d。変わるのが、怖いか。'%(k+1);t['dur']=3.75
    t['role']='hook' if k==0 else ('ending' if k==3 else t['role']);t['search']={'queries':['qa%da'%k,'qb%db'%k],'avoid':['logo'],'minHeight':1080};sc4.append(t)
D4['scenes']=sc4;D4['script']=''.join(s['text'] for s in sc4);D4J=json.dumps(D4,ensure_ascii=False)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));cons=[];pg.on('console',lambda m:cons.append(m.text))
    REQ={'api':[],'cdn':[],'other':[]}
    import urllib.parse as up
    def h_api(route,req):
        REQ['api'].append(req.url);q=up.parse_qs(up.urlparse(req.url).query);hits=mkhits(q.get('q',['x'])[0])
        route.fulfill(status=200,body=json.dumps({'total':len(hits),'hits':hits}),content_type='application/json',headers={'access-control-allow-origin':'*'})
    def h_cdn(route,req):
        REQ['cdn'].append(req.url)
        if req.url.endswith('.jpg'):return route.fulfill(status=200,body=b'',content_type='image/png',headers={'access-control-allow-origin':'*'})
        route.fulfill(status=200,body=MP4,content_type='video/mp4',headers={'access-control-allow-origin':'*'})
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://cdn.pixabay.com/**',h_cdn)
    ctx.route('https://example.com/**',lambda r,q:(REQ['other'].append(q.url),r.fulfill(status=200,body='x')))
    pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    # T1 quota / epoch
    lim=pg.evaluate("()=>({s:CP.REAL.lim.s,d:CP.REAL.lim.d,cnt:CP.realCnt(),ep:CP.rlogGet().filter(x=>x.step==='epoch').length,b:CP.CP_BUILD})")
    c('A1 trial quota is search 5 / video 6, counters start at 0, the new quota generation is logged once',lim['s']==5 and lim['d']==6 and lim['cnt']=={'s':0,'d':0,'t':0} and lim['ep']==1 and __import__('re').search(r'r\d+-(am|b0)',lim['b']) is not None,lim)
    pg.reload();ready(pg);pg.wait_for_timeout(300)
    c('A1b reload does not log the generation again and does not reset counters',pg.evaluate("()=>CP.rlogGet().filter(x=>x.step==='epoch').length")==1)
    # import design
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
    n=pg.evaluate("()=>CP.S.sc.length-1");c('A2 4-scene 15s design imported',n==4,n)
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.check('#breal')
    # T4 preflight refuses when quota is short (no comm)
    pg.evaluate("()=>{CP.BT.lib=false;localStorage.setItem(CP.REAL.LS,JSON.stringify({s:3,d:0,t:0}))}")
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.batchRun({})}")
    c('A3 preflight: 4 scenes need 4 searches but only 2 remain -> nothing is sent, clear message, scenes untouched',len(REQ['api'])==0 and r['ok']==False and '通信枠が足りません' in r['halt'] and pg.evaluate("()=>CP.BT.st[0]&&CP.BT.st[0].st")in(None,'pending'),(r,len(REQ['api'])))
    pg.evaluate("()=>{CP.BT.lib=true;localStorage.setItem(CP.REAL.LS,JSON.stringify({s:0,d:0,t:0}))}")
    # T2 one-button auto
    t0=time.time();r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.autoMaterial()}");dt=time.time()-t0
    st=pg.evaluate("()=>CP.S.sc.slice(0,-1).map((s,i)=>({st:CP.BT.st[i].st,by:CP.S.clips[i]&&CP.S.clips[i].meta.by,url:CP.S.clips[i]&&CP.S.clips[i].meta.url,lic:CP.S.clips[i]&&CP.S.clips[i].meta.lic,pend:CP.S.clips[i]&&CP.S.clips[i].pend,rec:CP.BT.st[i].rec&&CP.BT.st[i].rec.id,credit:CP.BT.st[i].rec&&CP.BT.st[i].rec.credit}))")
    cnt=pg.evaluate("()=>CP.realCnt()")
    print('auto seconds',round(dt,1),{k:v for k,v in r.items() if k not in('r1','r2')})
    c('A4 one button: all 4 scenes get a clip with creator/URL/license/credit recorded automatically (no typing)',all(x['st']=='done' and x['by'] and x['url'] and x['lic'] and x['credit'] for x in st),st)
    c('A5 communications: exactly 4 searches (1 per scene although 2 queries each) and 4 video downloads; counters 4/5 and 4/6',len(REQ['api'])==4 and len([u for u in REQ['cdn'] if u.endswith('.mp4')])==4 and cnt['s']==4 and cnt['d']==4,(len(REQ['api']),REQ['cdn'],cnt))
    c('A6 no communication outside pixabay.com / cdn.pixabay.com',REQ['other']==[])
    c('A7 distinct assets per scene; rights are left pending for the owner confirmation (not auto-confirmed)',len({x['rec'] for x in st})==4 and all(x['pend'] for x in st),st)
    bst=pg.inner_text('#bst')
    c('A8 summary line: counts of searches/downloads/remaining and states that quality self-assessment is not done',('検索 4回' in bst) and ('動画 4本' in bst) and '映像品質の自己評価は行っていません' in bst,bst)
    c('A9 key never in the page text',KEY not in pg.inner_text('body') and not any(KEY in m for m in cons))
    # T3 reuse from the device library with zero communication
    nA,nC=len(REQ['api']),len(REQ['cdn'])
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.autoMaterial()}")
    st2=pg.evaluate("()=>CP.S.sc.slice(0,-1).map((s,i)=>({st:CP.BT.st[i].st,msg:CP.BT.st[i].msg}))")
    c('A10 re-making the same work reuses stored assets: 0 new searches, 0 new downloads, counters unchanged',len(REQ['api'])==nA and len(REQ['cdn'])==nC and pg.evaluate("()=>CP.realCnt()")==cnt and all(x['st']=='done' and '再利用' in x['msg'] for x in st2),(len(REQ['api'])-nA,len(REQ['cdn'])-nC,st2))
    # T5 candidate review text + download preflight
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
    pg.evaluate("()=>{CP.BT.lib=false;CP.BT.mode='review';localStorage.setItem(CP.REAL.LS,JSON.stringify({s:0,d:5,t:0}))}");nC=len(REQ['cdn'])
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.batchRun({})}")
    txt=pg.inner_text('#brev')
    c('A11 candidates are labelled as a proposal score from search words/length/size, not video quality',('提案点' in txt) and ('映像品質の評価ではありません' in txt),txt[:300])
    r2=pg.evaluate("async()=>await CP.batchAdoptTop()")
    c('A12 download preflight: 4 downloads needed but 1 remains -> nothing downloaded, message shown',len(REQ['cdn'])==nC and r2['ok']==False and '通信枠が足りません' in r2['halt'],(r2,len(REQ['cdn'])-nC))
    # T6 auto crop
    pg.evaluate("()=>{CP.BT.lib=true;CP.BT.mode='review'}")
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
    clip(pg,0,(FIX+'/cropfx/right.mp4'));clip(pg,1,(FIX+'/cropfx/center.mp4'));clip(pg,2,(FIX+'/cropfx/right.mp4'))
    q0=pg.evaluate("async()=>{const q=await CP.autoCropClip(0);return q&&{sx:q.sx,auto:q.auto}}")
    q1=pg.evaluate("async()=>await CP.autoCropClip(1)")
    pg.evaluate("()=>CP.cropSet(2,{sx:.2})");q2=pg.evaluate("async()=>await CP.autoCropClip(2)")
    c('A13 auto crop: subject on the right of a landscape clip -> crop follows it (sx about 0.8), flagged auto',q0 is not None and 0.7<q0['sx']<0.86 and q0['auto'],q0)
    c('A14 auto crop: centered subject -> no change (center crop as before)',q1 is None and pg.evaluate("()=>CP.S.crop[1]")is None,q1)
    c('A15 auto crop never overwrites a manual crop',q2 is None and abs(pg.evaluate("()=>CP.S.crop[2].sx")-.2)<1e-6)
    pg.evaluate("()=>CP.btRender()");c('A16 one-tap return to center is available for auto-estimated scenes only',pg.evaluate("()=>[...document.querySelectorAll('#brev button[data-a^=crop0]')].map(b=>b.disabled)")[:3]==[False,True,True])
    pg.click('#brev button[data-a="crop0:0"]');c('A17 returning to center removes the crop',pg.evaluate("()=>CP.S.crop[0]")is None)
    # production summary
    ps=pg.evaluate("()=>CP.prodSummary()")
    c('A18 production summary: manual taps counted, auto-material time measured',ps['manualTaps']>0 and ps['autoMaterialSec'] is not None,ps)
    c('A19 no page errors',errs==[],errs)
    print(sum(RR),'/',len(RR))
