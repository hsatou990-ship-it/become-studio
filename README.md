# BECOME. STUDIO v2.3
index.html, sw.js, manifest.webmanifest, icon.svg, icon-192.png, icon-512.png を同じ階層に置くだけで動く静的サイトです。ビルド不要、サーバー不要、費用0円。

## GitHub Pages（スマホのみ）
1. Chromeで github.com にログインし、右上の＋から New repository を開く。
2. 名前を become-studio、Public にして作成。
3. 作成後の画面で uploading an existing file を開き、6ファイルを選んでアップロード、Commit changes を押す。
   （zipは自動展開されないので、ファイルを個別に選ぶ）
4. Settings、Pages を開き、Branch を main、フォルダを / (root) にして Save。
5. 1〜数分後に https://ユーザー名.github.io/become-studio/ が公開される。
6. そのURLをChromeで開き、メニューの「ホーム画面に追加」またはアプリをインストール。

## Cloudflare Pages
dash.cloudflare.com、Workers & Pages、Create、Pages、Upload assets で6ファイルを選んで Deploy。アカウント作成は無料。

## 初回に必要な通信
Kokoroのモデルと日本語辞書（約24MB）をjsDelivrとHugging Faceから取得します。Wi-Fi推奨。


## v3.0
1ページ・3ステップ（テーマ入力→動画を作る→保存）。Kokoro日本語男声で全自動。詳細は「詳細設定」に集約。

## v4.0
- ナレーション第一候補: Gemini 3.8 Flash TTS（モデルID gemini-3.8-flash-tts。無料枠あり、公式料金ページ記載）。Kokoroは無料の予備。
- APIキーは公開ソースに入れず、利用者の端末のブラウザ内にだけ保存（任意で proxy/worker.js の中継に切替可。未検証）。
- 上限到達・キー無効・通信失敗時は課金せずKokoroへ自動切替。
- 演出テンプレート3種（ダークシネマ／心理学ストーリー／努力・成長ドキュメンタリー）をテーマから自動選択。
- 競合研究: 参考動画ファイルの数値分析（長さ・切替・間・音量推移）。他人の台本・映像・音声は使いません。
- 成果記録（再生・平均視聴・保存・フォロワー増）と比較・改善提案。
- エピソードは創作の例です。実体験に置き換えると効果が高まります。

## v5.0 TikTok連携
- worker/worker.js: Cloudflare Workers の中継（OAuth 2.0 コード交換・更新・Display API・下書き送信）。client_secret はWorkerのシークレットにのみ保存。
- アプリ: ログイン、プロフィール・フォロワー、公開動画の再生/いいね/コメント/シェア、自動分析、企画提案、下書き送信（自動投稿はしません）。
- 設定手順と審査の注意: docs/tiktok-setup.md
- 注意: 実際のTikTok・Cloudflareに接続した検証は未実施です。

## v6.0（2026-11-26）
- ElevenLabs連携（任意・有料）。キーは端末の中だけに保存。生成前に契約の残りを毎回確認し、不足・契約無効・確認失敗のときは生成せず停止（Gemini→Kokoroへ切替）。1本あたり／今月の自主上限、実消費の記録、同一台本の再生成は端末内キャッシュで追加消費なし。
- 映像：モーショングラフィックス（黒背景・白い人物・図解・数字カウント・音声同期の字幕・場面転換）を既定に。従来の背景は「映像スタイル」から選択可。
- 未検証：実際のElevenLabs応答と声質、Android実機での再生・保存。

## v6.1（2026-11-26）無料運用へ変更
- 標準ナレーション：Gemini TTS（無料枠）。失敗・上限・キー未設定時はKokoroへ自動切替。ElevenLabsは将来用に残し、既定はオフ。
- 1日のGemini呼び出し自主上限（初期60回）。上限で停止し、課金の発生する操作はしません。
- 動画スタイルを先頭で選択：図解モーショングラフィックス／実写モチベーション／ダークシネマ／心理学アニメーション／ストーリー。
- 未検証：実Geminiの声質と無料枠での動作、Kokoro実機、スマホでの保存・TikTok投稿。

## v6.2（2026-11-26）制作指示リンク
- URLの末尾に #s=スタイル(mg/real/cinema/psych/story)&t=テーマ&x=台本(改行は%0A)&d=秒(45/60/75/90/120) を付けて開くと、スタイル・テーマ・台本が自動入力される。動画作成は自動では始まらない（ボタンを押す）。
