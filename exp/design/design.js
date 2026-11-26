/* BECOME. STUDIO 映像設計JSON 仕様 become.design/1
   ChatGPT・Claudeなど外部AIが作った設計データを、追加API費用なしで取り込むための検証器。
   通信なし。eval/Function不使用。JSON.parseした値だけを扱い、未知のキーは無視、型・範囲違反は取り込み拒否。 */
(function(G){
const SCHEMA='become.design/1';
const ENUM={
 role:['hook','build','low','turn','rise','climax','ending'],
 camera:['push-in-slow','drift-lateral','handheld-sway','push-in-fast','pull-back-reveal','tilt-up','static-hold','parallax-drift'],
 transition:['cut','dissolve','dip-black','flash-white'],
 speed:['normal','slow-motion','speed-ramp'],
 grade:['cold-teal','warm-gold','muted-neutral'],
 cut:['none','j-cut','l-cut'],
 kinetic:['none','char','track'],
 sfx:['riser','sub','hit','whoosh','shimmer'],
 bgmMood:['dark-ambient','cinematic-rise','calm-piano','tense-pulse','warm-strings','silence'],
 pace:['slow','normal','fast'],
 /* 演出ライブラリ名。実装状況は IMPL で管理 */
 fx:['kinetic-typography','parallax-layers','mask-reveal','match-cut','beat-sync-cut','live-anim-fusion']};
/* 実装済み/設計のみ（画面にもそのまま表示する） */
const IMPL={
 'color-grade':'実装済み','camera-moves(8種)':'実装済み','transition(dip/flash/leak/endfade)':'実装済み','caption-emphasis':'実装済み','sfx(5種)':'実装済み',
 'speed-ramp':'実装済み（クリップ再生速度と模擬素材の時間を再マップ）','slow-motion':'実装済み（0.5倍）','j-cut':'実装済み（映像がナレーションより先に切替）','l-cut':'実装済み（映像が遅れて切替）',
 'parallax-drift(カメラ)':'近似のみ（平行移動。多層視差ではない）',
 'kinetic-typography':'実装済み（char=1文字ずつ弾むように出現・強調語は拡大から収束 / track=字間が広がりから収束。fxに指定するとchar）','parallax-layers':'設計のみ','mask-reveal':'設計のみ','match-cut':'設計のみ（映像の中身の照合が必要）','beat-sync-cut':'実装済み（bgm.bpmが必要。場面の切替を拍に最大0.3秒吸着、BGMに拍の低音を追加、切替で軽いズーム）','live-anim-fusion':'設計のみ'};
const FXLIVE=['kinetic-typography','beat-sync-cut'];
const LIM={scenes:40,total:90,text:80,dur:[1.2,8],queries:4,q:40,emph:4,qa:10,qaLen:100,title:60,long:2000,mid:300};
const isObj=v=>v&&typeof v==='object'&&!Array.isArray(v);
const clean=s=>String(s).replace(/[\u0000-\u001f\u007f<>]/g,'').trim();
function validate(input){
 const err=[],warn=[];let d;
 try{d=typeof input==='string'?JSON.parse(input.replace(/^﻿/,'').replace(/^\s*```(?:json)?/i,'').replace(/```\s*$/,'')):input}catch(e){return{ok:false,errors:['JSONとして読めません: '+e.message],warnings:[],plan:null}}
 if(!isObj(d))return{ok:false,errors:['最上位はオブジェクトにしてください'],warnings:[],plan:null};
 if(d.schema!==SCHEMA)err.push('schema は "'+SCHEMA+'" にしてください');
 const str=(v,max,name,req)=>{if(v==null||v===''){if(req)err.push(name+' が必要です');return''}if(typeof v!=='string'){err.push(name+' は文字列にしてください');return''}if(v.length>max){err.push(name+' は'+max+'字以内にしてください');return''}return clean(v)};
 const num=(v,lo,hi,name,def)=>{if(v==null)return def;if(typeof v!=='number'||!isFinite(v)){err.push(name+' は数値にしてください');return def}if(v<lo||v>hi){err.push(name+' は'+lo+'〜'+hi+'の範囲にしてください');return def}return v};
 const en=(v,list,name,def)=>{if(v==null)return def;if(!list.includes(v)){err.push(name+' は '+list.join('/')+' のいずれかにしてください（受信: '+String(v).slice(0,20)+'）');return def}return v};
 const title=str(d.title,LIM.title,'title');const script=str(d.script,LIM.long,'script');
 const audience=str(d.audience,LIM.mid,'audience');const intent=str(d.intent,LIM.mid,'intent');
 if(!Array.isArray(d.scenes)||!d.scenes.length)err.push('scenes は1件以上の配列にしてください');
 else if(d.scenes.length>LIM.scenes)err.push('scenes は'+LIM.scenes+'件以内にしてください');
 const scenes=[];let t=0;
 if(Array.isArray(d.scenes)&&d.scenes.length<=LIM.scenes)d.scenes.forEach((s,i)=>{const P='scenes['+i+'].';
  if(!isObj(s)){err.push(P+' はオブジェクトにしてください');return}
  const text=str(s.text,LIM.text,P+'text',true);
  const dur=num(s.dur,LIM.dur[0],LIM.dur[1],P+'dur',null);if(dur==null&&s.dur==null)err.push(P+'dur が必要です');
  const role=en(s.role,ENUM.role,P+'role','build');
  const emo=isObj(s.emotion)?{v:num(s.emotion.valence,-1,1,P+'emotion.valence',0),a:num(s.emotion.arousal,0,1,P+'emotion.arousal',.4)}:{v:0,a:.4};
  if(s.emotion!=null&&!isObj(s.emotion))err.push(P+'emotion はオブジェクトにしてください');
  const camera=en(s.camera,ENUM.camera,P+'camera','drift-lateral');
  const transition=en(s.transition,ENUM.transition,P+'transition','cut');
  const speed=en(s.speed,ENUM.speed,P+'speed','normal');
  const grade=en(s.grade,ENUM.grade,P+'grade','muted-neutral');
  let cut={type:'none',off:0};if(s.cut!=null){if(!isObj(s.cut))err.push(P+'cut はオブジェクトにしてください');else{cut.type=en(s.cut.type,ENUM.cut,P+'cut.type','none');cut.off=num(s.cut.offset,.1,1,P+'cut.offset',.3)}}
  const arr=(v,name,max,each,len)=>{if(v==null)return[];if(!Array.isArray(v)){err.push(name+' は配列にしてください');return[]}if(v.length>max){err.push(name+' は'+max+'件以内にしてください');return[]}return v.map((x,k)=>str(x,len,name+'['+k+']')).filter(Boolean)};
  const emphasis=arr(s.emphasis,P+'emphasis',LIM.emph,0,20);emphasis.forEach(e=>{if(!text.includes(e))warn.push(P+'emphasis「'+e+'」は text に含まれていないため無視します')});
  const sr=isObj(s.search)?s.search:{};const queries=arr(sr.queries,P+'search.queries',LIM.queries,0,LIM.q);
  const avoid=arr(sr.avoid,P+'search.avoid',LIM.queries,0,LIM.q);
  const minHeight=num(sr.minHeight,360,4320,P+'search.minHeight',1080);
  let sfx={};if(s.sfx!=null){if(!Array.isArray(s.sfx))err.push(P+'sfx は配列にしてください');else s.sfx.forEach(k=>{if(!ENUM.sfx.includes(k))err.push(P+'sfx に未対応の値: '+String(k).slice(0,20));else sfx[k]=1})}
  const fx=arr(s.fx,P+'fx',4,0,30);const fxOk=[];fx.forEach(f=>{if(!ENUM.fx.includes(f)){err.push(P+'fx に未対応の値: '+f)}else{fxOk.push(f);if(!FXLIVE.includes(f))warn.push(P+'fx「'+f+'」は設計のみのため、完成動画には反映されません')}});
  const kinetic=en(s.kinetic,ENUM.kinetic,P+'kinetic',fxOk.includes('kinetic-typography')?'char':'none');
  const beat=fxOk.includes('beat-sync-cut');
  const start=num(s.start,0,90,P+'start',null);const st0=start==null?t:start;
  scenes.push({i,text,role,emotion:{v:emo.v,a:emo.a},start:+st0.toFixed(2),dur:dur||0,camera,transition,speed,grade,emphasis:emphasis.filter(e=>text.includes(e)),concepts:[],sfx,queries,avoid,minHeight,cut,fx:fxOk,kinetic,beat,notes:str(s.notes,LIM.mid,P+'notes')});
  t=st0+(dur||0)});
 for(let i=1;i<scenes.length;i++){if(scenes[i].start<scenes[i-1].start+scenes[i-1].dur-.05)err.push('scenes['+i+'] の開始が前の場面と重なっています');}
 const total=scenes.length?scenes[scenes.length-1].start+scenes[scenes.length-1].dur:0;
 if(total>LIM.total)err.push('全体の長さは'+LIM.total+'秒以内にしてください（現在 '+total.toFixed(1)+'秒）');
 const bgm=isObj(d.bgm)?{mood:en(d.bgm.mood,ENUM.bgmMood,'bgm.mood','dark-ambient'),bpm:num(d.bgm.bpm,40,200,'bgm.bpm',null)}:null;
 const narration=isObj(d.narration)?{voice:str(d.narration.voice,LIM.mid,'narration.voice'),pace:en(d.narration.pace,ENUM.pace,'narration.pace','normal'),tone:str(d.narration.tone,LIM.mid,'narration.tone')}:null;
 const ending=isObj(d.ending)?{holdSec:num(d.ending.holdSec,.5,4,'ending.holdSec',1.8),text:str(d.ending.text,LIM.text,'ending.text')}:{holdSec:1.8,text:''};
 const qa=Array.isArray(d.qa)?d.qa.slice(0,LIM.qa).map(x=>clean(String(x)).slice(0,LIM.qaLen)):[];
 const palette=isObj(d.color)?{mood:str(d.color.mood,LIM.mid,'color.mood')}:null;
 if(scenes.some(x=>x.beat)&&!(bgm&&bgm.bpm)){warn.push('beat-sync-cut には bgm.bpm が必要です。bpm が無いため拍への吸着は行いません');scenes.forEach(x=>{x.beat=false})}
 const known=['schema','title','script','audience','intent','scenes','bgm','narration','ending','qa','color'];
 Object.keys(d).forEach(k=>{if(!known.includes(k))warn.push('未対応の項目 "'+k.slice(0,30)+'" は無視します')});
 if(err.length)return{ok:false,errors:err.slice(0,30),warnings:warn.slice(0,30),plan:null};
 const plan={meta:{totalSec:+total.toFixed(1),beats:scenes.length,source:'design-json',title,script,audience,intent,bgm,narration,ending,qa,palette,advice:[],notes:'外部AI（ChatGPT/Claude等）が作った設計データ。形式検証のみ済み。内容の妥当性・素材との一致は未確認'},scenes};
 return{ok:true,errors:[],warnings:warn.slice(0,30),plan};
}
function requestPrompt(script){
 const ex={schema:SCHEMA,title:'夜明け前',audience:'20〜30代・努力が報われず悩む人',intent:'孤独を認めたうえで、小さな一歩に希望を見せる',
  scenes:[{text:'誰も見ていない朝',dur:2.6,role:'hook',emotion:{valence:-.2,arousal:.3},camera:'push-in-slow',transition:'cut',speed:'normal',grade:'cold-teal',emphasis:['誰も'],search:{queries:['dark room desk dawn','lonely person window'],avoid:['logo','text'],minHeight:1080},sfx:['riser']},
   {text:'それでも一歩だけ前へ',dur:3.4,role:'turn',emotion:{valence:.4,arousal:.7},camera:'push-in-fast',transition:'flash-white',speed:'speed-ramp',grade:'warm-gold',cut:{type:'j-cut',offset:.3},emphasis:['一歩'],search:{queries:['walking forward sunrise']},sfx:['hit']}],
  bgm:{mood:'cinematic-rise',bpm:72},narration:{voice:'低く落ち着いた女性',pace:'slow',tone:'優しく力強い'},ending:{holdSec:1.8,text:''},qa:['各場面の字幕は80字以内','全体90秒以内']};
 return '次の台本を、縦型(1080x1920)のモチベーション動画の編集設計として、JSON「だけ」で出力してください（説明文・コードブロック記号は不要）。\n\n【ルール】\n- schema は "'+SCHEMA+'" 固定。\n- scenes は1〜'+LIM.scenes+'件、各 dur は'+LIM.dur[0]+'〜'+LIM.dur[1]+'秒、合計'+LIM.total+'秒以内。text は'+LIM.text+'字以内（字幕兼ナレーション）。\n- role: '+ENUM.role.join(' | ')+'\n- camera: '+ENUM.camera.join(' | ')+'\n- transition: '+ENUM.transition.join(' | ')+'\n- speed: '+ENUM.speed.join(' | ')+'（speed-ramp＝加速から減速、slow-motion＝0.5倍。山場・転換・結びに限って使い、多用しない）\n- grade: '+ENUM.grade.join(' | ')+'\n- cut.type: '+ENUM.cut.join(' | ')+'（j-cut＝映像が声より先に切替、l-cut＝映像が遅れて切替。offset は0.1〜1秒）\n- sfx: '+ENUM.sfx.join(' | ')+' の配列\n- emphasis は text の一部をそのまま抜き出す（最大'+LIM.emph+'個）。\n- search.queries は素材検索用の英語キーワード（最大'+LIM.queries+'個）。著作物・ロゴ・実在人物の指名は避ける。\n- 感情は emotion.valence(-1〜1) と arousal(0〜1)。物語として感情が変化し、冒頭に引きがあり、結びに余韻があること。\n- kinetic は '+ENUM.kinetic.join(' | ')+'（char=1文字ずつ弾む出現、track=字間が広がりから収束。冒頭・転換・山場に限る）。fx は '+ENUM.fx.join(' | ')+' が使えます。反映されるのは kinetic-typography と beat-sync-cut（bgm.bpm 必須）のみで、他は設計メモ扱いです。\n- 1つの場面に演出を詰め込みすぎず、意味に応じて使い分けてください。\n\n【出力例の形】\n'+JSON.stringify(ex,null,1)+'\n\n【台本】\n'+(script||'（ここに台本）');
}
G.BSDesign={SCHEMA,ENUM,IMPL,LIM,validate,requestPrompt};
if(typeof module!=='undefined')module.exports=G.BSDesign;
})(typeof window!=='undefined'?window:globalThis);
