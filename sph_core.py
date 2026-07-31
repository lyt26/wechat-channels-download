#!/usr/bin/env python3
"""Core helpers for WeChat Channels (视频号) download."""

from __future__ import annotations

import json
import os
import re
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

PARSE_API = "https://sph.litao.workers.dev/api/fetch_video_profile"
SPH_URL_RE = re.compile(r"https?://weixin\.qq\.com/sph/[A-Za-z0-9]+", re.I)
UNSAFE_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
# Strip emoji / symbols that break Windows GBK console or look ugly in filenames.
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U00002600-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Default: bypass OS proxy (common cause of WinError 10054 with Workers/CDN).
# Set SPH_USE_SYSTEM_PROXY=1 to honor system/env proxies.
USE_SYSTEM_PROXY = os.environ.get("SPH_USE_SYSTEM_PROXY", "").strip() in ("1", "true", "yes")

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


def _ssl_context() -> ssl.SSLContext:
    """Build an SSL context; prefer certifi CA bundle when available."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _build_opener() -> urllib.request.OpenerDirector:
    """HTTPS opener; by default ignore broken system proxies."""
    handlers: list = [urllib.request.HTTPSHandler(context=_ssl_context())]
    if not USE_SYSTEM_PROXY:
        handlers.insert(0, urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(*handlers)


def _is_retryable_network_error(exc: BaseException) -> bool:
    """True for transient disconnects like WinError 10054 / ConnectionReset."""
    if isinstance(exc, (TimeoutError, ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
        return True
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, (TimeoutError, ConnectionResetError, ConnectionAbortedError, OSError)):
            return True
        text = str(reason).lower()
        return any(
            key in text
            for key in (
                "10054",
                "10053",
                "10060",
                "forcibly closed",
                "connection reset",
                "connection aborted",
                "timed out",
                "temporary failure",
                "远程主机强迫关闭",
                "ssl",
                "eof occurred",
            )
        )
    if isinstance(exc, OSError):
        return getattr(exc, "winerror", None) in (10054, 10053, 10060) or getattr(exc, "errno", None) in (
            54,
            104,
            110,
        )
    return False


def _curl_bin() -> str | None:
    """Return curl.exe path on Windows when available."""
    return shutil.which("curl.exe") or shutil.which("curl")


def _http_bytes_urllib(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 60.0,
) -> bytes:
    """One-shot HTTP GET/POST via urllib; returns response body."""
    hdrs = {"User-Agent": USER_AGENT, "Connection": "close"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET", headers=hdrs)
    opener = _build_opener()
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()


def _http_bytes_curl(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 60.0,
) -> bytes:
    """One-shot HTTP GET/POST via system curl (often more stable on Windows)."""
    curl = _curl_bin()
    if not curl:
        raise RuntimeError("本机未找到 curl，无法回退")
    cmd = [
        curl,
        "-sS",
        "-L",
        "--http1.1",
        "--connect-timeout",
        str(max(5, int(timeout // 3))),
        "--max-time",
        str(int(timeout)),
        "-A",
        USER_AGENT,
        "-H",
        "Connection: close",
    ]
    if headers:
        for k, v in headers.items():
            if k.lower() == "user-agent":
                continue
            cmd.extend(["-H", f"{k}: {v}"])
    tmp_path: str | None = None
    try:
        if data is not None:
            fd, tmp_path = tempfile.mkstemp(prefix="sph_post_", suffix=".bin")
            os.close(fd)
            Path(tmp_path).write_bytes(data)
            cmd.extend(["-X", "POST", "--data-binary", f"@{tmp_path}"])
        cmd.append(url)
        completed = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
        if completed.returncode != 0:
            err = (completed.stderr or completed.stdout or b"").decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"curl 失败({completed.returncode}): {err or '未知错误'}")
        return completed.stdout
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _http_bytes(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 60.0,
    retries: int = 5,
    on_progress: ProgressCb | None = None,
    label: str = "网络请求",
) -> bytes:
    """HTTP with retries: urllib first, then curl fallback on Windows flaky TLS."""
    last: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            return _http_bytes_urllib(url, data=data, headers=headers, timeout=timeout)
        except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as exc:
            last = exc
            if not _is_retryable_network_error(exc) and not isinstance(exc, ssl.SSLError):
                # Non-retryable HTTP errors (4xx etc.) — still try curl once later.
                break
            if attempt < retries:
                wait = min(8.0, 1.2 * (2 ** (attempt - 1)))
                if on_progress:
                    on_progress(f"{label}中断，{wait:.0f} 秒后重试（{attempt}/{retries}）…")
                time.sleep(wait)

    # Windows: curl often survives TLS/CDN resets that urllib cannot.
    if _curl_bin():
        if on_progress:
            on_progress(f"{label}改用系统 curl 通道…")
        try:
            return _http_bytes_curl(url, data=data, headers=headers, timeout=timeout)
        except Exception as curl_exc:
            last = curl_exc if last is None else last
            raise RuntimeError(f"{label}失败：{last}；curl 回退也失败：{curl_exc}") from curl_exc

    assert last is not None
    raise last


def fetch_profile(share_url: str, timeout: float = 60.0, on_progress: ProgressCb | None = None) -> dict:
    """Call the sph parser API and return the parsed JSON object."""
    body = json.dumps({"url": share_url}).encode("utf-8")
    raw = _http_bytes(
        PARSE_API,
        data=body,
        headers={"Content-Type": "application/json"},
        timeout=timeout,
        on_progress=on_progress,
        label="解析",
    ).decode("utf-8", errors="replace")
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
    desc = EMOJI_RE.sub("", (description or "视频号").replace("\n", " ").strip())
    desc = re.sub(r"\s+", "", desc)[:24] or "视频"
    author = EMOJI_RE.sub("", (author or "未知作者").strip())[:20] or "未知作者"
    name = UNSAFE_NAME_RE.sub("_", f"{author}_{desc}").rstrip("._# ")
    return f"{name or '视频'}.mp4"


def _download_urllib(
    url: str,
    dest: Path,
    timeout: float,
    on_progress: ProgressCb | None,
) -> None:
    """Stream CDN file to disk with urllib."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://channels.weixin.qq.com/",
            "Connection": "close",
        },
    )
    opener = _build_opener()
    with opener.open(req, timeout=timeout) as resp, dest.open("wb") as out:
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


def _download_curl(url: str, dest: Path, timeout: float, on_progress: ProgressCb | None) -> None:
    """Download CDN file with system curl."""
    curl = _curl_bin()
    if not curl:
        raise RuntimeError("本机未找到 curl")
    if on_progress:
        on_progress("下载改用系统 curl 通道…")
    cmd = [
        curl,
        "-sS",
        "-L",
        "--http1.1",
        "--connect-timeout",
        "20",
        "--max-time",
        str(int(timeout)),
        "-A",
        USER_AGENT,
        "-e",
        "https://channels.weixin.qq.com/",
        "-H",
        "Connection: close",
        "-o",
        str(dest),
        url,
    ]
    completed = subprocess.run(cmd, capture_output=True, timeout=timeout + 15)
    if completed.returncode != 0:
        err = (completed.stderr or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"curl 下载失败({completed.returncode}): {err or '未知错误'}")
    if not dest.exists() or dest.stat().st_size <= 0:
        raise RuntimeError("curl 下载结果为空")


def download_file(
    url: str,
    dest: Path,
    timeout: float = 180.0,
    on_progress: ProgressCb | None = None,
    retries: int = 5,
) -> None:
    """Download CDN media to dest with a channels Referer (retries + curl fallback)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    last: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            _download_urllib(url, dest, timeout, on_progress)
            return
        except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as exc:
            last = exc
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            if not _is_retryable_network_error(exc) and not isinstance(exc, ssl.SSLError):
                break
            if attempt < retries:
                wait = min(8.0, 1.2 * (2 ** (attempt - 1)))
                if on_progress:
                    on_progress(f"下载中断，{wait:.0f} 秒后重试（{attempt}/{retries}）…")
                time.sleep(wait)

    if _curl_bin():
        try:
            if dest.exists():
                dest.unlink()
        except OSError:
            pass
        try:
            _download_curl(url, dest, timeout, on_progress)
            if on_progress:
                on_progress(f"下载中… 已接收 {dest.stat().st_size / 1024 / 1024:.1f} MB")
            return
        except Exception as curl_exc:
            raise RuntimeError(f"下载失败：{last}；curl 回退也失败：{curl_exc}") from curl_exc

    assert last is not None
    raise last


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
    profile = fetch_profile(share_url, on_progress=on_progress)

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
