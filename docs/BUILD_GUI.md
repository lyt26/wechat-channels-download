# Build Windows GUI release (one-file exe)

Run from repo root on Windows:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile `
  --name "视频号下载器" `
  --paths . `
  --hidden-import sph_core `
  gui/app.py
```

Output: `dist/视频号下载器.exe`
