Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "Y:\PokeMinou"
WshShell.Run "cmd.exe /c " & chr(34) & "Y:\PokeMinou\start_silent.bat" & Chr(34), 0
Set WshShell = Nothing
