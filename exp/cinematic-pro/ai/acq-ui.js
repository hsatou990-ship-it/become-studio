import * as A from './acquire.js';
const $=id=>document.getElementById(id),mb=v=>v==null?'未測定':(v/1048576).toFixed(1)+' MB';let plan=null,ctl=null;
const say=t=>{$('aSt').textContent=t};
async function info(){try{const s=await A.storageInfo();$('aSto').textContent='端末の保存: 使用 '+mb(s.usage)+'／上限の目安 '+mb(s.quota)+'｜永続ストレージ: '+(s.persisted==null?'確認できません':s.persisted?'有効':'未付与（取得時に要求します。付与されなくても動きますが、ブラウザが削除する場合があります）')}catch{}}
async function show(deep){try{const s=await A.status(deep);$('aTab').innerHTML=s.rows.length?'<table><tr><th>ファイル</th><th>容量</th><th>照合</th><th>保存状態</th></tr>'+s.rows.map(r=>'<tr><td>'+r.name+'</td><td>'+mb(r.size)+'</td><td>'+(r.verified?'照合済み':'未検証')+'</td><td>'+({ok:'正常','missing':'消失（自動では再取得しません）','corrupt-size':'破損（容量不一致）','corrupt-hash':'破損（ハッシュ不一致）'}[r.state]||r.state)+'</td></tr>').join('')+'</table>':'<p class="note">未取得</p>';
 $('aRdy').textContent=s.ready?'分析の準備: 完了（通信なしで分析できます）':'分析の準備: 未完了'+(s.rows.length?'（上の表を確認。必要なら手動で取得）':'');return s}catch(e){say('保存状態を読めません: '+e.message)}}
document.addEventListener('securitypolicyviolation',e=>{say('未承認の接続をCSPが停止しました: '+(e.blockedURI||'').slice(0,80)+'（承認なしには許可しません）')});
$('aRes').onclick=async()=>{ctl=new AbortController();$('aRes').disabled=true;say('取得対象を確認中（メタデータのみ通信）…');
 try{plan=await A.resolve(ctl.signal);$('aList').innerHTML='<table><tr><th>種類</th><th>ファイル</th><th>容量</th><th>照合方式</th><th>接続先</th></tr>'+plan.files.map(f=>'<tr><td>'+f.kind+(f.exec?'（実行）':'')+'</td><td>'+f.name+'</td><td>'+mb(f.size)+'</td><td>'+({'sha256':'SHA-256','git-sha1':'git blob SHA-1'}[f.hash.alg])+'</td><td>'+new URL(f.url).hostname+'</td></tr>').join('')+'</table>';
  $('aPlan').textContent='合計 '+mb(plan.total)+'（'+plan.files.length+'ファイル）｜ONNX Runtime '+plan.ort+'｜ライブラリ '+A.TARGET.lib+'｜承認コード: '+plan.code+'｜この一覧をオーナー（とChatGPT）が確認し、問題なければ承認コードを下に入力して取得します';$('aGo').disabled=false;say('取得対象を確定しました。まだファイルは取得していません。')}
 catch(e){plan=null;say('確認に失敗: '+e.message)}finally{$('aRes').disabled=false}};
$('aGo').onclick=async()=>{if(!plan)return;ctl=new AbortController();$('aGo').disabled=true;$('aStop').disabled=false;
 try{const r=await A.download(plan,$('aCode').value.trim(),{signal:ctl.signal,persist:true,onProgress:p=>say('取得中: '+p.name+' '+mb(p.got)+' / '+mb(p.size)+'｜全体 '+mb(p.total)+' / '+mb(p.all))});say('取得完了: '+r.map(x=>x.name+'＝'+x.state).join('、'))}
 catch(e){say('停止: '+e.message+(e.partial&&e.partial.length?'｜ここまでの保存: '+e.partial.map(x=>x.name).join('、'):'')+'｜保存済みの分は残ります。再開は取得ボタンを手動で押してください')}
 finally{$('aGo').disabled=false;$('aStop').disabled=true;await show(false);await info()}};
$('aStop').onclick=()=>{if(ctl)ctl.abort()};
$('aChk').onclick=()=>show(false);$('aDeep').onclick=async()=>{say('保存内容のハッシュを再計算中…');await show(true);say('再検証が終わりました')};
$('aDel').onclick=async()=>{if(!$('aDelOk').checked){say('削除するには、横のチェックを入れてください（このページのAIデータのみ削除します）');return}await A.clearAll();$('aDelOk').checked=false;await show(false);await info();say('保存したAIデータを削除しました（編集画面の素材・プロジェクトには触れていません）')};
window.ACQ={A,show,info};info();show(false);
