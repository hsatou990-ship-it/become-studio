import './intent.js';
const B=window.BSIntent,$=id=>document.getElementById(id),Q=new URLSearchParams(location.search);
const ADAPTERS={transformers:'./adapter-transformers.js',stub:'./adapter-stub.js'};   // 許可リスト以外は読まない
const S={abort:false,clips:[],plan:null,report:null};
/* 同一オリジン以外への通信を、念のためコード側でも拒否（CSPに加える二重の防止） */
const _f=window.fetch;window.fetch=(u,o)=>{const x=new URL(typeof u==='string'?u:u.url,location.href);if(x.origin!==location.origin&&x.protocol!=='blob:'&&x.protocol!=='data:')return Promise.reject(new Error('外部通信は許可されていません: '+x.origin));return _f(u,o)};
const mem=()=>performance&&performance.memory?performance.memory.usedJSHeapSize:null;
const mb=v=>v==null?'未測定':(v/1048576).toFixed(1)+' MB';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
$('env').textContent='環境: '+navigator.userAgent+'｜WebGPU: '+('gpu' in navigator?'あり（実際に使えるかは測定時に確認）':'なし')+'｜論理CPU: '+(navigator.hardwareConcurrency||'未測定')+'｜端末メモリ(目安): '+(navigator.deviceMemory?navigator.deviceMemory+' GB':'未測定')+'｜端末温度・端末全体のメモリ使用量: 未測定（ブラウザから取得できません）';
$('djf').onchange=async e=>{const f=e.target.files[0];if(f)$('dj').value=await f.text()};
$('vf').onchange=()=>{const keep={};document.querySelectorAll('#lab select').forEach(x=>{keep[x.dataset.n]=x.value});S.clips=[...$('vf').files];const n=(()=>{try{return B.buildCards(JSON.parse($('dj').value)).length}catch{return 0}})();
 $('lab').innerHTML='<table><tr><th>素材</th><th>正解の場面</th></tr>'+S.clips.map((f,i)=>'<tr><td>'+f.name.replace(/[<>&"]/g,'')+'</td><td><select data-i="'+i+'" data-n="'+f.name.replace(/[<>&"]/g,'')+'"><option value="-1">該当なし</option>'+Array.from({length:Math.max(n,8)},(_,k)=>'<option value="'+k+'">場面'+(k+1)+'</option>').join('')+'</select></td></tr>').join('')+'</table>';document.querySelectorAll('#lab select').forEach(x=>{if(keep[x.dataset.n]!==undefined)x.value=keep[x.dataset.n]})};
$('dj').onchange=$('vf').onchange;
$('stop').onclick=()=>{S.abort=true;$('st').textContent='中止を要求しました（現在の処理が終わり次第、安全に停止して解放します）'};
const log=t=>{$('st').textContent=t};
async function frames(file,n,cache,model){      // 動画から等間隔でフレームを取り、224×224に整える。解放は呼び出し側
 const url=URL.createObjectURL(file),v=document.createElement('video');v.muted=true;v.preload='auto';v.src=url;
 try{await new Promise((ok,ng)=>{v.onloadedmetadata=ok;v.onerror=()=>ng(new Error('動画を開けません: '+file.name));setTimeout(()=>ng(new Error('動画の読み込みが時間切れ: '+file.name)),15000)});
  const d=v.duration||1,out=[];for(let i=0;i<n;i++){if(S.abort)throw new Error('中止');const t=d*(.1+.8*(n===1?.5:i/(n-1)));
   await new Promise(r=>{v.onseeked=r;v.currentTime=t});const c=document.createElement('canvas');c.width=c.height=224;const g=c.getContext('2d'),s=Math.min(v.videoWidth,v.videoHeight);g.drawImage(v,(v.videoWidth-s)/2,(v.videoHeight-s)/2,s,s,0,0,224,224);out.push({t:+t.toFixed(2),c,key:file.name+':'+file.size+':'+file.lastModified+':'+t.toFixed(2)+':'+model})}
  return out}finally{v.removeAttribute('src');v.load();URL.revokeObjectURL(url)}}
function resBytes(){return performance.getEntriesByType('resource').filter(e=>/\/(models|vendor)\//.test(e.name)).reduce((a,e)=>({transfer:a.transfer+(e.transferSize||0),body:a.body+(e.encodedBodySize||0),files:a.files+1}),{transfer:0,body:0,files:0})}
const EC=new Map();let ecHit=0,ecMiss=0;
async function run(device,cards,labels,n0,nmax){
 const R={device,stages:{},errors:[]};let mod,A;const t0=performance.now();
 try{const name=Q.get('adapter')||'transformers';if(!ADAPTERS[name])throw new Error('不明なアダプタ: '+name);
  const m0=mem();log(device+': モデルを読み込み中…');A=await import(ADAPTERS[name]);mod=await A.load({device,failAt:Q.get('failAt')});
  R.stages.loadMs=Math.round(performance.now()-t0);R.model=mod.id;R.realModel=!!mod.real;R.stages.memAfterLoad=mem();R.stages.memBefore=m0;R.download=resBytes();
  const t1=performance.now(),tv=[];cards.forEach(c=>{c.posIdx=[];c.avoidIdx=[]});const texts=[];cards.forEach(c=>{c.prompts.pos.forEach(p=>{c.posIdx.push(texts.length);texts.push(p)});c.prompts.avoid.forEach(p=>{c.avoidIdx.push(texts.length);texts.push(p)})});
  const tvec=(await mod.embedTexts(texts)).map(B.l2);cards.forEach(c=>{c.posVec=c.posIdx.map(i=>tvec[i]);c.avoidVec=c.avoidIdx.map(i=>tvec[i])});R.stages.textMs=Math.round(performance.now()-t1);
  const per=[];let tImg=0,nFr=0;
  for(let ci=0;ci<S.clips.length;ci++){if(S.abort)throw new Error('中止');const f=S.clips[ci],clip={key:f.name,frames:[]},tt=performance.now();
   let n=n0,done=false,fr=[];
   while(!done){log(device+': 分析 '+(ci+1)+'/'+S.clips.length+' '+f.name+'（'+n+'枚）');const all=await frames(f,n,EC,mod.id);const need=[],idx=[];all.forEach((x,i)=>{const h=EC.get(x.key);if(h){ecHit++;clip.frames[i]=h}else{ecMiss++;need.push(x.c);idx.push(i)}});
    if(need.length){const e=await mod.embedImages(need);e.forEach((v,k)=>{const x=B.l2(v);EC.set(all[idx[k]].key,x);clip.frames[idx[k]]=x})}
    all.forEach(x=>{x.c.width=0});clip.frames.length=all.length;fr=clip.frames.slice();nFr+=need.length;
    const unc=cards.some((c,si)=>{const o=[];cards.forEach((d,sj)=>{if(sj!==si)o.push(...d.posVec)});const j=B.judge(fr,c,o);return labels[ci]===si&&j.verdict==='uncertain'});   // 正解の場面で割れる場合のみ追加
    if(unc&&n<nmax){n=Math.min(nmax,n+2)}else done=true}
   clip.ms=Math.round(performance.now()-tt);tImg+=clip.ms;per.push(clip)}
  R.stages.imageMs=tImg;R.stages.framesEmbedded=nFr;R.stages.memPeak=mem();
  const ranks=B.rank(cards,per),pairs=[];cards.forEach((c,si)=>per.forEach((cl,ci)=>{const r=ranks[si].find(x=>x.clip===ci);pairs.push({label:labels[ci]===si,score:r.posMean||0,verdict:r.verdict,clip:cl.key,scene:si+1})}));
  R.pairs=pairs;R.eval=B.evalPairs(pairs,B.TH.pos);R.falseAccept=pairs.filter(p=>!p.label&&p.verdict==='match').map(p=>p.clip+'→場面'+p.scene);R.missed=pairs.filter(p=>p.label&&p.verdict!=='match').map(p=>p.clip+'→場面'+p.scene+'（'+p.verdict+'）');
  R.avoidFlag=pairs.filter(p=>p.verdict==='avoid').map(p=>p.clip+'→場面'+p.scene);R.thresholdsCalibrated=false}
 catch(e){R.errors.push(String(e.message||e));R.stoppedSafely=true}
 finally{try{if(mod)await mod.dispose()}catch(e){R.errors.push('解放: '+e.message)};R.stages.memAfterRelease=mem();R.totalMs=Math.round(performance.now()-t0)}
 return R}
$('run').onclick=async()=>{S.abort=false;$('run').disabled=true;$('dl').disabled=true;
 try{let plan;try{plan=JSON.parse($('dj').value)}catch{throw new Error('設計JSONを読めません')}if(!S.clips.length)throw new Error('動画を選んでください');
  const cards=B.buildCards(plan),labels=[...document.querySelectorAll('#lab select')].map(s=>+s.value);
  const devs=$('be').value==='both'?['wasm','webgpu']:[$('be').value],n0=+$('n0').value,nmax=Math.max(n0,+$('nmax').value),runs=[];
  for(const d of devs){if(S.abort)break;runs.push(await run(d,cards,labels,n0,nmax));
   if(!runs[runs.length-1].errors.length&&!S.abort){const hit0=ecHit;const r2=await run(d,cards,labels,n0,nmax);r2.warmRerun=true;r2.cacheReuse={hit:ecHit-hit0,missAfter:r2.stages.framesEmbedded};runs.push(r2)}}
  S.report={at:new Date().toISOString(),page:'AI分析測定（段階B-0）',adapter:Q.get('adapter')||'transformers',cards:cards.map(c=>({i:c.i,ja:c.ja,pos:c.prompts.pos,avoid:c.prompts.avoid,unset:c.unset,needsReview:c.needsReview})),runs,
   unmeasured:['端末温度','端末全体のメモリ使用量','消費電力'],note:'疑似モデル（stub）の結果は精度・速度の測定値として使えません。閾値は未較正。CLIP類似度は品質を保証しません。'};
  $('out').textContent=JSON.stringify(S.report,(k,v)=>k==='pairs'?v.map(p=>p.clip+'→場面'+p.scene+(p.label?'(正)':'(誤)')+' '+p.score.toFixed(3)+' '+p.verdict):v,1);
  $('res').innerHTML=runs.map(r=>'<p class="'+(r.errors.length?'ng':'ok')+'">'+r.device+(r.warmRerun?'（2回目・キャッシュ再利用）':'')+'｜モデル: '+(r.model||'未読込')+(r.realModel===false?' ※疑似':'')+'｜読込 '+(r.stages.loadMs??'-')+' ms｜テキスト '+(r.stages.textMs??'-')+' ms｜画像 '+(r.stages.imageMs??'-')+' ms（新規'+(r.stages.framesEmbedded??0)+'枚）｜JSヒープ '+mb(r.stages.memBefore)+'→'+mb(r.stages.memPeak)+'→解放後 '+mb(r.stages.memAfterRelease)+'｜取得 '+(r.download?mb(r.download.transfer)+'（'+r.download.files+'ファイル）':'未測定')+(r.eval?'｜AUC '+(r.eval.auc==null?'-':r.eval.auc.toFixed(3))+'・誤採用 '+r.falseAccept.length+'・見逃し '+r.missed.length:'')+(r.errors.length?'｜停止: '+r.errors.join(' / '):'')+'</p>').join('');
  $('dl').disabled=false;log('完了（結果は上のとおり。端末温度・端末全体メモリは未測定）')}
 catch(e){log('停止: '+e.message)}finally{$('run').disabled=false}};
$('dl').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(S.report,null,1)],{type:'application/json'}));a.download='ai-measure-'+Date.now()+'.json';a.click()};
window.AIM={S,run,frames};
