#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键上传：先用 git push，连不上 github.com 就自动改走 GitHub API。

为什么需要这个脚本：这台机器访问 github.com:443 时通时不通（DNS 被污染 +
连接被重置），但 api.github.com 一直通。所以当 git push 失败时，
本脚本用 GitHub API 直接创建同样的提交（作者、时间、message、tree 全部照抄），
效果和 push 一样：提交会出现在仓库里，Cloudflare Pages 会自动重新构建。

用法：双击仓库根目录的 push.bat，或在命令行运行  python push.py
"""

import base64
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://api.github.com"
OWNER = "CYZR314"
REPO = "free-tokens-guide"
BRANCH = "main"
TOKEN_FILE = os.path.join(ROOT, ".secrets", "github_token")


def say(msg=""):
    print(msg, flush=True)


def die(msg):
    say("")
    say("✗ " + msg)
    sys.exit(1)


# ---------------- git ----------------

def git(args, check=True, quiet=True):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    if check and p.returncode != 0:
        err = p.stderr.decode("utf-8", "replace") or out
        if not quiet:
            say(err)
        return None
    return out


def git_ok(args):
    return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True).returncode == 0


# ---------------- token ----------------

def load_token():
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        return tok
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            tok = f.read().strip()
        if tok:
            return tok
    die("找不到 GitHub token：请把 token 写进 %s（一行，不要有空格）" % TOKEN_FILE)
    return ""


# ---------------- HTTP ----------------

_SSL_CTX = None


def _ctx(insecure=False):
    c = ssl.create_default_context()
    if insecure:
        c.check_hostname = False
        c.verify_mode = ssl.CERT_NONE
    return c


def api(method, path, body=None, token=None, allow_404=False, timeout=45):
    global _SSL_CTX
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    url = API + path
    last = None
    for attempt in range(1, 4):
        for insecure in (False, True):
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("Authorization", "Bearer " + token)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "push-script")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            if data is not None:
                req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=timeout,
                                            context=_ctx(insecure)) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", "replace")
                if e.code == 404 and allow_404:
                    return None
                last = "HTTP %s %s" % (e.code, err[:300])
                break  # 4xx/5xx 重试意义不大，直接走外层重试
            except Exception as e:  # 网络/TLS
                last = "%s: %s" % (type(e).__name__, e)
        if attempt < 3:
            time.sleep(2 * attempt)
    die("调用 GitHub API 失败（%s %s）：%s" % (method, path, last))


# ---------------- 提交对象 ----------------

NAME_RE = re.compile(r"^(author|committer) (.*?) <(.*?)> (\d+) ([+-]\d{4})$")


def parse_commit(sha):
    raw = git(["cat-file", "-p", sha])
    if raw is None:
        die("读不到本地提交 %s" % sha)
    head, _, message = raw.partition("\n\n")
    info = {"tree": None, "parents": [], "author": None, "committer": None}
    for line in head.splitlines():
        if line.startswith("tree "):
            info["tree"] = line[5:].strip()
        elif line.startswith("parent "):
            info["parents"].append(line[7:].strip())
        else:
            m = NAME_RE.match(line)
            if m:
                role, name, email, ts, tz = m.groups()
                sign = 1 if tz[0] == "+" else -1
                offset = timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5])) * sign
                dt = datetime.fromtimestamp(int(ts), tz=timezone(offset))
                info[role] = {"name": name, "email": email, "date": dt.isoformat()}
    info["message"] = message
    return info


def ensure_blob(blob_sha, cache):
    if blob_sha in cache:
        return
    content = subprocess.run(["git", "cat-file", "blob", blob_sha],
                             cwd=ROOT, capture_output=True).stdout
    res = api("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO), {
        "content": base64.b64encode(content).decode("ascii"),
        "encoding": "base64",
    }, token=TOKEN)
    if res.get("sha") != blob_sha:
        die("blob 校验失败：本地 %s，服务端 %s" % (blob_sha, res.get("sha")))
    cache.add(blob_sha)


def ls_tree(tree_sha):
    out = subprocess.run(["git", "ls-tree", "-r", "-t", "-z", tree_sha],
                         cwd=ROOT, capture_output=True).stdout
    entries = []
    for chunk in out.split(b"\x00"):
        if not chunk:
            continue
        meta, _, path = chunk.partition(b"\t")
        mode, typ, sha = meta.decode().split()
        entries.append((mode, typ, sha, path.decode("utf-8", "replace")))
    return entries


def ensure_tree(tree_sha, token, blobs, known):
    """把 tree_sha 及它下面的子目录全部上传，返回 True/False(已存在)"""
    if tree_sha in known:
        return
    if api("GET", "/repos/%s/%s/git/trees/%s" % (OWNER, REPO, tree_sha),
           token=token, allow_404=True) is not None:
        known.add(tree_sha)
        return

    entries = ls_tree(tree_sha)
    by_dir = {}
    for mode, typ, sha, path in entries:
        parent, _, base = path.rpartition("/")
        by_dir.setdefault(parent, []).append((mode, typ, sha, base))

    # 先文件：确保 blob 存在
    for parent, items in by_dir.items():
        for mode, typ, sha, base in items:
            if typ == "blob":
                ensure_blob(sha, blobs)

    # 再目录：从最深的一层往上建
    for parent in sorted(by_dir.keys(), key=lambda p: -p.count("/") if p else 1):
        items = by_dir[parent]
        body = []
        for mode, typ, sha, base in items:
            if typ == "tree":
                ensure_tree(sha, token, blobs, known)
                body.append({"path": base, "mode": "040000", "type": "tree", "sha": sha})
            else:
                m = mode if mode in ("100644", "100755", "120000") else "100644"
                body.append({"path": base, "mode": m, "type": "blob", "sha": sha})
        res = api("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO),
                  {"tree": body}, token=token)
        if res.get("sha") != tree_sha:
            die("tree 校验失败（%s）：本地 %s，服务端 %s"
                % (parent or "<root>", tree_sha, res.get("sha")))
    known.add(tree_sha)


# ---------------- 主流程 ----------------

def main():
    global TOKEN
    TOKEN = load_token()

    if git_ok(["rev-parse", "--git-dir"]) is False:
        die("这里不是 git 仓库：%s" % ROOT)

    # 1. 先把改动提交（如果有）
    git(["add", "-A"])
    if not git_ok(["diff", "--cached", "--quiet"]):
        msg = time.strftime("更新 %Y-%m-%d %H:%M")
        git(["commit", "-m", msg])
        say("· 已提交本地改动：%s" % msg)

    head = git(["rev-parse", "HEAD"]).strip()

    # 2. 看看远端在哪
    ref = api("GET", "/repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH),
              token=TOKEN, allow_404=True)
    remote = ref["object"]["sha"] if ref else None

    if remote == head:
        say("✓ 远端已经是最新的，没有要上传的东西")
        return

    if remote and not git_ok(["merge-base", "--is-ancestor", remote, "HEAD"]):
        die("远端有本地没有的提交（可能你在别处改过）。"
            "先联网执行  git fetch origin && git reset --hard origin/main  再上传。")

    pending = git(["rev-list", "--reverse", "%s..HEAD" % remote]).split() if remote else []
    if not pending:
        say("✓ 没有待上传的提交")
        return

    say("· 待上传 %d 个提交：%s" % (len(pending),
        ", ".join(c[:7] for c in pending)))

    # 3. 先试 git push（网络偶尔是通的，走它最省事）
    for attempt in range(1, 4):
        say("· 尝试 git push（第 %d 次）…" % attempt)
        p = subprocess.run(["git", "push", "origin", BRANCH],
                           cwd=ROOT, capture_output=True)
        if p.returncode == 0:
            say("✓ 上传成功（git push）")
            return
        err = p.stderr.decode("utf-8", "replace").strip().splitlines()
        say("  " + (err[-1] if err else "unknown error"))
        if attempt < 3:
            time.sleep(3)

    say("")
    say("· github.com 连不上，改走 GitHub API 上传（api.github.com 是通的）…")

    # 4. 用 API 逐个提交
    blobs, trees = set(), set()
    new_remote = remote
    for i, sha in enumerate(pending, 1):
        info = parse_commit(sha)
        ensure_tree(info["tree"], TOKEN, blobs, trees)
        body = {
            "message": info["message"],
            "tree": info["tree"],
            "parents": [new_remote] if new_remote else [],
        }
        if info.get("author"):
            body["author"] = info["author"]
        if info.get("committer"):
            body["committer"] = info["committer"]
        res = api("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
                  body, token=TOKEN)
        created = res.get("sha")
        say("· 第 %d/%d 个提交已创建：%s" % (i, len(pending), str(created)[:7]))
        if created != sha:
            say("  ! 服务端生成的 sha 和本地不一致（%s ≠ %s），历史会对不上，稍后用 git 同步一次"
                % (str(created)[:7], sha[:7]))
            sha = created
        patch = api("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH),
                    {"sha": sha, "force": False}, token=TOKEN)
        new_remote = patch["object"]["sha"]
        say("  → 远端 %s 已指向 %s" % (BRANCH, new_remote[:7]))

    # 5. 收尾：如果 sha 完全对上，顺手把本地 origin/main 也对齐
    if new_remote == head:
        subprocess.run(["git", "update-ref", "refs/remotes/origin/%s" % BRANCH, head],
                       cwd=ROOT, capture_output=True)
        say("")
        say("✓ 上传成功（GitHub API），本地与远端一致")
    else:
        say("")
        say("✓ 上传成功（GitHub API），文件内容已生效；"
            "本地 origin/main 记录落后，下次能连上 github.com 时运行  git fetch origin && git reset --hard origin/main  对齐即可")

    say("· Cloudflare Pages 会在 30–60 秒内自动重新构建：https://free-tokens-guide.pages.dev")


if __name__ == "__main__":
    main()