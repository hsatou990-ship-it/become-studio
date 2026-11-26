/* BECOME. STUDIO experimental H.264+AAC+MP4 encoder (Mediabunny). 音声は端末標準のAAC符号化のみ。WASM版AACは商用条件・特許が未確認のため削除済み（自動フォールバックなし）。 */
import {Output,Mp4OutputFormat,BufferTarget,CanvasSource,EncodedAudioPacketSource,EncodedPacket} from './mediabunny/src/index.js';
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
export async function aacAvailable(sampleRate=48000){if(typeof AudioEncoder==='undefined'||typeof AudioData==='undefined')return false;try{return !!(await AudioEncoder.isConfigSupported({codec:'mp4a.40.2',sampleRate,numberOfChannels:2,bitrate:128e3})).supported}catch{return false}}
export const NO_AAC_MESSAGE='この端末（ブラウザ）には標準のAAC符号化がないため、H.264+AAC書き出しは使えません。従来の「③書き出し」を使ってください。';
export async function encodeMp4({canvas,fps,frames,render,audio,vBitrate=8e6,aBitrate=128e3,progress}){
 const T={};const t0=performance.now();
 let A=null;
 if(audio){const ta=performance.now();A=await nativeAac(audio,aBitrate);if(!A){const e=new Error(NO_AAC_MESSAGE);e.code='NO_NATIVE_AAC';throw e}T.aacKind='native';T.aacEncode=performance.now()-ta}
 const out=new Output({format:new Mp4OutputFormat({fastStart:'in-memory'}),target:new BufferTarget()});
 const vs=new CanvasSource(canvas,{codec:'avc',bitrate:vBitrate,keyFrameInterval:1});out.addVideoTrack(vs,{frameRate:fps});
 let as=null;if(A){as=new EncodedAudioPacketSource('aac');out.addAudioTrack(as)}
 await out.start();
 if(as){let first=true;for(const p of A.pk){await as.add(new EncodedPacket(p.d,'key',p.t,p.dur),first?{decoderConfig:{codec:'mp4a.40.2',numberOfChannels:2,sampleRate:audio.sampleRate,description:A.desc}}:undefined);first=false}}
 const tv=performance.now();
 for(let i=0;i<frames;i++){await render(i,i/fps);await vs.add(i/fps,1/fps);if(progress&&i%10===0)progress(i/frames)}
 vs.close();if(as)as.close();await out.finalize();T.video=performance.now()-tv;T.total=performance.now()-t0;
 return{blob:new Blob([out.target.buffer],{type:'video/mp4'}),T}}
