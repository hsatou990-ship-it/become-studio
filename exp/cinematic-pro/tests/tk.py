from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:300])
def J(kin=None,fx=None,bpm=None,beat=False):
    sc=[{"text":"誰も見ていない朝","dur":3,"role":"hook"},{"text":"それでも一歩だけ前へ","dur":3.3,"role":"turn","emphasis":["一歩"]},{"text":"景色が変わる","dur":3.1,"role":"rise"},{"text":"君の朝が始まる","dur":3,"role":"ending"}]
    if kin:sc[1]['kinetic']=kin
    if fx:sc[1]['fx']=fx
    if beat:
        for i in (1,2):sc[i]['fx']=(sc[i].get('fx') or [])+['beat-sync-cut']
    d={"schema":"become.design/1","scenes":sc}
    if bpm:d['bgm']={"mood":"cinematic-rise","bpm":bpm}
    return json.dumps(d)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    def load(j):
        pg.fill('#dj',j);pg.click('#bDJ');pg.wait_for_timeout(250);return pg.inner_text('#djs')
    # ---- kinetic
    msg=load(J(kin='char'))
    n_char=pg.evaluate("()=>{const L=CP.S.ln[1];return L.toks.map(k=>k[0]).join('').length}")
    t0=pg.evaluate("()=>CP.S.ln[1].t0")
    lay=lambda t:pg.evaluate("t=>{CP.renderFrame(t);return window.__lay=null}",t)
    # use boxes() as layout probe
    pr=lambda t:pg.evaluate("t=>CP.boxes(t).map(b=>[Math.round(b.x0),Math.round(b.y0),Math.round(b.x1)])",t)
    early=pr(t0+.12);late=pr(t0+2.5)
    chk('K1 char mode: letters appear one by one (few boxes early, all later)',0<len(early)<len(late) and len(late)>=n_char-1,(len(early),len(late),n_char))
    msg=load(J());plain_late=pr(pg.evaluate("()=>CP.S.ln[1].t0")+2.5)
    chk('K2 default (no kinetic) layout unchanged: token-level boxes',len(plain_late)<=len(late)//1 and len(plain_late)<=4,(len(plain_late),len(late)))
    # final text equals
    txt=lambda t:pg.evaluate("t=>CP.boxes(t).length",t)
    # frame differs between kinetic and none at early time
    h=lambda t:pg.evaluate("t=>{CP.renderFrame(t);const o=CP.out,x=o.getContext('2d').getImageData(0,0,o.width,o.height).data;let h=0;for(let i=0;i<x.length;i+=61)h=(h*31+x[i])>>>0;return h}",t)
    load(J(kin='char'));ta=pg.evaluate("()=>CP.S.ln[1].t0")+.25;hk=h(ta)
    load(J());hn=h(pg.evaluate("()=>CP.S.ln[1].t0")+.25)
    chk('K3 kinetic changes the rendered frame',hk!=hn,(hk,hn))
    load(J(kin='track'));chk('K4 track mode renders & differs',h(pg.evaluate("()=>CP.S.ln[1].t0")+.25)!=hn and h(pg.evaluate("()=>CP.S.ln[1].t0")+.25)!=hk)
    msg=load(J(fx=['kinetic-typography']));chk('K5 fx=kinetic-typography implemented: no "not reflected" warning, sets char',pg.evaluate("()=>CP.S.sc[1].kin")=='char' and '設計のみ' not in msg and '反映されません' not in msg,msg)
    load(J(kin='char'));sc=pg.evaluate("()=>{const r=CP.safeCheck();return JSON.stringify(r)}");chk('K6 kinetic captions stay inside safe area (safeCheck over all frames)',pg.evaluate("()=>{const r=CP.safeCheck();return r===true||(r&&r.ok!==false)}"),sc)
    msg=load(J(fx=['live-anim-fusion']));chk('K7 design-only fx still warns',('設計のみ' in msg),msg)
    # old JSON compat (no new fields)
    msg=load(J());chk('K8 old JSON (no kinetic/beat fields) still imports',pg.inner_text('#djs').startswith('反映しました'),msg)
    # ---- beat sync
    msg=load(J(bpm=100,beat=True))  # beat=.6s grid
    st=pg.evaluate("()=>({a:CP.S.sc.map(s=>s.a),beat:CP.S.sc.map(s=>!!s.beat),bpm:CP.S.base.bpm})")
    bt=60/100
    onb=[abs(st['a'][i]/bt-round(st['a'][i]/bt))*bt for i in (1,2)] if (round:=lambda x:int(x+.5)) else 0
    chk('K9 beat scenes start on the beat grid (<=0.02s)',all(o<.02 for o in onb),(st,onb))
    base=load(J(bpm=100,beat=False));st2=pg.evaluate("()=>CP.S.sc.map(s=>s.a)")
    chk('K10 without beat flag boundaries are not snapped',any(abs(st2[i]/bt-round(st2[i]/bt))*bt>.02 for i in (1,2,3)),st2)
    msg=load(J(bpm=None,beat=True));base0=pg.evaluate("()=>CP.S.sc.map(s=>s.a)");load(J(bpm=None,beat=False));base1=pg.evaluate("()=>CP.S.sc.map(s=>s.a)")
    chk('K11 beat-sync without bpm and without BGM: warned, no snapping',('BGM' in msg) and base0==base1,(msg,base0,base1))
    # audio: kick pulses add low-frequency energy at beats
    def kick(j):
        load(j)
        return pg.evaluate("""async()=>{await CP.buildAudio();const x=CP.S.mix.getChannelData(0),sr=CP.S.mix.sampleRate,bpm=CP.S.base.bpm||100,bt=60/bpm;let e=0,n=0;for(let t=bt;t<CP.S.sc[CP.S.sc.length-1].a-.4;t+=bt){const a=Math.round((t+.01)*sr),b=Math.round((t+.08)*sr);let q=0;for(let i=a;i<b;i++)q+=x[i]*x[i];e+=q/(b-a);n++}return Math.sqrt(e/Math.max(1,n))}""")
    k1=kick(J(bpm=100,beat=True));k0=kick(J(bpm=100,beat=False))
    chk('K12 BGM gets beat pulses when beat-sync is on (energy at beats higher)',k1>k0*1.3,(k1,k0))
    # camera punch
    load(J(bpm=100,beat=True))
    z=pg.evaluate("()=>{const i=1,s=CP.S.sc[i];return [CP.camera(i,s.a+.01).z,CP.camera(i,s.a+.6).z-0]}")
    chk('K13 zoom punch right after beat cut (z higher at cut than .6s later, beyond camera drift)',z[0]-z[1]>.015,z)
    chk('K14 no page errors',not errs,errs)
    b.close()
print('ALL',all(R),sum(R),'/',len(R))
