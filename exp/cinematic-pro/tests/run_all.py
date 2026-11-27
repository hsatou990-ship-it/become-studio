"""試験の一括実行。使い方: python3 run_all.py [スイート名 ...]
環境変数: BECOME_REPO（リポジトリの場所。既定は、この試験コードの2つ上の2つ上）, BECOME_FIX（試験素材の場所）。
判定は、終了コードと出力の両方で行う。PASS と FAIL の行の数、異常終了（例外）、時間切れ、環境不足（素材の欠落）を区別する。
環境不足は、合格として数えない。終了コードは、失敗・異常・時間切れがあれば 1。環境不足だけの場合は 2。
"""
import os,sys,re,subprocess,time,socket,json
HERE=os.path.dirname(os.path.abspath(__file__))
REPO=os.environ.get('BECOME_REPO',os.path.abspath(HERE+'/../../..'));FIX=os.environ.get('BECOME_FIX','/tmp/become-fixtures')
PORT=8765;TIMEOUT=int(os.environ.get('BECOME_TIMEOUT','300'))
DEFAULT=['ts1','tright','thd','tcap','tsel','tres','tab1','tam','tam2','tam4','tam5','tcrop','tdr','tvb','tns','tsess','tbm','tbm2','tg','tbl','tbv','tev','tin','tsf','tk','tv3','tj','tc','tm2','tb']
names=sys.argv[1:] or DEFAULT
def port_free():
    s=socket.socket();r=s.connect_ex(('127.0.0.1',PORT));s.close();return r!=0
if not port_free():sys.exit('ポート %d が使用中です。同じ場所を配信中でなければ、止めてください'%PORT)
if not os.path.isdir(FIX+'/wavfx'):subprocess.run([sys.executable,HERE+'/make_fixtures.py',FIX],check=True)
srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'-d',REPO],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
env=dict(os.environ,BECOME_REPO=REPO,BECOME_FIX=FIX);res=[];tp=tf=0
try:
    for n in names:
        t0=time.time()
        try:
            p=subprocess.run([sys.executable,HERE+'/'+n+'.py'],cwd=HERE,env=env,capture_output=True,text=True,timeout=TIMEOUT);out=p.stdout+p.stderr;rc=p.returncode
        except subprocess.TimeoutExpired:
            res.append((n,'TIMEOUT',0,0,'%ds'%TIMEOUT));continue
        ps=len(re.findall(r'^PASS',out,re.M));fl=len(re.findall(r'^FAIL',out,re.M))
        m=re.search(r'(\d+) */ *(\d+)\s*$',out.strip().splitlines()[-1]) if out.strip() else None
        pf=re.findall(r'pass=(\d+) fail=(\d+)',out)
        if pf:ps,fl=int(pf[-1][0]),int(pf[-1][1])
        elif m and not ps and not fl:ps=int(m[1]);fl=int(m[2])-int(m[1]) if int(m[2])>=int(m[1]) else 0
        if re.search(r'FileNotFoundError|No such file',out):st='ENV'
        elif 'Traceback' in out or (rc!=0 and not fl):st='ERROR'
        elif fl or rc!=0:st='FAIL'
        elif ps==0:st='NOCOUNT'
        else:st='PASS'
        if st in('PASS','FAIL'):tp+=ps;tf+=fl
        res.append((n,st,ps,fl,'%.0fs'%(time.time()-t0)))
        if st in('ERROR','ENV'):open(HERE+'/last_'+n+'.log','w',encoding='utf-8').write(out[-3000:])
finally:
    srv.terminate()
print('%-8s %-8s %5s %5s %s'%('suite','status','pass','fail','time'))
for r in res:print('%-8s %-8s %5s %5s %s'%r)
bad=[r for r in res if r[1] in('FAIL','ERROR','TIMEOUT')];env_=[r for r in res if r[1] in('ENV','NOCOUNT')]
print('合計（PASS/FAILの結果のみ）: 合格 %d／失敗 %d｜異常・時間切れ %d｜環境不足・件数なし %d（合格に数えない）'%(tp,tf,len([r for r in bad if r[1]!='FAIL']),len(env_)))
json.dump(res,open(HERE+'/last_result.json','w'),ensure_ascii=False)
sys.exit(1 if bad else (2 if env_ else 0))
