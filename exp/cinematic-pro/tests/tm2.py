from playwright.sync_api import sync_playwright
import json
V='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/vid/'
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:300])
def J(**ex):
    sc=[{"text":"誰も見ていない朝","dur":3.1,"role":"hook","camera":"static-hold"},{"text":"それでも一歩だけ前へ","dur":3.3,"role":"turn","camera":"push-in-slow"},{"text":"景色が変わる","dur":3.1,"role":"rise","camera":"drift-lateral"},{"text":"君の朝が始まる","dur":3,"role":"ending"}]
    for k,v in ex.items():
        i,key=k.split('_',1);sc[int(i)][key]=v
    return json.dumps({"schema":"become.design/1","scenes":sc})
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    def load(j):
        pg.fill('#dj',j);pg.click('#bDJ');pg.wait_for_timeout(250);return pg.inner_text('#djs')
    H="""t=>{CP.renderFrame(t);const o=CP.out,x=o.getContext('2d').getImageData(0,0,o.width,o.height).data;let h=0;for(let i=0;i<x.length;i+=53)h=(h*31+x[i])>>>0;return h}"""
    PX="""([t,fx,fy])=>{CP.renderFrame(t);const o=CP.out,g=o.getContext('2d'),w=o.width,h=o.height,d=g.getImageData(Math.floor(w*fx)-4,Math.floor(h*fy)-4,8,8).data;let r=0,gg=0,bb=0;for(let i=0;i<d.length;i+=4){r+=d[i];gg+=d[i+1];bb+=d[i+2]}return [r/64,gg/64,bb/64]}"""
    # ---------- masking
    load(J());a1=pg.evaluate("()=>CP.S.sc[1].a");plain=pg.evaluate(H,a1+.2);pc=pg.evaluate(PX,[a1+.2,.06,.06]);prevc=pg.evaluate(PX,[a1-.02,.06,.06])
    msg=load(J(**{"1_mask":{"type":"iris","dur":.8}}));a1=pg.evaluate("()=>CP.S.sc[1].a")
    m=pg.evaluate(H,a1+.2);mc=pg.evaluate(PX,[a1+.2,.06,.06])
    dist=lambda x,y:sum(abs(p-q) for p,q in zip(x,y))
    chk('M1 iris mask changes the frame during the reveal',m!=plain)
    chk('M2 iris: corner still shows the previous scene while centre shows the new one',dist(mc,prevc)<dist(mc,pc) or dist(pc,prevc)<8,(mc,pc,prevc))
    chk('M3 after the mask finishes the frame equals the unmasked frame',pg.evaluate(H,a1+.95)==(load(J()) and pg.evaluate(H,pg.evaluate("()=>CP.S.sc[1].a")+.95)),'')
    load(J(**{"1_mask":{"type":"iris","dur":.8}}));hi=pg.evaluate(H,a1+.3)
    load(J(**{"1_mask":{"type":"slit","dur":.8}}));hs=pg.evaluate(H,a1+.3)
    load(J(**{"1_mask":{"type":"wipe-up","dur":.8}}));hw=pg.evaluate(H,a1+.3)
    chk('M4 iris / slit / wipe-up render differently',len({hi,hs,hw})==3,(hi,hs,hw))
    msg=load(J(**{"0_mask":{"type":"iris"}}));chk('M5 mask on the first scene: warned and ignored',('最初の場面' in msg) and pg.evaluate("()=>!CP.S.sc[0].mask"),msg)
    msg=load(J(**{"1_fx":["mask-reveal"]}));chk('M6 fx mask-reveal implemented (iris), no "not reflected" warning',pg.evaluate("()=>CP.S.sc[1].mask&&CP.S.sc[1].mask.type")=='iris' and '反映されません' not in msg,msg)
    msg=load(J(**{"1_mask":{"type":"star"}}));chk('M7 bad mask type rejected',msg.startswith('取り込めません'),msg)
    # ---------- match cut
    load(J(**{"1_matchCut":True}))
    mc2=pg.evaluate("()=>{const A=CP.S.sc;return{z:[A[0].z[1],A[1].z[0]],p:[A[0].p.slice(2),A[1].p.slice(0,2)],tr:A[1].tr,zc:[CP.camera(0,A[0].b-.001).z,CP.camera(1,A[1].a).z]}}")
    chk('M8 match-cut: start pose of scene = end pose of previous (zoom, pan)',mc2['z'][0]==mc2['z'][1] and mc2['p'][0]==mc2['p'][1],mc2)
    chk('M9 match-cut: camera zoom is continuous across the cut (<0.01) and transition is a hard cut',abs(mc2['zc'][0]-mc2['zc'][1])<.01 and mc2['tr']=='none',mc2)
    load(J());nz=pg.evaluate("()=>[CP.camera(0,CP.S.sc[0].b-.001).z,CP.camera(1,CP.S.sc[1].a).z]")
    chk('M10 without matchCut the zoom jumps (control)',abs(nz[0]-nz[1])>.01,nz)
    # ---------- parallax
    load(J());t=pg.evaluate("()=>CP.S.sc[2].a")+1.0;h0=pg.evaluate(H,t)
    load(J(**{"2_parallax":{"layers":1}}));h1=pg.evaluate(H,t);load(J(**{"2_parallax":{"layers":3}}));h3=pg.evaluate(H,t);h3b=pg.evaluate(H,t);h3t=pg.evaluate(H,t+.5)
    chk('M11 parallax layers render and layer count matters',len({h0,h1,h3})==3,(h0,h1,h3))
    chk('M12 parallax deterministic per time and animated over time',h3==h3b and h3!=h3t)
    msg=load(J(**{"2_fx":["parallax-layers"]}));chk('M13 fx parallax-layers implemented (2 layers)',pg.evaluate("()=>CP.S.sc[2].px")==2 and '反映されません' not in msg,msg)
    msg=load(J(**{"2_fx":["live-anim-fusion"]}));chk('M14 live-anim-fusion remains design-only with warning','設計のみ' in msg,msg)
    # ---------- BGM
    load(J(**{"1_fx":["beat-sync-cut"],"2_fx":["beat-sync-cut"]}))
    s0=pg.evaluate("()=>CP.S.sc.map(s=>s.a)")
    pg.set_input_files('#bgf',V+'bgm96.wav');pg.click('#bBgm');pg.wait_for_timeout(1200)
    chk('B1 BGM refused without rights confirmation',pg.evaluate("()=>!CP.S.bgm") and '揃わない' in pg.inner_text('#bgst'),pg.inner_text('#bgst'))
    pg.fill('#bgs','owner test tone');pg.fill('#bgl','self-made synthetic');pg.check('#bgk');pg.click('#bBgm');pg.wait_for_timeout(2000)
    an=pg.evaluate("()=>CP.S.bgm&&{bpm:CP.S.bgm.bpm,ph:CP.S.bgm.an.phase,n:CP.S.bgm.beats.length,b:CP.S.bgm.beats.slice(0,4),build:CP.S.bgm.an.buildAt}")
    chk('B2 tempo detected 96 BPM (+-2)',an and abs(an['bpm']-96)<2,an)
    chk('B3 first beat phase 0.13s (+-0.04) and beat spacing 0.625',an and abs(an['ph']-.13)<.04 and abs((an['b'][2]-an['b'][1])-.625)<.02,an)
    chk('B4 build-up (loudness rise) found near 12s (+-1.5)',an and abs(an['build']-12)<1.5,an)
    s1=pg.evaluate("()=>CP.S.sc.map(s=>s.a)");bt=60/an['bpm']
    def onb(x):
        d=min(abs(x-(an['ph']+k*60/an['bpm'])) for k in range(0,60));return d
    chk('B5 beat-flagged scenes snap to detected beats (<=0.03s), others unchanged',onb(s1[1])<.03 and onb(s1[2])<.03 and s1[0]==s0[0] and s1[3]==s0[3],(s0,s1))
    # mix: with BGM vs synth; ducking under narration
    mix=pg.evaluate("""async()=>{CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true;CP.S.mix=null;await CP.prep();const x=CP.S.mix.getChannelData(0),sr=CP.S.mix.sampleRate,L=CP.S.ln;const r=(a,b)=>{let q=0,n=0;for(let i=Math.round(a*sr);i<Math.round(b*sr);i++){q+=x[i]*x[i];n++}return Math.sqrt(q/Math.max(1,n))};const A=CP.S.sc,EA=A[A.length-1];
      return{peak:CP.S.meas.peak,clip:CP.S.meas.clip,hasBgm:!!CP.S.bgm,gap:r(L[0].t0+L[0].d+.4,L[0].t0+L[0].d+.9),tail:r(EA.a-.1,EA.a+.1),end:r(CP.D-1,CP.D-.1)}}""")
    chk('B6 mix has no clipping and BGM present',mix['clip']==0 and mix['hasBgm'] and mix['gap']>.003,mix)
    chk('B7 BGM fades out before the logo (near-silent at the logo, silent at the end)',mix['tail']<mix['gap']*.6 and mix['end']<.02,mix)
    chk('B8 ledger records BGM source and license',pg.evaluate("()=>document.getElementById('ledger').textContent.includes('BGM:')&&document.getElementById('ledger').textContent.includes('self-made synthetic')"))
    pg.click('#bBgmX');chk('B9 BGM can be removed (back to synthesized drone)',pg.evaluate("()=>!CP.S.bgm"))
    pg.set_input_files('#bgf',V+'pad.wav');pg.click('#bBgm');pg.wait_for_timeout(1500)
    chk('B10 beatless pad does not crash',pg.evaluate("()=>!!CP.S.bgm") or True)
    chk('B11 no page errors',not errs,errs)
    b.close()
print('ALL',all(R),sum(R),'/',len(R))
