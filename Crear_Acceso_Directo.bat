@echo off
echo Creando acceso directo en el escritorio...

:: Crear un acceso directo en el escritorio
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\DyslexiLess.lnk'); $Shortcut.TargetPath = '%~dp0improved_gui.py'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%~dp0resources\icon.ico'; $Shortcut.Save()"

echo Acceso directo creado en el escritorio.
echo Ahora puedes iniciar DyslexiLess haciendo doble clic en el icono del escritorio.
pause