#!/usr/bin/env python3
"""Download a WeChat Channels (视频号) video from a share URL.

Resolves the CDN media URL via sph.litao.workers.dev, then saves an mp4 locally.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PARSE_API = "https://sph.litao.workers.dev/api/fetch_video_profile"
SPH_URL_RE = re.compile(r"https?://weixin\.qq\.com/sph/[A-Za-z0-9]+", re.I)
UNSAFE_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')


def extract_share_url(text: str) -> str:
    """Pick the first sph share URL from raw user text."""
    text = text.strip()
    match = SPH_URL_RE.search(text)
    if match:
        return match.group(0)
    if "weixin.qq.com" in text or "channels.weixin.qq.com" in text:
        return text.split()[0]
    raise ValueError(f"未找到视频号分享链接: {text[:120]}")


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
    raise RuntimeError("响应中没有 videoUrl（可能仅有封面或链接已失效）")


def safe_filename(author: str, description: str) -> str:
    """Build a Windows-safe mp4 filename from author + short description."""
    desc = (description or "视频号").replace("\n", " ").strip()
    desc = re.sub(r"\s+", "", desc)[:24] or "视频"
    author = (author or "未知作者").strip()[:20]
    name = UNSAFE_NAME_RE.sub("_", f"{author}_{desc}")
    return f"{name}.mp4"


def download_file(url: str, dest: Path, timeout: float = 120.0) -> None:
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
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="下载微信视频号分享链接对应的视频")
    parser.add_argument("url", help="分享链接或含链接的文案")
    parser.add_argument("-o", "--output-dir", default="downloads", help="保存目录（默认 ./downloads）")
    parser.add_argument("--h265", action="store_true", help="优先尝试 H.265 地址")
    parser.add_argument("--json", action="store_true", help="额外打印完整解析 JSON 到 stderr")
    args = parser.parse_args(argv)

    try:
        share_url = extract_share_url(args.url)
        profile = fetch_profile(share_url)
        if args.json:
            print(json.dumps(profile, ensure_ascii=False, indent=2), file=sys.stderr)

        data = profile.get("data") or {}
        author = ((data.get("authorInfo") or {}).get("nickname")) or "未知作者"
        feed = data.get("feedInfo") or {}
        description = feed.get("description") or ""
        video_url = pick_video_url(profile, prefer_h265=args.h265)

        out_dir = Path(args.output_dir)
        dest = out_dir / safe_filename(author, description)
        download_file(video_url, dest)

        size = dest.stat().st_size
        print(f"作者: {author}")
        print(f"描述: {description.strip()[:120]}")
        print(f"文件: {dest.resolve()}")
        print(f"大小: {size} bytes ({size / 1024 / 1024:.2f} MB)")
        return 0
    except (ValueError, RuntimeError, urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
