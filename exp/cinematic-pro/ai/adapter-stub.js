/* 試験専用の疑似モデル（実モデルではない）。色と語句から決定的な3次元ベクトルを返し、測定ページの流れだけを試験する。
   これの結果は、AIの精度・速度・メモリの測定値として使わない。 */
const W=[[/dark|night|corridor|tunnel|empty/,[0,0,1]],[/clock|watch|hands/,[1,0,0]],[/sunrise|dawn|window|person|walk/,[0,1,0]],[/logo|watermark|text overlay/,[1,1,0]]];
const tv=t=>{const s=String(t).toLowerCase();for(const[r,v]of W)if(r.test(s))return v;return[.3,.3,.3]};
export async function load(opt){await new Promise(r=>setTimeout(r,5));if(opt&&opt.failAt==='load')throw new Error('試験用: 読み込み失敗');
 return{id:'stub',device:opt&&opt.device||'wasm',real:false,
  async embedTexts(t){return t.map(x=>Float32Array.from(tv(x)))},
  async embedImages(cs){return cs.map(c=>{const q=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let r=0,g=0,b=0,n=0;for(let i=0;i<q.length;i+=16){r+=q[i];g+=q[i+1];b+=q[i+2];n++}return Float32Array.from([r/n,g/n,b/n].map(v=>v/255+1e-3))})},
  async dispose(){}}}
