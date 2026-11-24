#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 free-tokens/data.json 里的 Tokens 内容同步进根目录 data.json 的 "tokens" 段。

为什么需要它：Tokens 站（free-tokens/）还单独在线，所以它的数据是主副本；
收藏夹是根目录的单页应用，它的数据放在根目录 data.json 里。
改完 free-tokens/data.json 之后跑一次这个脚本，收藏夹里的那份就跟着更新。

用法（在仓库根目录 H:\\dsh-jb\\git 下执行）：
    python tools/sync_tokens_data.py

只动根目录 data.json 的 "tokens" 字段，site / entries / resume 三个字段完全不动。
"""

import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "free-tokens", "data.json")
DST = os.path.join(ROOT, "data.json")


def main():
    if not os.path.exists(SRC):
        sys.exit("找不到 %s" % SRC)
    if not os.path.exists(DST):
        sys.exit("找不到 %s" % DST)

    with open(SRC, encoding="utf-8") as f:
        src = json.load(f)
    with open(DST, encoding="utf-8") as f:
        dst = json.load(f)

    tokens = {
        "site": src.get("site", {}),
        "apiGuide": src.get("apiGuide", {}),
        "changelog": src.get("changelog", []),
        "items": src.get("items", []),
    }
    dst["tokens"] = tokens

    # 总更新时间取两边较新的那个
    a = (dst.get("site") or {}).get("updated") or ""
    b = (src.get("site") or {}).get("updated") or ""
    if b > a:
        dst.setdefault("site", {})["updated"] = b

    with open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dst, f, ensure_ascii=False, indent=2)
        f.write("\n")

    items = tokens["items"]
    vouchers = [i for i in items if (i.get("credits") or {}).get("type") == "voucher"]
    total = sum((i.get("credits") or {}).get("amount", 0) for i in vouchers)
    print("同步完成：%d 个入口，代金券 %d 张合计 ¥%s" % (len(items), len(vouchers), total))
    print("→", DST)


if __name__ == "__main__":
    main()