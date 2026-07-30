#!/usr/bin/env python3
"""License gate for 上海三松强哥出品 · 视频号下载器.

Free until 2027-12-31 (inclusive). Afterwards an auth code is required:
- Monthly: ¥5 / month
- Lifetime: ¥15 buyout
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

BRAND = "上海三松强哥出品"
BRAND_FULL = "上海三松强哥出品 · 视频号下载器"
CONTACT = "购买授权请联系：上海三松强哥"
PRICE_MONTH = 5
PRICE_LIFE = 15
FREE_UNTIL = date(2027, 12, 31)

# Signing secret for auth codes (casual piracy deterrent for ¥5/¥15 tools).
_SECRET = b"SSQG-ShanghaiSanSong-QiangGe-SPH-License-v1"

LICENSE_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "SanSongQiangGe" / "sph_downloader"
LICENSE_FILE = LICENSE_DIR / "license.json"


@dataclass
class LicenseStatus:
    """Current entitlement snapshot."""

    ok: bool
    mode: str  # free | month | life | locked
    message: str
    expires: date | None = None


def _sign(payload: str) -> str:
    digest = hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:10].upper()


def generate_month_key(expire_on: date | None = None) -> str:
    """Create a one-month (or custom end-date) auth code."""
    end = expire_on or (date.today() + timedelta(days=31))
    payload = f"M-{end.strftime('%Y%m%d')}"
    return f"SSQG-{payload}-{_sign(payload)}"


def generate_life_key() -> str:
    """Create a lifetime buyout auth code."""
    payload = "LIFE"
    return f"SSQG-{payload}-{_sign(payload)}"


def parse_and_validate_key(raw: str, today: date | None = None) -> LicenseStatus:
    """Validate an auth code string."""
    today = today or date.today()
    key = "".join(raw.strip().upper().split())
    parts = key.split("-")
    if len(parts) < 3 or parts[0] != "SSQG":
        return LicenseStatus(False, "locked", "授权码格式不正确")

    if parts[1] == "LIFE":
        if len(parts) != 3:
            return LicenseStatus(False, "locked", "买断授权码格式不正确")
        payload = "LIFE"
        sig = parts[2]
        if not hmac.compare_digest(sig, _sign(payload)):
            return LicenseStatus(False, "locked", "授权码无效")
        return LicenseStatus(True, "life", "已授权：买断（永久）", expires=None)

    if parts[1] == "M" and len(parts) == 4:
        ymd = parts[2]
        sig = parts[3]
        payload = f"M-{ymd}"
        if not hmac.compare_digest(sig, _sign(payload)):
            return LicenseStatus(False, "locked", "授权码无效")
        try:
            exp = datetime.strptime(ymd, "%Y%m%d").date()
        except ValueError:
            return LicenseStatus(False, "locked", "授权码日期无效")
        if today > exp:
            return LicenseStatus(False, "locked", f"月付授权已过期（截止 {exp.isoformat()}）", expires=exp)
        return LicenseStatus(True, "month", f"已授权：月付（有效至 {exp.isoformat()}）", expires=exp)

    return LicenseStatus(False, "locked", "无法识别的授权码类型")


def save_license(raw_key: str) -> LicenseStatus:
    """Persist a validated license locally."""
    status = parse_and_validate_key(raw_key)
    if not status.ok:
        return status
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "key": "".join(raw_key.strip().upper().split()),
        "mode": status.mode,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "brand": BRAND,
    }
    LICENSE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return status


def load_saved_license(today: date | None = None) -> LicenseStatus | None:
    """Load and re-validate saved license, if any."""
    if not LICENSE_FILE.exists():
        return None
    try:
        data = json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
        key = data.get("key") or ""
        return parse_and_validate_key(key, today=today)
    except (OSError, json.JSONDecodeError, TypeError):
        return LicenseStatus(False, "locked", "本地授权文件损坏，请重新输入授权码")


def is_in_free_period(today: date | None = None) -> bool:
    """True when users may use the app without seeing/using auth UI."""
    today = today or date.today()
    return today <= FREE_UNTIL


def check_entitlement(today: date | None = None) -> LicenseStatus:
    """Return whether the product may be used today."""
    today = today or date.today()
    if is_in_free_period(today):
        # Keep message short; UI should not surface auth wording during free period.
        return LicenseStatus(True, "free", BRAND, expires=FREE_UNTIL)

    saved = load_saved_license(today=today)
    if saved and saved.ok:
        return saved

    msg = (
        f"免费期已结束（截止 {FREE_UNTIL.isoformat()}）。\n"
        f"继续使用需授权码：月付 ¥{PRICE_MONTH} / 月，或买断 ¥{PRICE_LIFE}。\n"
        f"{CONTACT}"
    )
    return LicenseStatus(False, "locked", msg)


def pricing_text() -> str:
    """Human-readable pricing and contact for dialogs."""
    return (
        f"{BRAND}\n\n"
        f"免费使用至：{FREE_UNTIL.isoformat()}\n"
        f"之后价格：\n"
        f"  · 月付 ¥{PRICE_MONTH} / 月\n"
        f"  · 买断 ¥{PRICE_LIFE}（一次付清，永久）\n\n"
        f"{CONTACT}\n"
        f"付款后发送凭证，即可获得授权码。"
    )
