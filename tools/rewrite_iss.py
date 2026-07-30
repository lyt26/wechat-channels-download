# -*- coding: utf-8 -*-
"""Rewrite xiaobai_setup.iss as UTF-8 BOM with correct Chinese strings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tools" / "xiaobai_setup.iss"

CONTENT = """; Shipinhao Downloader Setup - Inno Setup 6 (UTF-8 BOM)
; Compile: ISCC.exe tools\\xiaobai_setup.iss

#define MyAppName "视频号下载器"
#define MyAppNameFull "视频号下载器（小白版）"
#define MyAppVersion "1.2.2"
#define MyAppPublisher "上海三松强哥"
#define MyAppURL "https://github.com/lyt26/wechat-channels-download"
#define MyAppExeName "ShipinhaoDownloader.exe"
#define MyAppShortcut "ShipinhaoDownloader"

[Setup]
AppId={{A7C3E91B-2D44-4F8A-9C11-5B8E0F3A6D21}
AppName={#MyAppNameFull}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\\SanSongQiangGe\\ShipinhaoDownloader
DefaultGroupName=SanSongQiangGe
DisableProgramGroupPage=yes
OutputDir=..\\release_assets
OutputBaseFilename=ShipinhaoDownloader-Xiaobai-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppNameFull}
VersionInfoVersion=1.2.2
VersionInfoProductName={#MyAppName}
VersionInfoCompany={#MyAppPublisher}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkedonce

[Files]
Source: "..\\release_assets\\ShipinhaoDownloader-Xiaobai.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Icons]
; Shortcut filenames stay ASCII to avoid IPersistFile::Save 0x8007007B
Name: "{group}\\{#MyAppShortcut}"; Filename: "{app}\\{#MyAppExeName}"; Comment: "{#MyAppNameFull}"
Name: "{group}\\Uninstall {#MyAppShortcut}"; Filename: "{uninstallexe}"; Comment: "卸载"
Name: "{autodesktop}\\{#MyAppShortcut}"; Filename: "{app}\\{#MyAppExeName}"; Comment: "{#MyAppNameFull}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "立即运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent
"""


def main() -> None:
    OUT.write_text(CONTENT.lstrip("\n"), encoding="utf-8-sig")
    text = OUT.read_text(encoding="utf-8-sig")
    assert "视频号下载器" in text
    assert OUT.read_bytes()[:3] == b"\xef\xbb\xbf"
    print(f"Wrote {OUT}")
    for line in text.splitlines():
        if line.startswith("#define MyApp"):
            print(line)


if __name__ == "__main__":
    main()
