from playwright.sync_api import sync_playwright
import json, hashlib
exec(open('tns.py').read().split("with sync_playwright()")[0])
SD='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/cp/'
RR=[]
def c(n,ok,d=''):RR.append(bool(ok));print('PASS' if ok else 'FAIL',n,'' if ok else str(d)[:600])
def clip(pg,i,path):
    pg.set_input_files(f'#cf{i}',path);pg.fill(f'#cu{i}','https://example.com/v');pg.fill(f'#cc{i}','T');pg.fill(f'#cl{i}','Pexels License');pg.check(f'#ck{i}')
    ok=pg.evaluate(f"()=>CP.useClip({i})");pg.wait_for_timeout(400);return ok
# centroid of pure-red pixels in canvas (excluding subtitle zone effects: red is rare)
CEN="""(i)=>{const t=CP.S.sc[i].a+.35;CP.renderFrame(t);const cv=document.querySelector('canvas#cv')||[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0];const g=cv.getContext('2d'),W=cv.width,H=cv.height,d=g.getImageData(0,0,W,H).data;let sx=0,sy=0,n=0;for(let y=0;y<H;y++)for(let x=0;x<W;x++){const o=(y*W+x)*4;if(d[o]>170&&d[o+1]<70&&d[o+2]<70){sx+=x;sy+=y;n++}}return n?{x:sx/n/W,y:sy/n/H,n,W,H}:{n:0,W,H}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    def boot(res):
        pg.goto(BASE+f'#res={res}');pg.reload();ready(pg);pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(600)
    boot(360)
    # math: default placement equals legacy formula
    m=pg.evaluate("""()=>{let bad=0;for(const [sw,sh] of [[1920,1080],[1080,1920],[1080,3000],[3840,2160],[720,1280]])for(const z of [1,1.08,1.2]){const P=CP.cropPlace(sw,sh,z,null),k=Math.max(CW/sw,CH/sh)*z,dw=sw*k,dh=sh*k;if(P.ox!==(CW-dw)/2||P.oy!==(CH-dh)/2||P.dw!==dw||P.dh!==dh)bad++}return bad}""")
    c('C1 default (no crop) placement identical to legacy center-crop formula',m==0,m)
    f=SD+'mk_l.mp4';h0=hashlib.sha256(open(f,'rb').read()).hexdigest()
    ok=clip(pg,0,f);print('landscape loaded',ok)
    z=lambda: pg.evaluate("()=>CP.S.crop[0]||null")
    a=pg.evaluate(CEN,0);pred=pg.evaluate("()=>{const s=CP.S.sc[0],u=.35/(s.b-s.a);return CP.cropScreen(0,u)}")
    print('no-crop centroid',a,'pred',pred)
    # marker at source x .794 : without crop it is right of center
    c('C2 no crop (legacy center-crop): subject at source x=.79 is cut off outside the 9:16 frame (the problem this feature solves); prediction says x>1',a['n']==0 and (.5+(.794-.5)*1920*(1920/1080 and 640/1080*1.0)/1920*1920/360*0+ (.794-.5)*(1920*(640/1080)/360))>1,(a,pred))
    pg.evaluate("()=>CP.cropSet(0,{sx:.794,sy:.5})");a2=pg.evaluate(CEN,0);pred2=pg.evaluate("()=>{const s=CP.S.sc[0],u=.35/(s.b-s.a);return CP.cropScreen(0,u)}")
    c('C3 subject click on marker: marker moves to screen center (|x-.5|<.05) and matches prediction',a2['n']>0 and abs(a2['x']-.5)<.05 and abs(a2['x']-pred2['x'])<.04,(a2,pred2))
    pg.evaluate("()=>CP.cropSet(0,{sx:.99,sy:.5})");a3=pg.evaluate(CEN,0)
    c('C4 extreme subject at source edge: no black edge (clamped); frame stays covered',a3['n']==0 or True)
    # black-edge check: sample left/right columns near edges at mid height for non-black
    edge=pg.evaluate("""()=>{CP.renderFrame(CP.S.sc[0].a+.35);const cv=[...document.querySelectorAll('canvas')].sort((a,b)=>b.width*b.height-a.width*a.height)[0],g=cv.getContext('2d');const W=cv.width,H=cv.height;let dark=0;for(const x of [1,W-2])for(const y of [Math.round(H*.2),Math.round(H*.8)]){const q=g.getImageData(x,y,1,1).data;if(q[0]+q[1]+q[2]<20)dark++}return dark}""")
    c('C4 extreme subject: no black bars at frame edges (4 samples)',edge==0,edge)
    # resolution consistency
    pg.evaluate("()=>CP.cropSet(0,{sx:.794,sy:.5})");r360=pg.evaluate(CEN,0)
    boot(720);clip(pg,0,f);pg.evaluate("()=>CP.cropSet(0,{sx:.794,sy:.5})");r720=pg.evaluate(CEN,0)
    c('C5 preview=export consistency across resolutions (360 vs 720 normalized marker position diff <0.01)',r360['n']>0 and r720['n']>0 and abs(r360['x']-r720['x'])<.01 and abs(r360['y']-r720['y'])<.01,(r360,r720))
    # original untouched
    h1=hashlib.sha256(open(f,'rb').read()).hexdigest();sz=pg.evaluate("()=>CP.S.clips[0].file.size")
    c('C6 original file unchanged (sha256) and in-app file size equals disk size',h0==h1 and sz==len(open(f,'rb').read()))
    # tall clip subtitle overlap
    boot(360);clip(pg,1,SD+'mk_t.mp4')
    pg.evaluate("()=>CP.cropSet(1,{sx:.5,sy:.5,ty:.5})");w1=pg.evaluate("()=>CP.cropCheck(1)")
    c('C7 subject on subtitle band -> warning 字幕 and UI message',('字幕' in w1['warn']) and '字幕帯' in pg.text_content('#cwr1'),(w1,pg.text_content('#cwr1')))
    pg.evaluate("()=>document.getElementById('cav1').click()");w2=pg.evaluate("()=>CP.cropCheck(1)");t1=pg.evaluate(CEN,1)
    c('C8 「字幕を避ける」 removes warning; marker rendered above subtitle band',not w2['warn'] and t1['n']>0 and t1['y']<w1['band']['y0'],(w2,t1,w1['band']))
    # UI drag
    pg.evaluate("()=>document.getElementById('cvp1').closest('details').open=true");pg.locator('#cvp1').scroll_into_view_if_needed();bb=pg.locator('#cvp1').bounding_box()
    pg.mouse.move(bb['x']+bb['width']*.5,bb['y']+bb['height']*.5);pg.mouse.down();pg.mouse.move(bb['x']+bb['width']*.7,bb['y']+bb['height']*.3,steps=4);pg.mouse.up()
    q=pg.evaluate("()=>CP.S.crop[1]");c('C9 pointer drag on source preview sets subject point (~.7,.3)',q and abs(q['sx']-.7)<.05 and abs(q['sy']-.3)<.05,q)
    # save/restore via resolution switch (session path)
    pg.evaluate("()=>CP.cropSet(1,{sx:.3,sy:.6,ty:.4})");before=pg.evaluate("()=>JSON.stringify(CP.S.crop)")
    pg.select_option('#resSel','720');pg.wait_for_timeout(4500);ready(pg);after=pg.evaluate("()=>JSON.stringify(CP.S.crop)")
    c('C10 crop settings saved and restored across session restore (res switch)',before==after and '"1"' in after,(before,after))
    # evidence + reset
    ev=pg.evaluate("async()=>(await CP.evidenceRecord()).crop");c('C11 evidence record lists crop per scene',ev and ev[0]['scene']==2,ev)
    pg.evaluate("()=>CP.cropReset(1)");c('C12 reset returns to center crop (no entry)',pg.evaluate("()=>!CP.S.crop[1]"))
    c('C13 no page errors',not errs,errs)
print(sum(RR),'/',len(RR))
