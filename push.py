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

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
OWNER = "CYZR314"
REPO = "free-tokens-guide"
BRANCH = "main"
TOKEN_FILE = os.path.join(ROOT, ".secrets", "github_token")


def say(msg=""):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode(sys.stdout.encoding or "utf-8", "replace")
              .decode(sys.stdout.encoding or "utf-8", "replace"), flush=True)


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


def ls_blobs(tree_sha):
    """本地 tree -> {path: (mode, blob_sha)}，只看文件"""
    return {path: (mode, sha) for mode, typ, sha, path in ls_tree(tree_sha) if typ == "blob"}


def remote_tree(sha):
    """远端 tree -> {path: (mode, sha)}，只看文件"""
    if not sha:
        return {}
    res = api("GET", "/repos/%s/%s/git/trees/%s?recursive=1" % (OWNER, REPO, sha),
              token=TOKEN)
    out = {}
    for e in res.get("tree", []):
        if e.get("type") == "blob":
            out[e["path"]] = (e.get("mode", "100644"), e["sha"])
    return out


def upload_blobs(paths_shas):
    for path, sha in paths_shas:
        content = subprocess.run(["git", "cat-file", "blob", sha],
                                 cwd=ROOT, capture_output=True).stdout
        res = api("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO), {
            "content": base64.b64encode(content).decode("ascii"),
            "encoding": "base64",
        }, token=TOKEN)
        if res.get("sha") != sha:
            die("blob 校验失败：%s 本地 %s，服务端 %s" % (path, sha, res.get("sha")))


def build_tree(prev_tree_sha, commit_sha):
    """以远端前一版 tree 为底，提交这一版改动，返回新 tree 的 sha"""
    info = parse_commit(commit_sha)
    new_map = ls_blobs(info["tree"])
    base_map = remote_tree(prev_tree_sha)

    add = [(p, v) for p, v in new_map.items()
           if base_map.get(p, (None, None))[1] != v[1]]
    if add:
        upload_blobs(add)

    entries = []
    for path, (mode, sha) in add:
        entries.append({"path": path, "mode": mode, "type": "blob", "sha": sha})
    for path in base_map:
        if path not in new_map:
            entries.append({"path": path, "mode": "100644", "type": "blob",
                            "sha": None})

    if not entries:
        return prev_tree_sha, len(add), 0

    body = {"tree": entries}
    if prev_tree_sha:
        body["base_tree"] = prev_tree_sha
    res = api("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO), body, token=TOKEN)
    return res["sha"], len(add), len(entries) - len(add)


# ---------------- 主流程 ----------------

def main():
    global TOKEN
    TOKEN = load_token()

    if git_ok(["rev-parse", "--git-dir"]) is False:
        die("这里不是 git 仓库：%s" % ROOT)

    # 0. 清掉 Windows 保留名垃圾文件（git 读不了 CON，会让 add 整个失败）
    stray = os.path.join(ROOT, "CON")
    if os.path.exists(stray):
        try:
            if os.path.getsize(stray) < 4096:
                os.remove(stray)
                say("· 已清理垃圾文件 CON")
        except OSError:
            pass

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
    force_api = os.environ.get("FORCE_API") == "1"
    for attempt in range(1, 4 if not force_api else 1):
        if force_api:
            say("· 强制走 API（FORCE_API=1）")
            break
        say("· 尝试 git push（第 %d 次）…" % attempt)
        url = "https://x-access-token:%s@github.com/%s/%s.git" % (TOKEN, OWNER, REPO)
        p = subprocess.run(["git", "push", url, "HEAD:refs/heads/" + BRANCH],
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
    prev_tree = parse_commit(remote)["tree"] if remote else None
    new_remote = remote
    for i, sha in enumerate(pending, 1):
        info = parse_commit(sha)
        tree_sha, adds, dels = build_tree(prev_tree, sha)
        say("  · 改动：新增/修改 %d 个文件，删除 %d 个" % (adds, dels))
        prev_tree = tree_sha
        body = {
            "message": info["message"],
            "tree": tree_sha,
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