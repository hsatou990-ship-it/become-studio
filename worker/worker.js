// BECOME. STUDIO TikTok連携用の中継（Cloudflare Workers 無料枠）。
// 役割: client_secret を安全に保持し、OAuth 2.0 のコード交換・更新・TikTok API呼び出しを代行する。
// 必要なシークレット: TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / SESSION_KEY（ランダムな長い文字列）
// トークンは暗号化（AES-GCM）した文字列として利用者の端末だけに保存。サーバー側にDBは持たない。
const PAGES_DEFAULT='https://hsatou990-ship-it.github.io';
const TT='https://open.tiktokapis.com';
const SC={analyze:'user.info.basic,user.info.profile,user.info.stats,video.list',post:'user.info.basic,user.info.profile,user.info.stats,video.list,video.upload'};
const enc=new TextEncoder(),dec=new TextDecoder();
const b64u=b=>{let s='';new Uint8Array(b).forEach(x=>s+=String.fromCharCode(x));return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')};
const unb64u=s=>{s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';return Uint8Array.from(atob(s),c=>c.charCodeAt(0))};
async function ckey(env){const raw=await crypto.subtle.digest('SHA-256',enc.encode('bs|'+env.SESSION_KEY));return crypto.subtle.importKey('raw',raw,{name:'AES-GCM'},false,['encrypt','decrypt'])}
async function seal(env,o){const iv=crypto.getRandomValues(new Uint8Array(12)),ct=await crypto.subtle.encrypt({name:'AES-GCM',iv},await ckey(env),enc.encode(JSON.stringify(o)));return b64u(iv)+'.'+b64u(ct)}
async function open(env,s){const[a,b]=String(s).split('.');if(!a||!b)throw new Error('bad token');return JSON.parse(dec.decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:unb64u(a)},await ckey(env),unb64u(b))))}
const origin=env=>env.ALLOW_ORIGIN||PAGES_DEFAULT;
const cors=env=>({'Access-Control-Allow-Origin':origin(env),'Access-Control-Allow-Headers':'Content-Type,Authorization','Access-Control-Allow-Methods':'GET,POST,PUT,OPTIONS','Access-Control-Expose-Headers':'X-BS-Session','Vary':'Origin'});
const J=(env,o,st=200,h={})=>new Response(JSON.stringify(o),{status:st,headers:{...cors(env),'Content-Type':'application/json',...h}});
async function token(env,params){const r=await fetch(TT+'/v2/oauth/token/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({client_key:env.TIKTOK_CLIENT_KEY,client_secret:env.TIKTOK_CLIENT_SECRET,...params}).toString()});return r.json()}
function pack(t,sc){const now=Date.now();return{at:t.access_token,rt:t.refresh_token,ex:now+(t.expires_in||0)*1000,rx:now+(t.refresh_expires_in||0)*1000,oid:t.open_id,sc:t.scope||sc}}
async function session(req,env){const a=req.headers.get('Authorization')||'';if(!a.startsWith('Bearer '))throw Object.assign(new Error('no session'),{st:401});let s;try{s=await open(env,a.slice(7))}catch{throw Object.assign(new Error('bad session'),{st:401})}
 let ns=null;if(s.ex-60000<Date.now()){if(s.rx<Date.now())throw Object.assign(new Error('expired'),{st:401});const t=await token(env,{grant_type:'refresh_token',refresh_token:s.rt});if(!t.access_token)throw Object.assign(new Error('refresh failed'),{st:401});s=pack(t,s.sc);ns=await seal(env,s)}return{s,ns}}
function userFields(sc){const f=[];const h=x=>String(sc).includes(x);if(h('user.info.basic'))f.push('open_id','avatar_url','display_name');if(h('user.info.profile'))f.push('bio_description','username','is_verified','profile_deep_link');if(h('user.info.stats'))f.push('follower_count','following_count','likes_count','video_count');return f.join(',')}
export default{async fetch(req,env){
 const url=new URL(req.url),p=url.pathname;
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers:cors(env)});
 if(!env.TIKTOK_CLIENT_KEY||!env.TIKTOK_CLIENT_SECRET||!env.SESSION_KEY)return J(env,{error:{code:'not_configured',message:'シークレットが未設定です'}},500);
 if(p==='/'||p==='/health')return J(env,{ok:true,service:'become-studio-tiktok'});
 if(p==='/auth/start'&&req.method==='GET'){const scope=SC[url.searchParams.get('mode')]||SC.analyze,st=await seal(env,{n:b64u(crypto.getRandomValues(new Uint8Array(12))),t:Date.now(),s:scope});
  const u=new URL('https://www.tiktok.com/v2/auth/authorize/');u.search=new URLSearchParams({client_key:env.TIKTOK_CLIENT_KEY,scope,response_type:'code',redirect_uri:url.origin+'/auth/callback',state:st}).toString();return Response.redirect(u.toString(),302)}
 if(p==='/auth/callback'&&req.method==='GET'){const back=(q)=>Response.redirect(origin(env)+'/become-studio/#'+q,302);
  const err=url.searchParams.get('error');if(err)return back('tterr='+encodeURIComponent(err));
  let st;try{st=await open(env,url.searchParams.get('state'))}catch{return back('tterr=state_invalid')}if(Date.now()-st.t>10*60*1000)return back('tterr=state_expired');
  const code=url.searchParams.get('code');if(!code)return back('tterr=no_code');
  const t=await token(env,{code,grant_type:'authorization_code',redirect_uri:url.origin+'/auth/callback'});if(!t.access_token)return back('tterr='+encodeURIComponent(t.error||'token_failed'));
  return back('tt='+await seal(env,pack(t,st.s)))}
 if(p.startsWith('/api/')){
  if(req.headers.get('Origin')!==origin(env))return J(env,{error:{code:'forbidden_origin',message:'許可されていないアクセス元です'}},403);
  let S;try{S=await session(req,env)}catch(e){return J(env,{error:{code:'session_invalid',message:'再ログインが必要です'}},401)}
  const{s,ns}=S,H=ns?{'X-BS-Session':ns}:{},auth={Authorization:'Bearer '+s.at};
  const tt=async(path,init)=>{const r=await fetch(TT+path,init);const t=await r.text();return new Response(t,{status:r.status,headers:{...cors(env),'Content-Type':'application/json',...H}})};
  let body={};if(req.method==='POST'){try{body=await req.json()}catch{}}
  if(p==='/api/me')return tt('/v2/user/info/?fields='+userFields(s.sc),{headers:auth});
  if(p==='/api/videos'){const q={max_count:Math.min(20,+body.max_count||20)};if(body.cursor)q.cursor=+body.cursor;return tt('/v2/video/list/?fields=id,title,video_description,duration,create_time,cover_image_url,share_url,view_count,like_count,comment_count,share_count',{method:'POST',headers:{...auth,'Content-Type':'application/json'},body:JSON.stringify(q)})}
  if(p==='/api/logout'){await fetch(TT+'/v2/oauth/revoke/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({client_key:env.TIKTOK_CLIENT_KEY,client_secret:env.TIKTOK_CLIENT_SECRET,token:s.at}).toString()});return J(env,{ok:true})}
  if(p==='/api/upload/init'){if(!String(s.sc).includes('video.upload'))return J(env,{error:{code:'scope_not_authorized',message:'下書き送信の権限がありません'}},403,H);const size=Math.floor(+body.size);if(!(size>0&&size<=64*1024*1024))return J(env,{error:{code:'invalid_param',message:'動画サイズが範囲外です（64MBまで）'}},400,H);
   const r=await fetch(TT+'/v2/post/publish/inbox/video/init/',{method:'POST',headers:{...auth,'Content-Type':'application/json; charset=UTF-8'},body:JSON.stringify({source_info:{source:'FILE_UPLOAD',video_size:size,chunk_size:size,total_chunk_count:1}})});const j=await r.json();
   if(!r.ok||!j.data||!j.data.upload_url)return J(env,j,r.status||502,H);return J(env,{publish_id:j.data.publish_id,put:await seal(env,{u:j.data.upload_url,size,t:Date.now()})},200,H)}
  if(p==='/api/upload/put'&&req.method==='PUT'){let o;try{o=await open(env,url.searchParams.get('t'))}catch{return J(env,{error:{code:'bad_ticket',message:'無効な送信券です'}},400,H)}
   const len=+req.headers.get('Content-Length');if(len!==o.size||Date.now()-o.t>50*60*1000)return J(env,{error:{code:'invalid_param',message:'サイズまたは有効期限が一致しません'}},400,H);
   const r=await fetch(o.u,{method:'PUT',headers:{'Content-Type':req.headers.get('X-Video-Type')||'video/mp4','Content-Length':String(len),'Content-Range':`bytes 0-${len-1}/${len}`},body:req.body,duplex:'half'});return J(env,{ok:r.ok||r.status===201,status:r.status},r.ok||r.status===201?200:502,H)}
  if(p==='/api/status')return tt('/v2/post/publish/status/fetch/',{method:'POST',headers:{...auth,'Content-Type':'application/json; charset=UTF-8'},body:JSON.stringify({publish_id:String(body.publish_id||'')})});
  return J(env,{error:{code:'not_found',message:'未対応のパスです'}},404,H)}
 return J(env,{error:{code:'not_found',message:'not found'}},404)}}
