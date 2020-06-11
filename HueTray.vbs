Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c python hue_tray.py"
oShell.Run strArgs, 0, false