# TikTok連携の設定手順（2026-11-26 時点の公式ドキュメントに基づく）

## 先に知っておくこと（公式の記載）
- 審査（App review）を通すまで、本番のAPIは使えません。審査は「数日〜2週間」。
- 審査ガイドラインに「Apps must not be for private or personal use」「開発中・テスト中のアプリは承認されない」とあります。自分専用ツールは通らない可能性が高いです。
- 審査なしで試す方法として「サンドボックス」があります（対象アカウントは最大10、自分のTikTokを追加できる）。サンドボックスでContent Posting APIの公開投稿は使えません。Display APIがサンドボックスで使えるかは公式ページに明記がなく、確認できません。
- 未審査のクライアントが直接投稿すると、非公開（SELF_ONLY）限定、24時間で5ユーザーまで。
- 本アプリは「直接投稿」は実装せず、「下書きに送る」（video.upload）のみです。公開はTikTokアプリで本人が行います。

## 必要な値
- Worker のシークレット: TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / SESSION_KEY（ランダムな長い文字列）
- TikTok開発者ポータル側:
  - Redirect URI: `https://（WorkerのURL）/auth/callback`
  - Website URL: https://hsatou990-ship-it.github.io/become-studio/
  - プライバシーポリシー: .../privacy.html ／ 利用規約: .../terms.html
  - アイコン: icon-1024.png（1024×1024）
  - 製品: Login Kit、Display API、（任意）Content Posting API
  - スコープ: user.info.basic, user.info.profile, user.info.stats, video.list、（任意）video.upload

## 審査用の説明文（英語欄がある場合は、この内容を翻訳して使う。事実と異なる記載はしないこと）
- Login Kit: 利用者が自分のTikTokアカウントでログインし、アプリに連携を許可する。
- Display API / user.info.*: 利用者自身のプロフィールとフォロワー数などを表示し、成長の分析に使う。
- Display API / video.list: 利用者自身の公開動画の再生・いいね・コメント・シェア数を表示し、次回動画の企画提案に使う。
- Content Posting API / video.upload: 利用者が同意した場合に限り、アプリで作った動画をTikTokの下書きへ送る。利用者の操作なしの投稿はしない。
- デモ動画（最大5本・各50MB・実際のサイトのドメインを映す）: ログイン→許可→プロフィール表示→動画一覧→企画提案→（任意）下書き送信、を通しで画面録画する。
