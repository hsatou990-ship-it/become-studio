import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
J=open((REPO+'/exp/design/price-of-staying.design.json')).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500)
    print(pg.inner_text('#djs')[:300]);print('----');print(pg.inner_text('#djr'));print('----');print(pg.inner_text('#govt'));print('----')
    print(pg.evaluate("()=>JSON.stringify({D:CP.S.base.D,sc:CP.S.sc.map(o=>({id:o.id,a:+o.a.toFixed(2),b:+o.b.toFixed(2),cost:o.id==='END'?0:CP.fxCost(o),tr:o.tr,kin:o.kin,spd:o.spd,beat:o.beat,g:o.g&&[o.g.sat,o.g.con,o.g.vig]})),warn:CP.S.warn,ln:CP.S.ln.map(l=>[l.t0,l.d,l.toks.map(k=>k[0]).join('')])})"))
    pg.evaluate("()=>{CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true}")
    for t in (1.2,4.5,8.0,11.5):
        pg.evaluate(f"()=>CP.renderFrame({t})");pg.screenshot(path=f'/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/ss/price_{int(t*10)}.png',clip={'x':0,'y':0,'width':412,'height':915}) if False else None
    print('errs',errs)
    print(pg.inner_text('#memst'))
