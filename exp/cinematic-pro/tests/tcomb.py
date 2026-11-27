from playwright.sync_api import sync_playwright
import json
D='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/cp/ns/'
J=open('/home/claude/become-studio/exp/design/price-of-staying.design.json').read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new']);pg=b.new_context().new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360');pg.wait_for_timeout(800);pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500)
    pg.set_input_files('#narr',D+'a.wav');pg.wait_for_timeout(1500);pg.check('input[name=voice][value=beta]')
    r=pg.evaluate("""async()=>{CP.setBgmMode('none');CP.S.sc.forEach(o=>o.sfx={});const m=await CP.buildAudio();const x=m.getChannelData(0);let pk=0;for(let i=0;i<x.length;i++)pk=Math.max(pk,Math.abs(x[i]));
      const rms=(a,b)=>{let s=0,n=0;for(let i=Math.floor(a*48000);i<b*48000;i++){s+=x[i]*x[i];n++}return 10*Math.log10(s/n+1e-14)};
      return {pk,sp:CP.S.ln.map(l=>rms(l.t0+.1,l.t0+l.d-.1)),gap:rms(CP.S.ln[0].t0+CP.S.ln[0].d+.15,CP.S.ln[1].t0-.15),D:CP.S.sync.D,ok:CP.S.sync.ok,voice:CP.S.voice}}""")
    print(r,errs);b.close()
