[Setup]
AppId={{HermitVault-v2-Secure}}
AppName=HermitVault
AppVersion=2.0
AppPublisher=Alberto
AppPublisherURL=https://github.com/alberto2005-coder
AppSupportURL=https://github.com/alberto2005-coder/HermitVault
DefaultDirName={autopf}\HermitVault
DefaultGroupName=HermitVault
AllowNoIcons=yes
; Esto hace que se vea el icono en el panel de control / lista de apps
UninstallDisplayIcon={app}\HermitVault.exe
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Aquí apuntamos al EXE generado por PyInstaller
Source: "dist\HermitVault.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
; Las carpetas internas ya están dentro del EXE gracias a PyInstaller

[Icons]
Name: "{group}\HermitVault"; Filename: "{app}\HermitVault.exe"
Name: "{commondesktop}\HermitVault"; Filename: "{app}\HermitVault.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HermitVault.exe"; Description: "{cm:LaunchProgram,HermitVault}"; Flags: nowait postinstall skipifsilent
