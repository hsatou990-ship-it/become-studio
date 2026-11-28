"""段階B-0 r14: 取得管理・照合・端末内保存・隔離推論の試験。外部ホストは Playwright で模擬（実際の通信なし）。
ライブラリは試験用の疑似ライブラリ（実物ではない）。実モデルの精度・速度の測定ではない。"""
import os,json,subprocess,tempfile,hashlib,base64,time
from playwright.sync_api import sync_playwright
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio')
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else str(info)[:500])
REV='6b7c523703ae26e39be4b03774966f8571c7f523';M='Xenova/clip-vit-base-patch32';ORT='1.22.0-dev.20250409-89f8206ba4'
LIB=r'''export const env={allowLocalModels:false,allowRemoteModels:true,localModelPath:'/models/',useBrowserCache:true,backends:{onnx:{wasm:{}}},__stub:true,version:'fake'};
const W=[[/dark|night|corridor|tunnel|empty/,[0,0,1]],[/clock|watch|hands/,[1,0,0]],[/sunrise|dawn|window|person|walk/,[0,1,0]],[/logo|watermark|text overlay/,[1,1,0]]];
const tv=t=>{const s=String(t).toLowerCase();for(const[r,v]of W)if(r.test(s))return v;return[.3,.3,.3]};
async function need(p){const r=await fetch(env.localModelPath+'Xenova/clip-vit-base-patch32/'+p);if(!r.ok)throw new Error('missing '+p);return r.arrayBuffer()}
async function ortOK(){const w=env.backends.onnx.wasm.wasmPaths;const a=await fetch(w.wasm),b=await fetch(w.mjs);if(!a.ok||!b.ok)throw new Error('ort missing')}
async function probe(t){if(t==='probe'){try{await fetch('https://huggingface.co/x');return[0,1,0]}catch{return[1,0,0]}}if(t==='storage'){try{localStorage.getItem('x');return[0,1,0]}catch{return[1,0,0]}}return tv(t)}
export class AutoTokenizer{static async from_pretrained(){await need('tokenizer.json');return t=>({texts:t})}}
export class CLIPTextModelWithProjection{static async from_pretrained(id,cfg){if(env.allowRemoteModels)throw new Error('remote allowed');if(cfg.dtype!=='uint8')throw new Error('dtype');await need('onnx/text_model_uint8.onnx');await ortOK();return Object.assign(async i=>{const o=[];for(const t of i.texts)o.push(...await probe(t));return{text_embeds:{dims:[i.texts.length,3],data:Float32Array.from(o)}}},{dispose:async()=>{}})}}
export class AutoProcessor{static async from_pretrained(){await need('preprocessor_config.json');return im=>({im})}}
export class CLIPVisionModelWithProjection{static async from_pretrained(){await need('onnx/vision_model_uint8.onnx');return Object.assign(async p=>({image_embeds:{dims:[1,3],data:Float32Array.from(p.im.c)}}),{dispose:async()=>{}})}}
export class RawImage{static fromCanvas(c){const q=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let r=0,g=0,b=0,n=0;for(let i=0;i<q.length;i+=16){r+=q[i];g+=q[i+1];b+=q[i+2];n++}return{c:[r/n/255+1e-3,g/n/255+1e-3,b/n/255+1e-3]}}}
'''.encode()
rnd=lambda n,s:hashlib.sha256(s.encode()).digest()*(n//32+1)
FILES={'config.json':b'{"a":1}','merges.txt':b'a b\n','preprocessor_config.json':b'{"size":224}','special_tokens_map.json':b'{}','tokenizer.json':b'{"t":1}','tokenizer_config.json':b'{}','vocab.json':b'{"a":1}','onnx/vision_model_uint8.onnx':rnd(300000,'v')[:300000],'onnx/text_model_uint8.onnx':rnd(200000,'t')[:200000]}
ORTF={'ort-wasm-simd-threaded.jsep.mjs':b'export default 1;','ort-wasm-simd-threaded.jsep.wasm':b'\0asm'+rnd(5000,'w')[:5000]}
sha=lambda b:hashlib.sha256(b).hexdigest();b64=lambda b:base64.b64encode(hashlib.sha256(b).digest()).decode()
gsha=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
D=tempfile.mkdtemp()
for c,k in {'blue':'0x0000ff','red':'0xff0000','green':'0x00ff00','yellow':'0xffff00'}.items():subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=%s:s=320x240:d=3:r=15'%c,'-pix_fmt','yuv420p','-c:v','libx264',D+'/%s.mp4'%c],check=True)
URL='http://127.0.0.1:8765/exp/cinematic-pro/ai/measure.html?adapter=transformers'
def tree(sub,bad=False):
    out=[]
    for p,b in FILES.items():
        if (sub=='onnx')!=p.startswith('onnx/'):continue
        it={'type':'file','path':p,'size':len(b),'oid':gsha(b)}
        if p.startswith('onnx/'):it['lfs']={'oid':sha(b) if not bad else '0'*64,'size':len(b)};it['oid']='x'*40
        out.append(it)
    return out
class Net:
    def __init__(s,bad=False,slow=0,fail=None,redir=False):s.redir=redir;s.log=[];s.bad=bad;s.slow=slow;s.fail=fail;s.attempts={}
    def handler(s,route):
        u=route.request.url;s.log.append(u);H={'access-control-allow-origin':'*'}
        def js(o):route.fulfill(status=200,body=json.dumps(o),content_type='application/json',headers=H)
        if '/api/models/'+M+'/tree/'+REV+'/onnx' in u:return js(tree('onnx',s.bad))
        if '/api/models/'+M+'/tree/'+REV in u:return js(tree('root'))
        if u.startswith('https://huggingface.co/'+M+'/resolve/'+REV+'/'):
            p=u.split('/resolve/'+REV+'/')[1];s.attempts[p]=s.attempts.get(p,0)+1
            if s.redir and p.startswith('onnx/'):return route.fulfill(status=302,headers={'location':'https://cas-bridge.xethub.hf.co/'+p,**H})
            if s.fail and p==s.fail:return route.abort()
            if s.slow:time.sleep(s.slow)
            return route.fulfill(status=200,body=FILES[p],headers=H)
        if u.endswith('/transformers@3.8.1/package.json'):return js({'version':'3.8.1','dependencies':{'onnxruntime-web':ORT}})
        if 'data.jsdelivr.com' in u and 'transformers@3.8.1' in u:return js({'files':[{'name':'/dist/transformers.min.js','hash':b64(LIB),'size':len(LIB)},{'name':'/dist/transformers.js','hash':'x','size':1}]})
        if 'data.jsdelivr.com' in u and 'onnxruntime-web@'+ORT in u:return js({'files':[{'name':'/dist/'+n,'hash':b64(b),'size':len(b)} for n,b in ORTF.items()]+[{'name':'/dist/ort.min.js','hash':'x','size':9},{'name':'/dist/ort-wasm-simd-threaded.wasm','hash':'x','size':9}]})
        if u=='https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1/dist/transformers.min.js':s.attempts['lib']=s.attempts.get('lib',0)+1;return route.fulfill(status=200,body=LIB,content_type='text/javascript',headers=H)
        for n,b in ORTF.items():
            if u.endswith('/onnxruntime-web@'+ORT+'/dist/'+n):return route.fulfill(status=200,body=b,headers=H)
        route.abort()
    def files(s):return [u for u in s.log if '/resolve/' in u or u.endswith('.min.js') or '/dist/ort' in u]
def newpage(p,net):
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});ctx.route(lambda u:not u.startswith('http://127.0.0.1'),net.handler);pg=ctx.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(400);return b,pg
def resolve(pg):
    pg.click('#aRes');pg.wait_for_function("()=>!document.getElementById('aRes').disabled",timeout=20000);return pg.inner_text('#aPlan')
def code(pg):
    import re;m=re.search(r'承認コード: ([0-9a-f]{8})',pg.inner_text('#aPlan'));return m.group(1) if m else None
def settle(pg,t=30000):pg.wait_for_function("()=>document.getElementById('aGo').disabled===false||document.getElementById('aSt').textContent.includes('取得完了')||document.getElementById('aSt').textContent.includes('停止')",timeout=t);pg.wait_for_timeout(300)
plan={"schema":"become.design/1","title":"t","scenes":[{"text":"あ","search":{"queries":["dark empty corridor"],"avoid":["logo"]},"camera":"static-hold","grade":"cold-teal"},{"text":"い","search":{"queries":["clock hands close up"],"avoid":["logo"]},"camera":"static-hold","grade":"cold-teal"},{"text":"う","search":{"queries":["person at window sunrise"],"avoid":["logo"]},"camera":"static-hold","grade":"warm-gold"}]}
def run_analysis(pg):
    vids=['blue','red','green','yellow'];pg.fill('#dj',json.dumps(plan,ensure_ascii=False));pg.set_input_files('#vf',[D+'/%s.mp4'%v for v in vids]);pg.wait_for_timeout(300)
    for i,v in enumerate(vids):pg.select_option('#lab select >> nth=%d'%i,str(i if v!='yellow' else -1))
    pg.select_option('#be','wasm');pg.click('#run');pg.wait_for_function("()=>!document.getElementById('run').disabled",timeout=120000);return json.loads(pg.inner_text('#out'))
with sync_playwright() as p:
    net=Net();b,pg=newpage(p,net)
    ck('Q1 ページを開いただけでは外部通信しない',net.log==[],net.log)
    pg.evaluate("()=>localStorage.setItem('cp_marker','keep')")
    txt=resolve(pg);fl=net.files()
    ck('Q2 取得対象の確認はメタデータのみ（ファイル本体は取得しない）',len(net.log)==5 and not fl,net.log)
    ck('Q3 対象は12ファイル・合計容量・承認コード・ORT版を表示',pg.inner_text('#aList').count('\n')>=12 and '承認コード' in txt and ORT in txt and code(pg),txt)
    exp=sum(len(v) for v in FILES.values())+len(LIB)+sum(len(v) for v in ORTF.values())
    ck('Q4 合計容量が一覧の合計と一致',('%.1f MB'%(exp/1048576)) in txt,(txt,exp))
    ck('Q5 必要な2つのwasm系ファイルだけを選ぶ（他のORT/配布物は取得しない）','ort.min.js' not in pg.inner_text('#aList') and 'transformers.js' not in pg.inner_text('#aList').replace('transformers.min.js',''))
    pg.fill('#aCode','00000000');pg.click('#aGo');pg.wait_for_timeout(500)
    ck('Q6 承認コードが違うと取得しない',not net.files() and '承認コード' in pg.inner_text('#aSt'),pg.inner_text('#aSt'))
    pg.fill('#aCode',code(pg));pg.click('#aGo');settle(pg)
    ck('Q7 取得完了。各ファイルを1回だけ取得',all(v==1 for v in net.attempts.values()) and len(net.attempts)==10 and '取得完了' in pg.inner_text('#aSt'),(net.attempts,pg.inner_text('#aSt')))
    ck('Q8 全ファイルが照合済み・正常で、分析の準備が完了','分析の準備: 完了' in pg.inner_text('#aRdy') and pg.inner_text('#aTab').count('照合済み')==12,pg.inner_text('#aTab'))
    before=len(net.log);pg.click('#aGo');settle(pg)
    ck('Q9 取得済みは再取得しない（重複取得の防止）',len(net.log)==before and net.attempts.get('lib')==1)
    # 推論は通信なし・隔離フレーム
    o=run_analysis(pg);r0=o['runs'][0];ext=[u for u in net.log[before:]]
    ck('Q10 隔離フレームで分析が完了（疑似ライブラリ）・正例>誤例',not r0['errors'] and r0['realModel']==False and r0['eval']['auc']==1 and not r0['falseAccept'],(r0['errors'],r0.get('eval')))
    ck('Q11 分析中の外部通信は0件',ext==[] and r0['download']['files']==0,(ext,r0.get('download')))
    ck('Q12 キャッシュ再利用（2回目は新規0枚）',o['runs'][1]['stages']['framesEmbedded']==0)
    pr=pg.evaluate("async()=>{const m=await (await import('./adapter-sandbox.js')).load({device:'wasm'});const a=await m.embedTexts(['probe']),b=await m.embedTexts(['storage']);await m.dispose();return[Array.from(a[0]),Array.from(b[0])]}")
    ck('Q13 隔離フレームは外部へ接続できない',pr[0]==[1,0,0],pr)
    ck('Q14 隔離フレームは編集画面の保存領域に触れない',pr[1]==[1,0,0],pr)
    ck('Q15 解放後に隔離フレームが残らない',pg.evaluate("()=>document.querySelectorAll('iframe').length")==0)
    # 破損・消失
    pg.evaluate("async()=>{const c=await caches.open(ACQ.A.CACHE);await c.put('https://bs.local/f/vocab.json',new Response('longer-content-than-seven'))}")   # 容量が違う
    pg.click('#aChk');pg.wait_for_timeout(500);ck('Q16 容量の不一致（破損）を検出',('破損（容量不一致）' in pg.inner_text('#aTab')),pg.inner_text('#aTab'))
    pg.evaluate("async()=>{const c=await caches.open(ACQ.A.CACHE);await c.put('https://bs.local/f/merges.txt',new Response('b a\\n'))}")   # 同サイズで内容違い
    pg.click('#aDeep');pg.wait_for_timeout(1500);ck('Q17 同サイズの内容改変を、再検証のハッシュで検出',('破損（ハッシュ不一致）' in pg.inner_text('#aTab')),pg.inner_text('#aTab'))
    pg.evaluate("async()=>{const c=await caches.open(ACQ.A.CACHE);await c.delete('https://bs.local/f/vocab.json')}");pg.click('#aChk');pg.wait_for_timeout(500)
    n=len(net.log);o=run_analysis(pg)
    ck('Q18 消失・破損があると分析を止め、無断で再取得しない',o['runs'][0]['errors'] and '自動では再取得しません' in o['runs'][0]['errors'][0] and len(net.log)==n and '消失（自動では再取得しません）' in pg.inner_text('#aTab'),(o['runs'][0]['errors'],len(net.log)-n))
    # 削除
    pg.click('#aDel');pg.wait_for_timeout(300);ck('Q19 削除はチェックなしでは実行しない','保存した' not in pg.inner_text('#aSt') and 'チェック' in pg.inner_text('#aSt'))
    pg.check('#aDelOk');pg.click('#aDel');pg.wait_for_timeout(500)
    ck('Q20 削除はAIデータだけ（編集画面の保存領域は無傷）',pg.evaluate("()=>localStorage.getItem('cp_marker')")=='keep' and '未取得' in pg.inner_text('#aTab'))
    ck('Q21 ページエラーなし',pg.errs==[],pg.errs);b.close()
    # ハッシュ不一致
    net=Net(bad=True);b,pg=newpage(p,net);resolve(pg);pg.fill('#aCode',code(pg));pg.click('#aGo');settle(pg)
    ck('Q22 公開ハッシュと不一致なら破棄し、未検証のまま（保存・実行しない）','ハッシュ不一致' in pg.inner_text('#aSt') and '分析の準備: 未完了' in pg.inner_text('#aRdy'),(pg.inner_text('#aSt'),pg.inner_text('#aRdy')))
    o=run_analysis(pg);ck('Q23 未検証・未取得では分析しない（通信もしない）',o['runs'][0]['errors'] and 'モデルが利用できません' in o['runs'][0]['errors'][0],o['runs'][0]['errors']);b.close()
    # 未承認ホスト・再試行・中断
    net=Net(fail='vocab.json');b,pg=newpage(p,net);resolve(pg);pg.fill('#aCode',code(pg));pg.click('#aGo');settle(pg)
    ck('Q24 通信失敗の再試行は2回まで（無制限の再試行なし）・原因表示',net.attempts.get('vocab.json')==2 and '停止' in pg.inner_text('#aSt'),(net.attempts,pg.inner_text('#aSt')))
    hk=pg.evaluate("async()=>{const A=ACQ.A;const f=[{kind:'lib',name:'x',url:'https://evil.example/x.js',size:1,hash:{alg:'sha256',hex:'0'},exec:true}];const code=await A.approvalCode(f);try{await A.download({files:f,total:1,code},code,{});return 'sent'}catch(e){return e.message}}")
    ck('Q25 未承認ホストへの接続は停止',('未承認ホスト' in hk) and not any('evil' in u for u in net.log),hk);b.close()
    net=Net(slow=1.5);b,pg=newpage(p,net);resolve(pg);pg.fill('#aCode',code(pg));pg.click('#aGo');pg.wait_for_timeout(2200);pg.click('#aStop');settle(pg)
    ck('Q26 取得を中断でき、取得済みの分は保存されたまま残る','中断' in pg.inner_text('#aSt') and pg.inner_text('#aTab').count('照合済み')>=1,pg.inner_text('#aSt'))
    ck('Q27 ページエラーなし',pg.errs==[],pg.errs);b.close()
    # リダイレクト先が未承認ホストの場合: 原因の表示と、取得済みの保持・再開
    net=Net(redir=True);b,pg=newpage(p,net);resolve(pg);cd=code(pg);pg.fill('#aCode',cd);pg.click('#aGo');settle(pg,40000);pg.wait_for_timeout(500)
    cs=pg.inner_text('#aCsp')
    ck('Q28 CSP停止の対象ファイル・要求URL・停止したホスト・指示を表示',('onnx/vision_model_uint8.onnx' in cs) and ('要求したURL: https://huggingface.co/' in cs) and '停止したホスト' in cs and 'connect-src' in cs,cs)
    st=pg.evaluate("async()=>(await ACQ.A.status(false)).rows.filter(r=>r.verified&&r.state==='ok').length")
    ck('Q29 取得済みの設定ファイル7件は保持される（CSPの緩和なし）',st==7 and '分析の準備: 未完了' in pg.inner_text('#aRdy'),st)
    pg.reload();pg.wait_for_timeout(500);net.redir=False;m0=len(net.log)
    pg.click('#aResume');pg.wait_for_timeout(500);ck('Q30 再開は保存済みの取得対象を使い、メタデータを再取得しない・残り5件を表示',len(net.log)==m0 and '残り 5 件' in pg.inner_text('#aList'),(len(net.log)-m0,pg.inner_text('#aList')))
    pg.fill('#aCode',cd);pg.click('#aGo');settle(pg)
    got=[u for u in net.log[m0:] if '/resolve/' in u]
    ck('Q31 再開では残り5件だけ取得し、7件は再取得しない・全件照合済みで準備完了',len(net.log[m0:])==5 and len(got)==2 and '分析の準備: 完了' in pg.inner_text('#aRdy'),(net.log[m0:],pg.inner_text('#aRdy')))
    ck('Q32 ページエラーなし',pg.errs==[],pg.errs);b.close()
print('TOTAL',sum(R),'/',len(R))
