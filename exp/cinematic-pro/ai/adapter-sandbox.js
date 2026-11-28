/* 親ページ側の接続部。照合済みのバイト列を隔離フレーム（sandbox.html）へ渡し、推論の依頼と結果の受け取りだけを行う。
   通信は一切しない（取得は acquire.js のボタン操作のみ）。キャッシュが無い・未検証なら停止し、無断で再取得しない。 */
import {loadVerified,TARGET} from './acquire.js';
export async function load(opt){
 const {files}=await loadVerified();   // 欠損・破損・未検証はここで例外（通信しない）
 const fr=document.createElement('iframe');fr.setAttribute('sandbox','allow-scripts');fr.style.display='none';fr.src=new URL('sandbox.html',import.meta.url).href;
 let seq=0;const waits=new Map();let readyRes;const ready=new Promise((ok,ng)=>{readyRes=ok;setTimeout(()=>ng(new Error('隔離フレームが起動しません')),15000)});
 const onMsg=e=>{if(e.source!==fr.contentWindow)return;const m=e.data||{};if(m.t==='ready')return readyRes();const w=waits.get(m.id);if(w){waits.delete(m.id);m.ok?w.ok(m.r):w.ng(new Error(m.err))}};
 window.addEventListener('message',onMsg);document.body.appendChild(fr);
 const call=(msg,tr,ms)=>new Promise((ok,ng)=>{const id=++seq;waits.set(id,{ok,ng});fr.contentWindow.postMessage({...msg,id},'*',tr||[]);setTimeout(()=>{if(waits.delete(id))ng(new Error('隔離フレームの応答が時間切れ（'+(msg.t)+'）'))},ms||120000)});
 const cleanup=()=>{window.removeEventListener('message',onMsg);try{fr.remove()}catch{}};
 try{await ready;const tr=Object.values(files);const info=await call({t:'init',files,device:opt&&opt.device||'wasm'},tr,300000);
  return{id:TARGET.model+'@'+TARGET.rev.slice(0,7)+'｜lib '+TARGET.lib,device:opt&&opt.device||'wasm',real:!info.stub,
   async embedTexts(t){return call({t:'texts',texts:t})},
   async embedImages(cs){const imgs=cs.map(c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height);return{w:c.width,h:c.height,buf:d.data.buffer}});return call({t:'images',imgs},imgs.map(x=>x.buf))},
   async dispose(){try{await call({t:'dispose'},[],20000)}catch{}cleanup()}}}
 catch(e){cleanup();throw e}}
