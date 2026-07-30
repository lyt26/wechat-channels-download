# WeChat Channels Downloader

<p align="center">
  <img src="docs/assets/logo.png" width="120" alt="SPH Logo" />
</p>

<p align="center">
  <b>Turn a WeChat Channels share link into an MP4 — in one command.</b><br/>
  No capture tools. No certificates. Beginner-friendly.
</p>

<p align="center">
  <a href="README.md">简体中文</a> ·
  <a href="#-30-second-quick-start">English</a> ·
  <a href="README_JA.md">日本語</a> ·
  <a href="README_KO.md">한국어</a>
</p>

<p align="center">
  <img src="docs/assets/hero-banner.png" width="900" alt="Hero banner" />
</p>

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/lyt26/wechat-channels-download?style=for-the-badge&logo=github&color=07C160" /></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

---

## 🟢 Easiest for beginners: Windows GUI

1. Open the [latest Release](https://github.com/lyt26/wechat-channels-download/releases/latest)
2. Download **`WeChatChannelsDownloader-Windows.exe`**
3. Double-click → paste the share link → hit the green button

Or from source:

```bash
python gui/app.py
```

---

## Why star this?

| Pain | Before | Now |
|------|--------|-----|
| Save a Channels video on PC | Re-record the screen (ugly) | **One command → clean MP4** |
| Does `yt-dlp` work? | **No** — unsupported URL | Built specifically for `weixin.qq.com/sph/...` |
| Need to be a developer? | MITM / certs / packet capture | **Copy link → Enter** |

If this saves you time, **a Star helps more people find it.** ⭐

---

## 🚀 30-second quick start

<p align="center">
  <img src="docs/assets/steps-flow.png" width="900" alt="3-step flow" />
</p>

1. **Copy the share link** from WeChat Channels  
   Example: `https://weixin.qq.com/sph/xxxxxx`
2. **Install Python 3.10+** (once)
3. **Run:**

```bash
git clone https://github.com/lyt26/wechat-channels-download.git
cd wechat-channels-download

python scripts/download_sph.py "https://weixin.qq.com/sph/YOUR_ID" -o ./downloads
```

Open the `downloads` folder — your `.mp4` is ready.

---

## ✨ Highlights

- **Zero third-party Python deps** (stdlib only)
- Extracts URLs from messy share text
- Safe filenames on Windows / macOS / Linux
- Optional `--h265` for higher bitrate
- Includes a **Cursor Agent Skill** for AI-assisted download

---

## 📦 Usage

```bash
python scripts/download_sph.py "SHARE_URL" -o ./downloads
python scripts/download_sph.py "check this https://weixin.qq.com/sph/xxxx" -o ./downloads
python scripts/download_sph.py "https://weixin.qq.com/sph/xxxx" -o ./downloads --h265
```

| Flag | Meaning |
|------|---------|
| `url` | Share link or text containing it |
| `-o` | Output folder (default `./downloads`) |
| `--h265` | Prefer H.265 URL when available |
| `--json` | Print raw parse JSON to stderr |

---

## How it works

```text
Share link → resolve real CDN videoUrl → download with Referer → MP4 on disk
```

Official web preview often returns **cover only**. `yt-dlp` does not support Channels. This tool fills that gap.

Details: [`.cursor/skills/wechat-channels-download/reference.md`](.cursor/skills/wechat-channels-download/reference.md)

---

## FAQ

**Download failed / no videoUrl?**  
The share link may have expired — copy a fresh link from WeChat and retry.

**Commercial scraping?**  
For personal backup / authorized assets only. Respect copyright and platform rules.

---

## License

MIT. If it helped you, please **Star** the repo. ⭐

<p align="center">
  <a href="https://github.com/lyt26/wechat-channels-download">https://github.com/lyt26/wechat-channels-download</a>
</p>
