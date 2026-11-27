import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
R='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/riko/'
J=open((REPO+'/exp/design/price-of-staying.design.json')).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new'])
    pg=b.new_context().new_page();pg.goto('http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360');pg.wait_for_timeout(800)
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500);pg.set_input_files('#narr',R+'zip/BEYOND_Riko_A.wav');pg.wait_for_timeout(1500)
    print(pg.evaluate("""async()=>{const H=m=>{const x=m.getChannelData(0);let h=0;for(let i=0;i<x.length;i+=11)h=(h*31+Math.round(x[i]*1e6))|0;return h};const a=await CP.buildAudio(),b=await CP.buildAudio(),c=await CP.buildAudio();const x=a.getChannelData(0),y=b.getChannelData(0);let md=0;for(let i=0;i<x.length;i++)md=Math.max(md,Math.abs(x[i]-y[i]));return {h:[H(a),H(b),H(c)],maxdiff:md}}"""))
    b.close()
