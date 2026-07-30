#!/usr/bin/env python3
"""CLI for WeChat Channels (视频号) download."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sph_core import download_share, extract_share_url, fetch_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="下载微信视频号分享链接对应的视频")
    parser.add_argument("url", help="分享链接或含链接的文案")
    parser.add_argument("-o", "--output-dir", default="downloads", help="保存目录（默认 ./downloads）")
    parser.add_argument("--h265", action="store_true", help="优先尝试 H.265 地址")
    parser.add_argument("--json", action="store_true", help="额外打印完整解析 JSON 到 stderr")
    args = parser.parse_args(argv)

    try:
        if args.json:
            share_url = extract_share_url(args.url)
            profile = fetch_profile(share_url)
            print(json.dumps(profile, ensure_ascii=False, indent=2), file=sys.stderr)

        result = download_share(args.url, args.output_dir, prefer_h265=args.h265, on_progress=print)
        size = result["size"]
        print(f"作者: {result['author']}")
        print(f"描述: {result['description'].strip()[:120]}")
        print(f"文件: {result['path']}")
        print(f"大小: {size} bytes ({size / 1024 / 1024:.2f} MB)")
        return 0
    except (ValueError, RuntimeError, urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
