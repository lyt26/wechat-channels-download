#!/usr/bin/env python3
"""Core helpers for WeChat Channels (视频号) download."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

PARSE_API = "https://sph.litao.workers.dev/api/fetch_video_profile"
SPH_URL_RE = re.compile(r"https?://weixin\.qq\.com/sph/[A-Za-z0-9]+", re.I)
UNSAFE_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')

ProgressCb = Callable[[str], None]


def extract_share_url(text: str) -> str:
    """Pick the first sph share URL from raw user text."""
    text = text.strip()
    match = SPH_URL_RE.search(text)
    if match:
        return match.group(0)
    if "weixin.qq.com" in text or "channels.weixin.qq.com" in text:
        return text.split()[0]
    raise ValueError("未找到视频号分享链接，请粘贴类似 https://weixin.qq.com/sph/xxxx 的内容")


def fetch_profile(share_url: str, timeout: float = 60.0) -> dict:
    """Call the sph parser API and return the parsed JSON object."""
    body = json.dumps({"url": share_url}).encode("utf-8")
    req = urllib.request.Request(
        PARSE_API,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    if data.get("errCode", 0) not in (0, None):
        raise RuntimeError(f"解析失败 errCode={data.get('errCode')} errMsg={data.get('errMsg')}")
    return data


def pick_video_url(profile: dict, prefer_h265: bool = False) -> str:
    """Choose the best available videoUrl from a profile response."""
    feed = (profile.get("data") or {}).get("feedInfo") or {}
    if prefer_h265:
        candidates = [
            (feed.get("h265VideoInfo") or {}).get("videoUrl"),
            feed.get("videoUrl"),
            (feed.get("h264VideoInfo") or {}).get("videoUrl"),
        ]
    else:
        candidates = [
            feed.get("videoUrl"),
            (feed.get("h264VideoInfo") or {}).get("videoUrl"),
            (feed.get("h265VideoInfo") or {}).get("videoUrl"),
        ]
    for url in candidates:
        if url:
            return url
    raise RuntimeError("响应中没有 videoUrl（可能仅有封面或链接已失效，请重新复制分享链接）")


def safe_filename(author: str, description: str) -> str:
    """Build a Windows-safe mp4 filename from author + short description."""
    desc = (description or "视频号").replace("\n", " ").strip()
    desc = re.sub(r"\s+", "", desc)[:24] or "视频"
    author = (author or "未知作者").strip()[:20]
    name = UNSAFE_NAME_RE.sub("_", f"{author}_{desc}")
    return f"{name}.mp4"


def download_file(
    url: str,
    dest: Path,
    timeout: float = 120.0,
    on_progress: ProgressCb | None = None,
) -> None:
    """Download CDN media to dest with a channels Referer."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://channels.weixin.qq.com/",
        },
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        total = resp.headers.get("Content-Length")
        total_n = int(total) if total and total.isdigit() else 0
        done = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if on_progress:
                if total_n:
                    pct = min(99, int(done * 100 / total_n))
                    on_progress(f"下载中… {pct}%（{done / 1024 / 1024:.1f} MB）")
                else:
                    on_progress(f"下载中… 已接收 {done / 1024 / 1024:.1f} MB")


def download_share(
    text: str,
    output_dir: str | Path,
    prefer_h265: bool = False,
    on_progress: ProgressCb | None = None,
) -> dict:
    """Resolve share text and download MP4. Returns author/description/path/size."""

    def progress(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    progress("正在识别分享链接…")
    share_url = extract_share_url(text)
    progress(f"正在解析：{share_url}")
    profile = fetch_profile(share_url)

    data = profile.get("data") or {}
    author = ((data.get("authorInfo") or {}).get("nickname")) or "未知作者"
    feed = data.get("feedInfo") or {}
    description = feed.get("description") or ""
    video_url = pick_video_url(profile, prefer_h265=prefer_h265)

    progress(f"解析成功：{author}，开始下载视频…")
    out_dir = Path(output_dir)
    dest = out_dir / safe_filename(author, description)
    download_file(video_url, dest, on_progress=on_progress)

    size = dest.stat().st_size
    progress("下载完成！")
    return {
        "author": author,
        "description": description,
        "path": str(dest.resolve()),
        "size": size,
        "share_url": share_url,
    }
