from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:200])
J={"schema":"become.design/1","title":"t","scenes":[
 {"text":"誰も見ていない朝","dur":3,"role":"hook","camera":"push-in-slow","grade":"cold-teal","emphasis":["誰も"],"search":{"queries":["dawn room"]},"sfx":["riser"]},
 {"text":"それでも一歩前へ","dur":3,"role":"turn","camera":"push-in-fast","transition":"flash-white","speed":"speed-ramp","cut":{"type":"j-cut","offset":.4},"sfx":["hit"]},
 {"text":"景色が変わる","dur":3,"role":"rise","speed":"slow-motion","cut":{"type":"l-cut","offset":.3}},
 {"text":"そして、続く","dur":3,"role":"ending","transition":"dip-black"}],"ending":{"holdSec":2}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    pg.fill('#dj',json.dumps(J));pg.click('#bDJ');pg.wait_for_timeout(300)
    st=pg.evaluate("()=>({n:CP.S.sc.length,D:CP.S.base.D,sc:CP.S.sc.map(s=>[s.a,s.b,s.spd,s.cut&&s.cut.type,s.tr]),base:CP.S.base.sc.map(s=>[s.a,s.b]),ln:CP.S.ln.length,msg:document.getElementById('djs').textContent})")
    chk('P1 imported 4 scenes + end',st['n']==5 and st['ln']==4,st)
    chk('P2 length = 12+2 hold',st['D']==14,st['D'])
    chk('P3 spd mapped',[x[2] for x in st['sc'][:4]]==['','ramp','slow',''],st['sc'])
    chk('P4 J-cut: scene2 starts .4s earlier than base',abs(st['sc'][1][0]-(st['base'][1][0]-.4))<.02,(st['sc'][1],st['base'][1]))
    chk('P5 L-cut: scene3 starts .3s later',abs(st['sc'][2][0]-(st['base'][2][0]+.3))<.02,(st['sc'][2],st['base'][2]))
    chk('P6 boundaries contiguous',all(abs(st['sc'][i][1]-st['sc'][i+1][0])<1e-6 for i in range(4)),st['sc'])
    chk('P7 cut transition → none for hook',st['sc'][0][4]=='none' and st['sc'][1][4]=='flash',st['sc'])
    m=pg.evaluate("()=>{CP.S.sc[1].spd='ramp';CP.S.sc[2].spd='slow';const a=CP.S.sc[1],d=a.b-a.a,c=CP.S.sc[2],e=c.b-c.a;return{r0:CP.rateAt(1,0),r1:CP.rateAt(1,1),sl:CP.rateAt(2,.5),mr:CP.mediaT(1,a.b)/d,ms:CP.mediaT(2,c.b)/e,mm:CP.mediaT(1,a.a+d/2)/d}}")
    chk('P8 ramp rate 2.2→.3, slow .5',abs(m['r0']-2.2)<1e-6 and abs(m['r1']-.3)<1e-6 and m['sl']==.5,m)
    chk('P9 media time: ramp ≈.933·dur, slow .5·dur, monotonic',abs(m['mr']-.9333)<.01 and abs(m['ms']-.5)<.01 and m['mm']<m['mr'],m)
    # frames differ between slow and normal at same scene time (mock animation)
    h=pg.evaluate("""()=>{const s=CP.S.sc[2],t=s.a+s.b*0+ (s.b-s.a)*.8;const c=document.createElement('canvas');const grab=()=>{CP.renderFrame(t);const o=CP.out,x=o.getContext('2d').getImageData(0,0,o.width,o.height).data;let h=0;for(let i=0;i<x.length;i+=97)h=(h*31+x[i])>>>0;return h};
      s.spd='slow';const a=grab();s.spd='';const b=grab();return[a,b]}""")
    chk('P10 slow-mo changes rendered frame',h[0]!=h[1],h)
    # invalid import must not change state
    before=pg.evaluate("()=>CP.S.sc.length+'|'+CP.S.base.D")
    pg.fill('#dj','{"schema":"become.design/1","scenes":[{"text":"x","dur":999}]}');pg.click('#bDJ')
    after=pg.evaluate("()=>CP.S.sc.length+'|'+CP.S.base.D");msg=pg.inner_text('#djs')
    chk('P11 invalid JSON rejected, state unchanged',before==after and '取り込めません' in msg,(before,after,msg))
    pg.fill('#dj','{"schema":"become.design/1","scenes":[{"text":"<script>window.XSS=1</script>","dur":2}]}');pg.click('#bDJ');pg.wait_for_timeout(200)
    chk('P12 no script execution / no html injection',pg.evaluate("()=>!window.XSS&&!document.getElementById('djs').querySelector('script')"))
    pg.click('#bDJP');chk('P13 request prompt shown',pg.evaluate("()=>document.getElementById('djp').value.includes('become.design/1')&&!document.getElementById('djp').hidden"))
    chk('P14 impl table lists implemented and design-only',pg.evaluate("()=>{const t=document.getElementById('implt').textContent;return /✔ speed-ramp/.test(t)&&/△ live-anim-fusion/.test(t)}"))
    # director path still works and gets default j-cut at turn
    # 設計JSON取込は台本欄を設計の台本に更新する（段階B-0）。P12の1文のままではディレクター案に転換点が無いため、台本欄を複数文に戻してから試験する
    pg.fill('#dsc','変わるのが、怖いか。でも、時間は止まらない。その一歩が、未来を変える。今日から、始めよう。')
    pg.click('#bDir');pg.wait_for_timeout(300)
    d=pg.evaluate("()=>CP.S.sc.map(s=>s.cut&&s.cut.type)")
    chk('P15 director path: turn gets j-cut','j-cut' in d,d)
    chk('P16 no page errors',not errs,errs)
    b.close()
print('ALL',all(R),sum(R),'/',len(R))
