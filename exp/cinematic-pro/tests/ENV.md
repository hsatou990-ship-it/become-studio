# 試験環境の版（2026-11-28 時点で動作を確認した組み合わせ）
- Python 3.13.18
- Playwright（Python）1.63.0
- numpy 2.5.3
- Google Chrome for Testing 153.0.8010.12（--headless=new、swiftshader）
- ffmpeg 6.1.1
- OS: Linux（コンテナ）
外部の通信は行わない（pixabay の応答は、すべて模擬）。ブラウザは Playwright から /usr/bin/google-chrome を指定して起動する。
