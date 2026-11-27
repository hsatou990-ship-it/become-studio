from playwright.sync_api import sync_playwright
import json,sys
B='http://127.0.0.1:8765/exp/cinematic-pro/'
sc=[{"text":"a","dur":3,"role":"hook","camera":"push-in-fast"},{"text":"b","dur":3,"role":"rise","mask":{"type":"iris","dur":1.4}},{"text":"c","dur":3,"role":"ending"}]
J=json.dumps({"schema":"become.design/1","scenes":sc})
def measure(page):
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        pg=b.new_context(viewport={'width':412,'height':915}).new_page();pg.goto(B+page+'#res=360');pg.wait_for_timeout(800)
        pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(300)
        r=pg.evaluate("""()=>{const S=CP.S,a=S.sc[1].a,end=S.sc[0].b;
          // 前場面(静止問題)の指標: マスク開始直後の外周領域が、時間とともにどれだけ動くか
          function px(t){CP.renderFrame(t);const h=CP.og.canvas.height,w=CP.og.canvas.width,d=CP.og.getImageData(0,0,w,Math.floor(h*.3)).data,bw=16,bh=16,o=[];for(let by=0;by<Math.floor(h*.3)-bh;by+=bh)for(let bx=0;bx<w-bw;bx+=bw){let s=0;for(let y=0;y<bh;y++)for(let x=0;x<bw;x++){const i=((by+y)*w+bx+x)*4;s+=d[i]+d[i+1]+d[i+2]}o.push(s/(bw*bh*3))}return o}
          const T=[a+.1,a+.5,a+.9,a+1.3];const F=T.map(px);let d=[];for(let i=1;i<F.length;i++){let s=0;for(let k=0;k<F[i].length;k++)s+=Math.abs(F[i][k]-F[i-1][k]);d.push(s)}return d}""")
        b.close();return r
new=measure('index.html');old=measure('_old.html')
print('new',new);print('old',old)
ok=sum(new)>sum(old)*1.1
print('G12 new>old (detects the fix):',ok)
sys.exit(0 if ok else 1)
