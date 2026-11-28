/* 段階B-0 r14: モデル・ライブラリの取得管理（取得だけを担当。推論は sandbox.html の隔離フレームで行う）
   ・通信は「取得対象を確認」「取得」ボタンを押したときだけ。接続先は ALLOWED_HOSTS のみ。取得中以外は通信しない。
   ・取得対象は、公開メタデータ（HF API / jsDelivr API）から確定し、承認コード（一覧の指紋）の入力後にだけ取得する。
   ・照合: HFのLFSファイル=SHA-256(公開API)、HFの小ファイル=git blob SHA-1(公開API)、jsDelivr=SHA-256(公開API)。
     照合できない／不一致のファイルは「未検証」とし、保存せず、実行しない。計算した値だけで安全とは判断しない。
   ・保存: Cache Storage（このページ専用の名前）。消失・破損は検出して表示するだけで、無断で再取得しない。 */
export const TARGET={model:'Xenova/clip-vit-base-patch32',rev:'6b7c523703ae26e39be4b03774966f8571c7f523',lib:'3.8.1',
 hfFiles:['config.json','merges.txt','preprocessor_config.json','special_tokens_map.json','tokenizer.json','tokenizer_config.json','vocab.json','onnx/vision_model_uint8.onnx','onnx/text_model_uint8.onnx'],
 ortRe:/^\/dist\/ort-wasm-simd-threaded\.jsep\.(mjs|wasm)$/};
export const ALLOWED_HOSTS=['huggingface.co','cdn.jsdelivr.net','data.jsdelivr.com'];
export const CACHE='bsai-clip-b32-'+TARGET.rev.slice(0,7)+'-lib'+TARGET.lib+'-v1',MK='https://bs.local/__manifest.json',MAXTRY=2;
const hex=b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join(''),b64=b=>btoa(String.fromCharCode(...new Uint8Array(b)));
export async function hashOf(buf,alg){if(alg==='sha256'){const d=await crypto.subtle.digest('SHA-256',buf);return{hex:hex(d),b64:b64(d)}}
 if(alg==='git-sha1'){const h=new TextEncoder().encode('blob '+buf.byteLength+'\0'),m=new Uint8Array(h.length+buf.byteLength);m.set(h);m.set(new Uint8Array(buf),h.length);return{hex:hex(await crypto.subtle.digest('SHA-1',m))}}throw new Error('不明な照合方式')}
export function hostOk(u){try{const x=new URL(u);return x.protocol==='https:'&&ALLOWED_HOSTS.includes(x.hostname)}catch{return false}}
async function net(u,o){if(!hostOk(u))throw new Error('未承認ホストへの接続を停止しました: '+u);window.__bsNet=true;try{return await fetch(u,{credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store',...o})}finally{window.__bsNet=false}}
async function jget(u,o){const r=await net(u,o);if(!r.ok)throw new Error('メタデータ取得に失敗（'+r.status+'）: '+new URL(u).hostname);return r.json()}
export async function approvalCode(list){const s=JSON.stringify(list.map(f=>[f.name,f.url,f.size,f.hash.alg,f.hash.hex||f.hash.b64]));return hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))).slice(0,8)}
/* 1. 取得対象の確定（メタデータだけ。ファイル本体は取得しない） */
export async function resolve(signal){const T=TARGET,out=[],H='https://huggingface.co/';
 const tree=async p=>jget(H+'api/models/'+T.model+'/tree/'+T.rev+(p?'/'+p:''),{signal});
 const items=[...await tree(''),...await tree('onnx')].filter(x=>x.type==='file');
 for(const path of T.hfFiles){const it=items.find(x=>x.path===path);if(!it)throw new Error('モデルのファイルが見つかりません: '+path);
  const lfs=it.lfs&&it.lfs.oid;out.push({kind:'model',name:path,url:H+T.model+'/resolve/'+T.rev+'/'+path,size:lfs?it.lfs.size:it.size,hash:lfs?{alg:'sha256',hex:lfs}:{alg:'git-sha1',hex:it.oid},exec:false})}
 const pj=await jget('https://cdn.jsdelivr.net/npm/@huggingface/transformers@'+T.lib+'/package.json',{signal}),ort=String((pj.dependencies||{})['onnxruntime-web']||'');
 if(pj.version!==T.lib)throw new Error('ライブラリの版が一致しません: '+pj.version);if(!/^\d+\.\d+\.\d+(-[\w.-]+)?$/.test(ort))throw new Error('ONNX Runtimeの版を確定できません（'+ort+'）。固定版でない場合は取得しません');
 const flat=async(pkg)=>(await jget('https://data.jsdelivr.com/v1/packages/npm/'+pkg+'?structure=flat',{signal})).files||[];
 const lf=(await flat('@huggingface/transformers@'+T.lib)).find(x=>x.name==='/dist/transformers.min.js');if(!lf)throw new Error('transformers.min.js が見つかりません');
 out.push({kind:'lib',name:'transformers.min.js',url:'https://cdn.jsdelivr.net/npm/@huggingface/transformers@'+T.lib+'/dist/transformers.min.js',size:lf.size,hash:{alg:'sha256',b64:lf.hash},exec:true});
 const of=(await flat('onnxruntime-web@'+ort)).filter(x=>T.ortRe.test(x.name));if(of.length!==2)throw new Error('ONNX Runtimeのファイルを確定できません（'+of.length+'件）');
 of.forEach(x=>out.push({kind:'ort',name:x.name.split('/').pop(),url:'https://cdn.jsdelivr.net/npm/onnxruntime-web@'+ort+x.name,size:x.size,hash:{alg:'sha256',b64:x.hash},exec:true}));
 out.forEach(f=>{if(!hostOk(f.url))throw new Error('未承認ホスト: '+f.url)});
 return{files:out,ort,total:out.reduce((a,f)=>a+f.size,0),code:await approvalCode(out)}}
/* 保存・状態 */
async function mget(){const c=await caches.open(CACHE),r=await c.match(MK);return r?r.json():{files:[]}}
async function mput(m){const c=await caches.open(CACHE);await c.put(MK,new Response(JSON.stringify(m),{headers:{'content-type':'application/json'}}))}
export async function status(deep){const m=await mget(),c=await caches.open(CACHE),rows=[];
 for(const f of m.files){const r=await c.match('https://bs.local/f/'+f.name);let st='ok';if(!r)st='missing';else{const b=await r.arrayBuffer();if(b.byteLength!==f.size)st='corrupt-size';else if(deep){const h=await hashOf(b,f.hash.alg);if((f.hash.hex&&h.hex!==f.hash.hex)||(f.hash.b64&&h.b64!==f.hash.b64))st='corrupt-hash'}}
  rows.push({name:f.name,kind:f.kind,size:f.size,verified:!!f.verified,state:st,exec:f.exec})}
 const ex=m.expect||[],need=ex.length>0&&ex.every(n=>rows.some(r=>r.name===n&&r.verified&&r.state==='ok'))&&rows.every(r=>r.verified&&r.state==='ok');return{rows,ready:need,rev:TARGET.rev,lib:TARGET.lib,deep:!!deep,note:m.files.length?'':'未取得'}}
export async function storageInfo(){const e=navigator.storage&&navigator.storage.estimate?await navigator.storage.estimate():null;return{usage:e?e.usage:null,quota:e?e.quota:null,persisted:navigator.storage&&navigator.storage.persisted?await navigator.storage.persisted():null}}
export async function clearAll(){await caches.delete(CACHE)}
/* 2. 取得（承認コードの一致が必要）。中断可能。失敗時は原因を返す。ファイル単位で復旧（取得済み・検証済みは再取得しない） */
export async function download(plan,code,{onProgress,signal,persist}={}){
 if(!plan||!plan.files||code!==plan.code)throw new Error('承認コードが一致しません。取得しません');
 const si=await storageInfo();if(si.quota!=null&&si.usage!=null&&plan.total*1.1>si.quota-si.usage)throw new Error('保存容量が足りません（必要 '+Math.round(plan.total*1.1/1048576)+' MB／空き '+Math.round((si.quota-si.usage)/1048576)+' MB）');
 if(persist&&navigator.storage&&navigator.storage.persist){try{await navigator.storage.persist()}catch{}}
 const m=await mget(),c=await caches.open(CACHE),res=[];let done=0;
 m.expect=plan.files.map(f=>f.name);await mput(m);
 for(const f of plan.files){const have=m.files.find(x=>x.name===f.name&&x.url===f.url&&x.verified);if(have&&await c.match('https://bs.local/f/'+f.name)){res.push({name:f.name,state:'既に保存済み・再取得なし'});done+=f.size;continue}
  let lastErr=null,ok=false;
  for(let t=1;t<=MAXTRY&&!ok;t++){if(signal&&signal.aborted)throw new Error('中断しました');
   try{const r=await net(f.url,{signal});if(!r.ok)throw new Error('HTTP '+r.status);const rd=r.body.getReader(),parts=[];let got=0;
    for(;;){const q=await rd.read();if(q.done)break;parts.push(q.value);got+=q.value.length;onProgress&&onProgress({name:f.name,got,size:f.size,total:done+got,all:plan.total})}
    const buf=new Uint8Array(got);let o=0;parts.forEach(p=>{buf.set(p,o);o+=p.length});
    if(got!==f.size){lastErr=new Error('サイズ不一致（'+got+' / '+f.size+'）。保存しません');break}
    const h=await hashOf(buf.buffer,f.hash.alg);if((f.hash.hex&&h.hex!==f.hash.hex)||(f.hash.b64&&h.b64!==f.hash.b64)){lastErr=new Error('ハッシュ不一致（'+f.name+'）。未検証として破棄しました');break}
    await c.put('https://bs.local/f/'+f.name,new Response(buf,{headers:{'content-type':f.exec?'text/javascript':'application/octet-stream'}}));
    const i=m.files.findIndex(x=>x.name===f.name);const e={name:f.name,kind:f.kind,url:f.url,size:f.size,hash:f.hash,exec:f.exec,verified:true,at:new Date().toISOString()};if(i>=0)m.files[i]=e;else m.files.push(e);await mput(m);ok=true;done+=f.size;res.push({name:f.name,state:'取得・照合済み'})}
   catch(e){if(e.name==='AbortError')throw new Error('中断しました');lastErr=e;if(/CSP|Content Security|Failed to fetch|NetworkError/i.test(String(e.message))&&t>=1&&!/HTTP/.test(e.message)){lastErr=new Error('接続できません（通信失敗、または未承認ホストへのリダイレクトをCSPが停止）: '+f.name+'。再試行は'+MAXTRY+'回までです');}}}
  if(!ok){const err=lastErr||new Error('取得失敗');err.file=f.name;err.partial=res;throw err}}
 return res}
/* 推論用: 照合済みファイルのバイト列だけを返す。欠損・破損・未検証なら通信せずに停止（無断で再取得しない） */
export async function loadVerified(){const s=await status(false);if(!s.ready)throw new Error('モデルが利用できません（'+(s.rows.length?s.rows.filter(r=>!r.verified||r.state!=='ok').map(r=>r.name+':'+(r.verified?r.state:'未検証')).join(', '):'未取得')+'）。自動では再取得しません。取得ボタンから手動で取得してください');
 const c=await caches.open(CACHE),m=await mget(),files={};for(const f of m.files)files[f.name]=await (await c.match('https://bs.local/f/'+f.name)).arrayBuffer();return{files,meta:m}}
