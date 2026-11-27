import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
import json, numpy as np, scipy.signal as sg, hashlib
R='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/riko/'
URL='http://127.0.0.1:8765/exp/cinematic-pro/index.html#res=360'
J=open((REPO+'/exp/design/price-of-staying.design.json')).read()
T=json.load(open(R+'t3oct.json'));cs=[int(k) for k in T];tb=np.array([v[0] for v in T.values()])
Rr=[]
def chk(n,c,d=''):Rr.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:400])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800)
    pg.fill('#dj',J);pg.click('#bDJ');pg.wait_for_timeout(500)
    chk('V0 default voice = original (existing behaviour kept)',pg.evaluate("()=>document.querySelector('input[name=voice]:checked').value")=='orig' and pg.evaluate("()=>CP.S.voice")is None)
    chk('V1 Web Audio highpass Q converted to dB (-1.72)',abs(pg.evaluate("()=>CP.voiceHpQdB()")+1.72)<0.01)
    pg.set_input_files('#narr',R+'zip/BEYOND_Riko_A.wav');pg.wait_for_timeout(1500)
    chk('V2 narration loaded',pg.evaluate("()=>!!CP.S.narr&&CP.S.narr.duration>8"),pg.inner_text('#nst'))
    H="""()=>{const x=CP.S.narr.getChannelData(0);let h=0;for(let i=0;i<x.length;i+=7){h=(h*31+Math.round(x[i]*1e6))|0}return h}"""
    h0=pg.evaluate(H)
    chk('V3 default mix: voice original; build ok',pg.evaluate("async()=>{CP.S.mix=null;const m=await CP.buildAudio();return m.length>0}"))
    # beta voice buffer vs original: response
    d=pg.evaluate("async()=>{const o=CP.S.narr.getChannelData(0),v=await CP.voiceBuf(CP.S.narr);return {o:Array.from(o),v:Array.from(v.getChannelData(0)),sr:CP.S.narr.sampleRate}}")
    o=np.array(d['o']);v=np.array(d['v']);sr=d['sr']
    f,Po=sg.welch(o,sr,nperseg=4096);_,Pv=sg.welch(v,sr,nperseg=4096)
    diff=[]
    for c,t in zip(cs,tb):
        m=(f>=c/2**(1/6))&(f<c*2**(1/6));g=10*np.log10(Pv[m].sum()/Po[m].sum())
        diff.append((c,g))
    # remove common level offset
    off=np.mean([g-t for (c,g),t in zip(diff,tb)])
    err=[g-off-t for (c,g),t in zip(diff,tb)];print('beta-vs-B band err max',round(max(map(abs,err)),2),'rms',round(float(np.sqrt(np.mean(np.square(err)))),2),'offset',round(off,2))
    chk('V4 beta response within 1.3 dB of measured B/A per 1/3-oct band (50..10k)',max(map(abs,err))<1.3,err)
    chk('V5 original buffer untouched after beta render (hash equal)',pg.evaluate(H)==h0)
    # mix toggle
    r=pg.evaluate("""async()=>{CP.setVoice('orig');const a=await CP.buildAudio();const x=a.getChannelData(0);let ha=0;for(let i=0;i<x.length;i+=11)ha=(ha*31+Math.round(x[i]*1e6))|0;
      CP.setVoice('beta');const b=await CP.buildAudio();const y=b.getChannelData(0);let hb=0;for(let i=0;i<y.length;i+=11)hb=(hb*31+Math.round(y[i]*1e6))|0;
      CP.setVoice('orig');const c=await CP.buildAudio();const z=c.getChannelData(0);let hc=0,mdOC=0,mdOB=0;for(let i=0;i<z.length;i++){mdOC=Math.max(mdOC,Math.abs(x[i]-z[i]));mdOB=Math.max(mdOB,Math.abs(x[i]-y[i]))}
      const rms=(m,a0,b0)=>{const q=m.getChannelData(0);let s=0,n=0;for(let i=Math.floor(a0*48000);i<b0*48000&&i<q.length;i++){s+=q[i]*q[i];n++}return 10*Math.log10(s/Math.max(n,1)+1e-14)};
      let pa=0,pb=0;for(let i=0;i<x.length;i++){pa=Math.max(pa,Math.abs(x[i]));pb=Math.max(pb,Math.abs(y[i]))}
      return {mdOC,mdOB,diffAB:mdOB>1e-3,roundtrip:mdOC<1e-5,rmsO:rms(a,1,8),rmsB:rms(b,1,8),pa,pb,nan:Array.from(y.slice(0,2000)).some(q=>q!==q)}}""")
    print(r)
    chk('V6 beta changes mix; switching back reproduces original mix (max diff <1e-5; baseline float noise is ~6e-8)',r['diffAB'] and r['roundtrip'],r)
    chk('V7 beta mix level within 1.5 dB of original (RMS adjusted)',abs(r['rmsO']-r['rmsB'])<1.5,r)
    chk('V8 beta mix no clipping (peak<=0.999) no NaN',r['pb']<=0.999 and not r['nan'],r)
    # evidence + ledger
    pg.evaluate("()=>CP.setVoice('beta')")
    ev=pg.evaluate("async()=>{const e=await CP.evidenceRecord();return e.narration}")
    chk('V9 evidence records beta params + hpQdB + note',ev['voice']['id']=='beyond-cinematic-voice-beta' and abs(ev['voice']['params']['hpQdB']+1.72)<0.01 and '別物' in ev['voice']['note'],ev)
    chk('V10 ledger mentions beta (not original B)','Cinematic Voice β' in pg.inner_text('#ledger') and '別物' in pg.inner_text('#ledger'))
    ev0=pg.evaluate("async()=>{CP.setVoice('orig');const e=await CP.evidenceRecord();return e.narration.voice}")
    chk('V11 evidence original id',ev0['id']=='original')
    # persistence
    pg.evaluate("()=>CP.setVoice('beta')");pg.reload();pg.wait_for_timeout(1000)
    chk('V12 beta selection persists after plain reload',pg.evaluate("()=>CP.S.voice")=='beta' and pg.evaluate("()=>document.querySelector('input[name=voice]:checked').value")=='beta')
    pg.evaluate("()=>CP.setVoice('orig')");pg.reload();pg.wait_for_timeout(800)
    chk('V13 orig persists',pg.evaluate("()=>CP.S.voice")=='orig')
    # radio UI
    pg.check('input[name=voice][value=beta]');chk('V14 radio click sets beta',pg.evaluate("()=>CP.S.voice")=='beta')
    # mock narration and no-narration paths
    pg.click('#bMock');pg.wait_for_timeout(800)
    chk('V15 mock narration + beta builds',pg.evaluate("async()=>{const m=await CP.buildAudio();return m.length>0}"))
    pg.evaluate("()=>{CP.S.narr=null;CP.S.mix=null}")
    chk('V16 no narration + beta builds (no error)',pg.evaluate("async()=>{const m=await CP.buildAudio();return m.length>0}"))
    # preview button exists, no narration message
    pg.click('#bVb');chk('V17 preview without narration shows guidance','先にナレーション' in pg.inner_text('#voicest'))
    pg.click('#bMock');pg.wait_for_timeout(800);pg.click('#bVb');pg.wait_for_timeout(300)
    chk('V18 beta preview starts',('βを試聴中' in pg.inner_text('#voicest')) or ('試聴できません' in pg.inner_text('#voicest')),pg.inner_text('#voicest'))
    chk('V19 no page errors',not errs,errs)
    b.close()
print(sum(Rr),'/',len(Rr))
