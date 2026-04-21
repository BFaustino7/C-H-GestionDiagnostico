Set WshShell = CreateObject("WScript.Shell")
' Reemplazá la ruta de abajo por la ruta real donde guardaste el archivo .bat
WshShell.Run chr(34) & "C:\Users\Faustino\Desktop\proyects\C-H-GestionDiagnostico\iniciar_servidor.bat" & Chr(34), 0
Set WshShell = Nothing