#define MyAppName "DyslexiLess"
#define MyAppVersion "1.0"
#define MyAppPublisher "DyslexiLess Project"
#define MyAppURL "https://dyslexiless.org"
#define MyAppExeName "DyslexiLess.exe"

[Setup]
; Identificadores únicos
AppId={{0A2B3C4D-5E6F-7G8H-9I0J-1K2L3M4N5O6P}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Configuración de instalación
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=DyslexiLess_Setup
Compression=lzma
SolidCompression=yes
; Requiere privilegios de administrador para instalar
PrivilegesRequired=admin

; Configuración visual
WizardStyle=modern
SetupIconFile=resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Iconos adicionales:"
Name: "startupicon"; Description: "Ejecutar al iniciar Windows"; GroupDescription: "Opciones de inicio:"

[Files]
; Archivos principales
Source: "dist\DyslexiLess\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DyslexiLess\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Crear accesos directos
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Opciones post-instalación
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[CustomMessages]
spanish.WelcomeMessage=Bienvenido al asistente de instalación de DyslexiLess
spanish.InstallMessage=Este asistente te guiará a través del proceso de instalación de DyslexiLess, tu asistente personal de escritura.
spanish.FinishMessage=¡La instalación se ha completado exitosamente!

[Code]
// Función para mostrar mensajes personalizados
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := ExpandConstant('{cm:WelcomeMessage}');
  WizardForm.WelcomeLabel2.Caption := ExpandConstant('{cm:InstallMessage}');
end;

// Función para verificar requisitos del sistema
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  
  // Verificar versión de Windows
  if Version.Major < 10 then
  begin
    MsgBox('DyslexiLess requiere Windows 10 o superior.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Función para detectar instalaciones previas
function InitializeUninstall(): Boolean;
begin
  Result := True;
  // Cerrar la aplicación si está en ejecución
  if CheckForMutexes('DyslexiLessRunning') then
  begin
    if MsgBox('DyslexiLess está en ejecución. ¿Deseas cerrarlo para continuar?',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('', ExpandConstant('{app}\{#MyAppExeName}'), '/quit', '', SW_HIDE, ewWaitUntilTerminated, Result);
    end
    else
      Result := False;
  end;
end;
