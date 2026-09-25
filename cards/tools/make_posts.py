"""SNS投稿の予定表（100日分・投稿文つき）と、反応の記録表を作る。

使い方:  python tools/make_posts.py [開始日 YYYY-MM-DD]
出力:
  sns/schedule.csv   … 日付・カード・動画ファイル名・投稿文（そのままコピーして貼れる）
  sns/tracking.csv   … 反応の記録表（投稿したら数字を書きこむ。Excel で開ける）
  sns/captions/<番号>_<id>.txt … 投稿文だけのテキスト（スマホに送ってコピーする用）
並び: 1日目はイエス・キリスト。レアなカードから順に、同じタイプが続かないように並べる。
"""
import csv, datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sns")
RANK = {"hr": 0, "s2": 1, "s1": 2, "cr": 3, "d4": 4, "d3": 5, "d2": 6, "d1": 7}
RNAME = {"hr": "ハイパーレア SSSSSSSSSSSSSSS", "s2": "スーパースペシャル ☆☆", "s1": "スペシャル ☆", "cr": "クラウン 👑",
         "d4": "ダブルレア ◆◆◆◆", "d3": "レア ◆◆◆", "d2": "アンコモン ◆◆", "d1": "コモン ◆"}
TYPE_TAG = {"F": "信仰", "L": "愛", "W": "知恵", "P": "力", "R": "預言", "H": "平和", "S": "光"}


def load_cards():
    src = open(os.path.join(ROOT, "verses.js"), encoding="utf-8").read()
    return json.loads(src[src.index("const VERSES = [") + len("const VERSES = "):].rstrip().rstrip(";"))


def order(cards):
    """レア順に並べつつ、直前と同じタイプ（アイテム同士も）が続かないよう入れ替える。"""
    pool = sorted(cards, key=lambda c: (RANK[c["rarity"]], c["no"]))
    out = []
    while pool:
        last = out[-1].get("type", "item") if out else None
        pick = next((c for c in pool[:6] if c.get("type", "item") != last), pool[0])
        pool.remove(pick)
        out.append(pick)
    return out


def caption(c, day):
    kind = "人物カード" if c["kind"] == "person" else "アイテムカード"
    verse = c["text"].replace(" ", "")
    tags = ["#みことばカード", "#聖書", "#クリスチャン", "#トレカ", "#聖書の人物" if c["kind"] == "person" else "#聖書のアイテム",
            "#" + c["name"].replace("・", "").replace(" ", "")]
    if c.get("type") in TYPE_TAG:
        tags.append(f"#{TYPE_TAG[c['type']]}タイプ")
    return (
        f"【No.{c['no']:03d} {c['name']}】{kind}・{RNAME[c['rarity']]}\n"
        f"{c['desc']}\n\n"
        f"📖 {verse}\n（{c['ref']}・口語訳）\n\n"
        f"聖書の人物とアイテムが、みことばと一緒にカードになりました。全100枚を毎日1枚ずつ紹介中（{day}日目）。\n"
        f"欲しい！と思ったら、コメントで「欲しい」と教えてください🙏\n"
        f"売上の10%は教会に献金します。\n\n" + " ".join(tags)
    )


def main():
    start = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today() + datetime.timedelta(days=1)
    cards = order(load_cards())
    os.makedirs(os.path.join(OUT, "captions"), exist_ok=True)
    with open(os.path.join(OUT, "schedule.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["日目", "日付", "No", "id", "名前", "種類", "レアリティ", "動画", "投稿文"])
        for day, c in enumerate(cards, 1):
            d = start + datetime.timedelta(days=day - 1)
            name = f"{c['no']:03d}_{c['id']}"
            cap = caption(c, day)
            w.writerow([day, d.isoformat(), c["no"], c["id"], c["name"], "人物" if c["kind"] == "person" else "アイテム",
                        RNAME[c["rarity"]], f"videos/{name}.mp4", cap])
            with open(os.path.join(OUT, "captions", f"{day:03d}日目_{name}.txt"), "w", encoding="utf-8") as t:
                t.write(cap + "\n")
    track = os.path.join(OUT, "tracking.csv")
    if not os.path.exists(track):  # 記録を上書きしないよう、初回だけ作る
        with open(track, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["日付", "日目", "No", "名前", "SNS", "投稿URL", "再生数", "いいね", "保存", "シェア", "コメント",
                        "「欲しい」の数", "フォロワー増", "メモ"])
            for day, c in enumerate(cards, 1):
                d = start + datetime.timedelta(days=day - 1)
                for sns in ("Instagram", "TikTok"):
                    w.writerow([d.isoformat(), day, c["no"], c["name"], sns] + [""] * 9)
    print(f"sns/schedule.csv（{len(cards)}日分、{start}〜）")
    print(f"sns/captions/ に投稿文 {len(cards)} 件")
    print("sns/tracking.csv（記録表。既にあれば上書きしない）")
    print("最初の10日:", " / ".join(c["name"] for c in cards[:10]))


if __name__ == "__main__":
    main()
