"""段階A: 字幕セーフゾーン（設定の仕組みとプレビュー）の試験。TikTok公式の数値は確認できていないため、
試験は「未設定なら現在の位置のまま」「入力した数値の内側に収まる」「プレビューは書き出しに入らない」を確かめる。数値の正しさは、実機の実測で決める。"""
import os,sys,json
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
LAY="()=>{const o=[];for(let f=0;f<CP.N;f+=9){const t=f/CP.FPS;o.push(CP.capLayout(t).map(q=>[q.s,Math.round(q.x*10)/10,Math.round(q.y*10)/10,Math.round(q.sz*10)/10]))}return JSON.stringify(o)}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx,pg=mkctx(b);pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    base=pg.evaluate(LAY);ymax=pg.evaluate("()=>{let a=1e9,z=-1e9;for(let f=0;f<CP.N;f++)CP.boxes(f/CP.FPS).forEach(b=>{a=Math.min(a,b.y0);z=Math.max(z,b.y1)});return[a,z]}")
    ck('Z1 既定は未適用（数値が未確定のため、現在の字幕位置のまま）',pg.evaluate("()=>!CP.szActive()"))
    ck('Z1b 既定の画面表示は「未適用」',('未適用' in pg.evaluate("()=>document.getElementById('szSt').textContent")))
    pg.evaluate("()=>CP.szSet({on:false,top:10,bottom:30,left:5,right:20})");same=pg.evaluate(LAY)
    ck('Z2 数値を入れても、「適用」を入れるまで字幕位置は変わらない',same==base)
    ck('Z3 字幕の既定位置は縦46%付近（既存仕様の維持）',abs((ymax[0]+ymax[1])/2-1920*.46)<260,ymax)
    # 下の余白 60%
    c=pg.evaluate("()=>CP.szSet({on:true,top:0,bottom:60,left:0,right:0})");after=pg.evaluate(LAY)
    box=pg.evaluate("()=>{let z=-1e9;for(let f=0;f<CP.N;f++){const t=f/CP.FPS;CP.capLayout(t).forEach(o=>{if(o.alpha>=.95)z=Math.max(z,o.y+o.sz*.25)});const l=CP.logoLayout(t);if(l&&l.alpha>=.95)z=Math.max(z,l.y+60)}return z}")
    ck('Z4 下の余白を大きくすると、字幕が上へ寄り、下端が安全域の内側に収まる',after!=base and box<=1920*.4+12,box)
    ck('Z5 全フレームの検査（szCheck）が合格を返す',c['configured'] and c['ok'],c)
    # 右の余白 20% → 最大幅
    c=pg.evaluate("()=>CP.szSet({on:true,top:0,bottom:0,left:0,right:20})");mw=pg.evaluate("()=>CP.szMaxW()")
    xs=pg.evaluate("()=>{let a=1e9,z=-1e9;for(let f=0;f<CP.N;f++)CP.capLayout(f/CP.FPS).forEach(o=>{if(o.alpha>=.95){a=Math.min(a,o.x);z=Math.max(z,o.x+o.w)}});return[a,z]}")
    ck('Z6 右の余白に合わせて、字幕の最大幅を狭める（左右対称）',abs(mw-(1080-2*216))<1 and xs[0]>=215 and xs[1]<=865,(mw,xs))
    # 説明文の行数と1行の高さ
    pg.evaluate("()=>CP.szSet({on:true,top:0,bottom:10,desc:3,lineH:3,left:0,right:0})");band=pg.evaluate("()=>CP.szCheck().band")
    ck('Z7 説明文の行数×1行の高さが、下の余白に加わる（10%+9%）',abs(band['ba']-1920*(1-.19))<2,band)
    # 字幕ブロックが帯より高い→ 超過を報告
    c=pg.evaluate("()=>CP.szSet({on:true,top:40,bottom:55,desc:0,lineH:0,left:0,right:0})")
    ck('Z8 帯が狭すぎて収まらない場合は、収まらないと報告する（隠さない）',c['configured'] and c['ok']==False,c)
    ck('Z9 reportに安全域の検査が含まれる',pg.evaluate("()=>typeof CP.report().sz.configured")=='boolean')
    # 保存と再読み込み
    pg.evaluate("()=>CP.szSet({on:true,top:5,bottom:25,desc:2,lineH:2.5,left:4,right:12})")
    pg.reload();ready(pg);pg.wait_for_timeout(600)
    v=pg.evaluate("()=>({on:CP.SZ.on,top:CP.SZ.top,bottom:CP.SZ.bottom,desc:CP.SZ.desc,lineH:CP.SZ.lineH,left:CP.SZ.left,right:CP.SZ.right,ui:document.getElementById('szBottom').value,act:CP.szActive()})")
    ck('Z10 設定は再読み込み後も保たれる（後から調整できる）',v['on'] and v['top']==5 and v['bottom']==25 and v['desc']==2 and v['lineH']==2.5 and v['left']==4 and v['right']==12 and str(v['ui'])=='25' and v['act'],v)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900);pg.evaluate("()=>CP.szSet({on:false})");base=pg.evaluate(LAY)   # 再読み込みで設計が消えるため、読み直して基準を取り直す
    # 画面の入力から設定
    pg.evaluate("()=>{document.getElementById('szp').open=true}");pg.fill('#szBottom','30');pg.dispatch_event('#szBottom','change');pg.wait_for_timeout(200)
    ck('Z11 画面の入力で数値を変えられる',pg.evaluate("()=>CP.SZ.bottom")==30)
    # プレビューは書き出しの画像に入らない
    pg.evaluate("()=>CP.szSet({on:true,top:5,bottom:25,desc:0,lineH:0,left:4,right:12,preview:false})")
    def hashOut():return pg.evaluate("()=>{CP.renderFrame(1.0);const g=CP.og.getImageData?CP.og:null;const c=CP.out;const x=c.getContext?null:null;const d=document.createElement('canvas');d.width=c.width;d.height=c.height;const q=d.getContext('2d');q.drawImage(c,0,0);const a=q.getImageData(0,0,d.width,d.height).data;let h=0;for(let i=0;i<a.length;i+=97)h=(h*31+a[i])>>>0;return h}")
    h0=hashOut();pg.evaluate("()=>CP.szSet({preview:true})");h1=hashOut()
    ov=pg.evaluate("()=>{const o=document.getElementById('szov');return{hidden:o.hidden,painted:(()=>{const a=o.getContext('2d').getImageData(0,0,o.width,o.height).data;let n=0;for(let i=3;i<a.length;i+=4)if(a[i])n++;return n})()}}")
    ck('Z12 プレビューは別のキャンバスに描く（書き出す画像は同一）',h0==h1 and (not ov['hidden']) and ov['painted']>500,(h0,h1,ov))
    pg.evaluate("()=>{try{CP.exportGuard(0)}catch{}}");pv=pg.evaluate("()=>({on:CP.SZ.preview,hidden:document.getElementById('szov').hidden})")
    ck('Z13 書き出しの開始でプレビューは自動で消える',pv['on']==False and pv['hidden']==True,pv)
    pg.evaluate("()=>CP.szSet({on:false,top:0,bottom:0,desc:0,lineH:0,left:0,right:0})");back=pg.evaluate(LAY)
    ck('Z14 適用を外すと、元の字幕位置に戻る',back==base)
    ck('Z15 ページエラーなし',pg.errs==[],pg.errs)
    print('TOTAL',sum(R),'/',len(R))
