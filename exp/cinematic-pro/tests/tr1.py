import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tab1.py").read().split("\nwith sync_playwright()")[0])
import base64
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
def mkctx(b,w=412,h=915):
    ctx=b.new_context(viewport={'width':w,'height':h});pg=ctx.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));pg.cons=[];pg.on('console',lambda m:pg.cons.append(m.type+': '+m.text))
    pg.REQ={'api':[],'cdn':[]}
    def h_api(route,req):
        pg.REQ['api'].append(req.url);q=up.parse_qs(up.urlparse(req.url).query);hits=mkhits(q.get('q',['x'])[0])
        for h in hits:
            for k in h.get('videos',{}).values():k['thumbnail']='https://cdn.pixabay.com/t/'+str(h['id'])+'.jpg'
        route.fulfill(status=200,body=json.dumps({'total':len(hits),'hits':hits}),content_type='application/json',headers={'access-control-allow-origin':'*'})
    def h_cdn(route,req):
        pg.REQ['cdn'].append(req.url)
        if req.url.endswith('.jpg'):return route.fulfill(status=200,body=PNG,content_type='image/png',headers={'access-control-allow-origin':'*'})
        route.fulfill(status=200,body=MP4,content_type='video/mp4',headers={'access-control-allow-origin':'*'})
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://cdn.pixabay.com/**',h_cdn)
    return ctx,pg
import urllib.parse as up
D4J=open((REPO+'/exp/design/price-of-staying.design.json'),encoding='utf-8').read()
def st(pg):return pg.evaluate("()=>({nst:document.getElementById('nst').textContent.slice(0,110),mock:CP.S.isMockNarr,narr:!!CP.S.narr,files:document.getElementById('narr').files.length,fname:(document.getElementById('narr').files[0]||{}).name||null,voicest:document.getElementById('voicest').textContent.slice(0,70)})")
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    # S1 WAV basic
    ctx,pg=mkctx(b);pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(400)
    pg.set_input_files('#narr',(FIX+'/wavfx/n48m.wav'));pg.wait_for_timeout(1500);print('S1a WAV48 mono',st(pg))
    pg.click('#bVo');pg.wait_for_timeout(500);print('S1b 原音を試聴',st(pg)['voicest'])
    pg.click('#bVb');pg.wait_for_timeout(1500);print('S1c βを試聴',st(pg)['voicest'])
    # S2 design import after WAV
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900);print('S2a 設計JSON反映後',st(pg))
    pg.click('#bVo');pg.wait_for_timeout(500);print('S2b その後の試聴',st(pg)['voicest'])
    # S4 mock after WAV (input still shows file)
    pg.set_input_files('#narr',(FIX+'/wavfx/n441s.wav'));pg.wait_for_timeout(1500);print('S4a WAV44.1 stereo',st(pg))
    pg.click('#bMock');pg.wait_for_timeout(1500);print('S4b 模擬ボタン後',st(pg))
    # S3 persistence: mock then WAV then reload+restore
    ctx2,pg2=mkctx(b);pg2.goto(BASE+'#res=360');pg2.evaluate("()=>{try{localStorage.clear()}catch{}}");pg2.reload();ready(pg2);pg2.wait_for_timeout(400)
    pg2.click('#bMock');pg2.wait_for_timeout(1500);pg2.set_input_files('#narr',(FIX+'/wavfx/n48m.wav'));pg2.wait_for_timeout(7000);print('S3a mock→WAV',st(pg2))
    pg2.reload();ready(pg2);pg2.wait_for_timeout(1500);vis=pg2.evaluate("()=>!document.getElementById('pjbar').hidden");print('S3b reload banner',vis,st(pg2))
    if vis:
        pg2.click('#pjgo');pg2.wait_for_timeout(3000);print('S3c restored',st(pg2))
    # S5 overflow
    for (w,h) in ((360,740),(412,915)):
        ctx3,pg3=mkctx(b,w,h);pg3.goto(BASE+'#res=360');pg3.evaluate("()=>{try{localStorage.clear()}catch{}}");pg3.reload();ready(pg3);pg3.wait_for_timeout(400)
        pg3.fill('#dj',D4J);pg3.click('#bDJ');pg3.wait_for_timeout(800)
        pg3.evaluate("()=>{document.querySelectorAll('details').forEach(d=>d.open=true)}")
        r=pg3.evaluate("""()=>{const W=innerWidth,out=[];for(const e of document.querySelectorAll('body *')){const r=e.getBoundingClientRect();if(!r.width||!r.height)continue;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;if(r.right>W+1)out.push((e.tagName+(e.id?'#'+e.id:'')+(e.className?'.'+String(e.className).slice(0,20):'')+' right='+Math.round(r.right)+' w='+Math.round(r.width)+' '+(e.textContent||'').trim().slice(0,28)))}
          return{docW:document.documentElement.scrollWidth,W,n:out.length,top:out.slice(0,8),height:document.documentElement.scrollHeight,buttons:document.querySelectorAll('button').length,visBtn:[...document.querySelectorAll('button')].filter(x=>x.offsetParent).length}}""")
        print('S5 overflow',w,r)
    # S6 thumbs (real transport mocks) 
    ctx4,pg4=mkctx(b);pg4.goto(BASE+'#res=360');pg4.evaluate("()=>{try{localStorage.clear()}catch{}}");pg4.reload();ready(pg4);pg4.wait_for_timeout(400)
    pg4.fill('#dj',D4J);pg4.click('#bDJ');pg4.wait_for_timeout(800)
    pg4.evaluate("()=>{document.getElementById('rt').open=true}");pg4.fill('#bkey',KEY);pg4.check('#breal')
    pg4.evaluate("async()=>{CP.BT.mode='review';CP.BT.key=document.getElementById('bkey').value;await CP.batchRun({})}")
    n=pg4.locator('#brev button[data-a^=thumb]').count();print('S6a thumb buttons',n,'cdn before',len(pg4.REQ['cdn']))
    try:
        pg4.locator('#brev button[data-a^=thumb]').first.click(timeout=4000);print('S6b click ok')
    except Exception as e:print('S6b click FAIL',str(e)[:160])
    pg4.wait_for_timeout(1200);print('S6c after click cdn',len(pg4.REQ['cdn']),'thumbs',pg4.evaluate("()=>Object.keys(CP.BT.th).length"),'bst:',pg4.inner_text('#bst')[:160],'| bnote:',pg4.inner_text('#bnote')[:160])
    # S6d non-real transport
    ctx5,pg5=mkctx(b);pg5.goto(BASE+'#res=360');pg5.evaluate("()=>{try{localStorage.clear()}catch{}}");pg5.reload();ready(pg5);pg5.wait_for_timeout(400)
    pg5.fill('#dj',D4J);pg5.click('#bDJ');pg5.wait_for_timeout(800)
    pg5.evaluate("async()=>{CP.BT.mode='review';await CP.batchRun({})}")
    print('S6d non-real: thumb buttons',pg5.locator('#brev button[data-a^=thumb]').count(),'bst:',pg5.inner_text('#bst')[:120])
    print('errors',pg.errs,pg2.errs,pg4.errs);print([c for c in pg.cons if 'error' in c][:5])
