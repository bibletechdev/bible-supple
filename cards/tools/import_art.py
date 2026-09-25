"""生成したイラストをカードに取りこむ。

使い方:
  1. 画像を art_inbox/ に入れる。ファイル名にカードの id を含める（例 jesus-christ.png, 001_moses (1).jpg）
  2. python tools/import_art.py            … images/<id>.webp に変換して、verses.js を作り直す
     python tools/import_art.py --videos   … さらに、そのカードのSNS動画も作り直す
取りこんだ元画像は art_inbox/done/ に移す。

縦横比は自動で合わせる：☆以上・👑・ハイパーレアは縦長（全面アート）、それ以外は横長。
"""
import json, os, re, shutil, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(ROOT, "art_inbox")
FULL = ("s1", "s2", "cr", "hr")
# カードの絵柄の窓の縦横比（cards.css の寸法から）
ASPECT_FULL = (100 - 5.6) / (148 - 5.6)          # 全面アート ≒ 0.663
ASPECT_WINDOW = (100 - 5.6 - 4.8 - 2) / (54 - 2)  # 普通の窓 ≒ 1.68


def load_cards():
    src = open(os.path.join(ROOT, "verses.js"), encoding="utf-8").read()
    return json.loads(src[src.index("const VERSES = [") + len("const VERSES = "):].rstrip().rstrip(";"))


def center_crop(im, aspect, bias_y=0.4):
    """指定の縦横比に中央で切り抜く（縦に切るときは少し上寄り＝顔が切れにくい）。"""
    w, h = im.size
    if w / h > aspect:
        nw = int(h * aspect); x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / aspect); y = int((h - nh) * bias_y)
    return im.crop((0, y, w, y + nh))


def main():
    os.makedirs(INBOX, exist_ok=True)
    cards = {c["id"]: c for c in load_cards()}
    ids_by_len = sorted(cards, key=len, reverse=True)  # 長い id から照合（mary と mary-magdalene を取り違えない）
    files = [f for f in os.listdir(INBOX) if re.search(r"\.(png|jpe?g|webp)$", f, re.I)]
    if not files:
        print(f"{INBOX} に画像がありません。<id>.png の名前で入れてください。"); return
    done, skipped = [], []
    os.makedirs(os.path.join(INBOX, "done"), exist_ok=True)
    for f in sorted(files):
        stem = os.path.splitext(f)[0].lower()
        vid = next((i for i in ids_by_len if re.search(rf"(^|[^a-z]){re.escape(i)}($|[^a-z])", stem)), None)
        if not vid:
            skipped.append(f); continue
        c = cards[vid]
        im = Image.open(os.path.join(INBOX, f)).convert("RGB")
        full = c["rarity"] in FULL
        im = center_crop(im, ASPECT_FULL if full else ASPECT_WINDOW)
        im.thumbnail((1100, 1100) if full else (1400, 1400), Image.LANCZOS)
        for ext in ("jpg", "png", "webp"):  # 古い画像を消して重複を防ぐ
            old = os.path.join(ROOT, "images", f"{vid}.{ext}")
            if os.path.exists(old): os.remove(old)
        im.save(os.path.join(ROOT, "images", f"{vid}.webp"), quality=86, method=6)
        shutil.move(os.path.join(INBOX, f), os.path.join(INBOX, "done", f))
        done.append(vid)
        print(f"取りこみ: {f} → images/{vid}.webp（{'縦長・全面' if full else '横長'} {im.size[0]}×{im.size[1]}）")
    if skipped:
        print("id が分からずスキップ:", ", ".join(skipped), "（ファイル名にカードの id を入れてください）")
    if done:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_cards.py")], check=True)
        if "--videos" in sys.argv:
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_videos.py"), *done], check=True)


if __name__ == "__main__":
    main()
