"""品質回帰（機械測定）: 更新前後（RET_OLD/RET_NEW）で、同じ台本・設定・素材の描画フレームが一致するか。字幕セーフゾーン未適用時は、完全一致が条件。
実素材の視聴評価ではない。/tmp/ret/<名前>/ に更新前後の配信物を置いて使う（tret と同じ）。"""
import os,hashlib
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
OLD=os.environ.get('RET_OLD','r11');NEW=os.environ.get('RET_NEW','r12')
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
def frames(b,name):
    ctx,pg=mkctx(b);pg.goto('http://localhost:8767/%s/exp/cinematic-pro/index.html#res=360'%name);pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900);pg.set_input_files('#narr',(FIX+'/wavfx/n48m.wav'));pg.wait_for_timeout(2500)
    h=pg.evaluate("""()=>{const o=[];for(const t of [0.5,1.2,2.0,3.1,4.0,5.5,7.0,9.0,11.0,13.5]){CP.renderFrame(t);const c=CP.out,d=document.createElement('canvas');d.width=c.width;d.height=c.height;const q=d.getContext('2d');q.drawImage(c,0,0);const a=q.getImageData(0,0,d.width,d.height).data;let h=0;for(let i=0;i<a.length;i+=7)h=(h*31+a[i])>>>0;o.push(h)}return o}""")
    ctx.close();return h
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    a=frames(b,OLD);c=frames(b,NEW)
    ck('Q1 同じ台本・設定・音声で、10時点の描画フレームが更新前後で一致（字幕セーフゾーン未適用）',a==c,[i for i,(x,y) in enumerate(zip(a,c)) if x!=y])
    print('TOTAL',sum(R),'/',len(R))
