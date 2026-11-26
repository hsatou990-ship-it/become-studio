/* BECOME. STUDIO AI映像ディレクター（試作v0・ルール＋辞書方式）。通信なし・外部AIなし。
   台本 → 感情曲線 → 役割 → 可変長タイムライン（カメラ・切替・色・字幕強調・音）。
   限界: 辞書にない表現の感情は取れない【推測方式】。映像素材との意味照合は未実装（次段: CLIP/SigLIP系）。 */
(function(G){
const LEX=[
 {id:'solitude',v:-.6,a:.3,w:['孤独','一人','ひとり','不安','怖','迷','暗','誰も','逃げ','寂']},
 {id:'pain',v:-.8,a:.5,w:['失敗','挫折','辛','苦し','痛','折れ','泣','涙','絶望','限界','諦','疲']},
 {id:'anger',v:-.4,a:.85,w:['悔し','怒','許せ','見返','負け']},
 {id:'resolve',v:.3,a:.7,w:['決め','誓','覚悟','立ち上が','始め','一歩','挑','それでも','やる']},
 {id:'hope',v:.7,a:.5,w:['希望','光','変わ','成長','未来','夢','前に','進','信じ']},
 {id:'triumph',v:.9,a:.85,w:['勝','達成','掴','成功','叶','頂','朝日','昇']},
 {id:'calm',v:.4,a:.1,w:['静か','ゆっくり','深呼吸','休','風','朝','穏']}];
const CONCEPT=[[/夜明け|朝日|日の出|朝/,'sunrise'],[/夕日|夕暮れ/,'sunset'],[/山|頂|登/,'mountain'],[/海|波/,'ocean'],[/走|ラン/,'running'],[/筋トレ|トレーニング|鍛/,'gym'],[/勉強|読書|学/,'book'],[/孤独|一人|誰も/,'alone'],[/暗|夜/,'night'],[/雨|涙/,'rain'],[/雲|空/,'sky'],[/街|都市/,'city'],[/道|歩|一歩|進/,'road'],[/階段/,'stairs'],[/時間|時計/,'clock'],[/森|木/,'forest'],[/光|輝/,'light'],[/嵐|失敗|折れ/,'storm'],[/炎|情熱/,'fire'],[/水|川/,'water'],[/扉|始め|決め/,'door']];
const CAM={'push-in-slow':{d:'ゆっくり寄る。緊張・内省'},'drift-lateral':{d:'横へ漂う。孤独・時間経過'},'handheld-sway':{d:'手持ち風の揺れ。不安・怒り'},'push-in-fast':{d:'素早く寄る。決断の瞬間'},'pull-back-reveal':{d:'引いて全体を見せる。解放・余韻'},'tilt-up':{d:'見上げる。希望・上昇'},'static-hold':{d:'動かさない。静けさ・結末'},'parallax-drift':{d:'奥行きのずれで漂う。世界の広がり'}};
const TR={'cut':'即カット','dissolve':'ゆっくり重ねる','dip-black':'暗転を挟む','flash-white':'白い閃光','match-cut':'形・動き・色が似た素材でつなぐ','j-cut':'次の声が先に入る','l-cut':'前の声が残る'};
const GRADE={cold:{name:'cold-teal',sat:.75,con:1.12,warm:-.3},neutral:{name:'muted-neutral',sat:.9,con:1.05,warm:0},warm:{name:'warm-gold',sat:1.08,con:1.1,warm:.35}};
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function rng(seed){let a=seed||1;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function splitBeats(script,cps){const sents=script.split(/[\n。！？!?]+/).map(s=>s.trim()).filter(Boolean),beats=[];
 for(const s of sents){const strong=/[！!]/.test(script.slice(script.indexOf(s)+s.length,script.indexOf(s)+s.length+2));
  if(s.length>(strong?18:28)&&/、|,/.test(s)){const parts=s.split(/、|,/).map(x=>x.trim()).filter(Boolean);let cur='';for(const p of parts){if((cur+p).length>(strong?14:22)&&cur){beats.push(cur);cur=p}else cur=cur?cur+'、'+p:p}if(cur)beats.push(cur)}else beats.push(s)}
 return beats}
function analyze(t,i){let v=0,a=.3,n=0,hits=[];for(const c of LEX)for(const w of c.w)if(t.includes(w)){v+=c.v;a+=c.a;n++;hits.push({w,v:c.v})}
 if(n){v/=n;a=(a-.3)/n*.7+.3*.3}else{v=0;a=.3}
 if(/[！!]/.test(t))a+=.15;if(/[？?]/.test(t))a+=.05;if(/ない|なかった|できない/.test(t)&&v>0)v*=.5;
 return{v:Math.max(-1,Math.min(1,v)),a:Math.max(0,Math.min(1,a)),hits}}
function phrase(t,w){const i=t.indexOf(w);if(i<0)return w;let a=i,e=i+w.length;const P='はがをにでともの、，,へやか';while(a>0&&/[\u4e00-\u9fff]/.test(t[a-1])&&e-a<4)a--;while(e<t.length&&!P.includes(t[e])&&e-a<7)e++;return t.slice(a,e)}
function concepts(t){const o=[];for(const [re,id] of CONCEPT)if(re.test(t)&&!o.includes(id))o.push(id);return o}
function plan(script,opt){opt=opt||{};const cps=opt.cps||5.2,target=opt.target||0,seed=hash(script+'|'+(opt.variant||0)),R=rng(seed),advice=[];
 const beats=splitBeats(script,cps);if(!beats.length)return{meta:{error:'台本が空です'},scenes:[]};
 const A=beats.map(analyze),V=A.map(x=>x.v),Ar=A.map(x=>x.a);
 const SV=V.map((_,i)=>{const w=[V[i-1],V[i],V[i+1]].filter(x=>x!==undefined);return w.reduce((p,q)=>p+q,0)/w.length});
 let low=0;for(let i=1;i<beats.length;i++)if(SV[i]<SV[low])low=i;
 let turn=-1,gain=.25;for(let i=Math.max(1,low);i<beats.length;i++){const g=V[i]-(V[i-1]);if(g>gain){gain=g;turn=i}}
 if(turn<0)for(let i=low+1;i<beats.length;i++)if(V[i]>V[low]+.3){turn=i;break}
 const last=beats.length-1;let climax=-1,mx=-1;for(let i=Math.max(turn,0);i<=last;i++)if(Ar[i]>mx){mx=Ar[i];climax=i}
 const role=i=>i===0?'hook':i===last&&last>0?'ending':i===turn?'turn':i===climax&&turn>=0&&i>turn?'climax':i===low&&SV[low]<-.2?'low':(turn>=0&&i>turn)?'rise':'build';
 const bpm=Math.round(60+30*(Ar.reduce((p,q)=>p+q,0)/Ar.length)),beat=60/bpm;
 let t=0,prevCam='',prevTr='',trRun=0;const scenes=[];
 beats.forEach((txt,i)=>{const r=role(i),an=A[i],speech=txt.replace(/[、，,\s]/g,'').length/cps;
  let pause=.25+.35*(1-an.a);if(r==='turn')pause+=.5;if(i===last)pause+=1.2;if(i===0)pause+=.15;
  let dur=Math.max(1.6,Math.min(6,speech+pause));
  const lead=i===0?.4:0;
  // camera
  const cand=[];const v=SV[i],a=an.a;
  if(r==='ending'){cand.push('pull-back-reveal','static-hold','parallax-drift')}
  else if(r==='turn'){cand.push('push-in-fast','tilt-up')}
  else if(r==='climax'){cand.push('push-in-fast','parallax-drift','tilt-up')}
  else if(v<-.3&&a>.6){cand.push('handheld-sway','push-in-slow')}
  else if(v<-.3){cand.push('push-in-slow','drift-lateral','handheld-sway')}
  else if(v>.4){cand.push('tilt-up','parallax-drift','pull-back-reveal')}
  else{cand.push('drift-lateral','parallax-drift','push-in-slow')}
  const pool=cand.filter(c=>c!==prevCam),cam=pool[Math.floor(R()*pool.length)]||cand[0];prevCam=cam;
  // grade
  const g=v<-.25?'cold':v>.3?'warm':'neutral';
  // transition (into this scene)
  let tr='cut';
  if(i>0){const p=scenes[i-1],dv=SV[i]-SV[i-1],shared=concepts(txt).filter(c=>p.concepts.includes(c));
   if(r==='turn'||r==='climax')tr='flash-white';else if(shared.length)tr='match-cut';else if(dv<-.35)tr='dip-black';
   else if(an.a<.35&&Math.abs(dv)<.25)tr=R()<.5?'j-cut':'dissolve';else if(i>low&&i<=low+1&&p.emotion.v<-.3)tr='l-cut';else if(an.a>.6)tr='cut';else tr='dissolve';
   if(tr===prevTr&&++trRun>=2){tr=tr==='cut'?'dissolve':'cut';trRun=0}else if(tr!==prevTr)trRun=0;prevTr=tr}
  const speed=r==='turn'||r==='climax'?'speed-ramp':r==='ending'?'slow-motion':'normal';
  const emph=an.hits.sort((x,y)=>Math.abs(y.v)-Math.abs(x.v)).slice(0,2).map(h=>phrase(txt,h.w));
  const cs=concepts(txt);
  const sfx=[];if(r==='turn'){sfx.push({at:'-1.2s',kind:'riser'},{at:'0s',kind:'low-hit'},{at:'-0.4s',kind:'silence-gap'})}if(r==='climax')sfx.push({at:'0s',kind:'whoosh+chime'});if(r==='ending')sfx.push({at:'+0.6s',kind:'tail-shimmer'});if(i>0&&tr==='dip-black')sfx.push({at:'0s',kind:'sub-drop'});
  scenes.push({i,text:txt,role:r,emotion:{v:+V[i].toFixed(2),a:+an.a.toFixed(2)},start:+t.toFixed(2),dur:+dur.toFixed(2),camera:cam,transition:tr,speed,grade:GRADE[g].name,emphasis:emph,concepts:cs,sfx,queries:cs.length?cs.slice(0,3):[r==='hook'?'dramatic sky':r==='ending'?'sunrise light':'person silhouette']});
  t+=dur});
 // 音楽の拍へ軽く吸着（±0.25秒）。最後の合計は変えない
 for(let i=1;i<scenes.length;i++){const s=scenes[i],near=Math.round(s.start/beat)*beat;if(Math.abs(near-s.start)<=.25){const d=near-s.start;scenes[i-1].dur=+(scenes[i-1].dur+d).toFixed(2);s.start=+near.toFixed(2);s.dur=+(s.dur-d).toFixed(2)}}
 const total=scenes.reduce((p,s)=>p+s.dur,0);
 if(Ar[0]<.45&&Math.abs(V[0])<.3)advice.push('冒頭が弱いです。最初の1文に感情語か問いかけを入れてください（最初の3秒が離脱の分かれ目）。');
 if(turn<0)advice.push('感情の転換点（落ちる→上がる）が見つかりません。苦しさと決意の落差を作ると映像の起伏が出ます。');
 if(SV[last]<.2)advice.push('結末が前向きになっていません。最後は余韻を残す言葉（希望・静けさ）で終えるのが無難です。');
 if(Math.max(...Ar)-Math.min(...Ar)<.25)advice.push('緊張の強弱が一定です。静かな文と強い文を混ぜると編集テンポに緩急が出ます。');
 if(target&&total>target*1.1)advice.push('台本が目標'+target+'秒より長いです（約'+total.toFixed(0)+'秒）。文を削るか目標秒数を延ばしてください。');
 if(target&&total<target*.7)advice.push('台本が目標'+target+'秒に対して短いです（約'+total.toFixed(0)+'秒）。間や余韻で埋めず、内容を足すことを勧めます。');
 return{meta:{totalSec:+total.toFixed(1),beats:beats.length,bpm,cps,seed,turn,low,advice,notes:'感情・役割は辞書とルールによる【推測】。実素材との意味照合は未実装'},scenes,curve:{valence:V,arousal:Ar}}}
G.DIR={plan,CAM,TR,GRADE,LEX,analyze,splitBeats};if(typeof module!=='undefined')module.exports=G.DIR;
})(typeof window!=='undefined'?window:globalThis);
