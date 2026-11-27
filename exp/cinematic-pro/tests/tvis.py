from playwright.sync_api import sync_playwright
V='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/vid/'
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:300])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new']);pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    pg.goto('http://127.0.0.1:8765/exp/vision/index.html')
    names=['cuts','sharp','blur','dup','still','wide']
    pg.set_input_files('#f',[V+n+'.mp4' for n in names]);pg.click('#go')
    for _ in range(120):
        pg.wait_for_timeout(500)
        if '近いフレーム' in pg.inner_text('#dup'):break
    txt=pg.inner_text('#o');dup=pg.inner_text('#dup');print(txt);print(dup)
    cards={}
    for c in pg.query_selector_all('.card'):
        t=c.inner_text();cards[t.split('｜')[0]]=t
    import re
    sc=lambda k:int(re.search(r'簡易総合 (\d+)',cards[k+'.mp4']).group(1))
    sh=lambda k:int(re.search(r'鮮明 (\d+)',cards[k+'.mp4']).group(1))
    chk('V1 all 6 analyzed',len(cards)==6 and all('簡易総合' in v for v in cards.values()),list(cards))
    chk('V2 scene cuts found at 2s and 4s in cuts.mp4','2' in re.search(r'シーン変化 ([^｜]*)',cards['cuts.mp4']).group(1) and '4' in re.search(r'シーン変化 ([^｜]*)',cards['cuts.mp4']).group(1),cards['cuts.mp4'])
    chk('V3 no false cuts in still',('シーン変化 なし' in cards['still.mp4']),cards['still.mp4'])
    chk('V4 sharp > blur sharpness',sh('sharp')>sh('blur')+10,(sh('sharp'),sh('blur')))
    chk('V5 vertical fit: portrait > landscape',int(re.search(r'縦型適合 (\d+)',cards['cuts.mp4']).group(1))>int(re.search(r'縦型適合 (\d+)',cards['wide.mp4']).group(1)))
    def pr(a,b):
        m=re.search(re.escape(a)+' ⇔ '+re.escape(b)+r'：最小距離 (\d+)/64・近いフレームの割合 (\d+)%',dup);return int(m.group(2)) if m else None
    chk('V6 re-encoded copy flagged duplicate',pr('cuts.mp4','dup.mp4')>=50,dup)
    chk('V7a different videos not flagged',pr('cuts.mp4','sharp.mp4')<50,dup)
    chk('V7b flat video not flagged against anything',all(pr(a,b)<50 for a,b in [('cuts.mp4','still.mp4'),('sharp.mp4','still.mp4'),('dup.mp4','still.mp4'),('still.mp4','wide.mp4')]),dup)
    chk('V7c partial overlap not full duplicate (cuts vs wide)',pr('cuts.mp4','wide.mp4')<50,dup)
    chk('V8 honest disclaimer present','美しさ・感情・台本との意味一致・権利の確認には使えません' in pg.inner_text('body'))
    chk('V9 no errors',not errs,errs)
    b.close()
print('ALL',all(R),sum(R),'/',len(R))
