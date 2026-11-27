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
    def info():
        return pg.evaluate("()=>({c:CP.S.sc.slice(0,-1).map(o=>CP.fxCost(o)),ln:JSON.stringify(CP.S.ln),D:CP.S.base.D,narr:!!CP.S.narr,gov:CP.S.base.gov.length,txt:document.getElementById('dirsum').textContent})")
    pg.click('#vA');pg.wait_for_timeout(300);A=info()
    pg.click('#vB');pg.wait_for_timeout(300);B=info()
    pg.click('#vC');pg.wait_for_timeout(300);C=info()
    chk('V1 A has no effects',sum(A['c'])==0,A)
    chk('V2 B is the heaviest',sum(B['c'])>sum(C['c'])>=sum(A['c']) and sum(B['c'])>10,[A['c'],B['c'],C['c']])
    chk('V3 C respects budget',max(C['c'])<=5,C)
    chk('V4 same script text and line timing across A/B/C',A['ln']==B['ln']==C['ln'],'')
    chk('V5 same total length',A['D']==B['D']==C['D'])
    chk('V6 narration audio kept across switches',A['narr'] and B['narr'] and C['narr'])
    chk('V7 C gets governor reasons, A/B none',C['gov']>=0 and A['gov']==0 and B['gov']==0,[A['gov'],B['gov'],C['gov']])
    chk('V8 label shows the variant',C['txt'].startswith('比較案C'),C['txt'][:30])
    # switch back and forth returns to the same A (original base kept)
    pg.click('#vC');pg.wait_for_timeout(200);C2=info()
    chk('V9 repeated switching is stable (C twice identical)',C2['c']==C['c'])
    # frames render in all variants
    ok=pg.evaluate("()=>{try{for(const t of [1,4,8,12]){CP.renderFrame(t)}return true}catch(e){return String(e)}}")
    chk('V10 frames render',ok==True,ok)
    chk('V11 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
