from playwright.sync_api import sync_playwright
URL='http://127.0.0.1:8765/exp/eval/index.html'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:300])
MAX=[20,15,15,15,10,10,10,5]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400)
    def fill(v,vals):
        for i,x in enumerate(vals):pg.fill(f'#s{v}{i}',str(x))
    def gate(v,val):
        for i in range(3):pg.select_option(f'#g{v}{i}',val)
    chk('E1 weights sum to 100',sum(MAX)==100)
    chk('E2 initial: not scored, shown as in progress',('未評価' in pg.inner_text('#res')))
    chk('E2b unscored shows 未評価 (never 0 points) in the record text',('未評価' in pg.input_value('#out')) and ('合計0点' not in pg.input_value('#out')),pg.input_value('#out')[:80])
    fill('P',MAX);chk('E3 full marks = 100',pg.evaluate("()=>EV.total('P')")==100)
    chk('E4 100 points but gates unconfirmed -> not publishable',('公開不可' in pg.inner_text('#res')) and '合格が揃っていません' in pg.inner_text('#res'),pg.inner_text('#res'))
    gate('P','合格');chk('E5 100 + all gates pass -> 公開可',('品質目標達成' in pg.inner_text('#res')),pg.inner_text('#res'))
    fill('Q',[18,13,13,13,9,9,9,4]);gate('Q','合格')   # 88
    chk('E6 88 points -> below target',pg.evaluate("()=>EV.total('Q')")==88 and '未達' in pg.inner_text('#res'),pg.inner_text('#res'))
    fill('R',[19,14,14,14,9,9,8,4]);gate('R','合格');pg.select_option('#gR1','不合格') # 91 but terms fail
    chk('E7 91 points but terms failed -> 公開不可',pg.evaluate("()=>EV.total('R')")==91 and pg.evaluate("()=>EV.verdict('R').t").find('公開不可')>=0,pg.evaluate("()=>EV.verdict('R').t"))
    pg.fill('#sP0','99');chk('E8 over-max input clamped to 20',pg.input_value('#sP0')=='20')
    pg.fill('#sP1','-5');chk('E9 negative clamped to 0',pg.input_value('#sP1')=='0')
    pg.fill('#sP1','15')
    pg.select_option('#mP','C');pg.select_option('#mQ','A');pg.select_option('#mR','B');pg.click('#rv')
    s=pg.inner_text('#sum');chk('E10 reveal maps P/Q/R to A/B/C and finds best',('最高点: C案' in s) and 'A案（動画Q）: 88点' in s,s)
    pg.select_option('#mR','A');pg.click('#rv');chk('E11 duplicate mapping rejected',('1つずつ' in pg.inner_text('#sum')))
    pg.reload();pg.wait_for_timeout(300)
    chk('E12 inputs persist after reload (localStorage)',pg.input_value('#sQ0')=='18')
    chk('E13 record text lists totals and gates',('動画Q 合計88点' in pg.input_value('#out')) and '著作権合格' in pg.input_value('#out'))
    chk('E14 no page errors',not errs,errs)
    print('ALL',all(R),sum(R),'/',len(R))
