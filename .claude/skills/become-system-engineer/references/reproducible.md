# Reproducible Engineering（開発環境の再現性。become-system-engineer の専門能力。独立スキルではない）

版: v0.1（2026-11-28）。必要なときだけ読む。

## 1. 目的
新しい環境（新しいクローン、新しいセッション）でも、過去の検証を再現できる状態を保つ。

## 2. 管理するもの
- テストコード: exp/cinematic-pro/tests（Git管理）。
- 試験素材: tests/make_fixtures.py が合成して作る（権利のある素材は使わない）。元の素材と同一ではなく、同じ構造の合成物。生成できない素材（vid、ns、dr、riko、am）を使う試験は、「環境不足」と報告され、合格に数えない。Rikoのオリジナル音声は、リポジトリに入れない（オーナー提供の別管理）。
- 依存関係と版: tests/ENV.md（Python、Playwright、numpy、Chrome、ffmpeg）。
- 実行条件: ローカルサーバ（ポート8765、リポジトリ直下）、ヘッドレスChrome、模擬の通信（実通信なし）。環境変数 BECOME_REPO（リポジトリの場所）、BECOME_FIX（試験素材の場所）。

## 3. 一括実行と判定
python3 exp/cinematic-pro/tests/run_all.py
- 判定は、終了コードと出力の両方。合格、失敗、異常終了（例外）、時間切れ、環境不足を区別する。
- 終了コード: 0=すべて合格、1=失敗・異常・時間切れあり、2=環境不足のみ。環境不足を合格と報告しない。
- 更新時のデータ保持の試験（tret.py）は、旧版を git worktree で用意し、同じオリジンから配信して行う。

## 4. 新規クローンからの復元手順
1. git clone でブランチ feature/auto-material を取得。
2. CLAUDE.md と .claude/DEVLOG.md を読む。
3. python3 exp/cinematic-pro/tests/make_fixtures.py
4. python3 exp/cinematic-pro/tests/run_all.py
5. 結果が DEVLOG の記録と一致するか確認する。環境不足の試験は、そのまま報告する。

## 5. 新しいセッションでのスキル発動確認
- 確認の方法: 新しいセッションで、依頼の例（動画の演出、不具合の修正、複数領域の依頼、セッションの再開）を出し、意図したスキルが選ばれて使われたかを、使われたスキルの記録で確認する。
- 現状: 未実施。保存されていることと、適切に使われていることは、別に評価する。結果は DEVLOG に記録する。

## 6. 品質ゲート
映像・音声の品質回帰試験と、台本入力から完成MP4保存までのE2E試験は、重要な品質ゲートとする（詳細は become-chief-orchestrator/references/quality-gate.md）。現状は未整備で、実機での15秒動画の完成と書き出しの後に整備する。
