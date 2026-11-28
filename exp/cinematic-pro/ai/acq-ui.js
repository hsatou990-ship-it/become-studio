import * as A from './acquire.js?v=r17';
const $=id=>document.getElementById(id),mb=v=>v==null?'未測定':(v/1048576).toFixed(1)+' MB';let plan=null,ctl=null;
const say=t=>{$('aSt').textContent=t};
async function info(){try{const s=await A.storageInfo();$('aSto').textContent='端末の保存: 使用 '+mb(s.usage)+'／上限の目安 '+mb(s.quota)+'｜永続ストレージ: '+(s.persisted==null?'確認できません':s.persisted?'有効':'未付与（取得時に要求します。付与されなくても動きますが、ブラウザが削除する場合があります）')}catch{}}
async function show(deep){try{const s=await A.status(deep);$('aTab').innerHTML=s.rows.length?'<table><tr><th>ファイル</th><th>容量</th><th>照合</th><th>保存状態</th></tr>'+s.rows.map(r=>'<tr><td>'+r.name+'</td><td>'+mb(r.size)+'</td><td>'+(r.verified?'照合済み':'未検証')+'</td><td>'+({ok:'正常','missing':'消失（自動では再取得しません）','corrupt-size':'破損（容量不一致）','corrupt-hash':'破損（ハッシュ不一致）'}[r.state]||r.state)+'</td></tr>').join('')+'</table>':'<p class="note">未取得</p>';
 $('aRdy').textContent=s.ready?'分析の準備: 完了（通信なしで分析できます）':'分析の準備: 未完了'+(s.rows.length?'（上の表を確認。必要なら手動で取得）':'');return s}catch(e){say('保存状態を読めません: '+e.message)}}
const clean=x=>{try{const q=new URL(x);return q.origin+q.pathname}catch{return String(x).split('?')[0]}};   // 署名付きURLの認証情報（?以降）は表示・記録しない
document.addEventListener('securitypolicyviolation',e=>{const c=window.__bsCur||{},b=clean(e.blockedURI||'');let h='';try{h=new URL(b).hostname}catch{h=b}
 $('aCsp').textContent='【CSPが接続を停止】\n対象ファイル: '+(c.name||'不明')+'\n要求したURL: '+clean(c.url||'不明')+'\nCSPが報告したURL: '+b+'\n停止したホスト: '+(h||'不明')+'\n停止した指示: '+(e.effectiveDirective||e.violatedDirective)+'\n注: 要求URLと同じ接続先が報告された場合は、リダイレクト先の別ホストが停止した可能性があります（ブラウザは転送先のホスト名を報告しないことがあります）。承認なしには許可しません。';say('CSPが接続を停止しました。詳細は下の枠を確認してください')});
$('aRes').onclick=async()=>{ctl=new AbortController();$('aRes').disabled=true;say('取得対象を確認中（メタデータのみ通信）…');
 try{plan=await A.resolve(ctl.signal);$('aList').innerHTML='<table><tr><th>種類</th><th>ファイル</th><th>容量</th><th>照合方式</th><th>接続先</th></tr>'+plan.files.map(f=>'<tr><td>'+f.kind+(f.exec?'（実行）':'')+'</td><td>'+f.name+'</td><td>'+mb(f.size)+'</td><td>'+({'sha256':'SHA-256','git-sha1':'git blob SHA-1'}[f.hash.alg])+'</td><td>'+new URL(f.url).hostname+'</td></tr>').join('')+'</table>';
  $('aPlan').textContent='合計 '+mb(plan.total)+'（'+plan.files.length+'ファイル）｜ONNX Runtime '+plan.ort+'｜ライブラリ '+A.TARGET.lib+'｜承認コード: '+plan.code+'｜この一覧をオーナー（とChatGPT）が確認し、問題なければ承認コードを下に入力して取得します';links(plan.files.filter(f=>f.kind==='model'&&/onnx/.test(f.name)));$('aGo').disabled=false;say('取得対象を確定しました。まだファイルは取得していません。')}
 catch(e){plan=null;say('確認に失敗: '+e.message)}finally{$('aRes').disabled=false}};
$('aGo').onclick=async()=>{if(!plan)return;ctl=new AbortController();$('aGo').disabled=true;$('aStop').disabled=false;
 try{const r=await A.download(plan,$('aCode').value.trim(),{signal:ctl.signal,persist:true,onProgress:p=>say('取得中: '+p.name+' '+mb(p.got)+' / '+mb(p.size)+'｜全体 '+mb(p.total)+' / '+mb(p.all))});say('取得完了: '+r.map(x=>x.name+'＝'+x.state).join('、'))}
 catch(e){say('停止: '+e.message+(e.partial&&e.partial.length?'｜ここまでの保存: '+e.partial.map(x=>x.name).join('、'):'')+'｜保存済みの分は残ります。再開は取得ボタンを手動で押してください')}
 finally{$('aGo').disabled=false;$('aStop').disabled=true;await show(false);await info()}};
$('aResume').onclick=async()=>{try{const p=await A.savedPlan();if(!p){say('保存された取得対象がありません。「取得対象を確認」から始めてください');return}plan=p;const s=await A.status(false),have=new Set(s.rows.filter(r=>r.verified&&r.state==='ok').map(r=>r.name)),left=p.files.filter(f=>!have.has(f.name));
 $('aList').innerHTML='<p class="note">保存済み '+have.size+' 件は保持。残り '+left.length+' 件: '+left.map(f=>f.name+'（'+mb(f.size)+'・'+new URL(f.url).hostname+'）').join('、')+'</p>';$('aPlan').textContent='再開｜承認コード: '+p.code+'｜通信はしません。コードを入力して「取得する」を押すと、残りだけを取得します';links(left);$('aGo').disabled=false;say('再開の準備ができました（メタデータの再取得なし）')}catch(e){say('再開できません: '+e.message)}};
function links(left){$('aLn').innerHTML=left.length?'<p class="note">【代替: 端末にダウンロードして取り込む】取得できないファイルは、下の公式リンクを押して端末にダウンロードし（通信はブラウザの通常のダウンロード）、その後「ファイルを選ぶ」で選んで取り込みます。ハッシュ照合は同じです。</p>'+left.filter(f=>/^https:\/\/huggingface\.co\//.test(f.url)).map(f=>'<div class="note"><a href="'+f.url+'" target="_blank" rel="noopener noreferrer" style="color:#7db4ff">'+f.name+'（'+mb(f.size)+'）</a></div>').join(''):''}
$('aImp').onclick=async()=>{try{const fs=[...$('aFile').files];if(!fs.length){say('取り込むファイルを選んでください');return}if(!plan)plan=await A.savedPlan();say('照合中…（大きいファイルは数十秒かかります）');const r=await A.importLocal(plan,fs);say('取り込み結果: '+r.map(x=>x.file+'＝'+x.state).join('｜'));$('aFile').value=''}catch(e){say('取り込めません: '+e.message)}finally{await show(false);await info()}};
$('aStop').onclick=()=>{if(ctl)ctl.abort()};
$('aChk').onclick=()=>show(false);$('aDeep').onclick=async()=>{say('保存内容のハッシュを再計算中…');await show(true);say('再検証が終わりました')};
$('aDel').onclick=async()=>{if(!$('aDelOk').checked){say('削除するには、横のチェックを入れてください（このページのAIデータのみ削除します）');return}await A.clearAll();$('aDelOk').checked=false;await show(false);await info();say('保存したAIデータを削除しました（編集画面の素材・プロジェクトには触れていません）')};
window.ACQ={A,show,info};info();show(false);

{const meta=document.querySelector('meta[http-equiv="Content-Security-Policy"]'),cs=meta?meta.content:'',m=cs.match(/connect-src([^;]*)/);$('aBuild').textContent='画面の版: r17-b0｜有効な接続許可（connect-src）:'+(m?m[1]:'確認できません')+'｜版が古い場合は、ブラウザの再読み込み（キャッシュ更新）をしてください'}
