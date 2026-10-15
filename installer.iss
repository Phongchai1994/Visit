
#define MyAppName "Visit"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Chanthaburi Provincial Prison"
#define MyAppExeName "Visit.exe"

[Setup]
AppId={{B38D4B81-57B9-4B42-B729-2C3E76DC3A21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\Programs\Visit
DefaultGroupName=Visit

PrivilegesRequired=lowest
UsePreviousAppDir=yes

OutputDir=installer_output
OutputBaseFilename=Visit_Setup_{#MyAppVersion}

Compression=lzma
SolidCompression=yes
WizardStyle=modern

CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\Visit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Visit"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Visit"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "เปิดโปรแกรม Visit"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
