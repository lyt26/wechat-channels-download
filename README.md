# WeChat Channels Downloader / 微信视频号下载器

<p align="center">
  <img src="docs/assets/logo.png" width="120" alt="SPH Logo" />
</p>

<p align="center">
  <b>上海三松强哥出品</b><br/>
  一键把视频号变成电脑里的 MP4<br/>
  Paste a <code>weixin.qq.com/sph/...</code> link → get an <code>.mp4</code> file.<br/>
  共有リンクを貼るだけ。誰でも使える。
</p>

<p align="center">
  <a href="#-30-秒上手小白版">简体中文</a> ·
  <a href="README_EN.md">English</a> ·
  <a href="README_JA.md">日本語</a> ·
  <a href="README_KO.md">한국어</a>
</p>

<p align="center">
  <img src="docs/assets/hero-banner.png" width="900" alt="一键下载视频号 Hero" />
</p>

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/lyt26/wechat-channels-download?style=for-the-badge&logo=github&color=07C160" /></a>
  <a href="https://github.com/lyt26/wechat-channels-download/issues"><img alt="Issues" src="https://img.shields.io/github/issues/lyt26/wechat-channels-download?style=for-the-badge&color=07C160" /></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
  <img alt="Platform" src="https://img.shields.io/badge/Windows%20%7C%20macOS%20%7C%20Linux-ready-07C160?style=for-the-badge" />
</p>

---

## 🟢 小白最推荐：下载带界面的 Windows 版

> **不会命令行？直接双击就行。**

1. 打开 [Releases 发布页](https://github.com/lyt26/wechat-channels-download/releases/latest)
2. 下载 **`ShipinhaoDownloader-Xiaobai.exe`**（小白版）或 `WeChatChannelsDownloader-Windows-v1.2.0.exe`
3. 双击运行 → 粘贴微信分享链接 → 点绿色「开始下载」
4. 视频默认保存在：`下载/视频号下载`

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download/releases/latest"><img alt="Download Windows GUI" src="https://img.shields.io/badge/⬇%20下载%20Windows%20界面版-latest-07C160?style=for-the-badge" /></a>
</p>

若 Windows 提示「未知发布者」，点 **更多信息 → 仍要运行**（开源软件常见提示，可先杀毒扫描再放心用）。

已安装 Python 的用户，也可以双击仓库里的 `启动界面版.bat`，或运行：

```bash
python gui/app.py
```

> **上海三松强哥出品** · 源码 MIT 开源 · **现在完全免费使用**  
> 觉得有用请 Star ⭐；想请强哥喝咖啡 / 联系加 **QQ：3031635159**  
> 详见 [`docs/SUPPORT.md`](docs/SUPPORT.md)（无授权、无到期锁；打包维护等星多了再说）

---

## 为什么值得 Star？

| 痛点 | 以前 | 现在 |
|------|------|------|
| 想保存视频号素材 | 只能手机里转存、录屏糊成一片 | **界面点一下 / 一行命令 → 清晰 MP4** |
| `yt-dlp` 行不行？ | **不行**，直接报不支持 | 本工具专门打通视频号分享链 |
| 要不要会编程？ | 各种抓包、证书劝退 | **复制链接 → 粘贴 → 下载** |

> 如果你也讨厌「只能微信里看、电脑下不下来」——  
> **点一下右上角 Star，让更多人找到这个工具。** ⭐

---

## 🚀 30 秒上手（命令行版）

<p align="center">
  <img src="docs/assets/steps-flow.png" width="900" alt="三步流程图" />
</p>

### 你只需要会这 3 步

**① 复制链接**  
在微信里打开视频号 → 分享 → 复制链接  
（长这样：`https://weixin.qq.com/sph/xxxxxx`）

**② 打开电脑，装好 Python**（大多数电脑装一次就行）

```bash
# 检查有没有 Python（有版本号就 OK）
python --version
```

**③ 下载本仓库，运行一行命令**

```bash
git clone https://github.com/lyt26/wechat-channels-download.git
cd wechat-channels-download

python scripts/download_sph.py "https://weixin.qq.com/sph/你的链接" -o ./downloads
```

成功后会打印：

```text
作者: xxx
描述: ...
文件: .../downloads/xxx.mp4
大小: 2.17 MB
```

去 `downloads` 文件夹双击就能播。🎉

---

## 🎬 演示：真实跑通

```bash
python scripts/download_sph.py "https://weixin.qq.com/sph/AS44aBHSMu" -o ./downloads
```

| 项目 | 结果 |
|------|------|
| 作者 | 科技头号 |
| 输出 | `downloads/*.mp4` |
| 大小 | 约 2.2 MB |
| 画面 | 720×1280 竖屏清晰画质 |

---

## ✨ 功能亮点

- **零依赖第三方 Python 包**：只用标准库，`pip install` 都不用
- **自动从分享文案抽链接**：整段微信转发文字丢进来也行
- **智能文件名**：作者 + 标题前缀，Windows 也安全
- **H.264 / H.265 可选**：默认兼容性最好；需要可加 `--h265`
- **Cursor Skill 附带**：给 AI Agent 也能一键复用同一流程

---

## 📦 命令说明（再简单一点）

```bash
# 最常用
python scripts/download_sph.py "分享链接" -o ./downloads

# 链接夹在一长段文字里也行
python scripts/download_sph.py "【视频号】看这个 https://weixin.qq.com/sph/xxxx 超好看" -o ./downloads

# 优先尝试更高码率 H.265
python scripts/download_sph.py "https://weixin.qq.com/sph/xxxx" -o ./downloads --h265

# 调试：把解析 JSON 打到屏幕
python scripts/download_sph.py "https://weixin.qq.com/sph/xxxx" -o ./downloads --json
```

| 参数 | 含义 | 小白怎么选 |
|------|------|------------|
| `url` | 分享链接或含链接文案 | 必填，从微信复制 |
| `-o` | 保存到哪个文件夹 | 建议 `./downloads` |
| `--h265` | 优先 H.265 | 一般不用管 |
| `--json` | 打印原始解析结果 | 出问题时给开发者看 |

---

## 🧠 它是怎么工作的？（看图说话）

```text
微信分享链  →  解析出真实视频地址  →  带正确来源下载  →  得到 MP4
   sph/...         videoUrl CDN              Referer               本地文件
```

1. `yt-dlp` 对视频号无效 —— 所以我们不用它当主路径  
2. 官方网页预览往往只有**封面图**，没有可播视频  
3. 本工具通过解析服务拿到 `videoUrl`，再安全落盘  

更细的技术说明见：[`.cursor/skills/wechat-channels-download/reference.md`](.cursor/skills/wechat-channels-download/reference.md)

---

## 🧩 给 Cursor / AI 用户

仓库内置 Cursor Skill：

```text
.cursor/skills/wechat-channels-download/
```

复制到本机 `~/.cursor/skills/` 后，对 Agent 说：

> 帮我下载这个视频号：https://weixin.qq.com/sph/xxxx

它会按 Skill 流程自动解析并下载。

---

## ❓ 小白常见问题

**Q：提示找不到 Python？**  
去 [python.org](https://www.python.org/downloads/) 安装，勾选 *Add Python to PATH*，装完重开终端。

**Q：下载失败 / 没有 videoUrl？**  
链接可能过期。回微信重新「分享 → 复制链接」，再跑一次。

**Q：可以商用批量扒别人视频吗？**  
不可以。本工具面向个人合法备份 / 已授权素材。批量搬运他人作品可能侵犯著作权，也违反平台规则。定制开发边界见 [`docs/SUPPORT.md`](docs/SUPPORT.md)。

**Q：想请喝咖啡或联系找谁？**  
加 QQ **3031635159**。自愿请咖啡即可，不影响使用。见 [`docs/SUPPORT.md`](docs/SUPPORT.md)。

**Q：解析服务挂了怎么办？**  
可用 [在线解析页](https://sph.litao.workers.dev/) 或 PC 微信插件方案（见 Skill 文档回退流程）。

---

## 🗺 路线图（一起打造成爆款）

- [x] 图形界面（双击即用）  
- [ ] 批量下载多个链接  
- [ ] 可选封面一并保存  
- [ ] macOS / Linux 打包  
- [ ] Star 多了再谈：官方打包与长期维护说明  
- [ ] 更多语言文档

有想法请开 Issue；愿意贡献请提 PR。  
**Star = 投票**：星星越多，更新越勤。⭐

---

## 🙏 致谢

- 解析思路与在线页参考社区项目 [ltaoo/wx_channels_download](https://github.com/ltaoo/wx_channels_download)
- 所有点 Star、提 Issue、转发的朋友们

---

## 📄 License

MIT — 自由使用，记得给仓库一颗 Star，这是对开源作者最好的鼓励。

---

<p align="center">
  <b>如果这个工具帮你省下了时间，请 Star ⭐ 让它被更多人看见。</b><br/>
  <a href="https://github.com/lyt26/wechat-channels-download">https://github.com/lyt26/wechat-channels-download</a>
</p>
