exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
BGS=[('白','#ffffff'),('明るい灰','#d9d9d9'),('空色','#87ceeb'),('明るい緑','#8fbc8f'),('ベージュ','#d2b48c'),('中間灰','#808080'),('暗い灰','#303030'),('黒に近い','#101010')]
JS="""(bgs)=>{
 let T=null;for(let t=0;t<D;t+=.05){const L=capLayout(t);if(L.length>=3&&L.every(o=>o.alpha>.95)){T=t;break}}
 if(T===null)return{err:'no caption time'};
 const lin=c=>{c/=255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)},Lm=(r,g,b)=>.2126*lin(r)+.7152*lin(g)+.0722*lin(b),cr=(a,b)=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
 const out=[];
 for(const [n,hex] of bgs){og.setTransform(1,0,0,1,0,0);og.globalAlpha=1;og.filter='none';og.fillStyle=hex;og.fillRect(0,0,CW,CH);CAPL.t=-9;
  const before=og.getImageData(Math.round(CW/2),Math.round(CH*.46),1,1).data.slice(0,3);
  const cs=capStyle(og,T,capLayout(T));
  drawCaps(og,T,0);
  const bx=cs.box;const px=og.getImageData(Math.round(bx.x0*SCL)+2,Math.round((bx.y0+bx.y1)/2*SCL),1,1).data.slice(0,3);
  const rb=[0,1,2].map(k=>(hex.length===7?parseInt(hex.slice(1+2*k,3+2*k),16):0));
  const eff=rb.map(c=>c*(1-cs.ab)*(1-cs.sa*(cs.sw>0?1:0)));const Lr=Lm(...eff);
  out.push({n,k:+cs.k.toFixed(2),ab:+cs.ab.toFixed(2),sw:+cs.sw.toFixed(1),white:+cr(1,Lr).toFixed(2),gold:+cr(Lm(212,175,55),Lr).toFixed(2),px:[...px],bg:rb})}
 // ちらつき: 白と黒に近い背景を毎フレーム入れ替える
 const ks=[];CAPL.t=-9;for(let f=0;f<60;f++){const t=T+f/30;og.setTransform(1,0,0,1,0,0);og.globalAlpha=1;og.fillStyle=f%2?'#ffffff':'#101010';og.fillRect(0,0,CW,CH);const c2=capStyle(og,Math.min(t,D-.01),capLayout(Math.min(t,D-.01)));if(c2)ks.push(c2.k)}
 let mx=0;for(let i=1;i<ks.length;i++)mx=Math.max(mx,Math.abs(ks[i]-ks[i-1]));
 const bxs=boxes(T);const m={x0:Math.min(...bxs.map(b=>b.x0)),x1:Math.max(...bxs.map(b=>b.x1)),y0:Math.min(...bxs.map(b=>b.y0)),y1:Math.max(...bxs.map(b=>b.y1))};
 return{out,flick:+mx.toFixed(3),m,W,H}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx,pg=mkctx(b);pg.goto(BASE.split('#')[0]+'#res=720');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(600)
    try:r=pg.evaluate(JS,BGS)
    except Exception as e:r={'err':str(e)[:200]}
    if 'err' in r:
        ck('0 字幕の視認性調整の機能が存在する',False,r['err'])
    else:
        for o in r['out']:print(o)
        bright=[o for o in r['out'] if o['n'] in('白','明るい灰','空色','明るい緑','ベージュ')]
        dark=[o for o in r['out'] if o['n'] in('暗い灰','黒に近い')]
        ck('1 明るい背景: 白文字と周囲のコントラストが4.5以上',all(o['white']>=4.5 for o in bright),[(o['n'],o['white']) for o in bright])
        ck('2 明るい背景: ゴールドと周囲のコントラストが3.0以上',all(o['gold']>=3.0 for o in bright),[(o['n'],o['gold']) for o in bright])
        ck('3 暗い背景: 背景帯なし（高級感を保つ）',all(o['ab']<=.02 for o in dark),[(o['n'],o['ab']) for o in dark])
        ck('4 明るい背景: 帯が必要最小限（最大でも濃度0.6以下）',all(0<o['ab']<=.6 for o in bright),[(o['n'],o['ab']) for o in bright])
        ck('5 明るい背景では縁取りが太くなり、暗い背景では細い',min(o['sw'] for o in bright)>max(o['sw'] for o in dark),([o['sw'] for o in bright],[o['sw'] for o in dark]))
        ck('6 背景が1フレームごとに白と黒で入れ替わっても、調整量の変化が1フレーム0.12以下（ちらつき防止）',r['flick']<=.12,r['flick'])
        m=r['m'];ck('7 字幕が横の余白60以上・縦は画面の12〜80%に収まる（TikTokの画面部品の位置は公式資料で確認できていない目安）',m['x0']>=60 and m['x1']<=r['W']-60 and m['y0']>=r['H']*.12 and m['y1']<=r['H']*.8,m)
    print('TOTAL',sum(R),'/',len(R))
