"""公開サイト（GitHub Pages）に反映する。

公開先: https://bibletechdev.github.io/bible-supple/cards/
  リポジトリ bibletechdev/bible-supple の cards/ フォルダ（ルートは「みことばサプリ」なので触らない）。
  手元のクローン: D:\\EDIT_work\\みことばサプリ

使い方:  python tools/deploy.py ["コミットメッセージ"]
  1. このフォルダで Git に記録されているファイルを cards/ にコピー（非公開の資料は除く）
  2. みことばサプリ側でコミットして push
"""
import os, shutil, subprocess, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = r"D:\EDIT_work\みことばサプリ"
DST = os.path.join(SITE, "cards")
PRIVATE = {"ナレーター様向け企画説明.md", ".gitignore"}  # 公開しないファイル


def git(args, cwd):
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "みことばカードを更新"
    files = [f for f in git(["ls-files", "-z"], SRC).stdout.split("\0")
             if f and not f.startswith("art_inbox/") and os.path.basename(f) not in PRIVATE]
    git(["pull", "--ff-only"], SITE)
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    for f in files:
        os.makedirs(os.path.join(DST, os.path.dirname(f)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
    git(["add", "-A", "cards"], SITE)
    if not git(["status", "--porcelain", "cards"], SITE).stdout.strip():
        print("変更なし（公開サイトは最新です）"); return
    r = git(["commit", "-m", msg + "\n\nCo-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"], SITE)
    print(r.stdout.strip().splitlines()[0] if r.stdout else r.stderr)
    r = git(["push", "origin", "main"], SITE)
    print(r.stderr.strip() or r.stdout.strip())
    print("数分で https://bibletechdev.github.io/bible-supple/cards/ に反映されます")


if __name__ == "__main__":
    main()
