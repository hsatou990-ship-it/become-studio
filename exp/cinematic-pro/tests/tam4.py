exec(open("tam.py").read().split("\nwith sync_playwright()")[0])
import urllib.parse as up
MP4=open(FX+'fx0.mp4','rb').read()
def hits(q):
    h=0
    for ch in q:h=(h*31+ord(ch))&0xffffffff
    return [{'id':(h%100000)*10+k,'pageURL':'https://pixabay.com/videos/x-%d/'%k,'duration':8,'user':'Maker%d'%k,'user_id':7,'tags':'a, '+q,'videos':{'large':{'url':'https://cdn.pixabay.com/video/a/%d.mp4'%k,'width':1080,'height':1920,'size':9000000,'thumbnail':'https://cdn.pixabay.com/video/a/t.jpg'}}} for k in range(3)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));cons=[];pg.on('console',lambda m:cons.append(m.text))
    REQ=[];M={'m':'ok'};HELD=[]
    OKH={'access-control-allow-origin':'*'}
    def ok(route,q='sunrise'):
        route.fulfill(status=200,body=json.dumps({'hits':hits(q)}),content_type='application/json',headers=OKH)
    def h_api(route,req):
        REQ.append(req.url);m=M['m']
        if m=='ok':return ok(route)
        if m=='abort':return route.abort('failed')
        if m=='400':return route.fulfill(status=400,body='[ERROR 400] Invalid key '+KEY,content_type='text/plain',headers=OKH)
        if m=='html':return route.fulfill(status=200,body='<html><title>Just a moment...</title></html>',content_type='text/html',headers=OKH)
        if m=='redir':return route.fulfill(status=302,headers={'location':'https://www.pixabay.com/api/videos/?x=1'})
        if m=='hold':HELD.append(route);return
        if m=='hang':return
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://www.pixabay.com/**',lambda r,q:r.fulfill(status=200,body='{}'))
    ctx.route('https://cdn.pixabay.com/**',lambda r,q:r.fulfill(status=200,body=MP4,content_type='video/mp4',headers=OKH))
    def fresh():
        pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.evaluate("()=>{CP.REAL.lim.s=1;CP.REAL.lim.d=1}");pg.wait_for_timeout(300)
        pg.evaluate("()=>{document.getElementById('rt').open=true;document.querySelectorAll('#rt details').forEach(d=>d.open=true)}");pg.fill('#bkey',KEY);pg.check('#breal');REQ.clear();HELD.clear()
    def done():pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=20000);pg.wait_for_timeout(150)
    out=lambda:pg.inner_text('#rOut');badge=lambda:pg.inner_text('#rBadge')
    # D1 double tap while the first request is still in flight
    fresh();M['m']='hold';pg.click('#rS');pg.wait_for_timeout(300)
    b1=badge();dis=pg.evaluate("()=>document.getElementById('rS').disabled&&document.getElementById('rD').disabled")
    pg.evaluate("()=>document.getElementById('rS').click()");pg.wait_for_timeout(300)
    c('D1 double tap: only ONE request, the button is disabled and the screen says 検索中 with elapsed seconds',len(REQ)==1 and len(HELD)==1 and dis and '⏳' in b1 and '検索中' in b1 and '秒' in b1,(len(REQ),b1,dis))
    ok(HELD[0],'sunrise mountain');done()
    c('D2 after the held request completes: success is shown clearly, counter 1/1, log has exactly one sent entry marked success',badge().startswith('✅') and pg.evaluate("()=>CP.realCnt().s")==1 and [e['state'] for e in json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch').filter(e=>e.sent))"))]==['ok'],(badge(),))
    # D3 first failure must not be overwritten by a later blocked tap
    fresh();M['m']='abort';pg.click('#rS');done();f1=badge();o1=out()
    pg.click('#rS');done();o2=out();f2=badge()
    lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    c('D3 first search fails (network): shown as 失敗; a second tap sends NOTHING (quota used) and does not overwrite the first result',len(REQ)==1 and f1.startswith('❌') and '結果: 失敗' in o2 and '通信は行いませんでした' in o2 and f2.startswith('⛔'),(f1,f2,len(REQ)))
    c('D4 log keeps both events: #1 sent/fail/NETFAIL, #2 not sent/blocked/LIMIT; counted before sending, limit checked before counting',lg[0]['sent'] and lg[0]['state']=='fail' and lg[0]['code']=='NETFAIL' and (not lg[1]['sent']) and lg[1]['state']=='blocked' and lg[1]['code']=='LIMIT',lg)
    c('D5 the diagnosis block names what could and could not be separated (key / HTTP / CORS / quota)','APIキー:' in o2 and 'HTTP応答:' in o2 and 'CORS:' in o2 and '通信制限:' in o2 and '区別不可' in o2,o2[:900])
    # D6 HTTP 400 with the key echoed in the body
    fresh();M['m']='400';pg.click('#rS');done();o=out();lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    c('D6 HTTP 400: status and response text recorded, key redacted, classified as possible invalid key, CORS reported readable',lg[0]['status']==400 and '[KEY]' in lg[0]['body'] and KEY not in json.dumps(lg) and KEY not in o and '無効、または未指定' in o and '許可されている' in o,(lg,o[:500]))
    # D7 200 but not JSON (interstitial)
    fresh();M['m']='html';pg.click('#rS');done();lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    c('D7 HTTP 200 with a non-JSON page is BADJSON (not mislabeled as a network failure)',lg[0]['code']=='BADJSON' and lg[0]['status']==200,lg)
    # D8 redirect to a non-approved host -> CSP
    fresh();M['m']='redir';pg.click('#rS');done();lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"));o=out()
    c('D8 redirect to a non-approved host is stopped by the CSP and identified as such (directive named; redirect target host is not exposed by browsers)',lg[0]['code']=='CSP' and any(x['d']=='connect-src' for x in lg[0].get('csp',[])) and 'CSP' in o,(lg,badge()))
    # D9 reset flow
    fresh();M['m']='abort';pg.click('#rS');done();M['m']='ok'
    pg.fill('#rRc','はい');pg.click('#rRs');c('D9 reset needs the confirmation word: without it the quota is untouched',pg.evaluate("()=>CP.realCnt().s")==1)
    pg.fill('#rRc','承認済み');pg.click('#rRs');pg.wait_for_timeout(200)
    c('D10 reset with the word: quota back to 0, reset count 1 shown in the result, reset is logged',pg.evaluate("()=>CP.realCnt().s")==0 and pg.evaluate("()=>CP.rrstGet().s")==1 and '枠の再設定: 検索 1回' in out() and any(e['state']=='reset' for e in json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))))
    n0=len(REQ);pg.click('#rS');done();c('D11 after the reset one new search is sent and succeeds (total sent entries = 2, resets = 1, auditable)',len(REQ)==n0+1 and badge().startswith('✅') and len([e for e in json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))")) if e['sent']])==2)
    # D12 log survives a reload, even for a request that never finished
    fresh();M['m']='hang';pg.click('#rS');pg.wait_for_timeout(500);pg.reload();ready(pg);pg.wait_for_timeout(300)
    lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    pg.evaluate("()=>{document.getElementById('rt').open=true;CP.RT.note=''}");txt=pg.evaluate("()=>CP.rtText()")
    c('D12 a search interrupted by closing/reloading the page leaves a persistent 未完了 log entry (counted, never silently lost)',len(lg)==1 and lg[0]['state']=='start' and lg[0]['sent'] and '未完了' in txt,lg)
    # D13 key never in logs/storage/console
    leak=pg.evaluate("(k)=>{const o=[];for(let i=0;i<localStorage.length;i++)if((localStorage.getItem(localStorage.key(i))||'').includes(k))o.push(localStorage.key(i));return o}",KEY)
    c('D13 the key is not in localStorage (log included) or console',leak==[] and not any(KEY in m for m in cons),leak)
    # D14 download path also keeps a failed/blocked result visible
    fresh();M['m']='ok';pg.click('#rS');done();pg.click('#rD');done();good=badge();o=out()
    pg.click('#rD');done()
    c('D14 download succeeds once; a second different/blocked press does not erase the first result',good.startswith('✅') and '結果: 成功' in out(),(good,))
    c('Z no page errors',not errs,errs[:3]);print(sum(RR),'/',len(RR))
