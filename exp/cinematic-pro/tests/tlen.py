from playwright.sync_api import sync_playwright
import json
exec(open('tns.py').read().split("with sync_playwright()")[0])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new']);pg=b.new_context().new_page();pg.goto(BASE+'#res=360');ready(pg)
    pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(500)
    for f in('a.wav','long.wav','short.wav'):
        pg.set_input_files('#narr',D+f);pg.wait_for_timeout(1500)
        for m in('keep','fit','legacy'):
            pg.evaluate(f"()=>CP.setSyncMode('{m}')");pg.wait_for_timeout(300)
            r=pg.evaluate("async()=>{const x=await CP.buildAudio();return {len:x.length/48000,D:CP.S.sc[CP.S.sc.length-1].b,sec:CP.S.sync&&CP.S.sync.D}}")
            print(f,m,'audio',round(r['len'],3),'timeline D',r['D'],'sync D',r['sec'],'OK' if abs(r['len']-r['D'])<.01 else 'MISMATCH')
    b.close()
