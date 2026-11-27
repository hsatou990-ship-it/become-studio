from playwright.sync_api import sync_playwright
import json
R='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/riko/zip/BEYOND_Riko_A.wav'
J=open('/home/claude/become-studio/exp/design/price-of-staying.design.json').read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new'])
    pg=b.new_context().new_page();pg.goto('http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360');pg.wait_for_timeout(800)
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500);pg.set_input_files('#narr',R);pg.wait_for_timeout(2000)
    print(pg.inner_text('#syncrep'));print(pg.evaluate("()=>CP.S.warn"))
    print(pg.evaluate("()=>({D:CP.S.sync&&CP.S.sync.D,ln:CP.S.ln.map(l=>[+l.t0.toFixed(2),+l.d.toFixed(2)]),sc:CP.S.sc.map(o=>+o.a.toFixed(2))})"))
    b.close()
