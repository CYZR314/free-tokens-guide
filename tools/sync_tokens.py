"""
把 free-tokens/ 的页面同步到 home/tokens/（一键更新用）。

用法（在仓库根目录 H:\\dsh-jb\\git 下执行）：
    python tools/sync_tokens.py

只复制 index.html、data.json、images/ 三样东西，不动 home/tokens/view.html
（那是带返回条的二级外壳）。原目录 free-tokens/ 只读不写。
"""

import filecmp
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "free-tokens"
DST = ROOT / "home" / "tokens"
FILES = ["index.html", "data.json"]


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"找不到源目录：{SRC}")
    DST.mkdir(parents=True, exist_ok=True)

    changed = []
    for name in FILES:
        s, d = SRC / name, DST / name
        if not s.is_file():
            raise SystemExit(f"缺少文件：{s}")
        if d.is_file() and filecmp.cmp(s, d, shallow=False):
            print(f"= {name}（没有变化）")
            continue
        shutil.copy2(s, d)
        changed.append(name)
        print(f"> {name}（已更新）")

    s_img, d_img = SRC / "images", DST / "images"
    d_img.mkdir(parents=True, exist_ok=True)
    for f in sorted(s_img.iterdir()):
        if not f.is_file():
            continue
        t = d_img / f.name
        if t.is_file() and filecmp.cmp(f, t, shallow=False):
            continue
        shutil.copy2(f, t)
        changed.append(f"images/{f.name}")
        print(f"> images/{f.name}（已更新）")

    print("-" * 40)
    print("完成，共更新 %d 个文件。" % len(changed) if changed else "完成，已经是最新的。")
    print("预览： " + str(DST.parent / "index.html"))


if __name__ == "__main__":
    main()