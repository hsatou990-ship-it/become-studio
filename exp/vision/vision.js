/* BECOME. STUDIO 映像の簡易分析（モデル不要・通信なし）
   ブラウザ内で動画を一定間隔でサンプリングし、低解像度の画素だけから指標を出す。
   指標: 鮮明さ(ラプラシアン分散)・明るさ/コントラスト・動き量・シーン変化・dHash(重複)・構図の重心・縦型適合・代表フレーム。
   重要: これらは「数値指標」であり、美しさ・感情・台本との意味一致・権利の証明ではない。 */
(function(G){
const W=96,H=170; // 解析用の縦長小フレーム
function gray(d){const n=d.length/4,g=new Float32Array(n);for(let i=0;i<n;i++)g[i]=.299*d[4*i]+.587*d[4*i+1]+.114*d[4*i+2];return g}
function lapVar(g,w,h){let s=0,s2=0,n=0;for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){const i=y*w+x,v=4*g[i]-g[i-1]-g[i+1]-g[i-w]-g[i+w];s+=v;s2+=v*v;n++}const m=s/n;return s2/n-m*m}
function stats(g){let s=0,s2=0;for(const v of g){s+=v;s2+=v*v}const m=s/g.length;return{mean:m,std:Math.sqrt(Math.max(0,s2/g.length-m*m))}}
function mad(a,b){let s=0;for(let i=0;i<a.length;i++)s+=Math.abs(a[i]-b[i]);return s/a.length}
function dhash(g,w,h){/* 9x8に縮小して隣接比較 → 64bit(配列) */const bits=[];const bx=w/9,by=h/8;const c=[];for(let y=0;y<8;y++){c.push([]);for(let x=0;x<9;x++){let s=0,n=0;for(let yy=Math.floor(y*by);yy<Math.floor((y+1)*by);yy++)for(let xx=Math.floor(x*bx);xx<Math.floor((x+1)*bx);xx++){s+=g[yy*w+xx];n++}c[y].push(s/Math.max(1,n))}}
 for(let y=0;y<8;y++)for(let x=0;x<8;x++)bits.push(c[y][x]>c[y][x+1]?1:0);return bits}
const ham=(a,b)=>{let d=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i])d++;return d};
function edgeCentroid(g,w,h){let sx=0,sy=0,sw=0;for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){const i=y*w+x,e=Math.abs(g[i+1]-g[i-1])+Math.abs(g[i+w]-g[i-w]);sx+=x*e;sy+=y*e;sw+=e}return sw?{x:sx/sw/w,y:sy/sw/h}:{x:.5,y:.5}}
/* フレーム列から指標を計算（テスト容易化のため純関数）。frames: [{g:Float32Array, t:sec}] */
function analyzeFrames(frames,meta){
 const n=frames.length,out={n,frames:[],sceneCuts:[],meta:meta||{}};
 const diffs=[];for(let i=1;i<n;i++)diffs.push(mad(frames[i-1].g,frames[i].g));
 const med=diffs.length?diffs.slice().sort((a,b)=>a-b)[diffs.length>>1]:0;
 const devs=diffs.map(d=>Math.abs(d-med)).sort((a,b)=>a-b),MAD=devs.length?devs[devs.length>>1]:0;
 const thr=Math.max(18,med+6*Math.max(MAD,2)); // 絶対下限18(0-255)と相対しきい値
 diffs.forEach((d,i)=>{if(d>thr)out.sceneCuts.push({t:+frames[i+1].t.toFixed(2),diff:+d.toFixed(1)})});
 frames.forEach((f,i)=>{const st=stats(f.g),lv=lapVar(f.g,W,H);out.frames.push({t:f.t,sharp:lv,mean:st.mean,std:st.std,hash:dhash(f.g,W,H),motion:i?diffs[i-1]:0,c:edgeCentroid(f.g,W,H)})});
 const F=out.frames,avg=k=>F.reduce((q,f)=>q+f[k],0)/Math.max(1,F.length);
 out.sharpness=avg('sharp');out.brightness=avg('mean');out.contrast=avg('std');out.motion=F.length>1?F.slice(1).reduce((q,f)=>q+f.motion,0)/(F.length-1):0;
 const cx=avg('c')?F.reduce((q,f)=>q+f.c.x,0)/F.length:.5,cy=F.reduce((q,f)=>q+f.c.y,0)/F.length;out.centroid={x:+cx.toFixed(2),y:+cy.toFixed(2)};
 /* 代表フレーム: 鮮明で露出が適正、シーン変化の直後を避ける */
 let best=-1,bs=-1;F.forEach((f,i)=>{const expo=1-Math.min(1,Math.abs(f.mean-120)/120),nearCut=out.sceneCuts.some(c=>Math.abs(c.t-f.t)<.25),s=Math.log1p(f.sharp)*(.4+.6*expo)*(nearCut?.3:1);if(s>bs){bs=s;best=i}});
 out.rep=best>=0?{index:best,t:F[best].t}:null;
 out.signature=F.filter(f=>f.std>=8).map(f=>f.hash); /* 平坦なフレーム(情報が少ない)は重複判定に使わない */
 return out}
/* 重複判定: 2動画の全サンプル対のdHashハミング距離の最小値（0〜64）。近いほど同一/酷似 */
function similarity(a,b){let m=64;for(const x of a.signature)for(const y of b.signature){const d=ham(x,y);if(d<m)m=d}return m}
/* 一致率: 短い方のフレームのうち、相手に距離<=thの近いフレームがある割合 */
function matchRatio(a,b,th){th=th==null?6:th;const [s,l]=a.signature.length<=b.signature.length?[a.signature,b.signature]:[b.signature,a.signature];if(!s.length)return 0;let k=0;for(const x of s)if(l.some(y=>ham(x,y)<=th))k++;return k/s.length}
function isDuplicate(a,b,th){return matchRatio(a,b,th)>=.5}
/* 簡易スコア(0-100)。重みは仮置き【推測】。解像度と縦型適合も含む。美しさ・感情の証明ではない */
function score(an){const m=an.meta||{},w=m.width||0,h=m.height||0,sc={};
 sc.sharp=Math.round(100*Math.min(1,Math.log1p(an.sharpness)/Math.log1p(400)));
 sc.exposure=Math.round(100*(1-Math.min(1,Math.abs(an.brightness-115)/115)));
 sc.contrast=Math.round(100*Math.min(1,an.contrast/55));
 sc.res=h>=1920||w>=1080?100:Math.round(100*Math.min(1,Math.max(w,h)/1920));
 sc.vertical=w&&h?(h>=w?100:Math.round(100*Math.max(0,1-(w/h-1)*.7))):0;
 sc.steady=Math.round(100*Math.max(0,1-Math.max(0,an.motion-3)/25));
 sc.total=Math.round(.28*sc.sharp+.18*sc.exposure+.12*sc.contrast+.14*sc.res+.18*sc.vertical+.10*sc.steady);
 return sc}
/* ブラウザ用: 動画要素をシークして一定間隔でサンプリング */
async function sampleVideo(el,opt){opt=opt||{};const dur=el.duration,step=opt.step||.5,max=opt.max||60,cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d',{willReadFrequently:true}),fr=[];
 const seek=t=>new Promise(ok=>{let d=false;const f=()=>{if(!d){d=true;el.removeEventListener('seeked',f);ok()}};el.addEventListener('seeked',f);try{el.pause()}catch{}el.currentTime=t;setTimeout(f,2000)});
 const vw=el.videoWidth,vh=el.videoHeight;
 for(let t=0,k=0;t<dur&&k<max;t+=step,k++){await seek(Math.min(t,Math.max(0,dur-.05)));
  /* cover表示（縦長枠に中央切り抜き） */const s=Math.max(W/vw,H/vh),dw=vw*s,dh=vh*s;g.fillStyle='#000';g.fillRect(0,0,W,H);g.drawImage(el,(W-dw)/2,(H-dh)/2,dw,dh);fr.push({g:gray(g.getImageData(0,0,W,H).data),t:+t.toFixed(2)})}
 return analyzeFrames(fr,{width:vw,height:vh,duration:dur})}
G.BSVision={W,H,gray,lapVar,dhash,ham,analyzeFrames,similarity,matchRatio,isDuplicate,score,sampleVideo};
if(typeof module!=='undefined')module.exports=G.BSVision;
})(typeof window!=='undefined'?window:globalThis);
