"""SNS用の縦長動画（1080×1920・約8秒）を、カードごとに mp4 で書き出す。

reel.html を1コマずつ撮影して ffmpeg でつなぐので、コマ落ちのないなめらかな動画になる。
音は入らない（BGMは Instagram / TikTok のアプリ側で付ける）。

使い方:
  python tools/make_videos.py --top            # イエスと☆以上・👑（上位10枚）
  python tools/make_videos.py jesus-christ moses
  python tools/make_videos.py --all            # 100枚（1枚30秒ほどかかる）
出力: sns/videos/<番号>_<id>.mp4 と、表紙用の静止画 sns/covers/<番号>_<id>.jpg
依存: pip install playwright && python -m playwright install chromium ／ ffmpeg
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import http.server, socketserver, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sns")
TOP_RARITIES = ("hr", "s2", "s1", "cr")


def load_cards():
    src = open(os.path.join(ROOT, "verses.js"), encoding="utf-8").read()
    body = src[src.index("const VERSES = [") + len("const VERSES = "):].rstrip().rstrip(";")
    return json.loads(body)


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    handler.log_message = lambda *a: None
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main():
    ap = argparse.ArgumentParser(description="カードの縦長動画を書き出す")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--top", action="store_true", help="イエスと☆以上・👑")
    ap.add_argument("--all", action="store_true", help="100枚すべて")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg が見つかりません（winget install ffmpeg）")
    cards = load_cards()
    if args.all:
        pick = cards
    elif args.top:
        pick = [c for c in cards if c["rarity"] in TOP_RARITIES]
    else:
        pick = [c for c in cards if c["id"] in args.ids]
    if not pick:
        sys.exit("対象のカードがありません（--top / --all / id を指定）")

    from playwright.sync_api import sync_playwright
    os.makedirs(os.path.join(OUT, "videos"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "covers"), exist_ok=True)
    httpd, port = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
            for c in pick:
                name = f"{c['no']:03d}_{c['id']}"
                t0 = time.time()
                page.goto(f"http://127.0.0.1:{port}/reel.html?v={c['id']}", wait_until="networkidle")
                page.evaluate("window.ready")
                dur = page.evaluate("window.DURATION") + 0.6
                frames = int(dur * args.fps)
                with tempfile.TemporaryDirectory() as tmp:
                    for i in range(frames):
                        page.evaluate(f"window.seek({i / args.fps})")
                        page.screenshot(path=os.path.join(tmp, f"{i:04d}.jpg"), type="jpeg", quality=92)
                    shutil.copy(os.path.join(tmp, f"{int(3.0 * args.fps):04d}.jpg"), os.path.join(OUT, "covers", name + ".jpg"))
                    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", str(args.fps), "-i", os.path.join(tmp, "%04d.jpg"),
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-movflags", "+faststart",
                                    os.path.join(OUT, "videos", name + ".mp4")], check=True)
                print(f"{name}.mp4  ({frames}コマ, {time.time() - t0:.0f}秒)")
            browser.close()
    finally:
        httpd.shutdown()
    print(f"\n出力: {os.path.join(OUT, 'videos')}")


if __name__ == "__main__":
    main()
