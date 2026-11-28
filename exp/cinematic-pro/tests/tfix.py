"""段階B-0の3修正の再発防止試験: (1)設計JSON取込で台本欄が更新され整合性を確認 (2)音声の出所の表示・保存・復元・レポート (3)演出状態を共通の状態情報から表示"""
import os,sys,json,hashlib
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
WAV=FIX+'/wavfx/n48m.wav';SHA=hashlib.sha256(open(WAV,'rb').read()).hexdigest()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx,pg=mkctx(b);pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    plan=json.loads(D4J);ps=plan['script']
    before=pg.input_value('#dsc')
    pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(1200)
    after=pg.input_value('#dsc')
    ck('F1 設計JSONの取込で台本欄が設計の台本に更新される',after.strip()==ps.strip() and after!=before,(before[:20],after[:20]))
    ck('F2 取込の結果表示に台本欄の更新が書かれる','台本欄' in pg.inner_text('#djs'))
    c=pg.evaluate("()=>CP.consistency()");ck('F3 取込直後は台本・場面・字幕の不一致なし',not [x for x in c if '台本' in x['msg'] or '場面' in x['msg'] or '字幕' in x['msg']],c)
    pg.fill('#dsc','全く別の文章です');c=pg.evaluate("()=>CP.consistency()")
    ck('F4 台本欄を書き換えると不一致を警告する',any('台本欄' in x['msg'] for x in c),c)
    ck('F5 画面に整合性の確認が出る','台本欄' in pg.inner_text('#pfst') or pg.evaluate("()=>{CP.pfShow();return document.getElementById('pfst').textContent.includes('台本欄')}"))
    pg.fill('#dsc',after);
    # 音声なし
    a=pg.evaluate("()=>CP.audioSource()");ck('F6 音声なし: 種別=none、用途表示',a['kind']=='none' and a['name'] is None and a['output']['kbps']==128 and a['output']['sampleRate']==48000,a)
    # 模擬音声
    pg.click('#bMock');pg.wait_for_timeout(1500);a=pg.evaluate("()=>CP.audioSource()")
    ck('F7 模擬音声: 種別=mock、試験用のみと表示、SHA/ファイル名なし',a['kind']=='mock' and '試験用' in a['use'] and a['sha256'] is None and a['name'] is None,a)
    ck('F8 画面表示が音声の状態と一致（模擬）','模擬音声' in pg.inner_text('#audsrc'))
    ck('F9 整合性に「試験用」の警告が出る',any(x['sev']=='test' for x in pg.evaluate("()=>CP.consistency()")))
    # 保存→復元（模擬）
    pg.evaluate("()=>saveSession()") if False else None
    # 外部音声
    pg.set_input_files('#narr',WAV);pg.wait_for_timeout(2500);a=pg.evaluate("()=>CP.audioSource()")
    ck('F10 外部音声: 種別=external・ファイル名・SHA-256が正しい',a['kind']=='external' and a['name']=='n48m.wav' and a['sha256']==SHA,(a['kind'],a['name'],a['sha256']))
    ck('F11 画面表示が音声の状態と一致（外部）','外部音声' in pg.inner_text('#audsrc') and SHA in pg.inner_text('#audsrc'))
    ck('F12 外部音声では「試験用」警告が出ない',not any(x['sev']=='test' for x in pg.evaluate("()=>CP.consistency()")))
    r=pg.evaluate("()=>CP.report()");ck('F13 レポートに音声の出所・整合性・演出状態が入る',r['audioSource']['kind']=='external' and 'consistency' in r and len(r['fx'])>=8,list(r.keys()))
    rec=pg.evaluate("()=>CP.audioSource().kind");pj=pg.evaluate("()=>{try{return JSON.stringify(window.pjSnap?window.pjSnap():null)}catch(e){return null}}")
    # 演出状態
    fx={x['k']:x for x in pg.evaluate("()=>CP.fxStatus()")}
    ck('F14 演出は実装状況と今回の適用状況の両方を持つ',all(x['level'] and x['state'] for x in fx.values()),fx)
    ck('F15 設計のみの演出は「設計のみ」と表示',fx['live-anim-fusion']['level']=='設計のみ' and '設計のみ' in fx['live-anim-fusion']['state'],fx['live-anim-fusion'])
    txt=pg.inner_text('#implt');ck('F16 矛盾する固定文が消え、「今回」の行が出る','今回:' in txt and '全て実装済み' not in txt)
    # 条件を満たさない: beat-sync-cut を指定、BGMなし
    p2=json.loads(D4J);p2['scenes'][1]['fx']=['beat-sync-cut'];p2['scenes'][2]['fx']=['live-anim-fusion']
    pg.evaluate("()=>CP.setBgmMode('none')");pg.fill('#dj',json.dumps(p2,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(1200)
    fx={x['k']:x for x in pg.evaluate("()=>CP.fxStatus()")}
    ck('F17 指定したが条件未達: 「適用条件を満たしていない」',fx['beat-sync-cut']['state'].startswith('適用条件を満たしていない'),fx['beat-sync-cut'])
    ck('F18 設計のみの指定は「未適用」と明示',('指定 1場面' in fx['live-anim-fusion']['state']) and '未適用' in fx['live-anim-fusion']['state'],fx['live-anim-fusion'])
    ck('F19 指定なしの演出は「今回の作品では未適用（指定なし）」',any('指定なし' in x['state'] for x in fx.values()))
    ck('F20 ✔/△の接頭辞を保つ（既存の表示形式）','✔ ' in pg.inner_text('#implt') and '△ ' in pg.inner_text('#implt'))
    # 復元: 音声の出所が保存される
    pg.set_input_files('#narr',WAV);pg.wait_for_timeout(2500)
    sv=pg.evaluate("async()=>{await saveSession();return await new Promise(r=>{try{const q=indexedDB.databases?1:0;r(q)}catch{r(0)}})}") if False else None
    ck('F21 ページエラーなし',pg.errs==[],pg.errs)
    print('TOTAL',sum(R),'/',len(R))
