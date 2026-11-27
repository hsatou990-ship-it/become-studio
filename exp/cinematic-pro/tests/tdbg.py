from playwright.sync_api import sync_playwright
import json, base64, hashlib, time, re
exec(open('tns.py').read().split("with sync_playwright()")[0])
FX='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/am/'
RR=[]
def c(n,ok,d=''):RR.append(bool(ok));print('PASS' if ok else 'FAIL',n,'' if ok else str(d)[:700])
KEY='SECRET-KEY-ABC123xyz'
# 17-scene (about 70 s) design built from the sample design
base=json.load(open('/home/claude/become-studio/exp/design/price-of-staying.design.json'))
T=base['scenes']
sc=[]
for k in range(17):
    t=json.loads(json.dumps(T[0 if k==0 else (3 if k==16 else (1 if k%2 else 2))]))
    t['text']='場面%d。変わるのが、怖いか。'%(k+1);t['dur']=3.0 if k==0 else (4.1 if k<16 else 4.1)
    t['role']='hook' if k==0 else ('ending' if k==16 else t['role'])
    t['search']={'queries':['qa%da'%k,'qb%db'%k],'avoid':['logo'],'minHeight':1080}
    sc.append(t)
D17=json.loads(json.dumps(base));D17['scenes']=sc;D17['script']=''.join(s['text'] for s in sc)[:1900]
D17J=json.dumps(D17,ensure_ascii=False)
MOCK="""()=>{window.__M={calls:{json:0,blob:0},failQ:null,c429:false,log:[]};
CP.setTransport({label:'mock',
 json:async(url,opt)=>{__M.calls.json++;__M.log.push(url);const u=new URL(url);const q=(u.searchParams.get('query')||u.searchParams.get('q'));
  if(__M.c429){const e=new Error('HTTP 429');e.status=429;throw e}
  if(__M.failQ&&[].concat(__M.failQ).some(f=>q===f)){throw new Error('HTTP 500 upstream '+((opt&&opt.headers&&opt.headers.Authorization)||u.searchParams.get('key')||''))}
  let h=0;for(const ch of q)h=(h*31+ch.charCodeAt(0))>>>0;
  const vids=[0,1,2,3].map(k=>{const id=((h%100000)*10+k);return{id,url:'https://www.pexels.com/video/'+(k==3?'logo-text-':'scene-')+q.replace(/\\s+/g,'-')+'-'+id+'/',width:1080,height:1920,duration:6,user:{name:'Creator'+((h+k)%12),url:'https://www.pexels.com/@c'+((h+k)%12)},image:'x',video_pictures:[{picture:'x'}],video_files:[{file_type:'video/mp4',width:1080,height:1920,link:'https://mock.invalid/v/'+id+'.mp4'}]}});
  if(u.hostname.includes('pixabay'))return{hits:vids.map(v=>({id:v.id,pageURL:v.url,duration:6,user:v.user.name,user_id:1,tags:v.url.split('/video/')[1]||'',videos:{medium:{url:'https://mock.invalid/v/'+v.id+'.mp4',width:1080,height:1920,thumbnail:'x'}}}))};
  return{videos:vids}},
 blob:async(url)=>{__M.calls.blob++;const m=/\\/v\\/(\\d+)\\.mp4/.exec(url);const b64=await window.mockBlob(m[1]);const bin=atob(b64),u8=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u8[i]=bin.charCodeAt(i);return new Blob([u8],{type:'video/mp4'})}})}"""
DUMP="""async()=>{const out={};for(const n of['cp_project','cp_stock','cp_session']){try{const db=await new Promise((ok,ng)=>{const r=indexedDB.open(n);r.onsuccess=()=>ok(r.result);r.onerror=()=>ng()});out[n]={};for(const s of [...db.objectStoreNames]){out[n][s]=await new Promise(ok=>{const q=db.transaction(s).objectStore(s).getAll();q.onsuccess=()=>ok(q.result.map(x=>JSON.stringify(x,(k,v)=>v instanceof Blob?'[blob '+v.size+']':v)));q.onerror=()=>ok([])})}}catch(e){out[n]='ERR'}}return out}"""
def mockblob(id_):
    return base64.b64encode(open(FX+'fx%d.mp4'%(int(id_)%21),'rb').read()).decode()
def clip(pg,i,path):
    pg.set_input_files(f'#cf{i}',path);pg.fill(f'#cu{i}','https://example.com/v');pg.fill(f'#cc{i}','T');pg.fill(f'#cl{i}','Pexels License');pg.check(f'#ck{i}')
    ok=pg.evaluate(f"()=>CP.useClip({i})");pg.wait_for_timeout(300);return ok
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.expose_function('mockBlob',mockblob)
    def boot(hash_='#res=360'):
        pg.goto(BASE+hash_);pg.reload();ready(pg);pg.wait_for_timeout(500)
    boot();pg.fill('#dj',D17J);pg.click('#bDJ');pg.wait_for_timeout(800);pg.evaluate(MOCK);pg.evaluate("async()=>{CP.BT.key='k';await CP.batchRun({})}")
    r=pg.evaluate("""async()=>{const cs=[...document.querySelectorAll('canvas')].map(c=>c.width+'x'+c.height+(c.id?'#'+c.id:''));const sc=4,t=CP.S.sc[sc].a+(CP.S.sc[sc].b-CP.S.sc[sc].a)*.6;
    const avg=(c)=>{const o=document.createElement('canvas');o.width=4;o.height=4;const g=o.getContext('2d');g.drawImage(c,0,0,4,4);const d=g.getImageData(0,0,4,4).data;let r=0,gg=0,b=0;for(let i=0;i<d.length;i+=4){r+=d[i];gg+=d[i+1];b+=d[i+2]}return [r/16|0,gg/16|0,b/16|0]};
    await CP.acquireClip(sc);CP.renderFrame(t);const a1=avg(CP.out);CP.releaseClip(sc);CP.renderFrame(t);const a2=avg(CP.out);await CP.acquireClip(sc);CP.renderFrame(t);const a3=avg(CP.out);
    return{cs,a1,a2,a3,rel:CP.S.clips[sc].rel,rd:CP.S.clips[sc].el.readyState,vw:CP.S.clips[sc].el.videoWidth}}""")
    print(r)
