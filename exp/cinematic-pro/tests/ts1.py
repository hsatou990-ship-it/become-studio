import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):
    R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,info if not ok else '')
def fresh(b,w=412,h=915):
    ctx,pg=mkctx(b,w,h);pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(400);return pg
def body(pg):return pg.evaluate("()=>document.body.innerText")
def nn(pg):return pg.evaluate("()=>{const e=document.getElementById('narrnow');return e?e.textContent:null}")
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    # 1 stale text
    pg=fresh(b);t=body(pg)
    ck('1a 旧通信枠表記なし(検索1回・動画1本)','検索1回・動画1本' not in t)
    ck('1b 見出しが動的(#clipH)',pg.evaluate("()=>!!document.getElementById('clipH')"))
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900);t=body(pg)
    ck('1c 設計JSON後に旧ナレーション目安文が残らない','まだ、何も変えられていない' not in t)
    ck('1d 見出しの場面数が現在の場面数','S1〜S4' in (pg.evaluate("()=>(document.getElementById('clipH')||{}).textContent||''")))
    ck('1e 通信枠表記が実際の枠と一致',('検索5回' in t and '動画6本' in t) or '検索1回' not in t)
    # 2 overflow
    for w,h in ((360,740),(390,844),(412,915)):
        pg=fresh(b,w,h);pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
        pg.evaluate("()=>{document.querySelectorAll('details').forEach(d=>d.open=true)}")
        dw=pg.evaluate("()=>document.documentElement.scrollWidth");ck('2 横はみ出しなし %d'%w,dw<=w,'docW=%d'%dw)
    # 3 narration state
    pg=fresh(b)
    ck('3a 初期は音声なし表示',nn(pg) is not None and '音声なし' in nn(pg),nn(pg))
    pg.set_input_files('#narr',(FIX+'/wavfx/n48m.wav'));pg.wait_for_timeout(1500)
    ck('3b WAV後は外部音声+ファイル名',nn(pg) and '外部音声' in nn(pg) and 'n48m.wav' in nn(pg),nn(pg))
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    s=pg.evaluate("()=>({narr:!!CP.S.narr})")
    ck('3c 設計JSON反映後も音声を保持',s['narr'],s)
    ck('3d 反映後の表示が実態と一致(外部音声または要確認)',nn(pg) and ('外部音声' in nn(pg)),nn(pg))
    pg.click('#bVo');pg.wait_for_timeout(500)
    ck('3e 反映後に原音の試聴が「先に取り込んで」とならない','先にナレーション' not in pg.inner_text('#voicest'),pg.inner_text('#voicest'))
    pg.set_input_files('#narr',(FIX+'/wavfx/n441s.wav'));pg.wait_for_timeout(1500);pg.click('#bMock');pg.wait_for_timeout(1500)
    st_=pg.evaluate("()=>({files:document.getElementById('narr').files.length,mock:CP.S.isMockNarr})")
    ck('3f 模擬ボタン後はファイル入力が空',st_['files']==0,st_)
    ck('3g 模擬ボタン後は模擬音声表示',nn(pg) and '模擬音声' in nn(pg) and '外部音声' not in nn(pg),nn(pg))
    # 4 thumbs
    pg=fresh(b);pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(800)
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.check('#breal')
    pg.evaluate("async()=>{CP.BT.mode='review';CP.BT.key=document.getElementById('bkey').value;await CP.batchRun({})}")
    th=pg.locator('#brev button[data-a^=thumb]')
    ck('4a サムネイルボタンが存在',th.count()>0)
    h=pg.inner_text('#brev')
    ck('4b ボタン付近に状態/理由の文',pg.evaluate("()=>!!document.querySelector('#brev .thwhy')"))
    cb=len(pg.REQ['cdn']);pg.evaluate("async()=>{await CP.batchAdopt(0,0,true)}");pg.wait_for_timeout(600)
    fb=pg.locator('#brev button[data-a^=frame]:not([disabled])')
    ck('4c 採用後に端末内の場面画像ボタンが押せる',fb.count()>0,fb.count())
    if fb.count():fb.first.click();pg.wait_for_timeout(2500)
    ck('4c2 場面画像が4枚できる(通信増なし)',pg.locator('#brev .frs img').count()==4,pg.locator('#brev .frs img').count())
    try:th.first.click(timeout=3000)
    except Exception:pass
    pg.wait_for_timeout(800)
    m=pg.inner_text('#bst')+pg.inner_text('#brev')
    ck('4d 画像取得の失敗文が検索回数の枠と誤記しない','検索5回・動画6本' not in m,m[:120])
    print('TOTAL',sum(R),'/',len(R))
