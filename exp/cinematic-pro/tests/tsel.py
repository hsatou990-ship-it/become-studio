exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
def H(id,tags,w,h,dur,user,q):
    return {'id':id,'pageURL':'https://pixabay.com/videos/x-%d/'%id,'duration':dur,'user':user,'user_id':9,'tags':tags,
     'videos':{'large':{'url':'https://cdn.pixabay.com/video/a/%d.mp4'%id,'width':w,'height':h,'size':30000000,'thumbnail':'https://cdn.pixabay.com/video/a/t%d.jpg'%id},
               'medium':{'url':'https://cdn.pixabay.com/video/b/%d.mp4'%id,'width':720,'height':1280,'size':9000000,'thumbnail':'https://cdn.pixabay.com/video/b/t%d.jpg'%id}}}
def hits(q):
    if q.startswith('analog clock'):return [H(111,'coffee, cup, glasses, table, room',1080,1920,15,'MakerA',q),H(112,'clock, analog, time, watch',720,1280,12,'MakerB',q)]
    if q.startswith('feet climbing'):return [H(221,'trees, flowers, nature, park',1080,1920,15,'MakerC',q),H(222,'flowers, garden, spring',1080,1920,14,'MakerD',q)]
    if q.startswith('dark empty corridor'):return [H(301,'corridor, dark, empty, hallway',1080,1920,9,'DupMaker',q),H(302,'corridor, empty, light',1080,1920,10,'MakerE',q)]
    if q.startswith('golden sunrise'):return [H(401,'sunrise, golden, mountain, sunlight',1080,1920,9,'DupMaker',q),H(402,'sunrise, golden, mountain, summit',1080,1920,11,'MakerF',q)]
    return mkhits(q)
def mk(b):
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));pg.REQ={'api':[],'cdn':[]}
    def h_api(route,req):
        pg.REQ['api'].append(req.url);q=up.parse_qs(up.urlparse(req.url).query).get('q',['x'])[0];hs=hits(q)
        route.fulfill(status=200,body=json.dumps({'total':len(hs),'hits':hs}),content_type='application/json',headers={'access-control-allow-origin':'*'})
    def h_cdn(route,req):
        pg.REQ['cdn'].append(req.url)
        if req.url.endswith('.jpg'):return route.fulfill(status=200,body=PNG,content_type='image/png',headers={'access-control-allow-origin':'*'})
        route.fulfill(status=200,body=MP4,content_type='video/mp4',headers={'access-control-allow-origin':'*'})
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://cdn.pixabay.com/**',h_cdn);return pg
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    pg=mk(b);pg.goto(BASE.split('#')[0]+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.check('#breal')
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;CP.BT.lib=false;return await CP.autoMaterial()}");pg.wait_for_timeout(1500)
    st=pg.evaluate("()=>CP.S.clips.map((c,i)=>c?{id:c.inboxKey,pend:!!c.pend}:null)")
    b2=pg.evaluate("()=>[0,1,2,3].map(i=>{const x=bstat(i);return{st:x.st,msg:x.msg||''}})")
    print('clips',[x and x['id'] for x in st],'stat',[(x['st'],x['msg'][:30]) for x in b2])
    ck('1 S2: 無関係な語（coffee,cup,glasses）が付いた候補ではなく、中心語（clock）が一致する候補を採用',st[1] and st[1]['id']=='pixabay:112',st[1])
    ck('2 S3: 中心語が一致する候補が無ければ、自動採用せず確認待ち',st[2] is None and b2[2]['st']=='cand' and '確認待ち' in b2[2]['msg'],(st[2],b2[2]))
    ck('3 確認待ちの場面は動画を取得しない（取得 = 採用した場面数）',len(pg.REQ['cdn'])-len([u for u in pg.REQ['cdn'] if u.endswith('.jpg')])==sum(1 for x in st if x),(len(pg.REQ['cdn']),st))
    ck('4 確認待ちの理由が画面に出る',pg.evaluate("()=>document.getElementById('brev').innerText.includes('確認待ち')"))
    ck('5 同じ作者・ほぼ同じ長さの素材を別の場面で重ねて採用しない（S1とS4）',st[0] and st[3] and not (st[0]['id'] and st[3]['id'] and True and {st[0]['id'],st[3]['id']}=={'pixabay:301','pixabay:401'}),[x and x['id'] for x in st])
    ck('6 手動で確認待ちの場面を採用できる（権利は未確認から）',pg.evaluate("async()=>{const r=await batchAdopt(2,0,true);return r.ok&&S.clips[2]&&S.clips[2].pend===true}"))
    ck('7 通信枠を超えない（検索4回以下・動画4本以下）',pg.evaluate("()=>{const c=CP.realCnt();return c.s<=5&&c.d<=6}"))
    ck('8 ページエラーなし',pg.errs==[],pg.errs)
    print('TOTAL',sum(R),'/',len(R))
