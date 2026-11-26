// 任意：Gemini APIキーを「サーバー側の秘密」として保管する中継（Cloudflare Workers の無料枠想定）。未検証。
// 設定: 環境変数（シークレット）GEMINI_API_KEY を登録。ALLOW_ORIGIN は未設定なら公開ページのオリジンのみ許可。
export default{async fetch(req,env){
 const o=env.ALLOW_ORIGIN||'https://hsatou990-ship-it.github.io',cors={'Access-Control-Allow-Origin':o,'Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'POST,OPTIONS'};
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers:cors});
 if(req.method!=='POST'||req.headers.get('Origin')!==o)return new Response('forbidden',{status:403,headers:cors});
 let b;try{b=await req.json()}catch{return new Response('bad request',{status:400,headers:cors})}
 const t=b&&b.input&&b.input[0]&&b.input[0].content&&b.input[0].content[0]&&b.input[0].content[0].text;
 if(!/^gemini-[\w.-]*tts$/.test(String(b.model))||typeof t!=='string'||t.length>400)return new Response('bad request',{status:400,headers:cors});
 const r=await fetch('https://generativelanguage.googleapis.com/v1beta/interactions',{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':env.GEMINI_API_KEY},body:JSON.stringify(b)});
 return new Response(await r.text(),{status:r.status,headers:{...cors,'Content-Type':'application/json'}})}}
