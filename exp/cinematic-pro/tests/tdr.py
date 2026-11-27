from playwright.sync_api import sync_playwright
import json, re, time
exec(open('tns.py').read().split("with sync_playwright()")[0])
DR=D+'../dr/';SD='/tmp/claude-0/-home-claude/bb67a613-d9e5-5fe2-80d2-b0e9f790cfb0/scratchpad/'
R4=[]
def c4(n,c,d=''):R4.append(bool(c));print('PASS' if c else 'FAIL',n,'' if c else str(d)[:700])
SNAP="""()=>JSON.stringify({b:CP.S.base,sc:CP.S.sc,ln:CP.S.ln,sy:CP.S.sync,w:CP.S.warn,off:CP.S.off,al:CP.S.aligned,cl:CP.S.clips.map(c=>c?{m:c.meta,n:c.name,t:+c.el.currentTime.toFixed(3)}:null),ls:Object.fromEntries(Object.entries(localStorage)),mix:!!CP.S.mix,D:CP.S.sc[CP.S.sc.length-1].b})"""
def clip(pg,i,path,url):
    pg.set_input_files(f'#cf{i}',path);pg.fill(f'#cu{i}',url);pg.fill(f'#cc{i}','Test Creator');pg.fill(f'#cl{i}','Pexels License');pg.check(f'#ck{i}')
    ok=pg.evaluate(f"()=>CP.useClip({i})");pg.wait_for_timeout(500);return ok
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
    pg=b.new_context(viewport={'width':412,'height':915}).new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE+'#res=360');ready(pg);pg.fill('#dj',json.dumps(J,ensure_ascii=False));pg.click('#bDJ');pg.wait_for_timeout(600)
    s0=pg.evaluate(SNAP);t=time.time();R=pg.evaluate("async()=>await CP.directorReview()");dt=time.time()-t
    s1=pg.evaluate(SNAP)
    c4('R1 review runs without clips (mock materials): category says not real-material evaluation',R and '実素材評価ではない' in R['category'],R and R['category'])
    c4('R2 read-only: project state, sync, warnings, localStorage, clip positions unchanged',s0==s1)
    txt=pg.evaluate("()=>CP.drText(CP.S.review)")
    c4('R3 three evaluation kinds are separated in output (機械測定/設計上の評価/要視聴（未評価）) plus 未測定 list',all(k in txt for k in('【機械測定】','【設計上の評価】','【要視聴（未評価）】','いま測定できていない項目')),txt[:300])
    c4('R4 no scores anywhere (no N点 / N/5 / score fields)',not re.search(r'\d+(\.\d+)?\s*(点|/\s*5)',txt) and not any('score' in k for it in R['items'] for k in it),re.findall(r'.{10}\d\s*点.{5}',txt))
    c4('R5 every human item is 未評価 (needs-viewing) with no value claimed',all(i['status']=='needs-viewing' and i['value']=='未評価' for i in R['items'] if i['kind']=='human') and sum(1 for i in R['items'] if i['kind']=='human')==18,[i['label'] for i in R['items'] if i['kind']=='human'][:3])
    c4('R6 un-imported materials reported as 未測定 (not given values)',all(i['status']=='unmeasured' for i in R['items'] if i['id'].startswith('crop')),[i for i in R['items'] if i['id'].startswith('crop')][:1])
    emo=[i for i in R['items'] if i['id']=='emo'][0];c4('R7 emotion values taken from design JSON and labelled as design values (not viewer emotion)',('-0.60' in emo['value']) and emo['kind']=='design' and '測定ではありません' in emo['note'],emo)
    cl=[i for i in R['items'] if i['id']=='climax'][0];c4('R8 climax position computed (turn at 6.5s of 13.5s ≈ 0.48) and flagged only as 初期仮説',abs(float(cl['value'])-6.5/13.5)<.02 and '初期仮説' in cl['basis'],cl)
    sub=[i for i in R['items'] if i['id']=='sub0'][0];c4('R9 first subtitle time 0.5s ok, basis cites TikTok official as proxy',sub['status']=='ok' and 'TikTok公式' in sub['basis'] and '代理指標' in sub['basis'],sub)
    # clips
    ok=[clip(pg,0,DR+'cold_p.mp4','https://www.pexels.com/video/test-1/'),clip(pg,1,DR+'warm_p.mp4','https://www.pexels.com/video/test-2/'),clip(pg,2,SD+'clip_l.mp4','https://www.pexels.com/video/test-3/'),clip(pg,3,DR+'gray_p.mp4','https://www.pexels.com/video/test-4/')]
    print('clips loaded',ok)
    s0=pg.evaluate(SNAP);t=time.time();R=pg.evaluate("async()=>await CP.directorReview()");dt=time.time()-t;s1=pg.evaluate(SNAP)
    c4('R10 with 4 real clips: category = 実素材評価 label; read-only still holds (incl. clip currentTime restored)',R and R['category'].startswith('実素材評価') and s0==s1,(R and R['category']))
    c4('R11 review time under 20 s',dt<20,dt)
    lg={i['id']:i for i in R['items']}
    vals=lambda k:[float(re.search(k,lg['light'+str(j)]['value']).group(1)) for j in range(4)]
    luma=vals(r'平均 ([0-9.]+)')
    print('luma per scene',luma,'warm',lg['warm']['value'])
    wv=[float(x) for x in re.search(r'^([-0-9.\s→]+)｜',lg['warm']['value']).group(1).replace('→',' ').split()]
    c4('R12 measured warmth: warm clip scene is warmer than cold clip scene by >0.1; brighter',wv[1]-wv[0]>0.1 and luma[1]>luma[0],(wv,luma))
    c4('R13 landscape clip flagged: visible width < 0.6 and status check, with note that subject position is not measured',lg['crop2']['status']=='check' and '被写体がどこにいるか' in lg['crop2']['note'] and lg['crop0']['status']=='ok',(lg['crop2'],lg['crop0']))
    c4('R14 rights completeness reported per scene',lg['rights']['value'].count('記録あり')==4 and lg['rights']['status']=='ok',lg['rights'])
    c4('R15 no duplicates detected for different clips',lg['dup']['status']=='ok',lg['dup'])
    # duplicate source
    clip(pg,3,DR+'cold_p.mp4','https://www.pexels.com/video/test-1/');clip(pg,2,DR+'cold_p.mp4','https://www.pexels.com/video/test-1/')
    R=pg.evaluate("async()=>await CP.directorReview()");lg={i['id']:i for i in R['items']}
    c4('R16 consecutive same source flagged (same URL)',lg['dup']['status']=='check' and '同じ素材' in lg['dup']['value'],lg['dup'])
    # continuity flag: cold vs warm adjacency
    clip(pg,2,DR+'cold_p.mp4','https://www.pexels.com/video/test-5/')
    R=pg.evaluate("async()=>await CP.directorReview()");lg={i['id']:i for i in R['items']}
    print('cont',lg['cont']['value'],lg['cont']['status'])
    c4('R17 continuity values reported for 3 adjacencies',len(lg['cont']['value'].split(' / '))==3)
    # first subtitle late -> check (test-only mutation, restored)
    pg.evaluate("()=>{CP.S._t0=CP.S.ln[0].t0;CP.S.ln[0].t0=4.2}");R=pg.evaluate("async()=>await CP.directorReview()");lg={i['id']:i for i in R['items']}
    c4('R18 first subtitle at 4.2s -> check',lg['sub0']['status']=='check');pg.evaluate("()=>{CP.S.ln[0].t0=CP.S._t0}")
    # narration sync item
    pg.set_input_files('#narr',D+'a.wav');pg.wait_for_timeout(1800)
    R=pg.evaluate("async()=>await CP.directorReview()");lg={i['id']:i for i in R['items']}
    c4('R19 narration sync item reports mode/confidence and says content match unverified',lg['sync']['kind']=='measured' and '確度' in lg['sync']['value'] and '未確認' in lg['sync']['note'],lg['sync'])
    # busy guard
    c4('R20 refuses while exporting/previewing (S.busy)',pg.evaluate("async()=>{CP.S.busy=true;const r=await CP.directorReview();CP.S.busy=false;return r}") is None)
    # UI
    pg.evaluate("()=>{document.querySelector('#bDR').closest('details').open=true}");pg.click('#bDR');pg.wait_for_function("()=>document.getElementById('drout').textContent.includes('件数')",timeout=30000)
    out=pg.inner_text('#drout');c4('R21 UI button shows report with counts',('■ 映像監督' in out) and ('■ 広告ディレクター' in out) and ('件数:' in out),out[:200])
    pg.click('#bDRc');c4('R22 copy button does not break page',not errs,errs)
    print(out[:1800])
    b.close()
print(sum(R4),'/',len(R4))
