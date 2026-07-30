# Build Windows GUI release (one-file exe)

Run from repo root on Windows:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile `
  --name "WeChatChannelsDownloader" `
  --paths . `
  --hidden-import sph_core `
  --hidden-import brand `
  --collect-all PIL `
  --add-data "docs/assets/wechat-pay-qr.png;docs/assets" `
  gui/app.py
```

Output: `dist/WeChatChannelsDownloader.exe`  
二维码用于「请喝咖啡」自愿打赏。
