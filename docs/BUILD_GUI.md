# Build Windows GUI release

## 便携 exe

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

Copy-Item dist\WeChatChannelsDownloader.exe release_assets\ShipinhaoDownloader-Xiaobai.exe -Force
```

## 安装向导（Setup.exe）

先安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)，再执行：

```powershell
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" tools\xiaobai_setup.iss
```

输出：`release_assets/ShipinhaoDownloader-Xiaobai-Setup.exe`
