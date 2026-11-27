exec(open("tam.py").read().split("\nwith sync_playwright()")[0])
import shutil
SRC='/home/claude/become-studio/exp/cinematic-pro/index.html';TMP='/home/claude/become-studio/exp/cinematic-pro/_nstest.html'
t=open(SRC,encoding='utf-8').read().replace('<meta name="robots"','<meta name="cp-ns" content="t_"><meta name="robots"',1);open(TMP,'w',encoding='utf-8').write(t)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.expose_function('mockBlob',mockblob)
    pg.goto(BASE+'#res=360');pg.reload();ready(pg);pg.wait_for_timeout(500)
    pv=pg.evaluate("""()=>({
     f:CP.pickVar({large:{url:'u',width:3840,height:2160,size:70e6},medium:{url:'u',width:1920,height:1080,size:20e6}}).n,
     g:CP.pickVar({large:{url:'u',width:1080,height:1920,size:90e6},medium:{url:'u',width:720,height:1280,size:9e6}}).n,
     h:CP.pickVar({large:{url:'u',width:1080,height:1920,size:30e6},medium:{url:'u',width:720,height:1280,size:9e6}}).n})""")
    c('Q1 default version ignores any fixed size cap: 90MB 1080x1920 is kept over 720p; 4K landscape (height 2160) is sufficient without upscale',pv=={'f':'large','g':'large','h':'large'},pv)
    VARS="""[{n:'large',w:1080,h:1920,size:90e6,url:'https://cdn.pixabay.com/L.mp4',thumb:''},{n:'medium',w:720,h:1280,size:30e6,url:'https://cdn.pixabay.com/M.mp4',thumb:''},{n:'small',w:540,h:960,size:9e6,url:'https://cdn.pixabay.com/S.mp4',thumb:''}]"""
    def run(free_mb,tiers=None,mem=None,down=False):
        js="""async()=>{const MB=1048576;navigator.storage.estimate=async()=>({quota:(%d+100)*MB,usage:100*MB});
          const T=%s;Object.defineProperty(navigator,'mediaCapabilities',{configurable:true,value:{decodingInfo:async(o)=>{const k=T?T[o.video.height]:undefined;if(k===undefined)return{supported:true,smooth:true,powerEfficient:true};return k}}});
          Object.defineProperty(navigator,'deviceMemory',{value:%s,configurable:true});
          const c={dur:8,vars:%s,file:'x',w:1,h:1,allowDown:%s};try{const r=await CP.chooseVariant(c);return{n:c.vname,reason:c.reason||c.vreason,h:c.fh}}catch(e){return{err:e.code,alt:e.alt}}}"""%(free_mb,json.dumps(tiers) if tiers else 'null',mem if mem else 'undefined',VARS,'true' if down else 'false')
        return pg.evaluate(js)
    r=run(5000);c('Q2 plenty of space & smooth decode: highest sufficient quality chosen even at 90MB (no 40MB exclusion)',r['n']=='large' and r['h']==1920,r)
    r=run(380);c('Q3 free 380MB (budget 40MB): the 90MB target is NOT silently downgraded -> stops with DOWNGRADE and names the alternative',r.get('err')=='DOWNGRADE' and r.get('alt')=='720×1280',r)
    r=run(380,down=True);c('Q3b same case after the owner confirms: 720x1280 taken and the reason records the approval',r['n']=='medium' and '承認済み' in r['reason'],r)
    r=run(5000,{'1920':{'supported':True,'smooth':False,'powerEfficient':False}});c('Q4 preview may stutter (not smooth): quality is kept, only a note is added (no downgrade)',r['n']=='large' and 'なめらか' in r['reason'],r)
    r=run(5000,{'1920':{'supported':False,'smooth':False,'powerEfficient':False},'1280':{'supported':False,'smooth':False,'powerEfficient':False}});c('Q5 target not decodable on this device: stops with DOWNGRADE (no silent change)',r.get('err')=='DOWNGRADE',r)
    r=run(5000,{'1920':{'supported':False,'smooth':False,'powerEfficient':False},'1280':{'supported':False,'smooth':False,'powerEfficient':False}},down=True);c('Q5b after confirmation: the smallest decodable version',r['n']=='small',r)
    r=run(310);c('Q6 almost no free space (310MB): no version fits -> NOSTORAGE',r.get('err')=='NOSTORAGE',r)
    # integration through the review UI (mock transport)
    pg.goto(BASE+'#res=360');ready(pg);pg.wait_for_timeout(500);pg.fill('#dj',D17J);pg.click('#bDJ');pg.wait_for_timeout(800)
    pg.expose_function('mockBlob',mockblob) if False else None
    pg.evaluate(MOCK.replace("CP.BT.mode='auto';",""));pg.fill('#bkey',KEY)
    pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;await CP.batchRun({})}")
    pg.evaluate("""()=>{const c=CP.BT.st[0].cands[0];c.vars=[{n:'large',w:1080,h:1920,size:90e6,url:'https://mock.invalid/v/5.mp4',thumb:''},{n:'medium',w:720,h:1280,size:30e6,url:'https://mock.invalid/v/6.mp4',thumb:''}];c.file=c.vars[0].url;c.fh=1920;c.fw=1080;c.dur=8;CP.BT.st[0].cands[0]=c;navigator.storage.estimate=async()=>({quota:480*1048576,usage:100*1048576})}""")
    r=pg.evaluate("async()=>{const r=await CP.batchAdopt(0,0);return{r,blob:__M.calls.blob,clip:!!CP.S.clips[0],down:CP.BT.st[0].down,st:CP.BT.st[0].st}}")
    c('Q7 adopt with insufficient space: no download, scene stays a candidate, owner is told and offered the explicit button',r['blob']==0 and not r['clip'] and r['down']==0 and not r['r']['ok'],r)
    pg.evaluate("()=>{document.querySelectorAll('#brev details')[0].open=true}")
    c('Q8 the confirm button is shown only for that candidate',pg.evaluate("()=>document.querySelectorAll('#brev button[data-a=\"adoptdown:0:0\"]').length")==1)
    r=pg.evaluate("async()=>{const r=await CP.batchAdopt(0,0,true);return{r,blob:__M.calls.blob,rec:CP.BT.st[0].rec&&CP.BT.st[0].rec.variant}}")
    c('Q9 after confirmation: one download, the record keeps the target/actual versions and the approval note',r['blob']==1 and r['rec'] and '承認済み' in r['rec']['reason'],r)
    pg.evaluate("()=>{navigator.storage.estimate=async()=>({quota:10e9,usage:1e6})}")
    # NS page
    pg.goto('http://localhost:8765/exp/cinematic-pro/_nstest.html#res=360');ready(pg);pg.wait_for_timeout(500)
    pg.evaluate("()=>{try{localStorage.clear()}catch{}}")
    pg.fill('#dsc','namespaced work');pg.evaluate("async()=>{await CP.pjSave(true);localStorage.setItem(CP.NS+'cp_realcnt','{}')}");pg.wait_for_timeout(800)
    dbs=pg.evaluate("async()=>(await indexedDB.databases()).map(d=>d.name)")
    c('N1 test page with namespace uses t_-prefixed databases only (cp_project not created at this origin by the test page)',CPNS:=True and any(d=='t_cp_project' for d in dbs) and not any(d.startswith('cp_') for d in dbs) and pg.evaluate("()=>CP.NS")=='t_',dbs)
    c('N2 localStorage keys are namespaced too',all(not k.startswith('cp_') for k in pg.evaluate("()=>Object.keys(localStorage)")),pg.evaluate("()=>Object.keys(localStorage)"))
    # production-like page: data in unprefixed DB stays untouched by test page and vice versa
    pg.goto(BASE+'#res=360');ready(pg);pg.wait_for_timeout(500)
    l=pg.evaluate("async()=>(await CP.pjList()).filter(x=>x.dsc=='namespaced work').length");c('N3 the unprefixed (production-style) page does not see the test page\'s saved work',l==0,l)
    c('N4 referrer and robots meta present (key never sent as referrer; page not indexed)',pg.evaluate("()=>!!document.querySelector('meta[name=referrer][content=no-referrer]')&&!!document.querySelector('meta[name=robots][content*=noindex]')"))
    c('Z no page errors',not errs,errs[:3]);print(sum(RR),'/',len(RR))
import os;os.remove(TMP)
