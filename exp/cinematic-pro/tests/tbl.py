from playwright.sync_api import sync_playwright
import json
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:400])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    pg.fill('#dsc','誰も見ていない朝。何度も失敗して、心が折れそうになる。それでも一歩だけ前へ。景色が変わり始める。君の朝が始まる。');pg.click('#bDir');pg.wait_for_timeout(500)
    pg.evaluate("()=>{CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true}")
    # stub exporter: renders a frame, returns a blob (native AAC is unavailable in this sandbox)
    r=pg.evaluate("""async()=>{const seen=[];const res=await CP.blindSet(async()=>{CP.renderFrame(2);seen.push({lab:document.getElementById('dirsum').textContent,gov:document.getElementById('govt').textContent,loud:CP.S.mixInfo});return {blob:new Blob([new Uint8Array(5000)],{type:'video/mp4'})}});
      return {n:res&&res.length,codes:res&&res.map(x=>x.code),mix:res&&res.map(x=>x.mix),seen,key:CP.S.cmp.key,txt:document.getElementById('blindl').innerText,links:[...document.querySelectorAll('#blindl a')].map(a=>a.download),rev:document.getElementById('revl').innerText,on:CP.S.cmp.on,dirsum:document.getElementById('dirsum').textContent}}""")
    chk('BL1 three files produced with blind names P/Q/R',r['n']==3 and r['codes']==['P','Q','R'] and r['links']==['CMP-P.mp4','CMP-Q.mp4','CMP-R.mp4'],r)
    chk('BL2 each variant used exactly once',sorted(r['key'].values())==['A','B','C'] and sorted(r['key'].keys())==['P','Q','R'],r['key'])
    chk('BL3 variant names hidden on screen during export',all('比較案' not in x['lab'] and x['gov']=='' for x in r['seen']),r['seen'])
    chk('BL4 answer not shown before reveal',r['rev']=='' and not any(v in r['txt'] for v in ['A 基本','B 高度','C ディレクター']),r['txt'])
    af=[m['after'] for m in r['mix']]
    chk('BL5 loudness matched within 0.5 dB across variants',max(af)-min(af)<=.5,[m for m in r['mix']])
    chk('BL6 loudness matching actually changed levels (before differ)',max(m['before'] for m in r['mix'])-min(m['before'] for m in r['mix'])>0.05,[m['before'] for m in r['mix']])
    chk('BL7 comparison mode switched off afterwards',r['on']==False)
    rev=pg.evaluate("()=>{CP.revealKey();return document.getElementById('revl').innerText}")
    chk('BL8 reveal shows mapping for P/Q/R',all(('動画'+c) in rev for c in 'PQR') and 'A 基本' in rev and 'C ディレクター' in rev,rev)
    # random order varies: run 6 times and check the mapping is not always the same
    maps=set()
    for i in range(6):
        k=pg.evaluate("""async()=>{await CP.blindSet(async()=>({blob:new Blob([new Uint8Array(3000)])}));return JSON.stringify(CP.S.cmp.key)}""");maps.add(k)
    chk('BL9 assignment is randomised (>=2 different mappings in 6 runs)',len(maps)>=2,maps)
    # same script / lines / length across variants
    same=pg.evaluate("""async()=>{const L=[],D=[];await CP.blindSet(async()=>{L.push(JSON.stringify(CP.S.ln));D.push(CP.S.base.D);return {blob:new Blob([new Uint8Array(3000)])}});return [new Set(L).size,new Set(D).size]}""")
    chk('BL10 same subtitle lines and length across the 3',same==[1,1],same)
    # failure path
    f=pg.evaluate("""async()=>{const r=await CP.blindSet(async()=>null);return {r,txt:document.getElementById('blindl').textContent,on:CP.S.cmp.on}}""")
    chk('BL11 export failure reported, comparison mode off',f['r'] is None and '失敗' in f['txt'] and f['on']==False,f)
    # perf summary function
    pf=pg.evaluate("()=>{CP.PF.f=[10,12,11,30,9,10,11,12,10,11];CP.PF.m=50*1048576;CP.PF.t0=performance.now()-2000;return CP.perfSummary({T:{total:3000}})}")
    chk('BL12 perf summary: avg/p95/max/heap computed',pf['frames']==10 and pf['maxMs']==30 and pf['heapMB']==50 and 10<pf['avgMs']<15,pf)
    chk('BL13 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
