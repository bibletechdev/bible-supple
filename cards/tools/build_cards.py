"""みことばカード（トレーディングカード風・全100枚）のデータを生成する。

  人物カード 75枚 ／ アイテムカード 24枚 ／ イエス・キリスト（ハイパーレア SSSSSSSSSSSSSSS）1枚

聖句（フレーバーテキスト）は口語訳（新約1954・旧約1955、パブリックドメイン）の全文データから機械的に抜き出す。
  データ: https://github.com/metastable-void/ja-colloquial （CC0） → tools/cache/books.jsonl に自動ダウンロード
アイコン: Lucide (ISC) → tools/cache/icons/ に自動ダウンロード。

使い方:  python tools/build_cards.py
  images/<id>.webp|jpg|png を置くと、そのカードの絵柄が絵文字から画像に替わる（置いたら再実行）。
  audio/<id>.mp3 を置くと朗読ボタンが有効になる。
  prompts/card_art_prompts.md に、100枚ぶんの画像生成プロンプトを書き出す。
"""
import json, os, re, sys, urllib.request
from collections import Counter

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", "cache")
BOOKS_URL = "https://raw.githubusercontent.com/metastable-void/ja-colloquial/main/books.jsonl"
ICON_URL  = "https://cdn.jsdelivr.net/npm/lucide-static@0.460.0/icons/{}.svg"

BOOK = {  # データの書名コード → 表示名
    "ge": "創世記", "exo": "出エジプト記", "num": "民数記", "josh": "ヨシュア記", "jdgs": "士師記", "ruth": "ルツ記",
    "1sm": "サムエル記上", "1ki": "列王紀上", "2ki": "列王紀下", "ezra": "エズラ記", "neh": "ネヘミヤ記", "est": "エステル記",
    "job": "ヨブ記", "isa": "イザヤ書", "jer": "エレミヤ書", "eze": "エゼキエル書", "dan": "ダニエル書", "jonah": "ヨナ書",
    "mat": "マタイによる福音書", "mark": "マルコによる福音書", "luke": "ルカによる福音書", "john": "ヨハネによる福音書",
    "acts": "使徒行伝", "rom": "ローマ人への手紙", "1cor": "コリント人への第一の手紙", "eph": "エペソ人への手紙",
    "phi": "ピリピ人への手紙", "1tim": "テモテへの第一の手紙", "1jn": "ヨハネの第一の手紙",
}

# タイプ（エネルギー）: 記号 → (キー, 名前, 色1, 色2, アイコン)
TYPES = {
    "F": ("faith",    "信仰", "#f3c64a", "#b9811a", "x-cross"),
    "L": ("love",     "愛",   "#ff7a93", "#d23457", "heart"),
    "W": ("wisdom",   "知恵", "#6fb2ff", "#2b64c8", "book-open"),
    "P": ("power",    "力",   "#ff9a52", "#c44f1a", "flame"),
    "R": ("prophecy", "預言", "#c49bff", "#7440c8", "eye"),
    "H": ("peace",    "平和", "#7fe0a6", "#23945a", "bird"),
    "S": ("light",    "光",   "#fff6c9", "#f0b93a", "sun"),
    "C": ("normal",   "無色", "#f2f0ea", "#a9a39a", "star"),
}
WEAK   = {"F": "P", "L": "W", "W": "R", "P": "F", "R": "L", "H": "P", "S": None}
RESIST = {"F": "R", "L": "P", "W": "L", "P": "H", "R": "W", "H": "F", "S": None}

# ── 人物カード ──
# (id, 名前, 時代, タイプ, HP, レア, 絵文字, 聖句(書,章,節,節), [わざ(名前, コスト, 威力, 効果)], 説明, 画像の説明)
# レア: d1=◆ d2=◆◆ d3=◆◆◆ d4=◆◆◆◆ s1=☆ s2=☆☆ cr=👑 hr=ハイパーレア
P = [
    ("adam", "アダム", "旧約", "H", 60, "d1", "🍎🌳", ("ge", 2, 7, 7),
     [("名づけ", "C", 10, "山札の上から1枚見て、好きな方に戻す。")], "神が土のちりから造った、最初の人。", "the first man in a lush garden of Eden, naming animals"),
    ("eve", "エバ", "旧約", "L", 60, "d1", "🍎🐍", ("ge", 3, 20, 20),
     [("いのちの母", "LC", 30, "自分の人物を1匹選び、HPを20回復する。")], "すべて生きた者の母。", "the first woman in the garden of Eden with a glowing apple tree"),
    ("abel", "アベル", "旧約", "F", 50, "d1", "🐑🔥", ("ge", 4, 4, 4),
     [("最良のささげもの", "F", 20, "")], "羊を飼う者。いちばん良いものを神にささげた。", "a young shepherd offering a lamb on a stone altar"),
    ("noah", "ノア", "旧約", "F", 130, "d4", "🚢🕊️", ("ge", 6, 22, 22),
     [("箱舟をつくる", "FC", 40, "次の相手の番、このカードが受けるダメージは50少なくなる。"),
      ("大洪水", "FFCC", 120, "")], "神の言葉どおりに箱舟を造った正しい人。", "an old bearded man with his great wooden ark and a dove, rainbow sky"),
    ("abraham", "アブラハム", "旧約", "F", 150, "s1", "⭐🐏", ("ge", 15, 6, 6),
     [("星をかぞえよ", "F", 0, "山札から好きなカードを1枚、手札に加える。"),
      ("信仰の父", "FFC", 130, "自分の場の「信仰」の人物の数×10ダメージ追加。")], "信仰の父。数えきれない星のような子孫を約束された。", "an old patriarch under a sky full of countless stars, with a ram"),
    ("sarah", "サラ", "旧約", "L", 80, "d2", "👶😄", ("ge", 21, 6, 6),
     [("約束の子", "L", 0, "山札から「イサク」を1枚、場に出す。"), ("笑い", "LC", 40, "")], "年老いてから、約束の子イサクを産んだ。", "an elderly woman laughing with joy holding a newborn baby"),
    ("isaac", "イサク", "旧約", "H", 90, "d2", "🐏🪵", ("ge", 22, 8, 8),
     [("神が備える", "HC", 50, "自分の手札を1枚、山札に戻してよい。")], "神が備えてくださることを、身をもって知った子。", "a young man carrying firewood up a mountain at dawn, a ram in a thicket"),
    ("rebekah", "リベカ", "旧約", "L", 70, "d1", "🏺🐫", ("ge", 24, 18, 18),
     [("らくだに水を", "LC", 30, "自分の人物1匹のHPを30回復する。")], "旅人とらくだに進んで水を飲ませた、やさしい娘。", "a young woman at a well giving water to camels, desert sunset"),
    ("jacob", "ヤコブ", "旧約", "P", 110, "d3", "🪜✨", ("ge", 28, 12, 12),
     [("天のはしご", "C", 0, "山札の上から3枚見て、1枚を手札に加える。"), ("夜明けまで組み打ち", "PPC", 90, "")], "天使と組み打ちして、イスラエルという名を受けた。", "a man sleeping on a stone pillow dreaming of a glowing ladder to heaven with angels"),
    ("joseph", "ヨセフ", "旧約", "W", 120, "d4", "🧥🌈", ("ge", 50, 20, 20),
     [("夢の解きあかし", "W", 0, "相手の手札を見る。"), ("悪を善に", "WWC", 100, "このカードにダメージがのっているなら、30ダメージ追加。")], "兄たちに売られても、神は悪を善に変えられた。", "a young man in a colorful coat standing before Egyptian pyramids, dreams of stars"),
    ("moses", "モーセ", "旧約", "R", 160, "s2", "🌊📜", ("exo", 14, 21, 21),
     [("燃える柴の召し", "R", 0, "山札から「十戒の石板」を1枚、手札に加える。"), ("紅海をわける", "RRCC", 160, "相手のベンチの人物すべてにも、20ダメージずつ。")], "神の民をエジプトから導き出した預言者。", "a prophet with a staff raised, parting a towering red sea with walls of water"),
    ("aaron", "アロン", "旧約", "F", 90, "d2", "🪄🌸", ("num", 17, 8, 8),
     [("芽吹いた杖", "FC", 40, "自分の人物1匹のHPを30回復する。")], "モーセの兄。その杖は一夜で花を咲かせた。", "a high priest in ornate robes holding a staff blooming with almond blossoms"),
    ("miriam", "ミリアム", "旧約", "L", 70, "d1", "🥁💃", ("exo", 15, 20, 20),
     [("鼓の賛美", "L", 20, "自分の人物すべてのHPを10回復する。")], "海を渡ったあと、鼓を手に神をたたえた。", "a joyful woman dancing with a tambourine by the sea shore"),
    ("joshua", "ヨシュア", "旧約", "P", 130, "d3", "🎺🧱", ("josh", 1, 9, 9),
     [("強く、雄々しくあれ", "P", 20, "次の自分の番、わざのダメージを30増やす。"), ("エリコの城壁", "PPC", 110, "")], "モーセの後をつぎ、民を約束の地へ導いた。", "a brave commander with trumpeters as the walls of Jericho crumble"),
    ("rahab", "ラハブ", "旧約", "F", 70, "d2", "🧵🔴", ("josh", 2, 21, 21),
     [("赤いひも", "FC", 30, "次の相手の番、このカードはきぜつしない（HP10で残る）。")], "偵察に来た者をかくまい、信仰によって救われた。", "a woman tying a scarlet cord from a window in a stone city wall"),
    ("gideon", "ギデオン", "旧約", "P", 100, "d3", "🏺🔥", ("jdgs", 6, 12, 12),
     [("300人の勇士", "PC", 30, "コインを3回投げ、オモテの数×30ダメージ追加。")], "わずか300人で大軍に勝った、臆病だった勇士。", "a young warrior holding a torch and a clay jar at night, 300 torches behind"),
    ("deborah", "デボラ", "旧約", "W", 90, "d2", "🌴⚖️", ("jdgs", 4, 4, 4),
     [("しゅろの木の裁き", "WC", 40, "相手はエネルギーを1つトラッシュする。")], "しゅろの木の下で民を裁いた女預言者。", "a wise woman judge sitting under a palm tree, people gathering"),
    ("samson", "サムソン", "旧約", "P", 150, "d4", "💪🦁", ("jdgs", 16, 28, 28),
     [("獅子を裂く", "PC", 60, ""), ("柱をおし倒す", "PPPC", 180, "このカードにも50ダメージ。")], "神から怪力を与えられたナジル人。", "a mighty long-haired strongman pushing apart two great stone pillars"),
    ("ruth", "ルツ", "旧約", "L", 80, "d2", "🌾💛", ("ruth", 1, 16, 16),
     [("あなたの神はわたしの神", "LC", 40, "自分のベンチの人物と入れ替えてよい。")], "しゅうとめを見捨てず、共に歩んだ異邦の女。", "a gentle young woman gleaning golden barley in a field"),
    ("naomi", "ナオミ", "旧約", "H", 70, "d1", "🌾🏠", ("ruth", 4, 14, 14),
     [("帰郷", "H", 10, "トラッシュからカードを1枚、手札に戻す。")], "悲しみの中から、神の祝福を受けたしゅうとめ。", "an elderly woman returning home holding a baby, warm village light"),
    ("boaz", "ボアズ", "旧約", "H", 90, "d1", "🌾🤲", ("ruth", 2, 12, 12),
     [("落ち穂を残す", "HC", 30, "相手の手札が3枚以下なら、自分は1枚引く。")], "落ち穂を拾うルツを守った、情けある地主。", "a kind landowner in a barley field at harvest time"),
    ("caleb", "カレブ", "旧約", "P", 90, "d1", "⛰️🍇", ("num", 13, 30, 30),
     [("約束の地の房", "PC", 40, "")], "巨人を恐れず、約束の地は取れると言った勇士。", "a scout carrying a huge cluster of grapes on a pole, mountains behind"),
    ("hannah", "ハンナ", "旧約", "F", 70, "d1", "🙏👶", ("1sm", 1, 27, 27),
     [("心を注いだ祈り", "F", 0, "山札から「サムエル」を1枚、手札に加える。")], "涙の祈りが聞かれ、サムエルを授かった母。", "a woman praying earnestly in a temple with lamplight"),
    ("samuel", "サムエル", "旧約", "R", 110, "d3", "👂🕯️", ("1sm", 3, 10, 10),
     [("しもべは聞きます", "R", 0, "山札の上から3枚を好きな順に並べかえる。"), ("王に油を注ぐ", "RRC", 80, "")], "幼い日に神の呼ぶ声を聞いた預言者。", "a young boy in a temple at night listening, a lamp glowing"),
    ("saul", "サウル", "旧約", "P", 120, "d2", "👑⚔️", ("1sm", 9, 2, 2),
     [("王の槍", "PPC", 80, "コインを投げウラなら、このカードにも20ダメージ。")], "イスラエル最初の王。人よりも肩から上だけ高かった。", "a tall first king of Israel in armor holding a spear"),
    ("david", "ダビデ", "旧約", "P", 150, "s1", "🪨👑", ("1sm", 17, 45, 45),
     [("羊飼いの竪琴", "C", 0, "自分の人物すべてのHPを20回復する。"), ("万軍の主の名によって", "PPC", 120, "相手が「ゴリアテ」なら、120ダメージ追加。")], "石投げひとつで巨人に立ち向かった、羊飼いの王。", "a young shepherd boy with a sling facing a giant, later a king with a harp"),
    ("jonathan", "ヨナタン", "旧約", "L", 90, "d2", "🏹🤝", ("1sm", 18, 1, 1),
     [("友の契り", "LC", 30, "自分のベンチの人物1匹のHPを50回復する。")], "ダビデを自分のように愛した王子。", "a prince handing his bow and robe to his friend in friendship"),
    ("goliath", "ゴリアテ", "旧約", "P", 190, "d3", "🗡️🛡️", ("1sm", 17, 4, 4),
     [("巨人のあざけり", "C", 0, "相手の手札を1枚、ランダムにトラッシュする。"), ("青銅のやり", "PPPC", 160, "")], "身の丈六キュビトの巨人。弱点は「石投げ」。", "a towering giant warrior in bronze armor with a huge spear"),
    ("solomon", "ソロモン", "旧約", "W", 140, "d4", "👑📜", ("1ki", 3, 9, 9),
     [("聞きわける心", "W", 0, "相手の山札の上から2枚を見て、好きな順に戻す。"), ("栄華の極み", "WWC", 110, "")], "知恵を求め、神から知恵と富を与えられた王。", "a wise king on a golden throne with scrolls, magnificent temple behind"),
    ("sheba", "シバの女王", "旧約", "W", 90, "d2", "💎🐪", ("1ki", 10, 1, 1),
     [("難問をたずねる", "WC", 30, "相手はカードを1枚えらんで山札の下に戻す。")], "ソロモンの知恵を確かめに、遠くから来た女王。", "a regal queen arriving with a caravan of camels and jewels"),
    ("elijah", "エリヤ", "旧約", "R", 140, "d4", "🔥🐦", ("1ki", 18, 38, 38),
     [("からすに養われる", "R", 0, "自分は2枚引く。"), ("天からの火", "RRCC", 150, "")], "天から火を呼び下し、火の車で天に上った預言者。", "a fiery prophet calling down fire from heaven onto an altar, chariot of fire"),
    ("elisha", "エリシャ", "旧約", "R", 110, "d3", "🫗🧥", ("2ki", 2, 9, 9),
     [("倍の霊", "RC", 30, "相手の場に「預言」の人物がいれば、60ダメージ追加。")], "エリヤの外套を受けつぎ、多くの奇跡を行った。", "a prophet catching a falling mantle as a fiery chariot rises"),
    ("jonah", "ヨナ", "旧約", "R", 100, "d3", "🐋🌊", ("jonah", 1, 17, 17),
     [("大きな魚のおなか", "C", 0, "このカードをベンチの人物と入れ替える。"), ("ニネベへの叫び", "RC", 70, "")], "逃げても、大きな魚にのまれても、神に呼び戻された。", "a man inside the belly of a giant whale praying, underwater light"),
    ("isaiah", "イザヤ", "旧約", "R", 110, "d3", "📜🔥", ("isa", 6, 8, 8),
     [("ここにわたしがおります", "R", 0, "山札から「預言」エネルギーを1枚つける。"), ("救い主の預言", "RRC", 90, "")], "救い主の来られることを告げた大預言者。", "a prophet before the heavenly throne with seraphim and a burning coal"),
    ("jeremiah", "エレミヤ", "旧約", "R", 100, "d2", "😢🏺", ("jer", 29, 11, 11),
     [("涙の預言", "RC", 40, "このカードにダメージがのっているなら、40ダメージ追加。")], "涙の預言者。それでも、平安と希望の計画を告げた。", "a weeping prophet holding a clay pot, ruined city at dusk"),
    ("ezekiel", "エゼキエル", "旧約", "R", 100, "d2", "🦴💨", ("eze", 37, 5, 5),
     [("枯れた骨よ、生きよ", "RC", 20, "トラッシュから人物を1枚、ベンチに出す。")], "枯れた骨の谷が、生き返る幻を見た預言者。", "a prophet in a valley of dry bones as wind breathes life into them"),
    ("daniel", "ダニエル", "旧約", "W", 130, "d4", "🦁🙏", ("dan", 6, 22, 22),
     [("日に三度の祈り", "W", 0, "このカードのHPを40回復する。"), ("獅子の穴", "WWC", 100, "このわざを使った次の相手の番、このカードはダメージを受けない。")], "獅子の穴に投げこまれても、神に守られた。", "a calm young man praying in a den of peaceful lions"),
    ("three-friends", "三人の若者", "旧約", "F", 120, "d3", "🔥🔥", ("dan", 3, 17, 17),
     [("燃える炉", "FFC", 90, "このカードは「やけど」にならない。")], "シャデラク、メシャク、アベデネゴ。炉の中でも焼けなかった。", "three young men standing unharmed in a blazing furnace with a fourth radiant figure"),
    ("esther", "エステル", "旧約", "L", 110, "d4", "👑💐", ("est", 4, 14, 14),
     [("この時のため", "L", 0, "自分の手札を全部山札に戻し、5枚引く。"), ("民のとりなし", "LLC", 100, "")], "命をかけて王に願い、民を救った王妃。", "a brave queen in royal robes approaching a king's throne"),
    ("mordecai", "モルデカイ", "旧約", "W", 80, "d1", "📜🐎", ("est", 10, 3, 3),
     [("王の書のしるし", "WC", 30, "")], "エステルを育て、民のために知恵を尽くした人。", "a wise man in royal robes riding a white horse through a city"),
    ("job", "ヨブ", "旧約", "F", 130, "d3", "🙏⛈️", ("job", 1, 21, 21),
     [("忍耐", "FC", 30, "このカードのHPが半分以下なら、90ダメージ追加。")], "すべてを失っても、神をほめたたえた。", "a man kneeling in prayer on ashes under a storm, light breaking through"),
    ("nehemiah", "ネヘミヤ", "旧約", "P", 90, "d1", "🧱🔨", ("neh", 8, 10, 10),
     [("城壁の再建", "PC", 30, "次の相手の番、このカードが受けるダメージは30少なくなる。")], "エルサレムの城壁を52日で建て直した。", "a leader rebuilding stone city walls with workers holding tools and swords"),
    ("ezra", "エズラ", "旧約", "W", 80, "d1", "📜✍️", ("ezra", 7, 10, 10),
     [("律法の朗読", "W", 20, "自分は1枚引く。")], "神の律法を学び、行い、教えた学者。", "a scribe reading a large scroll aloud to a crowd at dawn"),
    # ── 新約 ──
    ("mary", "マリヤ", "新約", "L", 130, "s1", "👶⭐", ("luke", 1, 38, 38),
     [("お言葉どおりに", "L", 0, "山札から好きなカードを1枚、手札に加える。"), ("マリヤの賛歌", "LLC", 100, "自分の人物すべてのHPを20回復する。")], "救い主の母となった、主のはしため。", "a gentle young mother holding a newborn baby under a bright star"),
    ("joseph-carpenter", "大工ヨセフ", "新約", "H", 90, "d2", "🪚🏠", ("mat", 1, 24, 24),
     [("夢のお告げ", "H", 0, "このカードをベンチの人物と入れ替える。"), ("家族を守る", "HC", 40, "")], "夢のお告げに従い、マリヤと幼子を守った。", "a humble carpenter protecting his wife and baby on a journey by night"),
    ("john-baptist", "バプテスマのヨハネ", "新約", "R", 130, "d4", "💧🦗", ("john", 1, 29, 29),
     [("荒野の叫び", "R", 20, "山札から「イエス・キリスト」を1枚、手札に加えてよい。"), ("悔い改めのバプテスマ", "RRC", 100, "")], "「見よ、神の小羊」と救い主を指さした。", "a rugged prophet in camel hair baptizing in the Jordan river"),
    ("peter", "ペテロ", "新約", "F", 150, "s1", "🎣🔑", ("mat", 16, 16, 16),
     [("人間をとる漁師", "C", 20, "山札から人物を1枚、ベンチに出す。"), ("岩の上に", "FFC", 130, "")], "「あなたこそ、生ける神の子キリストです」と告白した。", "a sturdy fisherman apostle holding keys, boat and nets on the sea of Galilee"),
    ("andrew", "アンデレ", "新約", "F", 80, "d1", "🐟🎣", ("john", 1, 41, 41),
     [("メシヤに会った", "F", 0, "山札から「ペテロ」を1枚、手札に加える。")], "兄ペテロを、イエスのもとへ連れていった。", "a fisherman pointing the way along the lakeshore at sunrise"),
    ("james", "使徒ヤコブ", "新約", "P", 90, "d1", "⚡🎣", ("mark", 3, 17, 17),
     [("雷の子", "PC", 40, "")], "「雷の子」と呼ばれた、熱い心の使徒。", "a fiery apostle with a lightning-lit sky over fishing boats"),
    ("john-apostle", "使徒ヨハネ", "新約", "L", 120, "d3", "❤️📜", ("1jn", 4, 7, 7),
     [("愛し合おう", "L", 0, "自分の人物すべてのHPを20回復する。"), ("黙示の幻", "LLC", 90, "")], "イエスに愛された弟子。愛の手紙を書いた。", "a young apostle writing a scroll by lamplight, visions of heaven"),
    ("matthew", "マタイ", "新約", "W", 80, "d2", "💰📖", ("mat", 9, 9, 9),
     [("収税所を立つ", "W", 0, "自分の手札を2枚トラッシュし、3枚引く。"), ("福音の記録", "WC", 40, "")], "取税人から弟子になり、福音書を書いた。", "a tax collector leaving his coins at a table to follow, holding a book"),
    ("thomas", "トマス", "新約", "W", 80, "d2", "✋👀", ("john", 20, 28, 28),
     [("わが主よ、わが神よ", "WC", 50, "コインを投げオモテなら、50ダメージ追加。")], "見て、触れて、そして誰よりも深く告白した。", "an apostle reaching out his hand in awe toward a radiant light"),
    ("philip", "ピリポ", "新約", "W", 70, "d1", "🍞❓", ("john", 14, 8, 8),
     [("来て、見なさい", "C", 10, "相手の手札を1枚見る。")], "「来て、見なさい」と友を誘った弟子。", "an apostle calling a friend under a fig tree, pointing the way"),
    ("nathanael", "ナタナエル", "新約", "H", 70, "d1", "🌳👁️", ("john", 1, 47, 47),
     [("いちじくの木の下で", "HC", 30, "")], "偽りのないイスラエル人、とイエスに言われた。", "a thoughtful man sitting under a fig tree"),
    ("mary-magdalene", "マグダラのマリヤ", "新約", "L", 110, "d3", "🌸🌅", ("john", 20, 18, 18),
     [("わたしは主を見ました", "L", 0, "トラッシュから人物を1枚、手札に戻す。"), ("復活の知らせ", "LLC", 90, "")], "よみがえりのイエスに、最初に会った女性。", "a woman at an empty tomb at sunrise with flowers, amazed and joyful"),
    ("martha", "マルタ", "新約", "H", 80, "d1", "🍲🏠", ("luke", 10, 41, 41),
     [("おもてなし", "HC", 30, "自分の人物1匹のHPを30回復する。")], "心をこめてイエスをもてなした姉。", "a busy woman preparing food in a warm home kitchen"),
    ("mary-bethany", "ベタニヤのマリヤ", "新約", "L", 80, "d1", "🏺💐", ("luke", 10, 39, 39),
     [("主の足もとで", "L", 0, "自分は2枚引く。")], "イエスの足もとに座り、みことばに聞き入った。", "a young woman sitting at the feet of a teacher, listening peacefully"),
    ("lazarus", "ラザロ", "新約", "F", 100, "d2", "🪦✨", ("john", 11, 43, 43),
     [("ラザロよ、出てきなさい", "FC", 40, "このカードがきぜつしたとき、1回だけHP50でベンチに戻る。")], "死んで四日たってから、よみがえらされた。", "a man walking out of a rock tomb wrapped in linen, light pouring in"),
    ("zacchaeus", "ザアカイ", "新約", "H", 70, "d2", "🌳💰", ("luke", 19, 5, 5),
     [("いちじく桑の木に登る", "C", 0, "山札の上から3枚見て、1枚を手札に加える。"), ("四倍にして返す", "HC", 40, "")], "背の低い取税人。木に登ってイエスを見ようとした。", "a short tax collector in a sycamore tree smiling as a crowd passes below"),
    ("nicodemus", "ニコデモ", "新約", "W", 80, "d1", "🌙📜", ("john", 3, 4, 4),
     [("夜の問い", "WC", 30, "相手の手札を見る。")], "夜にイエスをたずね、新しく生まれることを聞いた。", "a scholar visiting at night under the moon, holding a lamp"),
    ("samaritan-woman", "サマリヤの女", "新約", "L", 70, "d1", "💧🏺", ("john", 4, 14, 14),
     [("生ける水", "L", 20, "自分の人物1匹のHPを20回復する。")], "井戸のそばで、永遠の命の水の話を聞いた。", "a woman with a water jar at a well at noon, warm light"),
    ("centurion", "百卒長", "新約", "F", 100, "d2", "🛡️🙏", ("mat", 8, 8, 8),
     [("お言葉だけで", "FC", 50, "このわざは、相手のベンチの人物にも使える。")], "「ただお言葉をください」と言った、信仰の軍人。", "a Roman centurion in armor kneeling humbly with faith"),
    ("prodigal-son", "放蕩息子", "新約", "L", 70, "d1", "🐖🏠", ("luke", 15, 20, 20),
     [("父のもとへ帰る", "L", 0, "このカードのHPをすべて回復する。")], "遠く離れていても、父は走り寄って抱きしめた。", "a ragged young man running into the embrace of his father at a farm gate"),
    ("good-samaritan", "良きサマリヤ人", "新約", "L", 100, "d2", "🩹🐴", ("luke", 10, 33, 34),
     [("隣り人になる", "LC", 30, "相手の人物1匹と自分の人物1匹のHPを、それぞれ40回復する。")], "倒れた旅人を助けた、本当の隣り人。", "a traveler bandaging a wounded man on a roadside with a donkey"),
    ("paul", "パウロ", "新約", "W", 160, "s2", "✉️⚡", ("phi", 3, 14, 14),
     [("ダマスコの光", "C", 0, "山札から「知恵」エネルギーを2枚つける。"), ("異邦人への手紙", "WWCC", 150, "自分のトラッシュのアイテム1枚につき10ダメージ追加。")], "迫害者から使徒になり、地の果てまで福音を伝えた。", "an apostle writing letters by lamplight, a road with a blinding light from heaven"),
    ("barnabas", "バルナバ", "新約", "H", 90, "d2", "🤝🌿", ("acts", 11, 24, 24),
     [("慰めの子", "H", 0, "自分の人物1匹のHPを50回復する。"), ("共に旅する", "HC", 30, "")], "「慰めの子」。人を励まし、つなぐ人。", "a kind apostle with a warm smile encouraging a younger man"),
    ("stephen", "ステパノ", "新約", "F", 110, "d3", "🪨✨", ("acts", 7, 60, 60),
     [("天が開ける", "FFC", 90, "このカードがきぜつしたとき、自分は3枚引く。")], "最後まで人のゆるしを祈った、最初の殉教者。", "a radiant young man looking up to an opened heaven full of light"),
    ("timothy", "テモテ", "新約", "F", 70, "d1", "📜🌱", ("1tim", 4, 12, 12),
     [("若さをあなどらせるな", "F", 20, "")], "パウロの若い同労者。信仰の手本となった。", "a young pastor reading a letter, a sprouting plant beside him"),
    ("lydia", "ルデヤ", "新約", "L", 70, "d1", "🟣🧵", ("acts", 16, 14, 14),
     [("紫布の家", "LC", 20, "自分は1枚引く。")], "紫布の商人。心を開かれて、家族と共に信じた。", "a merchant woman with rich purple fabrics by a riverside prayer place"),
    ("priscilla", "プリスキラ", "新約", "H", 80, "d1", "⛺🧵", ("rom", 16, 3, 3),
     [("天幕づくり", "HC", 30, "")], "夫アクラと天幕をつくり、教会を支えた。", "a married couple sewing tents together in a workshop"),
    ("simeon", "シメオン", "新約", "R", 80, "d1", "👶🕊️", ("luke", 2, 30, 30),
     [("救いを見た", "R", 0, "山札から「イエス・キリスト」を1枚、手札に加えてよい。")], "幼子イエスを抱き、救いを見たと賛美した老人。", "an old man in the temple holding a baby with joyful tears, a dove above"),
    ("anna", "アンナ", "新約", "R", 70, "d1", "🙏🕯️", ("luke", 2, 38, 38),
     [("夜も昼も", "R", 10, "自分は1枚引く。")], "宮を離れず、祈りと断食で仕えた女預言者。", "an elderly prophetess praying in the temple by candlelight"),
    ("magi", "東の博士", "新約", "W", 110, "d3", "⭐🎁", ("mat", 2, 11, 11),
     [("星に導かれ", "C", 0, "山札から好きなカードを1枚、手札に加える。"), ("黄金・乳香・没薬", "WWC", 80, "")], "星に導かれ、幼子に贈り物をささげた。", "three wise men on camels following a brilliant star, bearing gifts"),
    ("shepherds", "羊飼いたち", "新約", "H", 70, "d1", "🐑⭐", ("luke", 2, 20, 20),
     [("いそいで行く", "C", 20, "このカードをベンチの人物と入れ替えてよい。")], "夜番の野で、最初に救い主の知らせを聞いた。", "shepherds in a night field looking up at angels, sheep around them"),
    ("gabriel", "天使ガブリエル", "新約", "S", 140, "d4", "🎺👼", ("luke", 1, 19, 19),
     [("受胎告知", "S", 0, "山札から「マリヤ」を1枚、場に出す。"), ("神の前に立つ者", "SSC", 120, "")], "神の前に立つ御使。救い主の誕生を告げた。", "a majestic angel with great wings of light announcing good news"),
]

# ── アイテムカード ──
# (id, 名前, レア, 絵文字, 聖句, 効果, 説明, 画像の説明)
I = [
    ("noahs-ark", "ノアの箱舟", "d3", "🚢", ("ge", 6, 14, 14), "次の相手の番、自分の人物すべてが受けるダメージを50少なくする。", "いのちを乗せて、洪水を越えた舟。", "a huge wooden ark on stormy waters with light breaking through clouds"),
    ("rainbow", "契約の虹", "d2", "🌈", ("ge", 9, 13, 13), "自分の人物すべてのHPを30回復する。", "もう洪水で滅ぼさない、という神の約束のしるし。", "a brilliant rainbow over a green world after the flood"),
    ("tablets", "十戒の石板", "d4", "🪨", ("exo", 31, 18, 18), "山札から好きなカードを2枚、手札に加える。", "神の指で書かれた、十の戒め。", "two glowing stone tablets engraved with commandments on a mountain"),
    ("moses-staff", "モーセの杖", "d3", "🪄", ("exo", 14, 16, 16), "相手のバトル場の人物とベンチの人物を1匹、入れ替える。", "海を分け、岩から水を出した杖。", "a wooden shepherd staff glowing, the sea parting behind it"),
    ("manna", "マナ", "d2", "🍞", ("exo", 16, 15, 15), "自分は2枚引く。", "荒野で毎朝降った、天からのパン。", "white flakes of manna covering the desert ground at sunrise"),
    ("ark-covenant", "契約の箱", "d4", "📦", ("exo", 25, 22, 22), "この番、自分の人物のわざのダメージを50増やす。", "神がそこで会うと約束された、聖なる箱。", "the golden ark of the covenant with two cherubim, radiant light"),
    ("jericho-trumpets", "エリコのラッパ", "d2", "🎺", ("josh", 6, 20, 20), "相手の場の「どうぐ」をすべてトラッシュする。", "吹き鳴らすと、城壁がくずれ落ちた。", "rams horn trumpets sounding as ancient walls crumble"),
    ("davids-sling", "ダビデの石投げ", "d3", "🪨", ("1sm", 17, 49, 49), "相手のバトル場の人物に60ダメージ。相手のHPが自分より大きいなら120ダメージ。", "小さな石が、大きな巨人を倒した。", "a leather sling and five smooth stones by a brook"),
    ("jacobs-ladder", "天のはしご", "d2", "🪜", ("john", 1, 51, 51), "山札の上から5枚見て、1枚を手札に加える。", "天と地をつなぐ、御使の上り下りするはしご。", "a shining ladder reaching from earth to heaven with angels"),
    ("josephs-coat", "ヨセフの晴れ着", "d2", "🧥", ("ge", 37, 3, 3), "この人物のHPを40増やす。（どうぐ）", "父の愛のしるし、そでの長い晴れ着。", "a beautiful multicolored long-sleeved robe"),
    ("burning-bush", "燃える柴", "d3", "🔥", ("exo", 3, 2, 2), "山札から「預言」の人物を1枚、手札に加える。", "燃えているのに、燃えつきない柴。", "a desert bush wreathed in holy fire that does not burn up"),
    ("gideons-jar", "ギデオンのつぼ", "d1", "🏺", ("jdgs", 7, 20, 20), "コインを投げオモテなら、相手はエネルギーを1つトラッシュする。", "たいまつを隠した土のつぼ。", "a clay jar with a torch hidden inside glowing in the night"),
    ("mustard-seed", "からし種", "d1", "🌱", ("luke", 17, 6, 6), "山札から基本エネルギーを1枚、自分の人物につける。", "どんな種よりも小さいのに、大きな木になる。", "a tiny mustard seed growing into a great tree with birds"),
    ("loaves-fish", "五つのパンと二匹の魚", "d4", "🍞", ("john", 6, 9, 9), "自分の人物すべてのHPを50回復する。手札が5枚になるまで引く。", "少年のささげた弁当が、五千人を満たした。", "a basket of five barley loaves and two fish multiplying with light"),
    ("water-wine", "カナのぶどう酒", "d2", "🍷", ("john", 2, 7, 7), "手札のエネルギーを1枚、好きなタイプのエネルギーとして人物につける。", "水がめの水が、最上のぶどう酒に変わった。", "stone water jars turning into rich wine at a wedding feast"),
    ("nard", "ナルドの香油", "d2", "🌸", ("mark", 14, 3, 3), "自分の人物1匹のHPをすべて回復する。", "惜しまずに注がれた、高価な香油。", "an alabaster jar of precious perfume broken open, fragrance drifting"),
    ("last-supper-cup", "最後の晩餐の杯", "d3", "🍷", ("luke", 22, 20, 20), "自分のトラッシュから人物を2枚、手札に戻す。", "わたしの血による新しい契約。", "a simple cup and broken bread on a table at the last supper, candlelight"),
    ("crown-thorns", "茨の冠", "d4", "🌿", ("john", 19, 5, 5), "自分の人物1匹のダメージをすべて取り除き、このカードをトラッシュする。", "王の王がかぶせられた、あざけりの冠。", "a crown of thorns resting on a wooden beam, soft light"),
    ("the-cross", "十字架", "cr", "✝️", ("1cor", 1, 18, 18), "自分の人物すべてのダメージと特殊状態をすべて回復する。このカードは山札に戻す。", "滅び行く者には愚か、救われる者には神の力。", "a wooden cross on a hill at sunrise, rays of glory spreading"),
    ("empty-tomb-stone", "空の墓の石", "d3", "🪨", ("mark", 16, 4, 4), "自分のトラッシュから人物を1枚、ベンチに出す。", "朝早く、すでに転がされていた大きな石。", "a large round stone rolled away from an empty tomb at dawn"),
    ("armor-of-god", "神の武具", "d4", "🛡️", ("eph", 6, 11, 11), "この人物が受けるダメージを40少なくする。（どうぐ）", "真理の帯、正義の胸当て、信仰の盾、御霊の剣。", "a shining set of armor: belt, breastplate, shield, helmet and sword"),
    ("living-water", "生ける水", "d1", "💧", ("john", 7, 38, 38), "自分の人物1匹のHPを30回復する。", "その腹から、生ける水が川となって流れ出る。", "a clear river of living water flowing with light"),
    ("true-vine", "ぶどうの木", "d1", "🍇", ("john", 15, 5, 5), "自分のベンチの人物すべてにエネルギーを1枚ずつつけてよい。", "つながっていれば、豊かに実を結ぶ。", "a lush grapevine heavy with fruit, branches connected to the trunk"),
    ("keys-kingdom", "天国のかぎ", "d2", "🔑", ("mat", 16, 19, 19), "山札から好きなアイテムを1枚、手札に加える。", "ペテロに与えられた、天国のかぎ。", "two golden keys glowing with heavenly light"),
]

# ── イエス・キリスト（ハイパーレア） ──
JESUS = ("jesus-christ", "イエス・キリスト", "新約", "S", "∞", "hr", "✝️🕊️", ("john", 8, 12, 12),
         [("いのちのことば", "S", 0, "自分の人物すべてのダメージと特殊状態を、すべて回復する。"),
          ("十字架のあがない", "SSS", "∞", "すべての罪をゆるす。このわざは、何ものにも防がれない。")],
         "道であり、真理であり、命である方。", "Jesus Christ radiating divine light, gentle and majestic, dove descending, golden rays")
JESUS_ABILITY = ("世の光", "このカードが場にある限り、自分の人物はやみの効果を受けない。")

ABILITIES = {  # 特性（☆以上の人物）
    "moses": ("神の人", "このカードは、相手のわざの効果を受けない。"),
    "david": ("主の油注がれた者", "このカードがバトル場にいる限り、自分の人物のわざのダメージ+20。"),
    "paul": ("すべての人に", "このカードは、すべてのタイプのエネルギーとして使える。"),
    "peter": ("立ち返る", "このカードがきぜつしたとき、1回だけHP60で戻る。"),
    "mary": ("恵みに満ちた者", "自分の番に1回、自分の人物1匹のHPを30回復できる。"),
    "abraham": ("約束の子孫", "自分の番に1回、山札から人物を1枚ベンチに出せる。"),
}

ART_STYLE = ("Japanese trading card game illustration, vibrant anime style, dynamic composition, glowing light effects, "
             "rich detailed background, no text, no letters, no logos, no card frame")


def fetch(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print("download", url)
        urllib.request.urlretrieve(url, path)
    return path


def load_bible():
    bible = {}
    for line in open(fetch(BOOKS_URL, os.path.join(CACHE, "books.jsonl")), encoding="utf-8"):
        d = json.loads(line)
        bible[(d["b"], d["c"], d["v"])] = d["t"]
    return bible


def tidy(text):
    """〔〕を除き、節をまたいだ片側のかぎ括弧を補う／外す。半角スペース（詩の改行）は残す。"""
    text = re.sub(r"〔[^〕]*〕", "", text).rstrip("〔").strip()
    out, depth = [], 0
    for ch in text:
        if ch == "「":
            depth += 1
        elif ch == "」":
            if depth == 0:
                continue
            depth -= 1
        out.append(ch)
    text = "".join(out)
    if depth:
        text = (text[:-1] + "」" * depth + "。") if text.endswith("。") else text + "」" * depth
    return text


def load_icon(name):
    custom = {"x-cross": '<path d="M10.2 2h3.6v5.6h5.4v3.6h-5.4V22h-3.6V11.2H4.8V7.6h5.4z"/>'}
    if name in custom:
        return custom[name]
    svg = open(fetch(ICON_URL.format(name), os.path.join(CACHE, "icons", name + ".svg")), encoding="utf-8").read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    return re.sub(r"\s+", " ", inner).replace(" />", "/>").strip()


def main():
    bible = load_bible()
    errors, out = [], []

    def verse(ref):
        b, c, v1, v2 = ref
        parts = []
        for v in range(v1, v2 + 1):
            t = bible.get((b, c, v))
            if t is None:
                errors.append(f"{b} {c}:{v} が見つかりません")
            parts.append(t or "")
        vs = f"{v1}" if v1 == v2 else f"{v1}-{v2}"
        return tidy("".join(parts)), f"{BOOK[b]} {c}:{vs}"

    def assets(item, vid):
        for ext in ("webp", "jpg", "png"):
            if os.path.exists(os.path.join(ROOT, "images", f"{vid}.{ext}")):
                item["img"] = f"images/{vid}.{ext}"; break
        if os.path.exists(os.path.join(ROOT, "audio", f"{vid}.mp3")):
            item["audio"] = f"audio/{vid}.mp3"

    def person(row, ability=None):
        vid, name, era, t, hp, rar, emoji, ref, attacks, desc, art = row
        text, refname = verse(ref)
        num = hp if isinstance(hp, int) else 999
        item = {
            "id": vid, "kind": "person", "name": name, "era": era, "type": t, "hp": hp, "rarity": rar, "emoji": emoji,
            "attacks": [{"name": a[0], "cost": a[1], "power": a[2], "text": a[3]} for a in attacks],
            "weak": WEAK[t], "resist": RESIST[t], "retreat": 0 if t == "S" else (1 if num <= 70 else 2 if num <= 110 else 3),
            "text": text, "ref": refname, "desc": desc, "art": art,
        }
        ab = ability or ABILITIES.get(vid)
        if ab:
            item["ability"] = {"name": ab[0], "text": ab[1]}
        assets(item, vid)
        return item

    # 並び：イエス → 旧約 → 新約 → アイテム
    out.append(person(JESUS, JESUS_ABILITY))
    out.extend(person(r) for r in P)
    for vid, name, rar, emoji, ref, effect, desc, art in I:
        text, refname = verse(ref)
        item = {"id": vid, "kind": "item", "name": name, "rarity": rar, "emoji": emoji, "effect": effect,
                "text": text, "ref": refname, "desc": desc, "art": art}
        assets(item, vid)
        out.append(item)
    for no, item in enumerate(out, 1):
        item["no"] = no
        item["title"] = item["name"]; item["one"] = item["desc"]  # 印刷・ARページとの互換

    dup = [k for k, n in Counter(x["id"] for x in out).items() if n > 1]
    if dup:
        errors.append(f"id 重複: {dup}")
    if errors:
        print("\n".join(errors)); sys.exit(1)

    types_js = {k: {"key": v[0], "name": v[1], "c1": v[2], "c2": v[3], "icon": v[4]} for k, v in TYPES.items()}
    with open(os.path.join(ROOT, "verses.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// 自動生成: python tools/build_cards.py （直接編集しないこと）\n")
        f.write("// 聖句：口語訳（新約1954・旧約1955、パブリックドメイン）\n")
        f.write("const TYPES = " + json.dumps(types_js, ensure_ascii=False) + ";\n")
        f.write("const VERSES = [\n" + ",\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n];\n")

    icons = {v[4]: load_icon(v[4]) for v in TYPES.values()}
    with open(os.path.join(ROOT, "icons.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// 自動生成: python tools/build_cards.py 。Lucide (ISC License, https://lucide.dev) と自作アイコン\n")
        f.write("const ICONS = " + json.dumps(icons, ensure_ascii=False, indent=1) + ";\n")

    os.makedirs(os.path.join(ROOT, "prompts"), exist_ok=True)
    with open(os.path.join(ROOT, "prompts", "card_art_prompts.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# カード絵柄の画像生成プロンプト（全100枚）\n\n")
        f.write("GPT Image / Nano Banana などで生成し、`art_inbox/` に `<id>.png` の名前で入れて `python tools/import_art.py` を実行する。\n")
        f.write("普通のカードは **横長 3:2（1536×1024）**。☆以上・👑・ハイパーレアは **縦長 2:3（1024×1536）** の全面アート。\n")
        f.write("1枚目ができたら、それを添付して「この画風で」と頼むと100枚の画風がそろう。\n\n")
        f.write(f"共通の末尾：\n```\n{ART_STYLE}\n```\n\n")
        for x in out:
            full = x["rarity"] in ("s1", "s2", "cr", "hr")
            f.write(f"## No.{x['no']:03d} {x['name']}　`{x['id']}`\n```\n{x['art']}, {'portrait 2:3 full-art, character in the upper half, lower third calm for text' if full else 'landscape 3:2, subject centered'}, {ART_STYLE}\n```\n\n")

    print(f"verses.js: {len(out)} 枚（人物 {sum(x['kind'] == 'person' for x in out)} / アイテム {sum(x['kind'] == 'item' for x in out)}）")
    print("レアリティ:", dict(sorted(Counter(x["rarity"] for x in out).items())))
    print("タイプ:", dict(Counter(x.get("type", "item") for x in out)))
    print("長い聖句:", sorted(((len(x["text"]), x["id"]) for x in out), reverse=True)[:6])


if __name__ == "__main__":
    main()
