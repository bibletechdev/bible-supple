"""12節ぶんのQRコード(PNG)を qr/ に書き出す。
使い方:  python make_qr.py https://<user>.github.io/mikotoba-postcard/
依存:    pip install qrcode[pil]
"""
import os, re, sys

def load_ids(path="verses.js"):
    src = open(path, encoding="utf-8").read()
    return re.findall(r'id:\s*"([^"]+)"', src)

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    try:
        import qrcode
    except ImportError:
        print("pip install qrcode[pil] を先に実行してください"); sys.exit(1)
    base = sys.argv[1].rstrip("/") + "/"
    os.makedirs("qr", exist_ok=True)
    for vid in load_ids():
        url = f"{base}?v={vid}"
        img = qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
        img.save(f"qr/{vid}.png")
        print(f"qr/{vid}.png  ->  {url}")

if __name__ == "__main__":
    main()
