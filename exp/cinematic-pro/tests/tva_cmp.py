"""適応型フレーム抽出と固定枚数の比較（精度と処理枚数）。合成素材（正解が分かるもの）で、判定の一致を測る。
実素材・実機の結果ではない。結果は last_cmp.json に保存。"""
import os,sys,base64,json,subprocess,time
REPO=os.environ.get('BECOME_REPO','/home/claude/become-studio');FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
exec(open("tr1.py").read().split("\nwith sync_playwright()")[0])
TRUTH={'ok_a':None,'ok_b':None,'ok_c':None,'dup_a':None,'dark':None,'static':None,'cut_mid':None,'cut_2':None,'cut_6':None,
 'black_mid':'black','flat':'flat','bk_0_2':'black','bk_5_7.5':'black','bk_2_5':'black','black_short':None,'bk_1_1.6':None,'bk_6.5_8':None,'bk_3_3.9':None}
CUT={'cut_mid','cut_2','cut_6'}
CFG=[('固定4',{'full':4}),('固定6',{'full':6}),('固定8',{'full':8}),('固定12',{'full':12}),
 ('適応 n0=2 max8',{'n0':2,'nMax':8}),('適応 n0=3 max8',{'n0':3,'nMax':8}),('適応 n0=3 max10',{'n0':3,'nMax':10}),('適応 n0=3 max12',{'n0':3,'nMax':12}),('適応 n0=4 max10',{'n0':4,'nMax':10}),('適応 n0=5 max12',{'n0':5,'nMax':12})]
def run():
    srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd=REPO,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
    out={}
    try:
      with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required'])
        ctx,pg=mkctx(b);pg.goto(BASE+'#res=360');pg.evaluate("()=>{try{localStorage.clear()}catch{}}");pg.reload();ready(pg);pg.wait_for_timeout(500)
        for n in TRUTH:
            d=base64.b64encode(open(f'{FIX}/vafx/{n}.mp4','rb').read()).decode()
            for name,o in CFG:
                r=pg.evaluate("""async([d,o])=>{const bin=Uint8Array.from(atob(d),c=>c.charCodeAt(0));const f=new File([bin],'x.mp4',{type:'video/mp4'});const t=performance.now();
                  const r=await CP.vaMeasure(f,0,8,o);return{n:r.n,bad:r.bad,flags:r.flags,conf:r.conf,bf:r.bf,ms:Math.round(performance.now()-t)}}""",[d,o])
                out.setdefault(name,{})[n]=r
    finally:srv.terminate()
    return out
def score(out):
    rows=[]
    for name,_ in CFG:
        fp=miss=hold=ok=0;fr=0;ms=0;cutok=0;N=0
        for n,t in TRUTH.items():
            r=out[name][n];N+=1;fr+=r['n'];ms+=r['ms']
            fixed=name.startswith('固定')   # 固定枚数は確信度の仕組みを持たない。黒いフレームの割合が20%以上なら黒、とする単純な規則
            act=(['black'] if r['bf']>=.2 else (['flat'] if 'flat' in r['bad'] else [])) if fixed else (r['bad'] if r['conf']=='high' else [])   # 適応型は、確信度が低い場合は何もしない
            if (not fixed) and r['conf']!='high':hold+=1
            if t is None:
                if act:fp+=1
                else:ok+=1
            else:
                if act==[t]:ok+=1
                else:miss+=1
            if n in CUT and 'cut' in r['flags']:cutok+=1
        rows.append({'設定':name,'平均枚数':round(fr/N,2),'正答':ok,'誤検出':fp,'見逃し':miss,'確信度低(保留)':hold,'場面変化の検出':str(cutok)+'/'+str(len(CUT)),'平均ms':round(ms/N)})
    return rows
if __name__=='__main__':
    out=run();rows=score(out)
    json.dump({'note':'合成素材での比較。実機・実素材ではない','rows':rows,'raw':out},open('last_cmp.json','w'),ensure_ascii=False,indent=1)
    print('素材数',len(TRUTH))
    for r in rows:print(r)
