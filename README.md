# BECOME. STUDIO v2.2
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
