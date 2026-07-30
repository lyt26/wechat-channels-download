; 瑙嗛鍙蜂笅杞藉櫒锛堝皬鐧界増锛夊畨瑁呭悜瀵?鈥?Inno Setup
; 缂栬瘧: ISCC.exe tools\xiaobai_setup.iss

#define MyAppName "瑙嗛鍙蜂笅杞藉櫒锛堝皬鐧界増锛?
#define MyAppVersion "1.2.1"
#define MyAppPublisher "涓婃捣涓夋澗寮哄摜"
#define MyAppURL "https://github.com/lyt26/wechat-channels-download"
#define MyAppExeName "ShipinhaoDownloader.exe"

[Setup]
AppId={{A7C3E91B-2D44-4F8A-9C11-5B8E0F3A6D21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\SanSongQiangGe\ShipinhaoDownloader
DefaultGroupName=涓婃捣涓夋澗寮哄摜
DisableProgramGroupPage=yes
OutputDir=..\release_assets
OutputBaseFilename=ShipinhaoDownloader-Xiaobai-Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
InfoBeforeFile=
LicenseFile=

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkedonce

[Files]
Source: "..\release_assets\ShipinhaoDownloader-Xiaobai.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent

