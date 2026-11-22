# 免费 Tokens 白嫖攻略

纯静态站点，页面代码在 [`free-tokens/`](free-tokens/) 目录里。

- 线上地址：部署到 Cloudflare Pages 后填写
- 站点入口：[`free-tokens/index.html`](free-tokens/index.html)
- 数据文件：[`free-tokens/data.json`](free-tokens/data.json) —— 加一个入口、改额度、改攻略，都只动这个文件
- 使用说明：[`free-tokens/README.md`](free-tokens/README.md)

## 更新流程

改 `free-tokens/data.json` → `git commit` → `git push`，Cloudflare Pages 会自动重新发布，几十秒后线上生效，不需要手动传文件。

浏览器里直接改也行：在 GitHub 打开 `free-tokens/data.json`，点右上角铅笔，改完提交，效果一样。

## 本地预览

Windows 下双击 `free-tokens/start.bat`，会在 `http://127.0.0.1:8123/` 打开页面。