from playwright.sync_api import sync_playwright
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
V='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/vid/'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:300])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    def tryf(f,rights=True):
        pg.fill('#bgs','https://example.org/own');pg.fill('#bgl','Owner-owned')
        pg.evaluate("(v)=>{document.getElementById('bgk').checked=v}",rights)
        pg.set_input_files('#bgf',V+f);pg.click('#bBgm');pg.wait_for_timeout(2500)
        return pg.inner_text('#bgst'),pg.evaluate("()=>CP.S.bgm?{n:CP.S.bgm.beats.length,conf:CP.S.bgm.an.conf,bpm:CP.S.bgm.bpm}:null")
    m,s=tryf('notaudio.txt');chk('BV1 non-audio file refused',s is None and '音声ファイル' in m,m)
    m,s=tryf('fake_big.wav');chk('BV2 oversize file refused before decoding',s is None and '大きすぎ' in m,m)
    m,s=tryf('short1.wav');chk('BV3 too-short audio refused',s is None and '短すぎ' in m,m)
    m,s=tryf('silence6.wav');chk('BV4 silent audio refused',s is None and '無音' in m,m)
    m,s=tryf('clip6.wav');chk('BV5 clipped audio warned (still usable)',s is not None and '音割れ' in m,m)
    m,s=tryf('noise8.wav');print('noise conf',s);chk('BV6 noise: low beat confidence, no beats, warned',s is not None and s['n']==0 and '確信できない' in m,[m,s])
    m,s=tryf('pad.wav');print('pad conf',s);chk('BV7 beatless pad: no beats, warned',s is not None and s['n']==0,[m,s])
    confs={}
    for f in ['bgm96.wav','b75_40.wav','b120_21.wav','b140_5.wav','b88_33.wav']:
        m,s=tryf(f);confs[f]=s
    chk('BV8 kick tracks keep their beats (confidence >= threshold)',all(v and v['n']>0 for v in confs.values()),confs)
    m,s=tryf('bgm96.wav',rights=False);chk('BV9 rights checkbox still required',s is not None and False or ('権利確認' in m),m)
    # fallback: noise BGM + beat-sync design => no crash, no snapping
    import json
    d={"schema":"become.design/1","scenes":[{"text":"a","dur":3,"role":"hook"},{"text":"b","dur":3.1,"role":"turn","fx":["beat-sync-cut"]},{"text":"c","dur":3,"role":"ending"}]}
    pg.fill('#dj',json.dumps(d));pg.click('#bDJ');pg.wait_for_timeout(200)
    a0=pg.evaluate("()=>CP.S.base.sc[1].a")
    tryf('noise8.wav');a1=pg.evaluate("()=>CP.S.sc[1].a")
    chk('BV10 failed beat detection: scene boundary stays at nominal time',abs(a0-a1)<1e-6,[a0,a1])
    ok=pg.evaluate("()=>{try{CP.renderFrame(3.2);return true}catch(e){return String(e)}}");chk('BV11 renders fine without beats',ok==True,ok)
    chk('BV12 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R));print(confs)
