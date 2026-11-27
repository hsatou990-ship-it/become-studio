from playwright.sync_api import sync_playwright
V='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/vid/'
R=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new']);pg=b.new_context().new_page()
    pg.goto('http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360');pg.wait_for_timeout(800)
    pg.fill('#bgs','t');pg.fill('#bgl','t');pg.check('#bgk')
    for bpm,ph in [(75,.4),(120,.21),(140,.05),(88,.33)]:
        pg.set_input_files('#bgf',V+'b%d_%d.wav'%(bpm,int(ph*100)));pg.click('#bBgm');pg.wait_for_timeout(2500)
        a=pg.evaluate("()=>CP.S.bgm&&{bpm:CP.S.bgm.bpm,ph:CP.S.bgm.an.phase}")
        per=60/bpm;d=abs(((a['ph']-ph+per/2)%per)-per/2)
        ok=abs(a['bpm']-bpm)<2 and d<.04;R.append(ok);print('PASS' if ok else 'FAIL',bpm,ph,a,'phase err %.3f'%d)
    b.close()
print('ALL',all(R))
