from playwright.sync_api import sync_playwright
import json, numpy as np, wave
exec(open('tns.py').read().split("with sync_playwright()")[0])  # reuse synth, design, helpers
R2=[]
def chk2(n,c,d=''):R2.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:500])
SNAP="""async()=>{const m=await CP.buildAudio();const x=m.getChannelData(0);let e=0;for(let i=0;i<x.length;i+=97)e+=x[i]*x[i];return {sc:CP.S.sc.map(o=>[+o.a.toFixed(4),+o.b.toFixed(4)]),ln:CP.S.ln.map(l=>[+l.t0.toFixed(4),+l.d.toFixed(4)]),aligned:CP.S.aligned,off:CP.S.off,len:x.length,e:+e.toFixed(3)}}"""
cases=[('a.wav',None),('j.wav',None)]
synth(D+'long.wav',16.0,[(.3,3.8),(4.4,8.0),(8.6,12.2),(12.8,15.8)],[440,660,880,1100])
synth(D+'short.wav',6.0,[(.2,1.2),(1.7,2.7),(3.2,4.4),(4.9,5.8)],[440,660,880,1100])
cases+= [('long.wav',None),('short.wav',None)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new'])
    def run(url,legacy):
        pg=b.new_context(viewport={'width':412,'height':915}).new_page();pg.goto(url+'#res=360');ready(pg)
        pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(500)
        if legacy:pg.select_option('#syncm','legacy')
        out={}
        for f,_ in cases:
            pg.set_input_files('#narr',D+f);pg.wait_for_timeout(1500)
            if legacy:pg.evaluate("()=>CP.setSyncMode('legacy')")
            out[f]=pg.evaluate(SNAP);out[f]['warn']=[w for w in pg.evaluate("()=>CP.S.warn") if w.startswith('ナレーション')]
        return out
    old=run('http://127.0.0.1:8766/exp/cinematic-pro/index.html',False)
    new=run('http://127.0.0.1:8765/exp/cinematic-pro/index.html',True)
    for f,_ in cases:
        o,n=old[f],new[f]
        same=o['sc']==n['sc'] and o['ln']==n['ln'] and o['aligned']==n['aligned'] and o['len']==n['len']
        chk2(f'L-{f}: legacy mode reproduces main timeline exactly (scenes, subtitles, length, aligned flag)',same,(o['sc'],n['sc'],o['ln'],n['ln']))
        chk2(f'L-{f}: audio energy equal to main (±1%)',abs(o['e']-n['e'])<=0.01*max(o['e'],1e-9)+1e-6,(o['e'],n['e']))
        chk2(f'L-{f}: main warnings are a subset of legacy warnings',all(w in n['warn'] or w.split('（')[0] in ''.join(n['warn']) for w in o['warn']),(o['warn'],n['warn']))
    b.close()
print(sum(R2),'/',len(R2))
