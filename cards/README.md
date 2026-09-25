# みことばカード（聖書トレーディングカード100枚＋QR遷移先ページ）

QRを読むと、みことばの図版と朗読が流れるページ。アプリ不要・サーバー不要・配信は GitHub Pages（無料）。
方針：**第1弾は「図版＋朗読」のみ（費用ゼロ）**。3D AR は看板商品の限定版だけ。

## カードデザイン（全100枚・トレーディングカード風）
ポケモンカード風のレイアウトで、聖書の人物とアイテムを1枚ずつカードにした。傾き・光の反射・ホロ・キラ・裏返し・拡大表示つき。
- 人物カード 76枚（旧約43・新約33）：タイプ、HP、特性、わざ（エネルギーのコスト・威力・効果）、弱点・抵抗力・にげる、聖句
- アイテムカード 24枚：効果とルール、聖句（ノアの箱舟、十戒の石板、五つのパンと二匹の魚、十字架 など）
- タイプ：信仰・愛・知恵・力・預言・平和・光（＋無色）
- レアリティ：◆31 / ◆◆27 / ◆◆◆20 / ◆◆◆◆14 / ☆4 / ☆☆2 / 👑1（十字架）/ **ハイパーレア SSSSSSSSSSSSSSS（イエス・キリスト）**
- ☆以上は全面アート。ハイパーレアは虹色のプリズム枠
- 絵柄は、画像が無い間はカラー絵文字で表示。`images/<id>.webp` を置いて `python tools/build_cards.py` を再実行すると画像に替わる
- 画像生成プロンプトは `prompts/card_art_prompts.md`（100枚ぶん。build_cards.py が書き出す）

## イラストをそろえる
1. `prompts/top10_art.md` の手順で、イエスを3つの画風で生成して1つ選ぶ → 残り9枚（最初にSNSで出す10枚）
2. 画像を `art_inbox/` に `<id>.png` の名前で入れる（例 `jesus-christ.png`。番号や「 (1)」が付いていても可）
3. `python tools/import_art.py` → 縦横比を合わせて `images/<id>.webp` に変換し、カードに反映。`--videos` を付けるとSNS動画も作り直す
- 残り90枚のプロンプトは `prompts/card_art_prompts.md`

## SNSで反応を確かめる（Instagram リール / TikTok）
- 動画：`python tools/make_videos.py --top`（上位）／ `id` を並べて指定 ／ `--all`（100枚）→ `sns/videos/<番号>_<id>.mp4`（1080×1920・約8秒・音なし）
- 投稿予定と投稿文：`python tools/make_posts.py 2026-09-26` → `sns/schedule.csv`（100日分）、`sns/captions/`（1日ずつの投稿文）
- 記録：`sns/tracking.csv` に、再生数・いいね・保存・コメント・「欲しい」の数を毎日書きこむ（Excel で開ける。作り直しても上書きしない）
- 画面録画で自分で撮るなら `reel.html?v=<id>` を開く（8秒の動きをくり返す）

## ファイル
| ファイル | 役割 |
|---|---|
| `index.html` | QRの遷移先。パラメータ無しで100枚のコレクション、`?v=<id>` で1枚のページ（カード＋朗読＋黙想） |
| `cards.css` / `cards.js` | カード本体のデザインと3D演出（ばね：mass 1 / tension 170 / friction 26） |
| `verses.js` / `icons.js` | 自動生成データ。**直接編集しない** |
| `tools/build_cards.py` | 100枚の定義（人物・アイテム・わざ・聖句の出典・絵文字・画像プロンプト）→ verses.js / icons.js / prompts を生成 |
| `reel.html` | SNS用の縦長動画（1080×1920）の1コマを描くページ |
| `tools/make_videos.py` / `make_posts.py` / `import_art.py` | 動画の書き出し／投稿予定と投稿文／イラストの取りこみ |
| `print.html` | 印刷入稿用。1ページ＝1枚（100×148mm）のPDFを作る。裏面QR付きも可 |
| `ar.html` / `card.html` | 限定版の3D AR |
| `make_qr.py` | QRコードPNGを `qr/` に書き出す（print.html を使うなら不要） |
| `prompts/` | 図版生成プロンプト集 |
| `images/` `audio/` `video/` | `<id>.jpg` / `<id>.mp3` / `<id>.mp4` を置く |
| `ナレーター様向け企画説明.md` | ナレーター依頼書 |

## カードを直す・素材を足す
    python tools/build_cards.py
- 聖句本文は口語訳の全文データ（CC0、metastable-void/ja-colloquial）から機械的に抜き出す。手打ちしないので誤字が入らない
- 節をまたぐ引用の片側かぎ括弧は自動で補う／外す。文の途中で切れる節は範囲を広げて選んである
- images/ や audio/ にファイルを置いたら再実行（ページが「図版あり」「朗読あり」になる）

## 印刷（入稿PDF）
1. `python -m http.server 8000` → http://localhost:8000/print.html?back=1&base=<公開URL>
2. 印刷 → 送信先「PDFに保存」、用紙「100×148mm」、余白「なし」、「背景のグラフィック」オン
3. 塗り足しが必要な印刷所は `&bleed=3`（106×154mm）。特定のカードだけなら `&ids=john-3-16,john-11-25`
- ホロやキラは画面上の演出なので印刷には出ない（静止した絵になる）
- 裏面は「QR＋タイトル＋ひとこと」の案内面。郵便はがきとして投函するなら宛名面の規格に合わせて作り直す

## ローカル確認
    python -m http.server 8000
→ http://localhost:8000/ （100枚の一覧） / http://localhost:8000/?v=john-11-25 （1枚のページ）
ダブルクリックで開くと verses.js や音声の読み込みが拒否されるので、必ずこの方法で。
スマホ実機の確認（特にAR・カメラ）は https が必要なので GitHub Pages に置く。

## 公開手順（GitHub Pages）
1. https://github.com/new で Owner `bibletechdev`、名前 `mikotoba-postcard`、Public、README なしで作成
2. `git push -u origin main`（remote は設定済み）
3. リポジトリの Settings → Pages → Branch: `main` / `(root)` → 数分で https://bibletechdev.github.io/mikotoba-postcard/ に公開
4. QR は `print.html?back=1&base=https://bibletechdev.github.io/mikotoba-postcard/` の裏面に入る

## 制作の流れ（1節あたり）
1. 図版：Nano Banana（Gemini 2.5 Flash Image）で文字なし図版 → Canva で聖句を重ねる → `images/<id>.jpg`
2. 朗読：ナレーターのドライ音源 ＋ Suno の BGM を CapCut/Audacity でミックス → `audio/<id>.mp3`（黙想文は verses.js の下書きを整えて渡す）
3. （任意）動画：図版を CapCut でケンバーンズ＋光の粒子 → `video/<id>.mp4`（10MB以下）
4. push → QR を読んで実機確認

## 3Dモデルの作り方（限定版のみ）
- Meshy (meshy.ai) : "golden cross on a small stone base, low poly, clean" 等 → GLBでダウンロード
- 5MB以下に抑える。Meshyの「Remesh」でポリゴンを減らす。iPhoneのQuick Look用USDZは model-viewer が自動変換。

## 聖書本文の著作権
口語訳（1955年）は保護期間満了で自由に使える。新改訳2017・聖書協会共同訳・新共同訳は許諾が必要。
