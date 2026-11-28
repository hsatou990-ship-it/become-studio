/* BECOME. STUDIO 段階B-0: 視覚意図カードと、複数フレーム判定（モデル非依存の純粋関数）。
   ・日本語の台本の意味は変換せず原文（ja）をそのまま保持する。英語の文は、設計JSONの明示項目
     （search.queries / search.avoid / camera / grade / emotion）の定型対応からだけ作る。自由翻訳はしない。
   ・CLIPの類似度は「候補の順位付けと除外の手がかり」であり、素材の品質・権利・見た目の良さを保証しない。
   ・閾値は未較正の仮の値。測定ページの正例/誤例の結果で決める（測るまでは「未較正」と表示）。 */
(function(root){
'use strict';
const LEX={
 camera:{'push-in-slow':'slow push-in camera movement','push-in-fast':'fast push-in camera movement','drift-lateral':'slow sideways drifting camera','handheld-sway':'handheld camera with gentle sway','pull-back-reveal':'camera pulling back to reveal the scene','tilt-up':'camera tilting up','static-hold':'static locked-off shot','parallax-drift':'drifting shot with depth parallax'},
 grade:{'cold-teal':'cold teal color grading, dim light','warm-gold':'warm golden light','muted-neutral':'muted neutral tones, soft light'}
};
const DEFAULT_AVOID=['logo','watermark','text overlay'];
function emotionEn(e){if(!e||typeof e.valence!=='number')return null;const v=e.valence,a=typeof e.arousal==='number'?e.arousal:.3;
 const tone=v<=-.4?'gloomy, lonely':v<-.1?'quiet, uneasy':v<.2?'calm, neutral':v<.5?'hopeful':'bright, uplifting';
 return tone+(a>=.6?', tense':a<=.2?', still':'')}
function buildCard(scene,i,plan){
 const s=scene||{},q=(s.search&&Array.isArray(s.search.queries)?s.search.queries:[]).map(x=>String(x).trim()).filter(Boolean);
 const av=[...new Set([...(s.search&&Array.isArray(s.search.avoid)?s.search.avoid:[]).map(x=>String(x).trim()).filter(Boolean),...DEFAULT_AVOID])];
 const light=LEX.grade[s.grade]||null,motion=LEX.camera[s.camera]||null,emo=emotionEn(s.emotion);
 const unset=['composition'];            // 設計JSONに構図の項目が無いため、未設定として明示する（推測で埋めない）
 if(!q.length)unset.push('subjects');if(!light)unset.push('light');if(!motion)unset.push('motion');if(!emo)unset.push('emotion');
 const pos=[];q.forEach(x=>{pos.push('a video frame of '+x);if(light)pos.push('a video frame of '+x+', '+light);if(emo)pos.push('a video frame of '+x+', '+emo+' mood')});
 return{i,ja:String(s.text||''),role:s.role||null,emphasis:s.emphasis||[],subjects:q,actions:[],avoid:av,emotion:emo,light,motion,
  world:(plan&&(plan.intent||plan.title))||null,   // 日本語のまま保持（英語化しない）
  prompts:{pos,avoid:av.map(x=>'a video frame with '+x)},unset,needsReview:!q.length,
  note:'英語は設計JSONの明示項目の定型対応のみ。日本語の台本の意味（ja）は原文のまま。動き（motion）は静止フレームでは評価できないため、候補の順位には使わない。'}}
function buildCards(plan){return(plan&&plan.scenes||[]).map((s,i)=>buildCard(s,i,plan))}
/* ---------- 数値 ---------- */
function l2(v){let n=0;for(let i=0;i<v.length;i++)n+=v[i]*v[i];n=Math.sqrt(n)||1;const o=new Float32Array(v.length);for(let i=0;i<v.length;i++)o[i]=v[i]/n;return o}
function cos(a,b){let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s}
function softmax(x,T){const m=Math.max(...x),e=x.map(v=>Math.exp((v-m)*T)),z=e.reduce((a,b)=>a+b,0);return e.map(v=>v/z)}
const TH={T:100,pos:.5,avoid:.5,agree:.6,minFrames:2,calibrated:false};
/* 1フレームの3者比較（肯定の最大／除外の最大／他の場面の最大）を確率にする */
function frameScore(f,card,othersPos,th){th=th||TH;const mx=(P)=>P.length?Math.max(...P.map(t=>cos(f,t))):-1;
 const sp=mx(card.posVec||[]),sa=mx(card.avoidVec||[]),so=mx(othersPos||[]);
 const hasO=(othersPos||[]).length>0,hasA=(card.avoidVec||[]).length>0;
 const g=[sp];if(hasA)g.push(sa);if(hasO)g.push(so);const p=softmax(g,th.T);let k=1;
 return{pos:p[0],avoid:hasA?p[k++]:0,other:hasO?p[k]:0,cos:{pos:sp,avoid:hasA?sa:null,other:hasO?so:null}}}
/* 複数フレームで判定する。保証ではなく「判定と理由」を返す */
function judge(frames,card,othersPos,th){th=th||TH;
 if(!card.posVec||!card.posVec.length)return{verdict:'unscored',reason:'英語の意図カードに被写体がありません（設計JSONに検索語が必要）',frames:0,guarantee:false};
 if(!frames||!frames.length)return{verdict:'unscored',reason:'フレームがありません',frames:0,guarantee:false};
 const F=frames.map(f=>frameScore(f,card,othersPos,th)),n=F.length,mean=k=>F.reduce((a,b)=>a+b[k],0)/n;
 const posMean=mean('pos'),otherMean=mean('other'),avoidMax=Math.max(...F.map(x=>x.avoid)),avoidFrames=F.filter(x=>x.avoid>=th.avoid).length,agree=F.filter(x=>x.pos>=th.pos).length/n;
 const sd=Math.sqrt(F.reduce((a,b)=>a+(b.pos-posMean)**2,0)/n);let verdict,reason;
 if(avoidFrames>0){verdict='avoid';reason='除外条件に近いフレームが'+avoidFrames+'/'+n+'枚あります'}
 else if(n<th.minFrames){verdict='uncertain';reason='フレーム数が少ないため判定できません（'+n+'枚）'}
 else if(otherMean>posMean&&(othersPos||[]).length){verdict='other-scene';reason='他の場面の意図に、より近い映像です'}
 else if(posMean>=th.pos&&agree>=th.agree){verdict='match';reason='肯定条件に近く、'+Math.round(agree*100)+'%のフレームが一致'}
 else{verdict='uncertain';reason='肯定条件との一致が弱い、またはフレーム間でばらつきがあります'}
 return{verdict,reason,frames:n,posMean:+posMean.toFixed(4),otherMean:+otherMean.toFixed(4),avoidMax:+avoidMax.toFixed(4),agree:+agree.toFixed(3),sd:+sd.toFixed(4),calibrated:th.calibrated,guarantee:false}}
/* 候補（クリップ）群から場面ごとの順位。同点は入力順。rank は確率の降順 */
function rank(cards,clips,th){th=th||TH;const out=cards.map(()=>[]);
 cards.forEach((c,si)=>{const oth=[];cards.forEach((d,sj)=>{if(sj!==si&&d.posVec)oth.push(...d.posVec)});
  clips.forEach((cl,ci)=>{const j=judge(cl.frames,c,oth,th);out[si].push({clip:ci,key:cl.key,...j})});
  out[si].sort((a,b)=>(b.posMean||-1)-(a.posMean||-1))});return out}
/* 正例/誤例ペアの評価。pairs=[{label:true|false,score}] */
function evalPairs(pairs,thr){const P=pairs.filter(x=>x.label),N=pairs.filter(x=>!x.label);
 let w=0;P.forEach(p=>N.forEach(n=>{w+=p.score>n.score?1:p.score===n.score?.5:0}));
 const auc=P.length&&N.length?w/(P.length*N.length):null;let tp=0,fp=0,fn=0,tn=0;
 pairs.forEach(x=>{const y=x.score>=thr;if(x.label&&y)tp++;else if(!x.label&&y)fp++;else if(x.label&&!y)fn++;else tn++});
 return{n:pairs.length,pos:P.length,neg:N.length,auc,tp,fp,fn,tn,precision:tp+fp?tp/(tp+fp):null,recall:tp+fn?tp/(tp+fn):null,accuracy:pairs.length?(tp+tn)/pairs.length:null}}
root.BSIntent={LEX,DEFAULT_AVOID,TH,buildCard,buildCards,l2,cos,softmax,frameScore,judge,rank,evalPairs};
if(typeof module!=='undefined')module.exports=root.BSIntent;
})(typeof window!=='undefined'?window:globalThis);
