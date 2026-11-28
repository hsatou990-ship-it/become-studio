/* Transformers.js（ブラウザ内の局所推論）の接続部。通信しない設計: リモート取得を禁止し、同一オリジンの
   ./vendor と ./models だけを読む。バージョンとモデルの版は固定。ライブラリとモデルは、承認後に取得して配置する。
   状態: ライブラリ未取得のため、この接続部は実モデルで未実行（段階B-0時点）。 */
export const PIN={lib:'未固定（取得時に確定して記録）',model:'Xenova/clip-vit-base-patch32',revision:'6b7c523703ae26e39be4b03774966f8571c7f523',dtype:'uint8'};
export async function load(opt){
 const base=new URL('./',import.meta.url);
 const T=await import(new URL('vendor/transformers.min.js',base).href);   // 無ければ例外 → 安全停止
 T.env.allowRemoteModels=false;T.env.allowLocalModels=true;T.env.useBrowserCache=true;
 T.env.localModelPath=new URL('models/',base).href;
 if(T.env.backends&&T.env.backends.onnx&&T.env.backends.onnx.wasm)T.env.backends.onnx.wasm.wasmPaths=new URL('vendor/',base).href;
 const device=opt&&opt.device||'wasm',cfg={device,dtype:PIN.dtype};
 const tok=await T.AutoTokenizer.from_pretrained(PIN.model),txt=await T.CLIPTextModelWithProjection.from_pretrained(PIN.model,cfg);
 const proc=await T.AutoProcessor.from_pretrained(PIN.model),vis=await T.CLIPVisionModelWithProjection.from_pretrained(PIN.model,cfg);
 const toArr=(t,d)=>{const o=[];for(let i=0;i<t.dims[0];i++)o.push(Float32Array.from(t.data.slice(i*d,(i+1)*d)));return o};
 return{id:PIN.model+'@'+PIN.revision.slice(0,7),device,real:true,
  async embedTexts(a){const i=tok(a,{padding:true,truncation:true}),o=await txt(i);const r=toArr(o.text_embeds,o.text_embeds.dims[1]);return r},
  async embedImages(cs){const out=[];for(const c of cs){const im=T.RawImage.fromCanvas(c),p=await proc(im),o=await vis(p);out.push(Float32Array.from(o.image_embeds.data));}return out},
  async dispose(){try{await txt.dispose();await vis.dispose()}catch{}}}}
