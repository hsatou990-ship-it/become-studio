from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/_old.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:400])
def heavy(i,role='rise'):
    return {"text":"場面%d"%i,"dur":3,"role":role,"kinetic":"char","mask":{"type":"iris","dur":.6},"parallax":{"layers":3},"fx":["beat-sync-cut"],"speed":"speed-ramp"}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    def load(d):
        pg.fill('#dj',json.dumps(d));pg.click('#bDJ');pg.wait_for_timeout(300)
        return pg.evaluate("()=>({gov:CP.S.base.gov,sc:CP.S.base.sc.map(o=>({id:o.id,c:CP.fxCost(o),mask:!!o.mask,mc:!!o.mc,tr:o.tr,px:o.px,kin:o.kin,beat:o.beat,spd:o.spd,role:o.role,g:o.g}))})")
    # G1 mask+matchCut conflict
    sc=[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3,"role":"rise","mask":{"type":"iris","dur":.6},"matchCut":True},{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G1 mask+matchCut: mask removed, reason logged',not r['sc'][1]['mask'] and r['sc'][1]['mc'] and any(g['rule']=='競合' for g in r['gov']),r['gov'])
    # G2 mask + flash transition
    sc=[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3,"role":"rise","mask":{"type":"slit","dur":.6},"transition":"flash-white"},{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G2 mask+flash: transition removed, mask kept',r['sc'][1]['tr']=='none' and r['sc'][1]['mask'],r)
    # G3 budget
    sc=[{"text":"a","dur":3,"role":"hook"},heavy(1),{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G3 over-budget scene trimmed to <=5',r['sc'][1]['c']<=5 and any(g['rule']=='過剰抑制' for g in r['gov']),r['sc'][1])
    # G4 heavy runs and G5 quiet scene
    sc=[{"text":"hook","dur":3,"role":"hook"}]+[heavy(i) for i in range(1,7)]+[{"text":"end","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    cs=[o['c'] for o in r['sc'][1:-1]]
    run=m=0
    for c in cs:
        run=run+1 if c>=4 else 0;m=max(m,run)
    chk('G4 no more than 2 heavy scenes in a row',m<=2,cs)
    chk('G5 at least 25% quiet scenes (cost<=1) when 6+ scenes',sum(1 for c in cs if c<=1)>=2,cs)
    chk('G5b every reduction has a visible reason',len(r['gov'])>=3 and all(g['msg'] for g in r['gov']),r['gov'])
    # G6 core roles keep char kinetic
    sc=[{"text":"a","dur":3,"role":"hook"},heavy(1,'turn'),heavy(2,'climax'),{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G6 turn/climax keep character kinetic',r['sc'][1]['kin']=='char' and r['sc'][2]['kin']=='char',r['sc'])
    # G7 grade unification
    sc=[{"text":"a%d"%i,"dur":3,"role":"rise","grade":g} for i,g in enumerate(['cold-teal','warm-gold','muted-neutral','cold-teal','warm-gold','muted-neutral'])]
    r=load({"schema":"become.design/1","scenes":sc})
    sats=[o['g']['sat'] for o in r['sc'][:-1]]
    pg.evaluate("()=>{CP.GOV.on=false}");r0=load({"schema":"become.design/1","scenes":sc});sats0=[o['g']['sat'] for o in r0['sc'][:-1]];pg.evaluate("()=>{CP.GOV.on=true}")
    chk('G7 grade spread narrowed vs governor off (sat range <=0.2 and smaller)',max(sats)-min(sats)<=.2001 and (max(sats)-min(sats))<(max(sats0)-min(sats0))-.05,[sats,sats0])
    # G8 disabled
    pg.evaluate("()=>{CP.GOV.on=false}")
    sc=[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3,"role":"rise","mask":{"type":"iris","dur":.6},"matchCut":True},{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G8 governor off: nothing changed',r['sc'][1]['mask'] and not r['gov'],r)
    pg.evaluate("()=>{CP.GOV.on=true}")
    # G9 reasons displayed
    sc=[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3,"role":"rise","mask":{"type":"iris","dur":.6},"matchCut":True},{"text":"c","dur":3,"role":"ending"}]
    load({"schema":"become.design/1","scenes":sc});t=pg.inner_text('#govt')
    chk('G9 reasons shown on screen',('競合' in t) and ('S2' in t),t)
    # G10 clean plan: nothing trimmed
    sc=[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3,"role":"rise","kinetic":"char"},{"text":"c","dur":3,"role":"ending"}]
    r=load({"schema":"become.design/1","scenes":sc})
    chk('G10 light plan untouched',not r['gov'] or all(g['rule']=='色の統一' for g in r['gov']),r['gov'])
    # G11 ramp media continues past scene end (previous scene not frozen under mask)
    v=pg.evaluate("()=>{const S=CP.S;S.sc[1].spd='ramp';const b=S.sc[1].b;return [CP.mediaT(1,b),CP.mediaT(1,b+.5)]}")
    chk('G11 ramp media time keeps advancing after scene end',abs((v[1]-v[0])-.15)<.01,v)
    # G12 previous scene visibly moves during mask window
    sc=[{"text":"a","dur":3,"role":"hook","camera":"push-in"},{"text":"b","dur":3,"role":"rise","mask":{"type":"iris","dur":1.2}},{"text":"c","dur":3,"role":"ending"}]
    load({"schema":"become.design/1","scenes":sc})
    d=pg.evaluate("""()=>{const S=CP.S,a=S.sc[1].a;function px(t){CP.renderFrame(t);const w=CP.og.canvas.width,h=CP.og.canvas.height;return Array.from(CP.og.getImageData(2,Math.floor(h*.5),24,24).data)}
      const A=px(a+.15),B=px(a+.45);let s=0;for(let i=0;i<A.length;i++)s+=Math.abs(A[i]-B[i]);return s}""")
    chk('G12 outer region (previous scene) changes during mask',d>0,d)
    chk('G13 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
