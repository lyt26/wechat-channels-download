#!/usr/bin/env python3
"""Generate auth codes for 上海三松强哥出品 (owner-only tool).

Examples:
  python tools/gen_license.py --life
  python tools/gen_license.py --month
  python tools/gen_license.py --month --days 31
  python tools/gen_license.py --month --until 2028-03-31
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from license_gate import BRAND, generate_life_key, generate_month_key


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{BRAND} · 生成授权码")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--life", action="store_true", help="生成买断码（¥15）")
    g.add_argument("--month", action="store_true", help="生成月付码（¥5）")
    parser.add_argument("--days", type=int, default=31, help="月付有效天数（默认 31）")
    parser.add_argument("--until", type=str, help="月付截止日期 YYYY-MM-DD")
    args = parser.parse_args()

    if args.life:
        key = generate_life_key()
        print(f"类型: 买断（永久）")
        print(f"授权码: {key}")
        return 0

    if args.until:
        end = datetime.strptime(args.until, "%Y-%m-%d").date()
    else:
        end = date.today() + timedelta(days=args.days)
    key = generate_month_key(end)
    print(f"类型: 月付")
    print(f"有效至: {end.isoformat()}")
    print(f"授权码: {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
