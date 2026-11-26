# become.design/1 映像設計JSON 仕様（ChatGPT・Claude共通）

用途: 台本から映像設計を作り、CINEMATIC PRO（/exp/cinematic-pro/）の「外部AIの映像設計を取り込む」欄に貼り付けて取り込む。追加のAPI費用なし。
出力ルール: JSONのみ（説明文は不要。```json の囲みは受け付ける）。UTF-8。

## 1. 項目
最上位:
| 項目 | 必須 | 型・制限 |
|---|---|---|
| schema | 必須 | 文字列。必ず "become.design/1" |
| scenes | 必須 | 配列。1〜40件 |
| title | 任意 | 文字列 60字以内 |
| script | 任意 | 台本全文 2000字以内 |
| audience | 任意 | ターゲット 300字以内 |
| intent | 任意 | 制作意図 300字以内 |
| bgm | 任意 | {mood: dark-ambient / cinematic-rise / calm-piano / tense-pulse / warm-strings / silence, bpm: 40〜200} |
| narration | 任意 | {voice: 300字以内, pace: slow / normal / fast, tone: 300字以内} |
| ending | 任意 | {holdSec: 0.5〜4（既定1.8）, text: 80字以内} |
| qa | 任意 | 品質確認項目の文字列配列。10件・各100字以内 |
| color | 任意 | {mood: 300字以内}（現時点では記録のみ） |

scenes[] の各場面:
| 項目 | 必須 | 型・制限 |
|---|---|---|
| text | 必須 | 字幕兼ナレーション 80字以内 |
| dur | 必須 | 秒。1.2〜8 |
| start | 任意 | 開始秒（0〜90）。省略すると前の場面の直後。前の場面と重ならないこと |
| role | 任意（既定 build） | hook / build / low / turn / rise / climax / ending |
| emotion | 任意 | {valence: -1〜1, arousal: 0〜1} |
| camera | 任意（既定 drift-lateral） | push-in-slow / drift-lateral / handheld-sway / push-in-fast / pull-back-reveal / tilt-up / static-hold / parallax-drift |
| transition | 任意（既定 cut） | cut / dissolve / dip-black / flash-white（この場面の頭の切替） |
| speed | 任意（既定 normal） | normal / slow-motion / speed-ramp |
| kinetic | 任意（既定 none。fx に kinetic-typography があれば char） | none / char / track。char=1文字ずつ弾むように出現し強調語は拡大から収束、track=字間が広がりから収束。冒頭・転換・山場に限る |
| mask | 任意 | {type: none / iris / slit / wipe-up, dur: 0.3〜1.5秒（既定0.7）}。場面の頭で前の場面からマスクで開く（2場面目以降。山場・転換に限る）。fx に mask-reveal があれば iris |
| matchCut | 任意 | true で、その場面の開始カメラ位置・拡大を前の場面の終わりに連続させる（つなぎはカット）。fx に match-cut でも可。被写体の位置合わせは未実装 |
| parallax | 任意 | {layers: 1〜3}。前景の光の粒を奥行きごとに別速度で重ねる。fx に parallax-layers があれば2層 |
| grade | 任意（既定 muted-neutral） | cold-teal / warm-gold / muted-neutral |
| cut | 任意 | {type: none / j-cut / l-cut, offset: 0.1〜1秒（既定0.3）}。j-cut=映像が声より先に切替、l-cut=映像が遅れて切替 |
| emphasis | 任意 | text の一部をそのまま抜き出した文字列。4個以内・各20字以内 |
| search | 任意 | {queries: 英語の検索語 4個以内・各40字以内, avoid: 避ける語 4個以内, minHeight: 360〜4320（既定1080）} |
| sfx | 任意 | riser / sub / hit / whoosh / shimmer の配列 |
| fx | 任意 | kinetic-typography / parallax-layers / mask-reveal / match-cut / beat-sync-cut / live-anim-fusion の配列（4個以内）。live-anim-fusion 以外は完成動画に反映される（match-cut はカメラ連続のみの部分実装）。live-anim-fusion は設計メモ扱いで警告が出る |
| notes | 任意 | 300字以内の演出メモ |

## 2. 全体の制限
- 場面数 1〜40。合計の長さ（最後の場面の開始＋dur）は 90 秒以内。
- 余韻（ending.holdSec）が最後に付く。画面上の実際の動画長は合計＋余韻（最大90秒で打ち切り）。
- 文字列の `<` `>` と制御文字は自動で除去される。
- 未知の項目は警告のうえ無視される（エラーではない）。

## 3. 演出の実装状況
- color-grade: 実装済み
- camera-moves(8種): 実装済み
- transition(dip/flash/leak/endfade): 実装済み
- caption-emphasis: 実装済み
- sfx(5種): 実装済み
- speed-ramp: 実装済み（クリップ再生速度と模擬素材の時間を再マップ）
- slow-motion: 実装済み（0.5倍）
- j-cut: 実装済み（映像がナレーションより先に切替）
- l-cut: 実装済み（映像が遅れて切替）
- parallax-drift(カメラ): 近似のみ（平行移動。多層視差ではない）
- kinetic-typography: 実装済み（char=1文字ずつ出現＋強調語の拡大から収束 / track=字間が広がりから収束。fx に指定すると char）
- parallax-layers: 実装済み（前景の光の粒を1〜3層、奥行きごとに速度を変えて重ねる。映像そのものの多層分離ではない）
- mask-reveal: 実装済み（場面の頭で前の場面からマスク形状で開く。iris=円 / slit=横スリット / wipe-up=下から上）
- match-cut: 部分実装（その場面の開始カメラ位置・拡大を前の場面の終わりに連続させ、つなぎはカット。被写体の位置合わせ・形状一致は未実装）
- beat-sync-cut: 実装済み（bgm.bpm、またはBGM取り込みで検出した拍が必要。場面の切替を拍に最大0.3秒吸着、切替で軽いズーム。bpm指定のみの場合はBGMに拍の低音も追加。どちらも無い場合は警告して無効）
- live-anim-fusion: 設計のみ

fx のうち完成動画に反映されないのは live-anim-fusion のみ（警告が出る）。既存のJSON（新しい項目を使わないもの）は変更なしで同じように取り込める（互換）。

## 4. 検証器の仕様（exp/design/design.js の BSDesign.validate）
- 入力はJSON文字列かオブジェクト。```json の囲みと先頭のBOMは除去される。
- 戻り値 {ok, errors[], warnings[], plan}。errors が1件でもあれば ok=false で何も取り込まない（編集中の状態は変わらない）。
- 型違い、範囲外、列挙値外、文字数超過、場面数超過、合計長超過、場面の重なりはエラー。
- 強調語が text に含まれない場合は警告し、その語を無視する。
- eval・Function・innerHTML は使わない。取り込んだ文字列は textContent のみで表示する。

## 5. エラーが出たとき（ChatGPT・Claudeの修正方針）
- エラー文に項目名（例: scenes[2].dur）と許容範囲が出る。該当項目だけ直して全体を再出力する。
- 列挙値は上の一覧の英語表記をそのまま使う（日本語や別名は不可）。
- 合計が90秒を超える場合は、場面数か dur を減らす。
- 字幕が80字を超える場合は、場面を分割する。

## 6. 取り込めるサンプル（検証済み・22.2秒・6場面。sample.design.json と同じ）
```json
{
 "schema": "become.design/1",
 "title": "夜明け前の一歩",
 "script": "誰も見ていない朝。何度も失敗して、心が折れそうになる。それでも一歩だけ前へ。景色が変わり始める。",
 "audience": "20〜30代・努力が報われず悩む人",
 "intent": "孤独を否定せず、小さな一歩で希望を見せる",
 "scenes": [
  {
   "text": "誰も見ていない朝",
   "dur": 3,
   "role": "hook",
   "emotion": {
    "valence": -0.2,
    "arousal": 0.3
   },
   "camera": "push-in-slow",
   "transition": "cut",
   "speed": "normal",
   "grade": "cold-teal",
   "emphasis": [
    "誰も"
   ],
   "search": {
    "queries": [
     "dark room dawn window",
     "lonely desk night"
    ],
    "avoid": [
     "logo",
     "text"
    ],
    "minHeight": 1080
   },
   "sfx": [
    "riser"
   ]
  },
  {
   "text": "何度も失敗して",
   "dur": 3.2,
   "role": "low",
   "emotion": {
    "valence": -0.8,
    "arousal": 0.4
   },
   "camera": "static-hold",
   "transition": "dip-black",
   "speed": "normal",
   "grade": "cold-teal",
   "emphasis": [
    "失敗"
   ],
   "search": {
    "queries": [
     "rain window night"
    ]
   }
  },
  {
   "text": "心が折れそうになる",
   "dur": 3.2,
   "role": "low",
   "emotion": {
    "valence": -0.9,
    "arousal": 0.5
   },
   "camera": "handheld-sway",
   "transition": "cut",
   "speed": "slow-motion",
   "grade": "cold-teal",
   "search": {
    "queries": [
     "person sitting alone dark"
    ]
   }
  },
  {
   "text": "それでも一歩だけ前へ",
   "dur": 3.4,
   "role": "turn",
   "emotion": {
    "valence": 0.4,
    "arousal": 0.8
   },
   "camera": "push-in-fast",
   "transition": "flash-white",
   "speed": "speed-ramp",
   "grade": "warm-gold",
   "cut": {
    "type": "j-cut",
    "offset": 0.3
   },
   "emphasis": [
    "一歩"
   ],
   "search": {
    "queries": [
     "feet walking forward",
     "stairs climbing sunrise"
    ]
   },
   "sfx": [
    "hit"
   ]
  },
  {
   "text": "景色が変わり始める",
   "dur": 3.6,
   "role": "rise",
   "emotion": {
    "valence": 0.7,
    "arousal": 0.6
   },
   "camera": "pull-back-reveal",
   "transition": "dissolve",
   "speed": "normal",
   "grade": "warm-gold",
   "search": {
    "queries": [
     "sunrise mountain road"
    ]
   },
   "sfx": [
    "whoosh"
   ]
  },
  {
   "text": "君の朝が、始まる",
   "dur": 3.2,
   "role": "ending",
   "emotion": {
    "valence": 0.8,
    "arousal": 0.3
   },
   "camera": "static-hold",
   "transition": "dip-black",
   "speed": "slow-motion",
   "grade": "warm-gold",
   "cut": {
    "type": "l-cut",
    "offset": 0.3
   },
   "search": {
    "queries": [
     "golden light city morning"
    ]
   },
   "sfx": [
    "shimmer"
   ]
  }
 ],
 "bgm": {
  "mood": "cinematic-rise",
  "bpm": 72
 },
 "narration": {
  "voice": "低く落ち着いた声",
  "pace": "slow",
  "tone": "優しく力強い"
 },
 "ending": {
  "holdSec": 1.8,
  "text": ""
 },
 "qa": [
  "全場面80字以内",
  "合計90秒以内",
  "人物の顔が識別できる素材は孤独の場面で避ける"
 ]
}
```

## 6b. 新しい演出（kinetic・拍同期・mask・matchCut・parallax）を使うサンプル（sample2.design.json。検証済み）
```json
{
 "schema": "become.design/1",
 "title": "夜明け前の一歩",
 "script": "誰も見ていない朝。何度も失敗して、心が折れそうになる。それでも一歩だけ前へ。景色が変わり始める。",
 "audience": "20〜30代・努力が報われず悩む人",
 "intent": "孤独を否定せず、小さな一歩で希望を見せる",
 "scenes": [
  {
   "text": "誰も見ていない朝",
   "dur": 3,
   "role": "hook",
   "emotion": {
    "valence": -0.2,
    "arousal": 0.3
   },
   "camera": "push-in-slow",
   "transition": "cut",
   "speed": "normal",
   "grade": "cold-teal",
   "emphasis": [
    "誰も"
   ],
   "search": {
    "queries": [
     "dark room dawn window",
     "lonely desk night"
    ],
    "avoid": [
     "logo",
     "text"
    ],
    "minHeight": 1080
   },
   "sfx": [
    "riser"
   ],
   "kinetic": "track"
  },
  {
   "text": "何度も失敗して",
   "dur": 3.2,
   "role": "low",
   "emotion": {
    "valence": -0.8,
    "arousal": 0.4
   },
   "camera": "static-hold",
   "transition": "dip-black",
   "speed": "normal",
   "grade": "cold-teal",
   "emphasis": [
    "失敗"
   ],
   "search": {
    "queries": [
     "rain window night"
    ]
   }
  },
  {
   "text": "心が折れそうになる",
   "dur": 3.2,
   "role": "low",
   "emotion": {
    "valence": -0.9,
    "arousal": 0.5
   },
   "camera": "handheld-sway",
   "transition": "cut",
   "speed": "slow-motion",
   "grade": "cold-teal",
   "search": {
    "queries": [
     "person sitting alone dark"
    ]
   }
  },
  {
   "text": "それでも一歩だけ前へ",
   "dur": 3.4,
   "role": "turn",
   "emotion": {
    "valence": 0.4,
    "arousal": 0.8
   },
   "camera": "push-in-fast",
   "transition": "flash-white",
   "speed": "speed-ramp",
   "grade": "warm-gold",
   "cut": {
    "type": "j-cut",
    "offset": 0.3
   },
   "emphasis": [
    "一歩"
   ],
   "search": {
    "queries": [
     "feet walking forward",
     "stairs climbing sunrise"
    ]
   },
   "sfx": [
    "hit"
   ],
   "kinetic": "char",
   "fx": [
    "beat-sync-cut"
   ]
  },
  {
   "text": "景色が変わり始める",
   "dur": 3.6,
   "role": "rise",
   "emotion": {
    "valence": 0.7,
    "arousal": 0.6
   },
   "camera": "pull-back-reveal",
   "transition": "dissolve",
   "speed": "normal",
   "grade": "warm-gold",
   "search": {
    "queries": [
     "sunrise mountain road"
    ]
   },
   "sfx": [
    "whoosh"
   ],
   "fx": [
    "beat-sync-cut"
   ],
   "mask": {
    "type": "iris",
    "dur": 0.8
   },
   "parallax": {
    "layers": 2
   }
  },
  {
   "text": "君の朝が、始まる",
   "dur": 3.2,
   "role": "ending",
   "emotion": {
    "valence": 0.8,
    "arousal": 0.3
   },
   "camera": "static-hold",
   "transition": "dip-black",
   "speed": "slow-motion",
   "grade": "warm-gold",
   "cut": {
    "type": "l-cut",
    "offset": 0.3
   },
   "search": {
    "queries": [
     "golden light city morning"
    ]
   },
   "sfx": [
    "shimmer"
   ],
   "matchCut": true
  }
 ],
 "bgm": {
  "mood": "cinematic-rise",
  "bpm": 72
 },
 "narration": {
  "voice": "低く落ち着いた声",
  "pace": "slow",
  "tone": "優しく力強い"
 },
 "ending": {
  "holdSec": 1.8,
  "text": ""
 },
 "qa": [
  "全場面80字以内",
  "合計90秒以内",
  "人物の顔が識別できる素材は孤独の場面で避ける"
 ]
}
```

## 7. 設計のコツ（品質のために）
- 冒頭（hook）で引きを作り、中盤に低点（low）、転換（turn）、上昇（rise）、余韻のある結び（ending）で感情を変化させる。
- speed-ramp・slow-motion・j-cut・l-cut は山場・転換・結びに限り、1動画で多用しない。
- 同じ camera・transition を連続させない。
- mask は山場・転換に限り1〜2か所。matchCut は前後の場面の構図が似ている場合に使う。parallax は静かな場面の空気感づけに（多用しない）。
- BGM はJSONに書かず、CINEMATIC PRO の「BGM（自分の音源）」で取り込む（権利確認が必要）。取り込むと波形から拍・テンポ・盛り上がりを検出し、beat-sync-cut の吸着先になる。
- kinetic は冒頭・転換・山場に限り、全場面には使わない（読みづらくなる）。beat-sync-cut は感情の高まる2〜3か所に限る。bpm は BGM の雰囲気に合わせて 60〜120 程度。
- search.queries は英語で具体的に（被写体・場所・光・動き）。ロゴ・実在人物・著作物の指名は避ける。
- 実装済み・設計のみの区別、素材の権利確認、オーナーの最終承認は維持される。
