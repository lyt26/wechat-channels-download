#!/usr/bin/env python3
"""Brand & soft support info · 上海三松强哥出品（无授权门禁）."""

from __future__ import annotations

import sys
from pathlib import Path

BRAND = "上海三松强哥出品"
BRAND_FULL = "上海三松强哥出品 · 视频号下载器"
QQ = "3031635159"
COFFEE_HINT = "如果觉得好用，可以请强哥喝杯咖啡（自愿）"
CONTACT = f"联系 / 请喝咖啡 / 定制：QQ {QQ}"


def coffee_text() -> str:
    """Short voluntary tip message for UI / CLI."""
    return (
        f"{BRAND}\n\n"
        f"{COFFEE_HINT}\n"
        f"{CONTACT}\n\n"
        "源码开源（MIT）。官方打包与长期维护，等项目星多了再单独说明。\n"
        "现在不强制收费、无授权码、无到期锁。"
    )


def pay_qr_path() -> Path | None:
    """Locate optional WeChat tip QR (请喝咖啡)."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / "docs" / "assets" / "wechat-pay-qr.png",
        Path(getattr(sys, "_MEIPASS", here)) / "docs" / "assets" / "wechat-pay-qr.png",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None
