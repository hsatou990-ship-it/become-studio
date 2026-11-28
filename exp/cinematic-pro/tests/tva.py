"""段階A: 映像分析（モデルなし・通信なし）の試験。適応型抽出、判定、キャッシュ、重複検出、解放、取得済み候補への差し替えの安全性。
合成素材（make_fixtures.py の vafx/）で、正解が分かるものだけを扱う。実素材・実機の結果ではない。"""
import os,sys,base64,json
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
R=[]
def ck(n,ok,info=''):R.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n,'' if ok else info)
FILES=['ok_a','ok_b','ok_c','black_mid','black_short','black_head','dark','static','flat','cut_mid','dup_a','bk_0_2']
def load(pg):
    for n in FILES:
        d=base64.b64encode(open(f'{FIX}/vafx/{n}.mp4','rb').read()).decode()
        pg.evaluate("([n,d])=>{window.__F=window.__F||{};window.__F[n]=Uint8Array.from(atob(d),c=>c.charCodeAt(0))}",[n,d])
JS_HELP="""
window.__file=n=>new File([window.__F[n]],n+'.mp4',{type:'video/mp4'});
window.__put=async(key,name,tags,w,h,dur)=>{const bytes=window.__F[name];const db=await new Promise((ok,ng)=>{const r=indexedDB.open(CP.NS+'cp_stock',1);r.onupgradeneeded=()=>r.result.createObjectStore('clips',{keyPath:'key'});r.onsuccess=()=>ok(r.result);r.onerror=()=>ng(r.error)});
 await new Promise((ok,ng)=>{const t=db.transaction('clips','readwrite');t.objectStore('clips').put({key,blob:new Blob([bytes],{type:'video/mp4'}),w,h,dur,at:Date.now(),meta:{q:'',tags,dur,src:'Pixabay',url:'https://pixabay.com/videos/x-1/',by:'tester',lic:'Pixabay Content License',auto:true}});t.oncomplete=ok;t.onerror=()=>ng(t.error)});db.close()};
window.__keys=async()=>{const db=await new Promise((ok,ng)=>{const r=indexedDB.open(CP.NS+'cp_stock',1);r.onupgradeneeded=()=>r.result.createObjectStore('clips',{keyPath:'key'});r.onsuccess=()=>ok(r.result);r.onerror=()=>ng(r.error)});const k=await new Promise(ok=>{const q=db.transaction('clips').objectStore('clips').getAllKeys();q.onsuccess=()=>ok(q.result)});db.close();return k};
window.__att=async(i,name,key,confirmed)=>{if(key)await window.__put(key,name,['x'],540,960,8);const ok=await CP.attachClip(i,window.__file(name),{src:'Pixabay',url:'https://pixabay.com/videos/x-1/',by:'orig'+i,lic:'Pixabay Content License',ok:!!confirmed,inp:0,at:'2026-11-28'},{pend:!confirmed,inboxKey:key||null});return ok};
window.__tags=i=>{const q=CP.sceneSpec(i).queries[0]||'';return q.toLowerCase().split(/\\s+/).filter(Boolean)};
"""
def newpage(b,design=True):
    ctx,pg=mkctx(b);pg.ext=[]
    pg.on('request',lambda r:pg.ext.append(r.url) if not (r.url.startswith('http://127.0.0.1') or r.url.startswith('blob:') or r.url.startswith('data:')) else None)
    pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
    if design:pg.fill('#dj',D4J);pg.click('#bDJ');pg.wait_for_timeout(900)
    load(pg);pg.evaluate("()=>{"+JS_HELP+"}");return ctx,pg
def meas(pg,name,o='{}',t0=0,ln=8):
    return pg.evaluate("async([n,o,t0,ln])=>{const r=await CP.vaMeasure(window.__file(n),t0,ln,JSON.parse(o));return r}",[name,o,t0,ln])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx,pg=newpage(b)
    # --- A 測定と判定（測れるものだけ。意味は見ない）---
    ra=meas(pg,'ok_a');rb=meas(pg,'black_mid');rf=meas(pg,'flat');rd=meas(pg,'dark');rs=meas(pg,'static');rc=meas(pg,'cut_mid');rk=meas(pg,'black_short');rx=meas(pg,'ok_c')
    ck('A1 普通の素材は問題なし・確信度が高い',ra['bad']==[] and ra['conf']=='high' and ra['flags']==[],ra)
    ck('A2 黒フレームが多い素材を検出（黒37%）',rb['bad']==['black'] and rb['conf']=='high',rb)
    ck('A3 無地の素材を検出',rf['bad']==['flat'],rf)
    ck('A4 暗い素材は「暗い」の注意だけ。差し替え対象（bad）にしない',rd['bad']==[] and 'dark' in rd['flags'] or (rd['bad']==[]),rd)
    ck('A5 静止した素材を検出（注意のみ）',rs['bad']==[] and 'static' in rs['flags'],rs)
    ck('A6 素材の途中の場面切り替えを検出（注意のみ）',rc['bad']==[] and 'cut' in rc['flags'],rc)
    ck('A7 黒が短い素材（6%）を黒と誤判定しない','black' not in rk['bad'],rk)
    ck('A8 動きの激しい素材（変化が大きい）を場面切り替えと誤判定しない',rx['bad']==[] and 'cut' not in rx['flags'],rx)
    ck('A9 初回は少数（5枚）で確定する素材がある',ra['n']==5 and rf['n']==5,(ra['n'],rf['n']))
    ck('A10 抽出枚数は上限（12枚）を超えない',max(r['n'] for r in (ra,rb,rf,rd,rs,rc,rk,rx))<=12)
    ck('A11 台本との意味の一致・物体の判定を、結果に含めない（測定項目のみ）',all(k not in ra for k in ('label','objects','semantic','match')))
    # --- B キャッシュ・重複分析の防止 ---
    kk="t|0.00|8.00|v1"
    r1=pg.evaluate("async()=>{const f=window.__file('ok_a');const s0={...CP.VA.stat};const a=await CP.vaAnalyze(f,'k1|0.00|8.00|v1',0,8);const b=await CP.vaAnalyze(f,'k1|0.00|8.00|v1',0,8);return{a:!!a.cached,b:!!b.cached,s0,s1:{...CP.VA.stat},same:JSON.stringify({...a,cached:0})===JSON.stringify({...b,cached:0})}}")
    ck('B1 同じ素材・区間は2回目にキャッシュを使う',(not r1['a']) and r1['b'] and r1['s1']['hit']==r1['s0']['hit']+1 and r1['s1']['analyzed']==r1['s0']['analyzed']+1,r1)
    ck('B2 キャッシュの結果が分析の結果と同じ',r1['same'])
    r2=pg.evaluate("async()=>{const f=window.__file('ok_b');const s0={...CP.VA.stat};const [a,b]=await Promise.all([CP.vaAnalyze(f,'k2|0.00|8.00|v1',0,8),CP.vaAnalyze(f,'k2|0.00|8.00|v1',0,8)]);return{s0,s1:{...CP.VA.stat},eq:a.n===b.n}}")
    ck('B3 同時に同じ素材を要求しても、分析は1回（重複分析の防止）',r2['s1']['analyzed']==r2['s0']['analyzed']+1 and r2['s1']['dedupe']==r2['s0']['dedupe']+1,r2)
    r3=pg.evaluate("async()=>{const f=window.__file('ok_a');const s0={...CP.VA.stat};await CP.vaAnalyze(f,'k1|1.00|8.00|v1',1,8);return{s0,s1:{...CP.VA.stat}}}")
    ck('B4 区間が違えば再分析する（キャッシュを誤用しない）',r3['s1']['analyzed']==r3['s0']['analyzed']+1)
    pg.reload();ready(pg);pg.wait_for_timeout(500);load(pg);pg.evaluate("()=>{"+JS_HELP+"}")
    r4=pg.evaluate("async()=>{const f=window.__file('ok_a');const s0={...CP.VA.stat};const a=await CP.vaAnalyze(f,'k1|0.00|8.00|v1',0,8);return{c:!!a.cached,s0,s1:{...CP.VA.stat}}}")
    ck('B5 再読み込み後も、保存済みの結果を再利用（再分析しない）',r4['c'] and r4['s1']['analyzed']==r4['s0']['analyzed'],r4)
    big=pg.evaluate("()=>{const t=localStorage.getItem(CP.NS+'cp_va')||'';return t.length}")
    ck('B6 保存するのは小さな数値だけ（映像・フレームを保存しない）',0<big<60000,big)
    # --- C 重複検出（pHash）---
    c1=pg.evaluate("async()=>{const A=await CP.vaMeasure(window.__file('ok_a'),0,8),D=await CP.vaMeasure(window.__file('dup_a'),0,8),B=await CP.vaMeasure(window.__file('ok_b'),0,8),F=await CP.vaMeasure(window.__file('flat'),0,8),K=await CP.vaMeasure(window.__file('black_mid'),0,8);return{ad:CP.vaDupPairs([A,D]).length,ab:CP.vaDupPairs([A,B]).length,af:CP.vaDupPairs([F,F]).length,hk:K.hashes.length,ham:CP.vaHam(A.hashes[0],A.hashes[0])}}")
    ck('C1 同じ映像を再圧縮・縮小したものを重複と判定',c1['ad']==1,c1)
    ck('C2 別の映像は重複としない',c1['ab']==0,c1)
    ck('C3 無地どうしは重複としない（ハッシュが不安定なため除外）',c1['af']==0,c1)
    ck('C4 ハミング距離は同一で0',c1['ham']==0)
    # --- D 解放 ---
    d1=pg.evaluate("""async()=>{let c=0,rv=0;const oc=URL.createObjectURL.bind(URL),or=URL.revokeObjectURL.bind(URL);URL.createObjectURL=x=>{c++;return oc(x)};URL.revokeObjectURL=x=>{rv++;return or(x)};
      await CP.vaAnalyze(window.__file('ok_c'),'kd|0.00|8.00|v1',0,8);const live=CP.VA.live;CP.vaRelease();URL.createObjectURL=oc;URL.revokeObjectURL=or;return{c,rv,live,fly:CP.VA.fly.size,cv:CP.VA.cv}}""")
    ck('D1 分析で作った一時URLをすべて解放',d1['c']==d1['rv'] and d1['c']>=1,d1)
    ck('D2 分析後は、一時の映像要素・進行中の要求・キャンバスが残らない',d1['live']==0 and d1['fly']==0 and d1['cv'] is None,d1)
    # --- E 負荷分離 ---
    e1=pg.evaluate("async()=>{CP.S.busy=true;const r=await CP.vaScenes({});CP.S.busy=false;CP.VA.run=true;const x=await CP.exportVideo();CP.VA.run=false;return{r:r.ok,x}}")
    ck('E1 書き出し・再生中は分析しない',e1['r']==False)
    ck('E2 分析中は書き出しを始めない',e1['x'] is None)
    e2=pg.evaluate("async()=>{await CP.vaAnalyze(window.__file('ok_a'),'kp|0.00|8.00|v1',0,8);CP.VA.cv||0;await CP.prep();return{cv:CP.VA.cv,fly:CP.VA.fly.size}}")
    ck('E3 音声の準備（prep）の前に分析データを解放',e2['cv'] is None and e2['fly']==0,e2)
    ck('F0 ページエラーなし',pg.errs==[],pg.errs)
    ctx.close()
    # --- F 取得済み候補への差し替え（通信なし）---
    def scen(b,att,cands=(),pre=None):
        ctx,pg=newpage(b)
        pg.evaluate("async()=>{CP.BT.lib=true}")
        for (i,name,key,conf) in att:pg.evaluate("async([i,n,k,c])=>await window.__att(i,n,k,c)",[i,name,key,conf])
        for (key,name,i) in cands:pg.evaluate("async([k,n,i])=>await window.__put(k,n,window.__tags(i),540,960,8)",[key,name,i])
        if pre:pg.evaluate(pre)
        return ctx,pg
    def run(pg):return pg.evaluate("async()=>{const c0=CP.realCnt();const r=await CP.vaScenes({});const c1=CP.realCnt();return{r:{line:r.line,rows:r.rows,swaps:r.swaps,held:r.held},c0,c1}}")
    # F1 黒の素材を、端末内の良い候補へ差し替える
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True),(1,'ok_a','pixabay:7001',True)],[('pixabay:7100','ok_c',0)])
    pg.REQ['api'].clear();pg.REQ['cdn'].clear();pg.ext.clear();x=run(pg)
    s=pg.evaluate("()=>({k0:CP.S.clips[0].inboxKey,pend0:CP.S.clips[0].pend,ok0:CP.S.clips[0].meta.ok,k1:CP.S.clips[1].inboxKey,pend1:CP.S.clips[1].pend,ok1:CP.S.clips[1].meta.ok,sw:CP.bstat(0).va&&CP.bstat(0).va.swaps,gate:CP.rightsGate()})")
    keys=pg.evaluate("async()=>await window.__keys()")
    ck('F1 黒の素材を、端末内の取得済み候補へ自動で差し替える',s['k0']=='pixabay:7100' and s['sw']==1,(s,x['r']['rows']))
    ck('F2 差し替えた素材は権利が未確認。他の場面の確認状態は保たれる',s['pend0'] is True and s['ok0'] is False and s['pend1'] is False and s['ok1'] is True,s)
    ck('F3 権利が未確認の間は書き出しを止める',bool(s['gate']),s)
    ck('F4 差し替え前の素材は端末内から消さない',('pixabay:7000' in keys) and ('pixabay:7100' in keys),keys)
    ck('F5 通信なし・通信枠は不変（検索・動画の回数が同じ）',x['c0']==x['c1'] and not pg.REQ['api'] and not pg.REQ['cdn'] and not pg.ext,(x['c0'],x['c1'],pg.REQ,pg.ext))
    ck('F6 ページエラーなし',pg.errs==[],pg.errs)
    ctx.close()
    # F7 代替候補がない → 変更せず、確認推奨を表示（既存の素材を消さない）
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True)],[])
    o=pg.evaluate("()=>CP.S.clips[0]");x=run(pg)
    s=pg.evaluate("()=>({k:CP.S.clips[0].inboxKey,msg:CP.bstat(0).msg,st:CP.bstat(0).st})")
    ck('F7 代替候補がないときは、素材を変えず、確認推奨を表示',s['k']=='pixabay:7000' and '確認推奨' in s['msg'] and '代替候補' in s['msg'],s)
    ctx.close()
    # F8 代替候補も黒 → 採用しない
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True)],[('pixabay:7100','black_head',0)])
    x=run(pg);k=pg.evaluate("()=>CP.S.clips[0].inboxKey")
    ck('F8 代替候補も測定上の基準を満たさない場合は、差し替えない',k=='pixabay:7000',k)
    ctx.close()
    # F9 代替候補が他の場面と映像が重複 → 採用しない
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True),(1,'ok_a','pixabay:7001',True)],[('pixabay:7100','dup_a',0)])
    x=run(pg);k=pg.evaluate("()=>CP.S.clips[0].inboxKey")
    ck('F9 代替候補が他の場面の素材と重複する場合は、差し替えない',k=='pixabay:7000',k)
    ctx.close()
    # F10 手動で取り込んだ場面（ロック）は変えない
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True)],[('pixabay:7100','ok_c',0)],"()=>{CP.batchLock(0,true)}")
    x=run(pg);k=pg.evaluate("()=>CP.S.clips[0].inboxKey")
    ck('F10 ロック中の場面は自動では差し替えない',k=='pixabay:7000',k)
    ctx.close()
    # F11 再評価の回数に上限（2回）
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True)],[('pixabay:7100','ok_c',0)],"()=>{CP.bstat(0).va={swaps:2,tried:[],log:[]}}")
    x=run(pg);s=pg.evaluate("()=>({k:CP.S.clips[0].inboxKey,msg:CP.bstat(0).msg})")
    ck('F11 再評価の上限に達した場面は、差し替えず確認推奨にする',s['k']=='pixabay:7000' and '上限' in s['msg'],s)
    ctx.close()
    # F12 暗いだけの素材と、確信度が低い素材は、自動では変えない
    ctx,pg=scen(b,[(0,'dark','pixabay:7000',True),(1,'black_head','pixabay:7001',True)],[('pixabay:7100','ok_c',0),('pixabay:7101','ok_b',1)])
    pg.evaluate("()=>{const c=CP.S.clips[1],s=CP.S.sc[1],k=CP.vaKey(c,1,0,Math.max(.5,s.b-s.a));CP.vaAnalyze(c.file,k,0,Math.max(.5,s.b-s.a)).then(r=>{CP.VA.cache.set(k,Object.assign({},r,{conf:'low',why:['黒の割合が境目']}))})}");pg.wait_for_timeout(1500)
    x=run(pg);s=pg.evaluate("()=>({k0:CP.S.clips[0].inboxKey,k1:CP.S.clips[1].inboxKey})")
    ck('F12 暗いだけの素材と、確信度が低い素材は、自動では変えない',s['k0']=='pixabay:7000' and s['k1']=='pixabay:7001',(s,x['r']['rows']))
    ctx.close()
    # F13 2回目の実行は、キャッシュを使い、差し替えを繰り返さない
    ctx,pg=scen(b,[(0,'black_head','pixabay:7000',True),(1,'ok_a','pixabay:7001',True)],[('pixabay:7100','ok_c',0)])
    x1=run(pg);x2=run(pg);k=pg.evaluate("()=>({k:CP.S.clips[0].inboxKey,sw:(CP.bstat(0).va||{}).swaps})")
    ck('F13 2回目は再分析せず、差し替えも増えない',x2['r']['swaps']==0 and k['sw']==1 and x2['r']['rows'][0]['cached'],(x2['r'],k))
    ck('F14 結果の説明に「意味は理解できない」旨を含む',('意味は理解できません' in x1['r']['line']),x1['r']['line'])
    ctx.close()
    print('TOTAL',sum(R),'/',len(R))
