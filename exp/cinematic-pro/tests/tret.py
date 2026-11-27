exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
import tempfile,shutil
U9='http://localhost:8767/r9/exp/cinematic-pro/index.html#res=360';U10='http://localhost:8767/r10/exp/cinematic-pro/index.html#res=360'
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
def snap(pg):
    return pg.evaluate("""()=>({cnt:CP.realCnt(),lim:CP.REAL.lim,clips:CP.S.clips.filter(Boolean).length,nclip:CP.S.clips.length,narr:!!CP.S.narr,dur:CP.S.narr?+CP.S.narr.duration.toFixed(2):0,D:CP.S.base?CP.S.base.D:0,dj:!!CP.S.dj,ep:CP.rlogGet().filter(x=>x.step==='epoch').length,meta:CP.S.clips.filter(Boolean).map(c=>(c.meta.id||c.meta.url||'')+'|'+(c.meta.by||'')+'|'+(c.pend?'pend':'ok'))})""")
with sync_playwright() as p:
    d=tempfile.mkdtemp()
    ctx=p.chromium.launch_persistent_context(d,executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'],viewport={'width':412,'height':915})
    REQ={'api':[],'cdn':[]}
    def h_api(route,req):
        REQ['api'].append(req.url);q=up.parse_qs(up.urlparse(req.url).query);hits=mkhits(q.get('q',['x'])[0])
        route.fulfill(status=200,body=json.dumps({'total':len(hits),'hits':hits}),content_type='application/json',headers={'access-control-allow-origin':'*'})
    def h_cdn(route,req):
        REQ['cdn'].append(req.url);route.fulfill(status=200,body=MP4,content_type='video/mp4',headers={'access-control-allow-origin':'*'})
    ctx.route('https://pixabay.com/**',h_api);ctx.route('https://cdn.pixabay.com/**',h_cdn)
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    # A: r9 でデータを作る
    pg.goto(U9);pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    pg.set_input_files('#narr','/tmp/wavfx/n48m.wav');pg.wait_for_timeout(2500)
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.check('#breal')
    r=pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.autoMaterial()}");pg.wait_for_timeout(1500)
    A=snap(pg);print('A(r9)',{k:v for k,v in A.items() if k!='meta'},'api',len(REQ['api']),'cdn',len(REQ['cdn']))
    ck('A0 r9で素材が配置され通信枠が使われた',A['clips']>=1 and A['cnt']['s']>=1 and A['cnt']['d']>=1,A)
    pg.wait_for_timeout(1500)
    pg.close()
    # B: 同じブラウザデータで r10 を開く
    pg2=ctx.new_page();pg2.on('pageerror',lambda e:errs.append(str(e)))
    api0,cdn0=len(REQ['api']),len(REQ['cdn'])
    pg2.goto(U10);ready(pg2);pg2.wait_for_timeout(1500)
    vis=pg2.evaluate("()=>!document.getElementById('pjbar').hidden");ck('B1 r10 起動時に続きから再開の表示が出る',vis)
    B0=snap(pg2);ck('B2 通信枠の使用数が更新で変わらない',B0['cnt']==A['cnt'] and B0['lim']==A['lim'],(B0['cnt'],A['cnt']))
    ck('B3 通信枠の基準日の記録が増えない(リセットされない)',B0['ep']==A['ep'],(B0['ep'],A['ep']))
    if vis:
        pg2.click('#pjgo');pg2.wait_for_timeout(4000)
    B=snap(pg2);print('B(r10)',{k:v for k,v in B.items() if k!='meta'})
    ck('B4 取得済み素材の本数が同じ',B['clips']==A['clips'],(B['clips'],A['clips']))
    ck('B5 素材の識別・作者・権利状態が同じ',B['meta']==A['meta'],(B['meta'],A['meta']))
    ck('B6 ナレーション(外部音声)が復元される',B['narr'] and abs(B['dur']-A['dur'])<0.05,(B['dur'],A['dur']))
    ck('B7 設計JSON・動画の長さが同じ',B['dj']==A['dj'] and B['D']==A['D'],(B['dj'],B['D'],A['D']))
    ck('B8 復元と更新で追加の通信が発生しない',len(REQ['api'])==api0 and len(REQ['cdn'])==cdn0,(len(REQ['api'])-api0,len(REQ['cdn'])-cdn0))
    ck('B9 通信枠の使用数が復元後も同じ',B['cnt']==A['cnt'],(B['cnt'],A['cnt']))
    ck('B10 復元後に音声表示が実態と一致',pg2.evaluate("()=>document.getElementById('narrnow').textContent").startswith('現在の音声: 外部音声'),pg2.evaluate("()=>document.getElementById('narrnow').textContent"))
    ck('B11 ページエラーなし',errs==[],errs)
    print('TOTAL',sum(R),'/',len(R))
    ctx.close();shutil.rmtree(d,ignore_errors=True)
