"""段階B-0: AI分析測定ページの試験（疑似モデルで流れだけを検証。実モデルの精度・速度ではない）。
安全停止／外部通信の遮断／キャッシュ再利用／正例誤例の評価／メモリ解放の記録／ライブラリ未配置時の停止"""
import os,json,subprocess,tempfile
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio')
from playwright.sync_api import sync_playwright
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else str(info)[:400])
D=tempfile.mkdtemp();cols={'blue':'0x0000ff','red':'0xff0000','green':'0x00ff00','yellow':'0xffff00'}
for k,c in cols.items():subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=%s:s=320x240:d=3:r=15'%c,'-pix_fmt','yuv420p','-c:v','libx264',D+'/%s.mp4'%k],check=True)
plan={"schema":"become.design/1","title":"t","scenes":[{"text":"変わるのが、怖いか。","search":{"queries":["dark empty corridor"],"avoid":["logo"]},"camera":"push-in-slow","grade":"cold-teal","emotion":{"valence":-.6,"arousal":.4}},{"text":"時間は止まらない。","search":{"queries":["clock hands close up"],"avoid":["logo"]},"camera":"static-hold","grade":"cold-teal","emotion":{"valence":-.7,"arousal":.6}},{"text":"今日から始めよう。","search":{"queries":["person at window sunrise"],"avoid":["logo"]},"camera":"static-hold","grade":"warm-gold","emotion":{"valence":.4,"arousal":.4}}]}
URL='http://127.0.0.1:8765/exp/cinematic-pro/ai/measure.html'
def setup(pg,q,vids):
    pg.goto(URL+q);pg.fill('#dj',json.dumps(plan,ensure_ascii=False));pg.set_input_files('#vf',[D+'/%s.mp4'%v for v in vids]);pg.wait_for_timeout(300)
def finish(pg,t=60000):
    pg.click('#run');pg.wait_for_function("()=>!document.getElementById('run').disabled",timeout=t)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));ext=[]
    pg.on('request',lambda r:ext.append(r.url) if not r.url.startswith(('http://127.0.0.1:8765','blob:','data:')) else None)
    # 1 ライブラリ未配置: 通信せず安全停止（既定アダプタ）
    setup(pg,'',['blue']);finish(pg);o=json.loads(pg.inner_text('#out'))
    ck('M1 モデル未配置では、通信せず安全に停止する',o['runs'][0]['errors'] and o['runs'][0].get('stoppedSafely') and not ext,(o['runs'][0]['errors'],ext))
    ck('M2 停止後もボタンが使える（固まらない）',not pg.evaluate("()=>document.getElementById('run').disabled"))
    # 2 疑似モデルで通し
    vids=['blue','red','green','yellow'];setup(pg,'?adapter=stub',vids)
    for i,v in enumerate(vids):pg.select_option('#lab select >> nth=%d'%i,str(i if v!='yellow' else -1))
    pg.select_option('#be','wasm');finish(pg);o=json.loads(pg.inner_text('#out'));r0,r1=o['runs'][0],o['runs'][1]
    ck('M3 通しで完了（エラーなし）、疑似モデルと明示',not r0['errors'] and r0['realModel']==False and '疑似' in pg.inner_text('#res'),r0['errors'])
    ck('M4 正例が誤例より高い（AUC=1）、誤採用0・見逃し0',r0['eval']['auc']==1 and not r0['falseAccept'] and not r0['missed'],r0['eval'])
    ck('M5 除外対象（黄=logo/text）が avoid として検出される',any('yellow' in x for x in r0['avoidFlag']),r0['avoidFlag'])
    ck('M6 2回目はキャッシュ再利用（新規0枚）で、再利用数を記録',r1['warmRerun'] and r1['stages']['framesEmbedded']==0 and r1['cacheReuse']['hit']>0,r1['stages'])
    ck('M7 読込・テキスト・画像の時間と、メモリ（読込前/ピーク/解放後）を記録',all(k in r0['stages'] for k in['loadMs','textMs','imageMs','memBefore','memPeak','memAfterRelease']),r0['stages'])
    ck('M8 取得容量を記録（同一オリジンのみ）',r0.get('download') is not None)
    ck('M9 端末温度・端末全体メモリは「未測定」と明記',all(x in o['unmeasured'] for x in['端末温度','端末全体のメモリ使用量']) and '未測定' in pg.inner_text('#env'))
    ck('M10 測定中も外部通信なし',not ext,ext)
    # 3 外部通信の遮断（コード側）
    r=pg.evaluate("()=>fetch('https://example.com/x').then(()=>'sent',e=>String(e.message))");ck('M11 外部URLへの通信は拒否される',('許可されていません' in r) or ('Refused' in r) or ('Failed' in r),r)
    # 4 エラーで安全停止（読み込み失敗）
    setup(pg,'?adapter=stub&failAt=load',['blue']);finish(pg);o=json.loads(pg.inner_text('#out'))
    ck('M12 読み込み失敗でも安全停止し、理由を残す',o['runs'][0]['errors'] and '読み込み失敗' in o['runs'][0]['errors'][0] and o['runs'][0].get('stoppedSafely'),o['runs'][0])
    # 5 不明なアダプタは読まない
    setup(pg,'?adapter=http://evil.example/x.js',['blue']);finish(pg);o=json.loads(pg.inner_text('#out'))
    ck('M13 許可リスト外のアダプタは読み込まない',any('不明なアダプタ' in e for e in o['runs'][0]['errors']) and not ext,(o['runs'][0]['errors'],ext))
    # 6 中止
    setup(pg,'?adapter=stub',vids);pg.click('#run');pg.click('#stop');pg.wait_for_function("()=>!document.getElementById('run').disabled",timeout=60000)
    ck('M14 中止要求で止まり、操作可能に戻る',not pg.evaluate("()=>document.getElementById('run').disabled"))
    ck('M15 入力なしは安全に案内',(lambda: (pg.goto(URL+'?adapter=stub'),pg.click('#run'),pg.wait_for_timeout(300),'設計JSON' in pg.inner_text('#st') or '動画' in pg.inner_text('#st'))[-1])())
    ck('M16 ページエラーなし',pg.errs==[],pg.errs)
print('TOTAL',sum(R),'/',len(R))
