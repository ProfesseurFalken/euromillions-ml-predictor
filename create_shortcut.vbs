' VBScript to create desktop shortcut for EuroMillions ML
' Alternative method that works on all Windows versions

Set WshShell = WScript.CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get paths
Desktop = WshShell.SpecialFolders("Desktop")
ScriptPath = FSO.GetParentFolderName(WScript.ScriptFullName)
ShortcutPath = Desktop & "\EuroMillions ML.lnk"
TargetPath = ScriptPath & "\launch_quick.bat"
IconPath = ScriptPath & "\icon.ico"

' Create shortcut
Set Shortcut = WshShell.CreateShortcut(ShortcutPath)
Shortcut.TargetPath = TargetPath
Shortcut.WorkingDirectory = ScriptPath
Shortcut.Description = "EuroMillions ML Prediction System"
Shortcut.WindowStyle = 1

' Set icon if exists
If FSO.FileExists(IconPath) Then
    Shortcut.IconLocation = IconPath
End If

Shortcut.Save

' Show success message
WScript.Echo "Desktop shortcut created successfully!" & vbCrLf & vbCrLf & _
             "Location: " & ShortcutPath & vbCrLf & vbCrLf & _
             "Double-click the icon to launch EuroMillions ML"
