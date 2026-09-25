# 最初の10枚のイラスト（画風決め → 10枚）

SNSで最初に紹介する10枚（イエス・モーセ・パウロ・アブラハム・ダビデ・マリヤ・ペテロ・十字架・ノア・ヨセフ）の画像生成プロンプト。
ChatGPT（GPT Image）か Gemini（Nano Banana）に1枚ずつ貼って生成する。

## 手順
1. **画風を決める**：下の「イエス」を A・B・C の3画風で生成して見比べ、1つ選ぶ
2. **残り9枚**：選んだイエスの画像を添付して、「この画像と同じ画風・同じ光の表現で」と書き添えてから、各カードのプロンプトを貼る
3. **保存**：ダウンロードした画像を `art_inbox/` フォルダに、`<id>.png` の名前で入れる（例 `jesus-christ.png`）
4. **反映**：`python tools/import_art.py` → カードの絵柄が画像に替わる。動画も作り直すなら `python tools/import_art.py --videos`

## サイズ
- ☆以上・👑・ハイパーレア（全面アート）：**縦長 2:3（1024×1536）**。人物は画面の上半分、下の3分の1は文字が乗るので落ち着いた背景に
- 普通のカード（ノア・ヨセフ）：**横長 3:2（1536×1024）**。主役は中央
- 生成AIの画像に文字が入ったら作り直す（「文字・ロゴなし」を毎回入れる）

---

## 画風の候補（イエスで比較する）

### A. アニメTCG（明るいセル調・光の粒）　※ポケモンカード風に最も近い
```
Japanese trading card game illustration, vibrant anime cel-shaded style, luminous light particles, dynamic composition, rich detailed background, no text, no letters, no logos, no card frame
```
### B. 水彩の絵本風（やさしい・贈り物向き）
```
soft watercolor storybook illustration, gentle pastel palette, visible paper texture, warm light, delicate linework, no text, no letters, no logos, no card frame
```
### C. 重厚なファンタジー油彩（迫力・コレクター向き）
```
epic painterly fantasy card art, rich oil painting texture, dramatic cinematic lighting, golden highlights, highly detailed, no text, no letters, no logos, no card frame
```

---

## 各カードのプロンプト（末尾に選んだ画風の文を付ける）

### No.001 イエス・キリスト　`jesus-christ`　ハイパーレア・縦長 2:3
```
Jesus Christ standing on a hill at sunrise with arms gently open in welcome, kind and peaceful expression, white robe with a deep red mantle, radiant golden light and rays spreading behind him like a halo, a white dove descending from above, flower petals and light particles in the air, reverent and majestic mood, character in the upper half, lower third calm soft light, portrait 2:3
```

### No.012 モーセ　`moses`　☆☆・縦長 2:3
```
Moses, an elderly prophet with a long white beard, raising his wooden staff high as the Red Sea parts into two towering walls of glowing blue water, the people crossing on dry ground far below, strong wind, dramatic sky with a pillar of light, character in the upper half, lower third calm, portrait 2:3
```

### No.066 パウロ　`paul`　☆☆・縦長 2:3
```
the apostle Paul, a bearded man in a traveling cloak, holding a scroll and writing letters by lamplight, behind him a road to Damascus with a blinding light from heaven breaking through the clouds, maps and ships of his missionary journeys faintly in the sky, character in the upper half, lower third calm, portrait 2:3
```

### No.006 アブラハム　`abraham`　☆・縦長 2:3
```
Abraham, an old patriarch with a staff, standing outside his tent at night looking up in awe at a sky filled with countless brilliant stars forming a sweeping river of light, a ram nearby, desert hills, character in the upper half, lower third calm, portrait 2:3
```

### No.027 ダビデ　`david`　☆・縦長 2:3
```
young David, a shepherd boy with a leather sling, standing bravely on a rocky hill, a giant warrior's shadow in the distance, sheep behind him, a small harp at his side, golden morning light, determined hopeful face, character in the upper half, lower third calm, portrait 2:3
```

### No.045 マリヤ　`mary`　☆・縦長 2:3
```
Mary, a gentle young mother in a blue mantle, tenderly holding the newborn baby Jesus wrapped in white cloth, a single bright star shining above the stable, warm lantern light, soft golden glow, peaceful and holy mood, character in the upper half, lower third calm, portrait 2:3
```

### No.048 ペテロ　`peter`　☆・縦長 2:3
```
the apostle Peter, a strong bearded fisherman, standing in a wooden boat on the Sea of Galilee holding a fishing net full of fish, two golden keys glowing at his belt, waves and sunrise, a large rock on the shore, character in the upper half, lower third calm, portrait 2:3
```

### No.095 十字架　`the-cross`　👑・縦長 2:3（アイテム）
```
a simple wooden cross standing on a green hill at sunrise, brilliant rays of golden light spreading from behind it across the sky, lilies blooming at its base, clouds lit in gold and pink, sacred hopeful atmosphere, no people, cross in the upper half, lower third calm, portrait 2:3
```

### No.005 ノア　`noah`　◆◆◆◆・横長 3:2
```
Noah, an old bearded man, standing in front of his enormous wooden ark as animals walk up the ramp in pairs, a white dove with an olive branch flying above, a rainbow appearing in the clearing sky, landscape 3:2, subject centered
```

### No.011 ヨセフ　`joseph`　◆◆◆◆・横長 3:2
```
Joseph, a young man in a brilliantly colorful long-sleeved coat, standing before Egyptian pyramids and golden grain storehouses, dreamlike stars and sheaves of wheat glowing in the sky, confident gentle expression, landscape 3:2, subject centered
```

---
残り90枚のプロンプトは `card_art_prompts.md` にある（`python tools/build_cards.py` で自動生成）。
