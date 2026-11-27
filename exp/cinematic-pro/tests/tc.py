from playwright.sync_api import sync_playwright
import base64,json,subprocess,time,os,sys
ARGS=['--no-sandbox','--headless=new','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html'
D=os.path.dirname(os.path.abspath('tc.py'))
R={}
def chk(n,c,i=''):R[n]=bool(c);print(('PASS ' if c else 'FAIL ')+n,str(i)[:200],flush=True)
def newpage(b,hash='#res=540'):
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];reqs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if ('Content Security' in m.text or m.type=='error') else None)
    pg.on('request',lambda r:reqs.append(r.url))
    pg.goto(URL+hash);pg.wait_for_timeout(700);return pg,errs,reqs
def frame(pg,t):return pg.evaluate("(t)=>{CP.renderFrame(t);return CP.out.toDataURL('image/png')}",t)
def px(pg,t,fn):
    return pg.evaluate("([t,fn])=>{CP.renderFrame(t);const g=CP.og,w=CP.out.width,h=CP.out.height,d=g.getImageData(0,0,w,h).data;return eval(fn)(d,w,h)}",[t,fn])
LUMA="(d)=>{let l=0,n=0;for(let k=0;k<d.length;k+=16){l+=(.2126*d[k]+.7152*d[k+1]+.0722*d[k+2])/255;n++}return l/n}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=ARGS)
    pg,errs,reqs=newpage(b)
    chk('C0 loads, WebGL active, no errors/CSP violations',pg.evaluate("()=>CP.GL")==True and not [e for e in errs if 'GPU stall' not in e and 'GL Driver' not in e],errs[:2])
    chk('C0b no external network requests',all(u.startswith(('file:','blob:','data:','http://127.0.0.1:8765/')) for u in reqs),[u for u in reqs if not u.startswith('file:')][:3])
    r=pg.evaluate("()=>CP.report()")
    chk('C1 timeline: 450 frames, 5 scenes, 4 cuts, ASL 3.0, cut times 2.6/6.0/9.8/13.2',r['frames']==450 and r['scenes']==5 and r['cuts']==4 and abs(r['asl']-3.0)<.01 and r['cutTimes']==[2.6,6,9.8,13.2],r['cutTimes'])
    chk('C1b scenes contiguous 0..15',pg.evaluate("()=>{const A=CP.S.sc;return A[0].a===0&&A[4].b===15&&A.slice(0,4).every((s,i)=>Math.abs(s.b-A[i+1].a)<1e-9)}"))
    a1=frame(pg,4.0);a2=frame(pg,4.0);a3=frame(pg,4+1/30)
    chk('C2 deterministic: same time -> identical frame',a1==a2)
    chk('C2b different frames differ (grain/motion)',a1!=a3)
    l=lambda t:px(pg,t,LUMA)
    chk('C3 dip to black at S1->S2 cut',l(2.6)<.45*min(l(2.3),l(2.9)),[round(l(2.3),3),round(l(2.6),3),round(l(2.9),3)])
    chk('C3b white flash on the 6.0s hit',l(6.0)>l(6.25)+.05,[round(l(6.0),3),round(l(6.25),3)])
    chk('C3c fade to black before S5',l(13.15)<.4*l(12.3),[round(l(12.3),3),round(l(13.15),3)])
    gold=px(pg,14.5,"(d,w,h)=>{let g=0,wh=0;for(let k=0;k<d.length;k+=4){if(d[k]>170&&d[k+1]>130&&d[k+2]<110)g++;if(d[k]>230&&d[k+1]>230&&d[k+2]>230)wh++}return [g,wh]}")
    chk('C3d ending logo: white letters and gold line present',gold[0]>20 and gold[1]>200,gold)
    cl=lambda t:pg.evaluate("(t)=>CP.capLayout(t).map(o=>[o.s,o.emph,o.li])",t)
    chk('C4 no caption before narration starts',cl(0.2)==[])
    c15=cl(1.5)
    chk('C4b emphasis word 何も visible, gold-flagged, at 1.5s',any(x[0]=='何も' and x[1] for x in c15),c15)
    over=pg.evaluate("()=>{let m=0;for(let f=0;f<CP.N;f++){const s=new Set(CP.capLayout(f/CP.FPS).map(o=>o.li));m=Math.max(m,s.size)}return m}")
    chk('C4c never two caption lines at once (no overlap)',over<=1,over)
    sc=pg.evaluate("()=>CP.safeCheck()")
    chk('C5 captions stay inside the safe area (all 450 frames, serif)',sc['ok'],sc['bb'])
    ratio=pg.evaluate("()=>{let a=0,b=1e9;for(let f=0;f<CP.N;f++)CP.capLayout(f/CP.FPS).forEach(o=>{if(o.emph)a=Math.max(a,o.sz);else b=Math.min(b,o.sz)});return a/b}")
    chk('C5b emphasis words are larger (about 1.35x or more)',ratio>=1.3,round(ratio,2))
    pg.evaluate("()=>{document.getElementById('fnt').value='gothic';document.getElementById('fnt').dispatchEvent(new Event('change'))}")
    sc2=pg.evaluate("()=>CP.safeCheck()")
    chk('C6 gothic font: layout changes, still inside safe area',sc2['ok'] and sc2['bb']!=sc['bb'],sc2['bb'])
    pg.evaluate("()=>{document.getElementById('fnt').value='serif';document.getElementById('fnt').dispatchEvent(new Event('change'))}")
    # audio
    m=pg.evaluate("async()=>{CP.S.narr=CP.mockNarr();CP.S.isMockNarr=true;CP.S.mix=null;return await CP.prep()}")
    chk('C7 audio: no NaN, no clipping, peak<=0.98',m['nan']==0 and m['clip']==0 and m['peak']<=.98,m)
    chk('C7b narration windows at about -16 dB RMS (-24..-10)',all(-24<v<-10 for v in m['narrWin']),m['narrWin'])
    chk('C7c silence before ending is >=25 dB below narration',m['silence']<min(m['narrWin'])-25,[m['silence'],min(m['narrWin'])])
    chk('C7d BGM-only intro level -50..-25 dB (target about -30)',-50<m['bed1']<-25,m['bed1'])
    duck=pg.evaluate("""async()=>{const S=CP.S,keep=S.narr;const sr=48000,z=new AudioBuffer({length:15*sr,sampleRate:sr,numberOfChannels:1});S.narr=z;const a=await CP.buildAudio();const L=S.ln[2],x=a.getChannelData(0);S.narr=null;const b=await CP.buildAudio(),y=b.getChannelData(0);S.narr=keep;const f=(q)=>{let s=0,n=0;for(let i=Math.round((L.t0+.3)*sr);i<Math.round((L.t0+L.d-.3)*sr);i++){s+=q[i]*q[i];n++}return 10*Math.log10(s/n+1e-12)};return [f(x),f(y)]}""")
    chk('C7e BGM ducks under narration by >=5 dB',duck[1]-duck[0]>=5,duck)
    # align
    offs=[.2,.5,.3,.4]
    al=pg.evaluate("(o)=>{const S=CP.S;S.narr=CP.mockNarr(o);const ok=CP.alignNarr(S.narr);return {ok,t0:S.ln.map(l=>l.t0),cuts:S.sc.slice(1).map(s=>s.a),off:S.off}}",offs)
    exp=[[.6,3.0,6.3,10.0][i]+(offs[i]-offs[0]) for i in range(4)]
    chk('C8 narration onsets detected within 0.08s and lines re-timed',al['ok'] and all(abs(al['t0'][i]-exp[i])<.08 for i in range(4)),[al['t0'],exp])
    chk('C8b cuts follow the voice (differ from nominal, ordered, >=1.6s apart)',al['cuts']!=[2.6,6,9.8,13.2] and all(al['cuts'][i+1]-al['cuts'][i]>=1.59 for i in range(3)),al['cuts'])
    bad=pg.evaluate("""()=>{const S=CP.S,sr=48000,b=new AudioBuffer({length:15*sr,sampleRate:sr,numberOfChannels:1}),x=b.getChannelData(0);for(const [a,d] of [[1,2],[6,2]])for(let i=0;i<d*sr;i++)x[a*sr+i]=.2*Math.sin(2*Math.PI*150*i/sr);S.warn=[];const ok=CP.alignNarr(b);return {ok,warn:S.warn,nominal:JSON.stringify(S.sc.map(s=>[s.a,s.b]))===JSON.stringify(CP.SCN0.map(s=>[s.a,s.b]))}}""")
    chk('C8c undetectable narration: warns and keeps standard timing',(not bad['ok']) and bad['warn'] and bad['nominal'],bad)
    long=pg.evaluate("(o)=>{const S=CP.S;S.warn=[];S.narr=CP.mockNarr(o);CP.alignNarr(S.narr);return {w:S.warn,a5:S.sc[4].a}}",[0,.8,1.6,2.4])
    chk('C8d too-long narration: warns about the 15s limit',any('15秒' in w for w in long['w']),long)
    pg.evaluate("()=>{const S=CP.S;S.narr=CP.mockNarr();S.sc=JSON.parse(JSON.stringify(CP.SCN0));S.ln=JSON.parse(JSON.stringify(CP.LN0));S.off=0}")
    # clips & license gate
    base=frame(pg,3.5)
    pg.set_input_files('#cf0',os.environ.get('BECOME_FIX','/tmp/become-fixtures')+'/clip_p.mp4')
    r0=pg.evaluate("()=>CP.useClip(0)");msg=pg.inner_text('#cm0')
    chk('C9 clip without rights info is refused (mock stays)',r0==False and '使いません' in msg and pg.evaluate("()=>CP.S.clips[0]===null"),msg[:60])
    pg.fill('#cu0','https://www.pexels.com/video/test-123/');pg.fill('#cc0','Test Creator');pg.fill('#cl0','Pexels License');pg.check('#ck0')
    r1=pg.evaluate("()=>CP.useClip(0)");pg.wait_for_timeout(400)
    led=pg.inner_text('#ledger')
    chk('C9b with full rights info: clip accepted and ledger written',r1==True and 'Test Creator' in led and 'Pexels License' in led and 'Video by' in led and 'S2' in led,led[:100])
    f1=frame(pg,1.0)
    chk('C9c accepted clip is actually drawn (differs from mock)',f1!=base)
    pg.set_input_files('#cf1',os.environ.get('BECOME_FIX','/tmp/become-fixtures')+'/clip_l.mp4');pg.fill('#cu1','https://example.org/x');pg.fill('#cc1','C');pg.fill('#cl1','CC0');pg.check('#ck1')
    r2=pg.evaluate("()=>CP.useClip(1)");cm=pg.inner_text('#cm1')
    chk('C9d landscape/low-res clip: accepted with warnings',r2==True and '横向き' in cm and '解像度' in cm,cm)
    pg.evaluate("()=>{CP.S.clips[0]=null;CP.S.clips[1]=null;CP.ledger()}")
    # GL off
    pg2,e2,_=newpage(b,'#res=540&gl=0')
    chk('C10 2D fallback (no WebGL) renders without errors',pg2.evaluate("()=>CP.GL")==False and not e2,e2[:2])
    lg=lambda q,t:px(q,t,LUMA)
    dl=[abs(lg(pg,t)-lg(pg2,t)) for t in (1.2,4.5,8.2,11.5)]
    chk('C10b fallback brightness close to WebGL path (<0.12)',max(dl)<.12,[round(x,3) for x in dl])
    sc3=pg2.evaluate("()=>CP.safeCheck()")
    chk('C10c fallback: caption layout identical and safe',sc3['ok'] and sc3['bb']==sc['bb'])
    pg2.context.close()
    # performance (mock environment)
    pf=pg.evaluate("()=>{const t0=performance.now();for(let f=0;f<60;f++)CP.renderFrame(1+f/30);return (performance.now()-t0)/60}")
    chk('C11 render cost measured (headless software GL, NOT a device)',pf<400,'%.1f ms/frame at 540x960'%pf)
    # export
    pe,ee,_=newpage(b,'#res=360')
    pe.evaluate("()=>{const S=CP.S;S.narr=CP.mockNarr();S.isMockNarr=true}")
    t0=time.time()
    ex=pe.evaluate("async()=>{const r=await CP.exportVideo();const ab=await r.blob.arrayBuffer();let s='';const u=new Uint8Array(ab);for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return {full:r.full,codecsOk:r.codecsOk,status:document.getElementById('st').textContent,type:r.type,kind:r.kind,claimed:r.claimed,mismatch:r.mismatch,size:r.blob.size,v:r.v,stall:r.stall,b64:btoa(s),ft:CP.S.ft.length}}")
    el=time.time()-t0
    open('/tmp/tc_out.'+ex['kind'],'wb').write(base64.b64decode(ex['b64']))
    chk('C12 real-time export produced a video (>10KB) in about 15-20s',ex['size']>10000 and 14<el<26,'%s %dB %.1fs'%(ex['type'],ex['size'],el))
    print('INFO claimed',ex['claimed'],'actual',ex['kind'],'mismatch',ex['mismatch'])
    chk('C12b export verification passed (length 14-16.5s, narration audible, ending silent)',ex['v']['ok'] and not ex['v'].get('left'),ex['v'])
    fn='/tmp/tc_out.'+ex['kind']
    pr=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name,codec_type,width,height','-show_entries','format=duration,format_name','-of','json',fn],capture_output=True,text=True).stdout)
    cod={s['codec_type']:s['codec_name'] for s in pr['streams']};dur=float(pr['format']['duration'])
    chk('C12c ffprobe: real encoded video+audio streams, duration ~15s',('video' in cod and 'audio' in cod) and 14<dur<16.5,[cod,dur,pr['streams'][0].get('width')])
    print('INFO full mime',ex['full'],'codecsOk',ex['codecsOk'])
    chk('C12e actual codec is reported on screen; non-H.264 is warned (TikTok acceptance unconfirmed)',('コーデック' in ex['status']) and (ex['codecsOk'] or 'H.264/AAC' in ex['status']),ex['status'][-160:])
    fm=pr['format']['format_name']
    chk('C12d saved type/extension match the real container (no renamed file)',(ex['kind']=='mp4' and 'mp4' in fm) or (ex['kind']=='webm' and 'matroska' in fm),[ex['kind'],fm,ex['type']])
    # leave detection
    ex2=pe.evaluate("""async()=>{Object.defineProperty(document,'hidden',{get:()=>window.__h===1,configurable:true});setTimeout(()=>{window.__h=1;document.dispatchEvent(new Event('visibilitychange'));setTimeout(()=>{window.__h=0;document.dispatchEvent(new Event('visibilitychange'))},600)},3000);const r=await CP.exportVideo();return {ok:r.v.ok,left:!!r.v.left,msg:r.v.msg}}""")
    chk('C13 leaving the app during export: flagged, not passed',ex2['left']==True and ex2['ok']==False and '合格扱いにしません' in ex2['msg'],ex2)
    chk('C13b save button shows warning text',('要確認' in pe.inner_text('#dl')),pe.inner_text('#dl'))
    pe.context.close()
    # evaluation form
    vals=[8,7,9,6,5,8,7,6,9,7]
    out=pg.evaluate("(v)=>{v.forEach((x,i)=>document.getElementById('e'+i).value=x);document.getElementById('bEv').click();return document.getElementById('evo').textContent}",vals)
    exp=round(sum(vals)/(10*len(vals))*100)
    chk('C14 evaluation form: total and 100-point conversion correct, mock labelled reference-only',('合計 %d/100'%sum(vals) in out) and ('100点換算 %d'%exp in out) and '参考のみ' in out,out[:90].replace('\n',' '))
    rep=pg.evaluate("()=>CP.report()")
    chk('C15 report states mock footage cannot judge quality; audio and safe-area included',('判定には使えません' in rep['note']) and rep['audio'] and rep['safe']['ok'],rep['note'])
    chk('C16 no page errors in the whole session',not [e for e in errs if 'GPU stall' not in e and 'GL Driver' not in e],errs[:2])
    b.close()
print('ALL',all(R.values()),sum(R.values()),'/',len(R))
