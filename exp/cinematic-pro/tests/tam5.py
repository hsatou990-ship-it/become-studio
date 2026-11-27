exec(open("tam.py").read().split("\nwith sync_playwright()")[0])
import urllib.parse as up
GOOD='9876543-abcdef0123456789abcdef012'
def hits(q):
    return [{'id':k+1,'pageURL':'https://pixabay.com/videos/x-%d/'%k,'duration':8,'user':'M','user_id':7,'tags':'a','videos':{'large':{'url':'https://cdn.pixabay.com/video/a/%d.mp4'%k,'width':1080,'height':1920,'size':9000000,'thumbnail':''}}} for k in range(3)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));cons=[];pg.on('console',lambda m:cons.append(m.text))
    REQ=[];M={'m':'ok'};OKH={'access-control-allow-origin':'*'}
    def h_api(route,req):
        REQ.append(req.url)
        if M['m']=='400':return route.fulfill(status=400,body='[ERROR 400] Invalid or missing API key',content_type='text/plain',headers=OKH)
        route.fulfill(status=200,body=json.dumps({'hits':hits('x')}),content_type='application/json',headers=OKH)
    ctx.route('https://pixabay.com/**',h_api)
    def fresh():
        pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.evaluate("()=>{CP.REAL.lim.s=1;CP.REAL.lim.d=1}");pg.wait_for_timeout(300)
        pg.evaluate("()=>{document.getElementById('rt').open=true;document.querySelectorAll('#rt details').forEach(d=>d.open=true)}");pg.check('#breal');REQ.clear()
    def done():pg.wait_for_function("()=>!document.getElementById('rBadge').textContent.includes('⏳')",timeout=20000);pg.wait_for_timeout(150)
    fresh()
    U=pg.evaluate("""()=>{const f=(k)=>{const c=CP.keyCheck(k);return[c.level,c.msgs.length]};
      return{good:f('9876543-abcdef0123456789abcdef012'),sp:f('9876543-abcdef 0123456789abcdef012'),nl:f('9876543-abcdef\\n0123456789abcdef012'),zw:f('9876543-abcdef\\u200b0123456789abcdef012'),fw:f('９８７６５４３-abcdef0123456789abcdef012'),eq:f('key=9876543-abcdef0123456789abcdef012'),url:f('https://pixabay.com/api/?key=987'),short:f('abc'),empty:f(''),up:f('9876543-ABCDEF0123456789abcdef012'),odd:f('abcdefghijklmnop'),q:f('9876543-abc"def012345678')}}""")
    c('K1 key validation: usable shapes pass; space/newline/zero-width/full-width/"key="/URL/too short/empty/quote are NG; unknown format or capitals only warn',
      U['good'][0]=='ok' and all(U[k][0]=='ng' for k in ['sp','nl','zw','fw','eq','url','short','empty','q']) and U['up'][0]=='warn' and U['odd'][0]=='warn',U)
    el=pg.evaluate("()=>{const e=document.getElementById('bkey');return{type:e.type,ac:e.autocomplete,cap:e.getAttribute('autocapitalize'),cor:e.getAttribute('autocorrect'),sp:e.getAttribute('spellcheck'),mask:e.style.webkitTextSecurity||getComputedStyle(e).webkitTextSecurity}}")
    c('K2 input is a plain text field (no password-manager autofill), autocapitalize/autocorrect/spellcheck off, masked on screen',el['type']=='text' and el['ac']=='off' and el['cap']=='off' and el['cor']=='off' and el['sp']=='false' and 'disc' in el['mask'],el)
    pg.fill('#bkey',GOOD);pg.wait_for_timeout(100);st=pg.inner_text('#bkst')
    c('K3 status line shows counts and verdict only — none of the key characters',('判定: OK' in st) and '長さ '+str(len(GOOD)) in st and 'abcdef0123' not in st and '9876543' not in st,st)
    pg.fill('#bkey','  '+GOOD+'\n');pg.wait_for_timeout(100)
    c('K4 leading/trailing spaces and a trailing newline are removed before use (still judged OK)','判定: OK' in pg.inner_text('#bkst') and pg.evaluate("()=>CP.BT.key")==GOOD)
    pg.fill('#bkey','9876543-abc def');pg.wait_for_timeout(100);bad=pg.inner_text('#bkst')
    pg.click('#rS');done()
    c('K5 an unusable key is stopped BEFORE sending: no request, quota not used, badge ⛔, log says BADKEY (blocked, not sent)',len(REQ)==0 and pg.evaluate("()=>CP.realCnt().s")==0 and pg.inner_text('#rBadge').startswith('⛔') and '使えません' in bad and json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))==[] or any(e['code']=='BADKEY' for e in json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))),(len(REQ),bad,pg.inner_text('#rBadge')))
    # reveal / mask
    pg.fill('#bkey',GOOD);pg.click('#bkshow');shown=pg.evaluate("()=>document.getElementById('bkey').style.webkitTextSecurity")
    pg.focus('#bkey');pg.evaluate("()=>document.getElementById('bkey').blur()");hid=pg.evaluate("()=>document.getElementById('bkey').style.webkitTextSecurity")
    c('K6 「10秒だけ表示」 reveals the key on the owner screen; leaving the field masks it again',shown=='none' and hid=='disc',(shown,hid))
    pg.click('#bkclr');c('K7 「キーを消去」 empties field and memory',pg.input_value('#bkey')=='' and pg.evaluate("()=>CP.BT.key")=='')
    # valid key: hand-off facts
    pg.fill('#bkey','  '+GOOD+'  ');pg.click('#rS');done()
    sent=up.parse_qs(up.urlparse(REQ[0]).query) if REQ else {}
    lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    c('K8 hand-off: the typed key (spaces trimmed) arrives in the URL parameter named key, URL-encoding changes nothing, other parameters are listed',len(REQ)==1 and sent.get('key')==[GOOD] and 'key' in lg[0]['qs'] and lg[0]['kin']==len(GOOD)==lg[0]['ks']['len'],(sent.get('key'),lg[0].get('qs')))
    o=pg.inner_text('#rOut')
    c('K9 result text states 入力 n文字 → 送信 n文字（一致）and the parameter names, without any key characters',('一致' in o) and '送信パラメータ名: key,' in o and GOOD not in o and 'abcdef0123' not in o,o[:1200])
    # HTTP 400 invalid key
    fresh();M['m']='400';pg.fill('#bkey',GOOD);pg.click('#rS');done();o=pg.inner_text('#rOut');lg=json.loads(pg.evaluate("()=>JSON.stringify(CP.rlogGet().filter(x=>x.step!=='epoch'))"))
    c('K10 HTTP 400 "Invalid or missing API key": reported as key rejected by the provider while transport/CORS are fine; hand-off shown as matching',lg[0]['status']==400 and '無効、または未指定' in o and '通信・CORSは正常' in o and '一致' in o and '取り違え' in o,o[:1400])
    leak=pg.evaluate("(k)=>{const o=[];for(let i=0;i<localStorage.length;i++)if((localStorage.getItem(localStorage.key(i))||'').includes(k))o.push(localStorage.key(i));return o}",GOOD)
    c('K11 key not stored anywhere (localStorage, log) and not in console',leak==[] and not any(GOOD in m for m in cons))
    c('Z no page errors',not errs,errs[:3]);print(sum(RR),'/',len(RR))
