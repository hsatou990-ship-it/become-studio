/* 推論専用の隔離フレーム。iframe sandbox="allow-scripts"（同一オリジンの権限なし）で動く。
   ・編集画面のデータ（localStorage / IndexedDB / Cache）に触れない。外部通信は CSP（connect-src blob:）と fetch の置き換えで遮断。
   ・モデル・ライブラリ・wasm は、親が照合済みのバイト列を渡してくる。ここでは取得しない。 */
const MODEL='Xenova/clip-vit-base-patch32';let T=null,tok=null,txt=null,proc=null,vis=null,urls=[],map={};
const nativeFetch=window.fetch.bind(window);
window.fetch=async(u)=>{const s=typeof u==='string'?u:(u&&u.url)||String(u);if(s.startsWith('blob:'))return nativeFetch(s);
 const p=new URL(s,'https://bs.local/').pathname,m=p.match(/\/models\/Xenova\/clip-vit-base-patch32\/(.+)$/);
 if(m&&map[m[1]]){const b=map[m[1]];return new Response(b,{status:200,headers:{'content-type':/\.json$/.test(m[1])?'application/json':'application/octet-stream','content-length':String(b.byteLength)}})}
 if(m)return new Response('',{status:404});throw new Error('隔離フレームでは外部通信できません: '+s.slice(0,80))};
const post=(o,tr)=>parent.postMessage(o,'*',tr||[]);
const blobURL=(b,type)=>{const u=URL.createObjectURL(new Blob([b],{type}));urls.push(u);return u};
async function init(m){const f=m.files;map={};for(const k of Object.keys(f))if(!/^(transformers\.min\.js|ort-)/.test(k))map[k]=f[k];
 const lib=blobURL(f['transformers.min.js'],'text/javascript'),mjs=Object.keys(f).find(k=>/^ort-wasm.*\.mjs$/.test(k)),wasm=Object.keys(f).find(k=>/^ort-wasm.*\.wasm$/.test(k));
 if(!mjs||!wasm)throw new Error('ONNX Runtimeのファイルがありません');
 T=await import(lib);const e=T.env;e.allowLocalModels=true;e.allowRemoteModels=false;e.localModelPath='/models/';e.useBrowserCache=false;
 if(e.backends&&e.backends.onnx&&e.backends.onnx.wasm){const w=e.backends.onnx.wasm;w.wasmPaths={mjs:blobURL(f[mjs],'text/javascript'),wasm:blobURL(f[wasm],'application/wasm')};w.numThreads=1;w.proxy=false}
 const cfg={device:m.device||'wasm',dtype:'uint8'};
 tok=await T.AutoTokenizer.from_pretrained(MODEL);txt=await T.CLIPTextModelWithProjection.from_pretrained(MODEL,cfg);
 proc=await T.AutoProcessor.from_pretrained(MODEL);vis=await T.CLIPVisionModelWithProjection.from_pretrained(MODEL,cfg);
 return{stub:!!e.__stub,lib:e.version||null}}
const rows=(t)=>{const d=t.dims[t.dims.length-1],o=[];for(let i=0;i<t.dims[0];i++)o.push(Float32Array.from(t.data.slice(i*d,(i+1)*d)));return o};
addEventListener('message',async ev=>{const m=ev.data||{};try{let r;
 if(m.t==='init')r=await init(m);
 else if(m.t==='texts'){const i=tok(m.texts,{padding:true,truncation:true}),o=await txt(i);r=rows(o.text_embeds)}
 else if(m.t==='images'){r=[];for(const im of m.imgs){const c=document.createElement('canvas');c.width=im.w;c.height=im.h;c.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(im.buf),im.w,im.h),0,0);
   const p=await proc(T.RawImage.fromCanvas(c)),o=await vis(p);r.push(Float32Array.from(o.image_embeds.data));c.width=0}}
 else if(m.t==='dispose'){try{await txt.dispose();await vis.dispose()}catch{}tok=txt=proc=vis=T=null;map={};urls.forEach(u=>URL.revokeObjectURL(u));urls=[];r=true}
 else throw new Error('不明な要求');
 post({id:m.id,ok:true,r},Array.isArray(r)&&r[0]&&r[0].buffer?r.map(x=>x.buffer):[])}
 catch(err){post({id:m.id,ok:false,err:String(err&&err.message||err)})}});
post({t:'ready'});
