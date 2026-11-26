/* BECOME. STUDIO export inspector (isolated). Parses real bytes; never trusts extension/mime. */
(function(G){
function u32(d,o){return d.getUint32(o)}
function t4(d,o){return String.fromCharCode(d.getUint8(o),d.getUint8(o+1),d.getUint8(o+2),d.getUint8(o+3))}
function boxes(d,s,e){const r=[];while(s+8<=e){let sz=u32(d,s),ty=t4(d,s+4),h=8;if(sz===1){sz=u32(d,s+8)*4294967296+u32(d,s+12);h=16}else if(sz===0)sz=e-s;if(sz<h||s+sz>e+0){if(s+sz>e)sz=e-s;if(sz<h)break}r.push({ty,s,h,e:s+sz,b:s+h});s+=sz}return r}
function kids(d,b,skip){return boxes(d,b.b+(skip||0),b.e)}
function find(l,t){return l.find(x=>x.ty===t)}
function mp4(buf){
 const d=new DataView(buf),top=boxes(d,0,buf.byteLength),R={container:'mp4',tracks:[],fragmented:false,problems:[]};
 const ft=find(top,'ftyp');if(!ft){R.problems.push('ftypなし');return R}
 R.brand=t4(d,ft.b);
 const moov=find(top,'moov');if(!moov){R.problems.push('moovなし');return R}
 const mk=kids(d,moov),mv=find(mk,'mvhd');let mts=1,mdur=0;
 if(mv){const v=d.getUint8(mv.b);if(v===1){mts=u32(d,mv.b+20);mdur=u32(d,mv.b+24)*4294967296+u32(d,mv.b+28)}else{mts=u32(d,mv.b+12);mdur=u32(d,mv.b+16)}}
 const mvex=find(mk,'mvex');R.fragmented=!!mvex||top.some(x=>x.ty==='moof');
 const trex={};if(mvex)kids(d,mvex).filter(x=>x.ty==='trex').forEach(x=>{trex[u32(d,x.b+4)]={dd:u32(d,x.b+12)}});
 const moofs=top.filter(x=>x.ty==='moof');
 for(const tk of mk.filter(x=>x.ty==='trak')){
  const tl=kids(d,tk),tkhd=find(tl,'tkhd'),mdia=find(tl,'mdia');if(!mdia)continue;
  const tid=u32(d,tkhd.b+(d.getUint8(tkhd.b)===1?20:12));
  const ml=kids(d,mdia),mdhd=find(ml,'mdhd'),hdlr=find(ml,'hdlr'),minf=find(ml,'minf');
  let ts,dur;const v=d.getUint8(mdhd.b);if(v===1){ts=u32(d,mdhd.b+20);dur=u32(d,mdhd.b+24)*4294967296+u32(d,mdhd.b+28)}else{ts=u32(d,mdhd.b+12);dur=u32(d,mdhd.b+16)}
  const kind=t4(d,hdlr.b+8),T={id:tid,kind:kind==='vide'?'video':kind==='soun'?'audio':kind};
  const st=find(kids(d,minf),'stbl'),sl=kids(d,st),sd=find(sl,'stsd'),en=boxes(d,sd.b+8,sd.e)[0];
  T.codecTag=en.ty;
  if(T.kind==='video'){T.width=d.getUint16(en.b+24);T.height=d.getUint16(en.b+26);
   const ch=boxes(d,en.b+78,en.e),av=find(ch,'avcC');
   if(av){const p=d.getUint8(av.b+1),pc=d.getUint8(av.b+2),l=d.getUint8(av.b+3);T.codec='H.264';T.profile=({66:'Baseline',77:'Main',100:'High',110:'High10'})[p]||('profile'+p);T.level=(l/10).toFixed(1)}
   else if(en.ty==='hvc1'||en.ty==='hev1')T.codec='H.265';else if(en.ty==='vp09')T.codec='VP9';else if(en.ty==='av01')T.codec='AV1';else T.codec=en.ty}
  else if(T.kind==='audio'){T.channels=d.getUint16(en.b+16);T.sampleRate=d.getUint16(en.b+24);
   if(en.ty==='mp4a'){const ch=boxes(d,en.b+28,en.e),es=find(ch,'esds');T.codec='AAC';if(es){let o=es.b+4,oti=null;for(let i=0;i<40&&o<es.e;i++){if(d.getUint8(o)===4){o++;while(d.getUint8(o)&128)o++;o++;oti=d.getUint8(o);break}o++}T.oti=oti;if(oti!==0x40){T.codec='mp4a(OTI 0x'+(oti||0).toString(16)+')'}}}
   else if(en.ty==='Opus')T.codec='Opus';else T.codec=en.ty}
  // samples
  let n=0,tot=0;
  const stts=find(sl,'stts');
  if(stts){const c=u32(d,stts.b+4);for(let i=0;i<c;i++){const k=u32(d,stts.b+8+i*8),dl=u32(d,stts.b+12+i*8);n+=k;tot+=k*dl}}
  for(const mf of moofs){for(const tf of kids(d,mf).filter(x=>x.ty==='traf')){const tl2=kids(d,tf),th=find(tl2,'tfhd');if(!th||u32(d,th.b+4)!==tid)continue;
    const fl=u32(d,th.b)&0xffffff;let o=th.b+8;if(fl&1)o+=8;if(fl&2)o+=4;let dd=trex[tid]?trex[tid].dd:0;if(fl&8){dd=u32(d,o);o+=4}
    for(const tr of tl2.filter(x=>x.ty==='trun')){const f=u32(d,tr.b)&0xffffff,c=u32(d,tr.b+4);let p=tr.b+8;if(f&1)p+=4;if(f&4)p+=4;
      for(let i=0;i<c;i++){let sd2=dd;if(f&0x100){sd2=u32(d,p);p+=4}if(f&0x200)p+=4;if(f&0x400)p+=4;if(f&0x800)p+=4;n++;tot+=sd2}}}}
  T.samples=n;T.duration=tot/ts;if(!T.duration&&dur)T.duration=dur/ts;
  if(T.kind==='video'&&T.duration>0)T.fps=+(n/T.duration).toFixed(2);
  R.tracks.push(T)}
 R.duration=Math.max(0,...R.tracks.map(t=>t.duration||0));return R}
// ---- WebM
function vint(d,o,keepMarker){let b=d.getUint8(o),l=1,m=128;while(l<=8&&!(b&m)){l++;m>>=1}let v=keepMarker?b:(b&(m-1));for(let i=1;i<l;i++)v=v*256+d.getUint8(o+i);return{v,l}}
function ebml(d,s,e,cb){while(s<e){const id=vint(d,s,true),sz=vint(d,s+id.l,false);let dl=sz.v;const unk=sz.v===Math.pow(2,7*sz.l)-1;const b=s+id.l+sz.l;if(unk||b+dl>e)dl=e-b;cb(id.v,b,dl);s=b+dl}}
function webm(buf){
 const d=new DataView(buf),R={container:'webm',tracks:[],problems:[]};let ts=1e6,dur=null,lastT=0,nFrames=0,vtr=null;
 const rd=(o,l)=>{let v=0;for(let i=0;i<l;i++)v=v*256+d.getUint8(o+i);return v};
 const str=(o,l)=>{let s='';for(let i=0;i<l;i++)s+=String.fromCharCode(d.getUint8(o+i));return s};
 ebml(d,0,buf.byteLength,(id,b,l)=>{if(id!==0x18538067)return;
  ebml(d,b,b+l,(id2,b2,l2)=>{
   if(id2===0x1549A966){ebml(d,b2,b2+l2,(i3,b3,l3)=>{if(i3===0x2AD7B1)ts=rd(b3,l3);if(i3===0x4489)dur=l3===8?d.getFloat64(b3):d.getFloat32(b3)})}
   if(id2===0x1654AE6B){ebml(d,b2,b2+l2,(i3,b3,l3)=>{if(i3!==0xAE)return;const T={};
     ebml(d,b3,b3+l3,(i4,b4,l4)=>{if(i4===0xD7)T.id=rd(b4,l4);if(i4===0x83)T.kind=rd(b4,l4)===1?'video':rd(b4,l4)===2?'audio':'other';if(i4===0x86)T.codecId=str(b4,l4);if(i4===0x23E383)T.dd=rd(b4,l4);
      if(i4===0xE0)ebml(d,b4,b4+l4,(i5,b5,l5)=>{if(i5===0xB0)T.width=rd(b5,l5);if(i5===0xBA)T.height=rd(b5,l5)});
      if(i4===0xE1)ebml(d,b4,b4+l4,(i5,b5,l5)=>{if(i5===0x9F)T.channels=rd(b5,l5);if(i5===0xB5)T.sampleRate=d.getFloat64?(l5===8?d.getFloat64(b5):d.getFloat32(b5)):0})});
     T.codec=({V_VP8:'VP8',V_VP9:'VP9',V_AV1:'AV1',V_MPEG4_ISO_AVC:'H.264',A_OPUS:'Opus',A_VORBIS:'Vorbis'})[T.codecId]||T.codecId;T.samples=0;R.tracks.push(T)})}
   if(id2===0x1F43B675){let ct=0;ebml(d,b2,b2+l2,(i3,b3,l3)=>{if(i3===0xE7)ct=rd(b3,l3);
     if(i3===0xA3||i3===0xA1){const tn=vint(d,b3,false),rel=d.getInt16(b3+tn.l);const t=ct+rel;const T=R.tracks.find(x=>x.id===tn.v);if(T){T.samples++;T.last=Math.max(T.last||0,t)}if(t>lastT)lastT=t}
     if(i3===0xA0)ebml(d,b3,b3+l3,(i4,b4,l4)=>{if(i4===0xA1){const tn=vint(d,b4,false),rel=d.getInt16(b4+tn.l);const T=R.tracks.find(x=>x.id===tn.v);if(T){T.samples++;T.last=Math.max(T.last||0,ct+rel)}}})})}})});
 const sec=lastT*ts/1e9;R.duration=dur?dur*ts/1e9:sec;R.durationNote=dur?'Info.Duration':'最終ブロック時刻(推定)';
 R.tracks.forEach(T=>{if(T.kind==='video'&&T.samples>1&&T.last>0)T.fps=+((T.samples-1)/(T.last*ts/1e9)).toFixed(2)});return R}
function inspect(buf){
 const d=new DataView(buf);let R;
 if(buf.byteLength>=12&&t4(d,4)==='ftyp')R=mp4(buf);else if(buf.byteLength>=4&&d.getUint32(0)===0x1A45DFA3)R=webm(buf);else R={container:'unknown',tracks:[],problems:['MP4でもWebMでもありません']};
 R.size=buf.byteLength;
 const v=R.tracks.find(t=>t.kind==='video'),a=R.tracks.find(t=>t.kind==='audio'),chk=[];
 chk.push(['コンテナMP4',R.container==='mp4']);
 chk.push(['映像H.264',!!v&&v.codec==='H.264']);
 chk.push(['音声AAC',!!a&&a.codec==='AAC']);
 chk.push(['1080x1920',!!v&&v.width===1080&&v.height===1920]);
 chk.push(['30fps(29.5-30.5)',!!v&&v.fps>=29.5&&v.fps<=30.5]);
 chk.push(['音声トラックあり',!!a]);
 if(v&&a&&v.duration&&a.duration){const df=Math.abs(v.duration-a.duration);chk.push(['映像/音声の長さ差0.3秒以内',df<=0.3,df.toFixed(3)+'s'])}
 R.checks=chk;R.allOk=chk.every(c=>c[1]);return R}
G.BSInspect=inspect;if(typeof module!=='undefined')module.exports=inspect;
})(typeof window!=='undefined'?window:globalThis);
