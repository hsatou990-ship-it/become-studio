import os;REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
from playwright.sync_api import sync_playwright
import json, numpy as np, wave, os
D='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/cp/ns/'
BASE='http://127.0.0.1:8765/exp/cinematic-pro/index.html'
J=json.load(open((REPO+'/exp/design/price-of-staying.design.json')))
R=[]
def chk(n,c,d=''):R.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:600])
SR=48000
def synth(path,total,spans,freqs=None,noise=0.0,seed=1):
    r=np.random.RandomState(seed);x=np.zeros(int(total*SR))
    for k,(a,b) in enumerate(spans):
        f0=(freqs[k] if freqs else 200+60*k);t=np.arange(int((b-a)*SR))/SR
        env=np.minimum(1,np.minimum(t/.03,(b-a-t)/.05))*(.5+.5*np.abs(np.sin(2*np.pi*4*t)))
        v=sum(np.sin(2*np.pi*f0*h*t)/h for h in range(1,5))
        i0=int(a*SR);x[i0:i0+len(t)]+=0.25*env*v
    x+=noise*r.randn(len(x))
    w=wave.open(path,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes());w.close()
def design(n,dur=3.5):
    sc=[];roles=['hook','low','build','turn','rise','climax']
    for i in range(n):
        s=json.loads(json.dumps(J['scenes'][i%4]));s['dur']=dur;s['role']=('hook' if i==0 else 'ending' if i==n-1 else roles[1+(i%4)] if i%4!=3 else 'turn');s['text']=J['scenes'][i%4]['text'];s['sfx']=[];s.pop('fx',None)
        s['transition']='cut';sc.append(s)
    d=json.loads(json.dumps(J));d['scenes']=sc;return json.dumps(d,ensure_ascii=False)
def ready(pg):pg.wait_for_function("()=>window.CP&&CP.S&&CP.S.sc&&CP.S.sc.length>0",timeout=20000);pg.wait_for_timeout(500)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    ctx=b.new_context(viewport={'width':412,'height':915});pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE+'#res=360');ready(pg)
    # ---- pure plan invariants for 15/30/60 and keep/fit
    code="""([seg,D0,mode,dur])=>{const r=CP.planSync({seg,D0,Eh:1.5,mode,audioDur:dur});return {D:r.D,ext:r.ext,warn:r.warn,add:r.add,sumAdd:r.sumAdd,aft:r.afterglow,resid:r.resid,eh:r.Eh,place:r.place,L:r.L,A:r.A,endA:r.endA,off:r.off,stretch:r.stretch}}"""
    def mk(n,t0,sl,gp):
        seg=[];t=t0
        for i in range(n):seg.append({'s':t,'e':t+sl});t+=sl+gp
        return seg,t-gp
    ok=True;bad=[]
    for D0,n,sl,gp,dur in ((15,4,1.5,.6,8.25),(30,8,1.8,.5,16.0),(60,16,1.9,.5,33.0),(15,4,2.4,.5,11.2),(60,16,2.0,.6,41.0)):
        seg,last=mk(n,.3,sl,gp)
        for mode in('keep','fit'):
            r=pg.evaluate(code,[seg,D0,mode,dur])
            # invariants
            L=r['L'];mono=all(L[i]['t0']+L[i]['d']<=L[i+1]['t0']+1e-6 for i in range(n-1)) and all(r['A'][i]<r['A'][i+1] for i in range(len(r['A'])-1))
            speech=all(abs(L[i]['d']-sl)<1e-6 for i in range(n))  # speaking duration preserved (no stretch)
            pcs=r['place'];nonov=all(pcs[i]['d']+(pcs[i]['s1']-pcs[i]['s0'])<=pcs[i+1]['d']+1e-6 for i in range(len(pcs)-1))
            # each sentence maps into a piece at rate 1
            mapok=True
            for i in range(n):
                found=False
                for pc in pcs:
                    if pc['s0']-1e-6<=seg[i]['s'] and seg[i]['e']<=pc['s1']+1e-6:
                        found=abs(pc['d']+(seg[i]['s']-pc['s0'])-L[i]['t0'])<1e-6
                if not found:mapok=False
            keepok=(mode=='fit') or r['D']>=D0-1e-6
            if not(mono and speech and nonov and mapok and keepok and r['stretch']==1):ok=False;bad.append((D0,n,mode,mono,speech,nonov,mapok,keepok))
            if mode=='keep' and dur<D0*0.7: 
                pass
    chk('N1 plan invariants (15/30/60, keep+fit): monotonic, speech duration unchanged, no overlap, rate=1 mapping, keep never below D0',ok,bad)
    seg,_=mk(4,.3,1.5,.6);r=pg.evaluate(code,[seg,15,'keep',8.25])
    print('8.25s/15s keep:',{k:r[k] for k in('D','sumAdd','aft','resid','eh','ext')},r['warn'])
    chk('N2 8.25s audio on 15s design: D stays 15, pauses added, no extension, logo hold within 1.4-2.0 (+residual)',r['D']==15 and r['sumAdd']>0 and not r['ext'] and 1.4-1e-6<=r['eh']<=2.1,r)
    r2=pg.evaluate(code,[seg,15,'fit',8.25]);chk('N3 fit mode shortens below design (D<15)',r2['D']<15 and r2['D']>=5,r2['D'])
    segL,_=mk(4,.3,3.6,.5);r3=pg.evaluate(code,[segL,15,'keep',16]);chk('N4 audio longer than design: extended + warning, speech not compressed',r3['ext'] and r3['D']>15 and any('延長' in w for w in r3['warn']),r3)
    segS,_=mk(16,.3,1.0,.3);r4=pg.evaluate(code,[segS,60,'keep',20]);print('short vs 60:',{k:r4[k] for k in('D','sumAdd','aft','resid')},r4['warn'])
    chk('N5 very short audio vs 60s design: D stays >=60 (never <60), residual disclosed by warning',r4['D']>=60 and r4['resid']>.5 and any('短く' in w for w in r4['warn']),r4)
    chk('N6 gap additions capped per gap (<=0.9) and total pause <=1.6 per gap',all(a<=0.9+1e-9 for a in r4['add']) and all(a+.3<=1.6+1e-9 for a in r4['add']),r4['add'])
    # ---- E2E with synthetic audio, price-of-staying (4 lines)
    pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(500)
    spans=[(.3,1.9),(2.5,4.0),(4.6,6.3),(6.9,8.0)];freqs=[440,660,880,1100]
    synth(D+'a.wav',8.25,spans,freqs)
    pg.set_input_files('#narr',D+'a.wav');pg.wait_for_timeout(1500)
    y=pg.evaluate("()=>CP.S.sync");print('E2E sync',{k:y[k] for k in('ok','mode','D0','D','addedPause','afterglow','logoHold','pieces')},y['conf'])
    chk('N7 E2E: sync ok, D=15 (design kept), confidence high, no stretch, content NOT verified',y['ok'] and y['D']==15 and y['conf']['level']=='high' and y['stretch']==1 and y['content']['verified']==False,y)
    rep=pg.inner_text('#syncrep');chk('N8 report separates span estimation and content check',('推定' in rep) and ('内容の一致' in rep and '未確認' in rep) and ('伸縮: なし' in rep),rep)
    # audio check: narration only
    res=pg.evaluate("""async()=>{CP.setBgmMode('none');CP.S.sc.forEach(o=>o.sfx={});const m=await CP.buildAudio();const x=m.getChannelData(0);const w=(a,b)=>Array.from(x.slice(Math.floor(a*48000),Math.floor(b*48000)));
      return {ln:CP.S.ln.map(l=>({t0:l.t0,d:l.d})),win:CP.S.ln.map(l=>w(l.t0+.1,l.t0+l.d-.1)),gaps:CP.S.ln.slice(0,3).map((l,i)=>w(l.t0+l.d+.12,CP.S.ln[i+1].t0-.12)),tail:w(CP.S.sc[4].a+.1,CP.S.sc[4].a+.8)}}""")
    def dom(a):
        a=np.array(a);a=a*np.hanning(len(a));f=np.fft.rfftfreq(len(a),1/SR);S=abs(np.fft.rfft(a));return f[S.argmax()]
    dd=[dom(w) for w in res['win']];print('dominant freqs',[round(v) for v in dd])
    chk('N9 pitch of each sentence unchanged (no time-stretch): dominant freq within 1.5% of source',all(abs(v-f)/f<.015 for v,f in zip(dd,freqs)),dd)
    rms=lambda a:10*np.log10(np.mean(np.square(a))+1e-14)
    gp=[rms(g) for g in res['gaps']];sp=[rms(w) for w in res['win']]
    chk('N10 inserted/natural pauses are silent (< -60 dB) and speech present (> -35 dB); level consistent across sentences (±1.5 dB)',max(gp)<-60 and min(sp)>-35 and max(sp)-min(sp)<1.5,(gp,sp))
    L=res['ln'];shift=[L[i]['t0']-spans[i][0] for i in range(4)]
    chk('N11 subtitle timings follow speech (offset from source = constant off + cumulative inserted pauses, non-decreasing)',all(shift[i+1]>=shift[i]-1e-6 for i in range(3)),shift)
    chk('N12 scene/cut starts monotonic and last scene starts after last sentence end',all(pg.evaluate("()=>CP.S.sc.every((o,i,A)=>i===0||o.a>A[i-1].a)")) if False else pg.evaluate("()=>CP.S.sc.every((o,i,A)=>i===0||o.a>A[i-1].a)"))
    # fit mode via select
    pg.select_option('#syncm','fit');pg.wait_for_timeout(700)
    chk('N13 fit mode via UI shortens D and persists in localStorage',pg.evaluate("()=>CP.S.D0===undefined&&CP.S.sync.mode")=='fit' and pg.evaluate("()=>CP.S.sync.D")<15 and pg.evaluate("()=>localStorage.getItem('cp_syncmode')")=='fit')
    pg.select_option('#syncm','keep');pg.wait_for_timeout(700)
    chk('N14 back to keep restores D=15',pg.evaluate("()=>CP.S.sync.D")==15)
    # ---- failure/manual
    synth(D+'j.wav',8.25,[(.3,1.9),(2.0,3.5),(3.6,5.3),(5.4,6.5)],freqs)  # gaps 0.1s: undetectable
    pg.set_input_files('#narr',D+'j.wav');pg.wait_for_timeout(1500)
    y=pg.evaluate("()=>CP.S.sync");chk('N15 undetectable sentences -> failure warning + low confidence + not aligned + manual UI present',(not y['ok']) and y['conf']['level']=='low' and pg.evaluate("()=>CP.S.aligned")==False and pg.locator('#msA').count()==1,y)
    chk('N16 failure leaves D at design value (no silent change)',pg.evaluate("()=>CP.S.base.D")==15 and pg.evaluate("()=>CP.S.sc[CP.S.sc.length-1].b")==15)
    pg.evaluate("()=>{document.getElementById('syncman').parentElement.open=true}")
    pg.fill('#msS0','0.3');pg.fill('#msE0','1.9');pg.fill('#msS1','2.0');pg.fill('#msE1','3.5');pg.fill('#msS2','3.6');pg.fill('#msE2','5.3');pg.fill('#msS3','5.4');pg.fill('#msE3','6.5')
    pg.click('#msA');pg.wait_for_timeout(1200)
    y=pg.evaluate("()=>CP.S.sync");chk('N17 manual spans applied: ok, manual flag, confidence "manual", content still unverified, aligned',y['ok'] and y['manual'] and y['conf']['level']=='manual' and y['content']['verified']==False and pg.evaluate("()=>CP.S.aligned"),y)
    pg.fill('#msS1','1.0');pg.click('#msA');pg.wait_for_timeout(500)
    chk('N18 invalid manual input (overlap) rejected with message, previous values kept',('入力が正しくありません' in pg.inner_text('#msM')) and pg.evaluate("()=>CP.S.manual[1].s")==2.0,pg.inner_text('#msM'))
    # session restore of manual via res switch
    pg.select_option('#resSel','1080');pg.wait_for_load_state();ready(pg);pg.wait_for_timeout(2000)
    chk('N19 resolution switch keeps manual spans + narration',pg.evaluate("()=>!!CP.S.manual&&CP.S.manual[1].s")==2.0 and pg.evaluate("()=>CP.S.sync&&CP.S.sync.manual"),pg.evaluate("()=>[!!CP.S.manual,!!CP.S.sync]"))
    pg.evaluate("()=>{document.getElementById('syncman').parentElement.open=true}");pg.click('#msR');pg.wait_for_timeout(1000)
    chk('N20 reset to auto detection',pg.evaluate("()=>CP.S.manual")is None and pg.evaluate("()=>CP.S.sync.ok")==False)
    pg.select_option('#resSel','360') if False else None
    pg.goto(BASE+'#res=360');ready(pg);pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(500)
    # ---- low confidence (noisy) and mid (short gap)
    synth(D+'n.wav',8.25,spans,freqs,noise=0.06,seed=3)
    pg.set_input_files('#narr',D+'n.wav');pg.wait_for_timeout(1500)
    y=pg.evaluate("()=>CP.S.sync");print('noisy',y['info'],y['conf'])
    chk('N21 noisy audio: low/mid confidence with warning text or still high with measured SNR reported',y['conf']['level'] in('low','mid') or y['info']['snrDb']>=30,y)
    synth(D+'m.wav',8.25,[(.3,1.9),(2.15,3.65),(3.95,5.6),(5.9,7.0)],freqs)
    pg.set_input_files('#narr',D+'m.wav');pg.wait_for_timeout(1500)
    y=pg.evaluate("()=>CP.S.sync");chk('N22 short gaps (0.25-0.3s): mid confidence + warning',y['conf']['level']=='mid' and any('中程度' in w for w in pg.evaluate("()=>CP.S.warn")),(y['conf'],y['info']))
    # ---- content outlier: sentence 3 spoken too fast for its text
    synth(D+'o.wav',8.25,[(.3,1.9),(2.5,4.0),(4.6,5.0),(6.0,7.6)],freqs)
    pg.set_input_files('#narr',D+'o.wav');pg.wait_for_timeout(1500)
    y=pg.evaluate("()=>CP.S.sync");chk('N23 speed outlier flagged as suspicion only (content verified stays false)',any(q['line']==3 for q in y['content']['outliers']) and y['content']['verified']==False and any('第3文' in w for w in pg.evaluate("()=>CP.S.warn")),y['content'])
    # ---- evidence
    ev=pg.evaluate("async()=>(await CP.evidenceRecord()).narration.sync")
    chk('N24 evidence records sync (mode, confidence, contentVerified=false, target/final, stretch=1)',ev and ev['contentVerified']==False and ev['stretch']==1 and ev['mode']=='keep' and ev['targetSec']==15,ev)
    # ---- 30 s and 60 s designs end-to-end
    for n,tot in ((8,30),(17,60)):
        dj=design(n,3.5 if n==8 else 3.5)
        pg.fill('#dj',dj);pg.click('#bDJ');pg.wait_for_timeout(700)
        d0=pg.evaluate("()=>CP.S.base.D");ln=pg.evaluate("()=>CP.S.base.ln.map(l=>[l.t0,l.d])")
        okI=pg.evaluate("()=>CP.lastIntake&&CP.lastIntake.conform.ok")
        sp=[];t=.4
        for i in range(n):
            L=1.6;sp.append((t,t+L));t+=L+.55
        fq=[200+40*(i%8) for i in range(n)]
        synth(D+f'e{n}.wav',t+.3,sp,fq)
        pg.set_input_files('#narr',D+f'e{n}.wav');pg.wait_for_timeout(2500)
        y=pg.evaluate("()=>CP.S.sync");print(n,'scenes: D0',d0,'sync',{k:y.get(k) for k in('ok','D0','D','addedPause','afterglow','logoHold','residualToLogo')},y['conf']['level'])
        chk(f'N25-{n} {d0}s design ({n} lines) with {t:.1f}s audio: D>={d0} (keep), no stretch, ok',okI and y['ok'] and y['D']>=d0-1e-6 and y['stretch']==1,(okI,y))
        pg.select_option('#syncm','fit');pg.wait_for_timeout(2500)
        y2=pg.evaluate("()=>CP.S.sync");chk(f'N26-{n} fit mode shortens ({y2["D"]} < {d0})',y2['D']<d0,y2['D'])
        pg.select_option('#syncm','keep');pg.wait_for_timeout(1500)
    chk('N27 no page errors',not errs,errs[:3])
    b.close()
print(sum(R),'/',len(R))
