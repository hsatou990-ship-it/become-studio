exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
SN="()=>CP.S.clips.map(c=>c?[c.meta.url,c.meta.by,c.meta.lic,c.meta.src,!!c.meta.ok,!!c.pend,c.inboxKey]:null)"
def build(b,confirm):
    ctx,pg=mkctx(b);pg.goto(BASE.split('#')[0]+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    pg.evaluate("()=>{document.getElementById('rt').open=true}");pg.fill('#bkey',KEY);pg.check('#breal')
    pg.evaluate("async()=>{CP.BT.key=document.getElementById('bkey').value;return await CP.autoMaterial()}");pg.wait_for_timeout(1200)
    if confirm:
        pg.evaluate("async()=>{document.getElementById('bokc').checked=true;return await rightsConfirmAll()}");pg.wait_for_timeout(500)
    return pg
def switch(pg,v):
    pg.select_option('#resSel',v);pg.wait_for_timeout(1000);ready(pg);pg.wait_for_timeout(5000)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    # 未確認のまま
    pg=build(b,False);A=pg.evaluate(SN)
    ck('0 前提: 自動取得直後は全素材が権利未確認',all(x and x[5] and not x[4] for x in A),A)
    switch(pg,'1080');B=pg.evaluate(SN)
    ck('1 解像度変更で未確認が確認済みに変わらない',B==A,(A,B))
    g=pg.evaluate("()=>rightsGate()");ck('1b 解像度変更後も書き出しが止まる',bool(g),g)
    # 確認済みの保持
    pg=build(b,True);A=pg.evaluate(SN)
    ck('2 前提: 確認後は全素材が確認済み',all(x and x[4] and not x[5] for x in A),A)
    switch(pg,'1080');B=pg.evaluate(SN)
    ck('2b 解像度変更後も確認済みが保たれる（ID・作者・取得元・ライセンス・状態）',B==A,(A,B))
    # 状態が不明な保存データは未確認
    pg=build(b,True)
    pg.evaluate("""async()=>{await saveSession();const db=await idbSess();const rec=await new Promise(ok=>{const q=db.transaction('s').objectStore('s').get('last');q.onsuccess=()=>ok(q.result)});rec.clips.forEach(c=>{delete c.ok;delete c.pend});rec.at=Date.now();await new Promise(ok=>{const t=db.transaction('s','readwrite');t.objectStore('s').put(rec);t.oncomplete=ok});location.hash='res=360&restore=1';location.reload()}""")
    pg.wait_for_timeout(1500);ready(pg);pg.wait_for_timeout(5000);B=pg.evaluate(SN)
    ck('3 権利状態が不明な保存データは未確認として復元',len(B)>0 and all(x and x[5] and not x[4] for x in B),B)
    # 書き出しの中核での検査
    pg=build(b,False)
    r=pg.evaluate("()=>{try{exportGuard(0);return 'passed'}catch(e){return e.code||String(e)}}");ck('4 書き出しの中核（exportGuard）が未確認素材で止まる',r=='RIGHTS',r)
    r=pg.evaluate("async()=>{const x=await exportOffline();return x===null?'blocked':'ran'}");ck('4b 書き出しボタン相当が未確認で止まる',r=='blocked',r)
    pg.evaluate("async()=>{document.getElementById('bokc').checked=true;await rightsConfirmAll()}")
    r=pg.evaluate("()=>{try{exportGuard(0);return 'passed'}catch(e){return e.code||String(e)}}");ck('4c 確認後は中核の検査を通る',r=='passed',r)
    pg.evaluate("()=>{S.clips[0].pend=true}")
    r=pg.evaluate("async()=>{const x=await exportVideo();return x===null?'blocked':'ran'}");ck('4d 従来の書き出し(exportVideo)も未確認で止まる',r=='blocked',r)
    pg.evaluate("()=>{S.clips[0].pend=false}")
    # 素材変更・音声変更・設計変更
    A=pg.evaluate(SN)
    pg.set_input_files('#narr',FIX+'/wavfx/n48m.wav');pg.wait_for_timeout(2500);B=pg.evaluate(SN)
    ck('5 音声変更で権利状態が変わらない',B==A,(A,B))
    ok_=pg.evaluate("async()=>{const b=bstat(0);if(!b.cands||b.cands.length<2)return 'nocand';const r=await batchPick(0,(b.sel+1)%b.cands.length);return r.ok?'ok':r.msg}");pg.wait_for_timeout(800);C=pg.evaluate(SN)
    ck('6 素材を変更した場面は確認状態を引き継がない（未確認に戻る）',ok_=='ok' and C[0] and C[0][5] and not C[0][4],(ok_,C[0]))
    ck('6b 変更していない場面の確認は保たれる',all(x and x[4] and not x[5] for x in C[1:]),C[1:])
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900);D=pg.evaluate(SN)
    ck('7 設計JSONを入れ直すと素材と確認状態が残らない',all(x is None for x in D),D)
    # 手動の取り込みで、前の確認チェックを引き継がない
    pg=build(b,True)
    pg.evaluate("()=>{const e=document.getElementById('ck0');e.checked=true}")
    pg.set_input_files('#cf0',FIX+'/cropfx/right.mp4');pg.wait_for_timeout(500)
    ck('8 手動で別のファイルを選ぶと、権利確認のチェックが外れる',pg.evaluate("()=>!document.getElementById('ck0').checked"))
    # プロジェクトの保存と復元で保たれる
    pg=build(b,True);A=pg.evaluate(SN);pg.evaluate("async()=>{await pjSave(true)}");pg.reload();ready(pg);pg.wait_for_timeout(1500)
    if pg.evaluate("()=>!document.getElementById('pjbar').hidden"):pg.click('#pjgo');pg.wait_for_timeout(4000)
    B=pg.evaluate(SN);ck('9 プロジェクトの復元で確認済みが保たれる',B==A,(A,B))
    print('TOTAL',sum(R),'/',len(R))
