/* BECOME. STUDIO experimental H.264+AAC+MP4 encoder (Mediabunny + libavcodec AAC via WASM). Isolated; not used by the main app. */
import {Output,Mp4OutputFormat,BufferTarget,CanvasSource,EncodedAudioPacketSource,EncodedPacket} from './mediabunny/src/index.js';
import createModule from './aac.js';
export class AacSync{
 async init(ch,sr,br){const m=this.m=await createModule();const w=(n,r,a)=>m.cwrap(n,r,a);
  this.f={init:w('init_encoder','number',['number','number','number']),fs:w('get_encoder_frame_size','number',['number']),ed:w('get_encoder_extradata','number',['number']),es:w('get_encoder_extradata_size','number',['number']),inp:w('get_encode_input_ptr','number',['number','number']),send:w('send_frame','number',['number','number']),recv:w('receive_packet','number',['number']),flush:w('flush_encoder_start',null,['number']),data:w('get_encoded_data','number',['number']),pts:w('get_encoded_pts','number',['number']),dur:w('get_encoded_duration','number',['number'])};
  this.ctx=this.f.init(ch,sr,br);if(!this.ctx)throw new Error('AAC符号化器を初期化できません');this.ch=ch;this.sr=sr;this.fsz=this.f.fs(this.ctx);
  const p=this.f.ed(this.ctx);this.desc=m.HEAPU8.slice(p,p+this.f.es(this.ctx));return this}
 drain(out){let n;while((n=this.f.recv(this.ctx))>0){const p=this.f.data(this.ctx);out.push({d:this.m.HEAPU8.slice(p,p+n),pts:Number(this.f.pts(this.ctx)),dur:this.f.dur(this.ctx)})}}
 encodeAll(buf){const ch=this.ch,len=buf.length,fs=this.fsz,out=[],chd=[];for(let c=0;c<ch;c++)chd.push(buf.getChannelData(Math.min(c,buf.numberOfChannels-1)));
  const fr=new Float32Array(fs*ch);for(let s=0;s<len;s+=fs){fr.fill(0);const n=Math.min(fs,len-s);for(let i=0;i<n;i++)for(let c=0;c<ch;c++)fr[i*ch+c]=chd[c][s+i];
   const b=new Uint8Array(fr.buffer.slice(0));const ptr=this.f.inp(this.ctx,b.length);this.m.HEAPU8.set(b,ptr);if(this.f.send(this.ctx,BigInt(s))<0)throw new Error('AAC符号化に失敗');this.drain(out)}
  this.f.flush(this.ctx);this.drain(out);return out}}
/* 端末標準のAAC符号化（OSが許諾を持つ実装）を優先。使えなければnull。 */
export async function nativeAac(audio,br){
 if(typeof AudioEncoder==='undefined'||typeof AudioData==='undefined')return null;
 const sr=audio.sampleRate,cfg={codec:'mp4a.40.2',sampleRate:sr,numberOfChannels:2,bitrate:br};
 try{const s=await AudioEncoder.isConfigSupported(cfg);if(!s.supported)return null}catch{return null}
 const pk=[];let desc=null,err=null;
 const enc=new AudioEncoder({output:(c,m)=>{const d=new Uint8Array(c.byteLength);c.copyTo(d);
   if(m&&m.decoderConfig&&m.decoderConfig.description&&!desc){const q=m.decoderConfig.description;desc=new Uint8Array(q instanceof ArrayBuffer?q.slice(0):q.buffer.slice(q.byteOffset,q.byteOffset+q.byteLength))}
   pk.push({d,t:c.timestamp/1e6,dur:(c.duration||Math.round(1024/sr*1e6))/1e6})},error:e=>{err=e}});
 enc.configure(cfg);
 const N=audio.length,CH=[audio.getChannelData(0),audio.getChannelData(Math.min(1,audio.numberOfChannels-1))],B=4096;
 for(let s=0;s<N;s+=B){const n=Math.min(B,N-s),pl=new Float32Array(n*2);pl.set(CH[0].subarray(s,s+n),0);pl.set(CH[1].subarray(s,s+n),n);
  const ad=new AudioData({format:'f32-planar',sampleRate:sr,numberOfFrames:n,numberOfChannels:2,timestamp:Math.round(s/sr*1e6),data:pl});enc.encode(ad);ad.close();if(err)throw err}
 await enc.flush();enc.close();if(err)throw err;
 if(!pk.length||!desc)return null;return{pk,desc,kind:'native'}}
export async function encodeMp4({canvas,fps,frames,render,audio,vBitrate=8e6,aBitrate=128e3,progress,audioMode='auto'}){
 const T={};const t0=performance.now();
 const out=new Output({format:new Mp4OutputFormat({fastStart:'in-memory'}),target:new BufferTarget()});
 const vs=new CanvasSource(canvas,{codec:'avc',bitrate:vBitrate,keyFrameInterval:1});out.addVideoTrack(vs,{frameRate:fps});
 let as=null,A=null;
 if(audio){const ta=performance.now();
  if(audioMode!=='wasm'){try{A=await nativeAac(audio,aBitrate)}catch(e){T.nativeError=String(e&&e.message||e);A=null}}
  if(!A){const enc=await new AacSync().init(2,audio.sampleRate,aBitrate);const pk=enc.encodeAll(audio);A={pk:pk.map(p=>({d:p.d,t:p.pts/audio.sampleRate,dur:p.dur/audio.sampleRate})),desc:enc.desc,kind:'wasm'}}
  T.aacKind=A.kind;T.aacEncode=performance.now()-ta;as=new EncodedAudioPacketSource('aac');out.addAudioTrack(as)}
 await out.start();
 if(as){let first=true;for(const p of A.pk){await as.add(new EncodedPacket(p.d,'key',p.t,p.dur),first?{decoderConfig:{codec:'mp4a.40.2',numberOfChannels:2,sampleRate:audio.sampleRate,description:A.desc}}:undefined);first=false}}
 const tv=performance.now();
 for(let i=0;i<frames;i++){await render(i,i/fps);await vs.add(i/fps,1/fps);if(progress&&i%10===0)progress(i/frames)}
 vs.close();if(as)as.close();await out.finalize();T.video=performance.now()-tv;T.total=performance.now()-t0;
 return{blob:new Blob([out.target.buffer],{type:'video/mp4'}),T}}
