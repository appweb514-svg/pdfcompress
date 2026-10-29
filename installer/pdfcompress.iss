; Installateur Windows de PDF Compress (Inno Setup 6).
; Installe pour l'utilisateur courant, sans droits administrateur, et ajoute :
;   - "Compresser avec PDF Compress" au clic droit sur les PDF et les dossiers ;
;   - "PDF Compress" dans le menu Envoyer vers (pratique pour plus de 15 fichiers) ;
;   - un raccourci dans le menu Demarrer (et sur le bureau si demande).
; Tout est retire a la desinstallation.
;
; Construction : iscc /DMyAppVersion=1.4.0 installer\pdfcompress.iss
; (attend la version dossier de PyInstaller dans dist-dir\pdfcompress\)

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppName "PDF Compress"
#define MyAppExe "pdfcompress.exe"
#define MyAppPublisher "appweb514-svg"
#define MyAppURL "https://github.com/appweb514-svg/pdfcompress"
#define MenuText "Compresser avec PDF Compress"

[Setup]
AppId={{78A3C0E5-D277-45CE-B998-404ABD0C4C9C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppComments=D'apres une proposition de Marie
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription=Installation de PDF Compress
DefaultDirName={localappdata}\Programs\PDF Compress
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\out
OutputBaseFilename=pdfcompress-installation
SetupIconFile=..\assets\pdfcompress.ico
UninstallDisplayIcon={app}\{#MyAppExe}
UninstallDisplayName={#MyAppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
CloseApplications=yes

[Languages]
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "menu"; Description: "Ajouter « {#MenuText} » au clic droit sur les PDF et les dossiers"
Name: "sendto"; Description: "Ajouter PDF Compress au menu « Envoyer vers »"
Name: "desktop"; Description: "Créer un raccourci sur le bureau"; Flags: unchecked

[Files]
Source: "..\dist-dir\pdfcompress\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktop
Name: "{usersendto}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Parameters: "--ouvrir"; Tasks: sendto

[Registry]
; Clic droit sur un ou plusieurs PDF (quelle que soit l'application PDF par defaut)
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFCompress"; ValueType: string; ValueName: ""; ValueData: "{#MenuText}"; Flags: uninsdeletekey; Tasks: menu
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFCompress"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#MyAppExe}"",0"; Tasks: menu
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\PDFCompress\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExe}"" --ouvrir ""%1"""; Tasks: menu
; Clic droit sur un dossier (PDF du dossier et de ses sous-dossiers)
Root: HKA; Subkey: "Software\Classes\Directory\shell\PDFCompress"; ValueType: string; ValueName: ""; ValueData: "{#MenuText}"; Flags: uninsdeletekey; Tasks: menu
Root: HKA; Subkey: "Software\Classes\Directory\shell\PDFCompress"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#MyAppExe}"",0"; Tasks: menu
Root: HKA; Subkey: "Software\Classes\Directory\shell\PDFCompress\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExe}"" --ouvrir ""%1"""; Tasks: menu

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Lancer PDF Compress"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\PDFCompress"
