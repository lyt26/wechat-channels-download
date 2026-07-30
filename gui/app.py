#!/usr/bin/env python3
"""Beginner-friendly GUI for WeChat Channels (视频号) download.

Brand: 上海三松强哥出品 — no license gate; optional「请喝咖啡」.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import tkinter as tk
import urllib.error
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REPO = Path(__file__).resolve().parents[1] if not getattr(sys, "frozen", False) else Path(sys.executable).resolve().parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from brand import BRAND, BRAND_FULL, COFFEE_HINT, CONTACT, QQ, coffee_text, pay_qr_path  # noqa: E402
from sph_core import download_share  # noqa: E402

GREEN = "#07C160"
GREEN_DARK = "#06AD56"
BG = "#F7FBF8"
CARD = "#FFFFFF"
TEXT = "#1F2A24"
MUTED = "#6B7C72"
BORDER = "#D7E8DD"
BRAND_BG = "#0B3D2E"
BRAND_FG = "#E8FFF3"
GOLD = "#F5C542"


class App(tk.Tk):
    """Main window: paste link → choose folder → download."""

    def __init__(self) -> None:
        super().__init__()
        self.title(f"视频号下载器 · {BRAND}")
        self.geometry("760x600")
        self.minsize(680, 540)
        self.configure(bg=BG)
        self._busy = False
        self._last_file: str | None = None
        self._coffee_photo = None

        default_out = Path.home() / "Downloads" / "视频号下载"
        self.out_var = tk.StringVar(value=str(default_out))
        self.h265_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="把微信里的分享链接粘贴过来，点绿色按钮即可。")

        self._build_style()
        self._build_ui()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Microsoft YaHei UI", 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Microsoft YaHei UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Microsoft YaHei UI", 9))

    def _build_ui(self) -> None:
        brand = tk.Frame(self, bg=BRAND_BG)
        brand.pack(fill="x")
        tk.Label(brand, text=BRAND, bg=BRAND_BG, fg=GOLD, font=("Microsoft YaHei UI", 16, "bold")).pack(pady=(12, 2))
        tk.Label(brand, text="视频号一键下载 · 开源免费", bg=BRAND_BG, fg=BRAND_FG, font=("Microsoft YaHei UI", 10)).pack(
            pady=(0, 12)
        )

        head = ttk.Frame(self, style="TFrame")
        head.pack(fill="x", padx=24, pady=8)
        ttk.Label(head, text="一键下载视频号", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            head,
            text="小白三步：复制链接 → 粘贴到这里 → 点下载。不用命令行。",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        card = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True, padx=24, pady=8)

        ttk.Label(card, text="① 粘贴分享链接或整段微信文案", style="Card.TLabel").pack(anchor="w", padx=16, pady=(16, 6))
        self.text = tk.Text(
            card,
            height=5,
            wrap="word",
            font=("Microsoft YaHei UI", 11),
            relief="solid",
            bd=1,
            highlightthickness=0,
            padx=10,
            pady=10,
        )
        self.text.pack(fill="x", padx=16)
        self.text.insert("1.0", "例如：https://weixin.qq.com/sph/xxxxxx")

        btn_row = ttk.Frame(card, style="Card.TFrame")
        btn_row.pack(fill="x", padx=16, pady=8)
        ttk.Button(btn_row, text="从剪贴板粘贴", command=self.paste_clipboard).pack(side="left")
        ttk.Button(btn_row, text="清空", command=lambda: self.text.delete("1.0", "end")).pack(side="left", padx=8)
        ttk.Button(btn_row, text="请强哥喝咖啡", command=self.show_coffee).pack(side="left", padx=8)

        ttk.Label(card, text="② 选择保存文件夹", style="Card.TLabel").pack(anchor="w", padx=16, pady=(8, 6))
        path_row = ttk.Frame(card, style="Card.TFrame")
        path_row.pack(fill="x", padx=16)
        ttk.Entry(path_row, textvariable=self.out_var, font=("Microsoft YaHei UI", 10)).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(path_row, text="浏览…", command=self.choose_dir).pack(side="left", padx=(8, 0))

        ttk.Checkbutton(card, text="优先尝试更高画质（H.265，部分电脑可能播不了）", variable=self.h265_var).pack(
            anchor="w", padx=16, pady=10
        )

        self.download_btn = tk.Button(
            card,
            text="③ 开始下载",
            bg=GREEN,
            fg="white",
            activebackground=GREEN_DARK,
            activeforeground="white",
            font=("Microsoft YaHei UI", 13, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.start_download,
            padx=16,
            pady=12,
        )
        self.download_btn.pack(fill="x", padx=16, pady=(4, 8))

        ttk.Label(card, text="运行状态", style="Muted.TLabel").pack(anchor="w", padx=16, pady=(8, 4))
        self.log = tk.Text(card, height=7, wrap="word", font=("Consolas", 10), bg="#F3F7F4", relief="flat", state="disabled")
        self.log.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        foot = ttk.Frame(self, style="TFrame")
        foot.pack(fill="x", padx=24, pady=(0, 8))
        ttk.Button(foot, text="打开保存文件夹", command=self.open_folder).pack(side="left")
        ttk.Button(foot, text="打开刚下的视频", command=self.open_last_file).pack(side="left", padx=8)
        ttk.Label(foot, textvariable=self.status_var, style="Sub.TLabel").pack(side="left", padx=12)

        tk.Label(
            self,
            text=f"{BRAND_FULL}  |  开源免费  |  {CONTACT}",
            bg=BG,
            fg=MUTED,
            font=("Microsoft YaHei UI", 8),
        ).pack(fill="x", padx=24, pady=(0, 10))

    def show_coffee(self) -> None:
        """Voluntary tip dialog — not a paywall."""
        win = tk.Toplevel(self)
        win.title(f"请喝咖啡 · {BRAND}")
        win.configure(bg=BG)
        win.geometry("400x620")
        win.transient(self)

        tk.Label(win, text=COFFEE_HINT, bg=BG, fg=TEXT, font=("Microsoft YaHei UI", 12, "bold")).pack(pady=(16, 6))
        tk.Label(win, text=f"QQ：{QQ}", bg=BG, fg=GREEN_DARK, font=("Microsoft YaHei UI", 12, "bold")).pack()
        tk.Label(win, text="微信扫码也可以（自愿，谢谢）", bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 9)).pack(
            pady=(8, 4)
        )

        qr = pay_qr_path()
        self._coffee_photo = None
        if qr is not None:
            try:
                from PIL import Image, ImageTk

                img = Image.open(qr)
                img.thumbnail((300, 420), Image.Resampling.LANCZOS)
                self._coffee_photo = ImageTk.PhotoImage(img)
                tk.Label(win, image=self._coffee_photo, bg=BG).pack(pady=8)
            except Exception:
                try:
                    self._coffee_photo = tk.PhotoImage(file=str(qr))
                    tk.Label(win, image=self._coffee_photo, bg=BG).pack(pady=8)
                except tk.TclError:
                    pass

        tk.Label(
            win,
            text="不影响使用：不赞助也能一直下载。\n打包与长期维护，等 Star 多了再单独说。",
            bg=BG,
            fg=MUTED,
            font=("Microsoft YaHei UI", 9),
            justify="center",
        ).pack(pady=8)
        ttk.Button(win, text="关闭", command=win.destroy).pack(pady=12)

    def paste_clipboard(self) -> None:
        try:
            clip = self.clipboard_get().strip()
        except tk.TclError:
            messagebox.showwarning("提示", "剪贴板是空的，请先在微信里复制分享链接。")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", clip)
        self._log("已从剪贴板粘贴内容。")

    def choose_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.out_var.get() or str(Path.home()))
        if path:
            self.out_var.set(path)

    def _log(self, msg: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.status_var.set(msg)

    def start_download(self) -> None:
        if self._busy:
            return
        raw = self.text.get("1.0", "end").strip()
        if not raw or raw.startswith("例如："):
            messagebox.showinfo("提示", "请先粘贴微信视频号分享链接。")
            return
        out_dir = self.out_var.get().strip()
        if not out_dir:
            messagebox.showinfo("提示", "请选择保存文件夹。")
            return

        self._busy = True
        self.download_btn.configure(state="disabled", text="下载中，请稍候…", bg="#A0D9B8")
        self._log("—— 开始任务 ——")
        self._log(f"出品：{BRAND}")

        def worker() -> None:
            try:
                result = download_share(
                    raw,
                    out_dir,
                    prefer_h265=self.h265_var.get(),
                    on_progress=lambda m: self.after(0, self._log, m),
                )
                self._last_file = result["path"]
                size_mb = result["size"] / 1024 / 1024

                def ok() -> None:
                    self._log(f"作者：{result['author']}")
                    self._log(f"文件：{result['path']}")
                    self._log(f"大小：{size_mb:.2f} MB")
                    self._log(f"—— 完成（{BRAND}）——")
                    messagebox.showinfo(
                        "下载成功",
                        f"{BRAND}\n\n作者：{result['author']}\n大小：{size_mb:.2f} MB\n\n已保存到：\n{result['path']}",
                    )

                self.after(0, ok)
            except (ValueError, RuntimeError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
                err = str(exc)
                self.after(0, lambda e=err: self._fail(e))
            finally:
                self.after(0, self._idle)

        threading.Thread(target=worker, daemon=True).start()

    def _fail(self, msg: str) -> None:
        self._log(f"失败：{msg}")
        messagebox.showerror("下载失败", msg + "\n\n可试：回微信重新「分享 → 复制链接」再下一次。")

    def _idle(self) -> None:
        self._busy = False
        self.download_btn.configure(state="normal", text="③ 开始下载", bg=GREEN)

    def open_folder(self) -> None:
        path = self.out_var.get().strip()
        if self._last_file:
            path = str(Path(self._last_file).parent)
        if not path or not Path(path).exists():
            Path(self.out_var.get()).mkdir(parents=True, exist_ok=True)
            path = self.out_var.get()
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def open_last_file(self) -> None:
        if not self._last_file or not Path(self._last_file).exists():
            messagebox.showinfo("提示", "还没有下载成功的视频。")
            return
        if sys.platform.startswith("win"):
            os.startfile(self._last_file)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{self._last_file}"')
        else:
            os.system(f'xdg-open "{self._last_file}"')


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
