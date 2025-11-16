# PowerShell script to create desktop shortcut for EuroMillions ML
# Run this script to create a desktop icon

$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "EuroMillions ML.lnk"
$TargetPath = Join-Path $PSScriptRoot "launch_quick.bat"
$IconPath = Join-Path $PSScriptRoot "icon.ico"

# Create the shortcut
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "EuroMillions ML Prediction System"
$Shortcut.WindowStyle = 1  # Normal window

# Set icon if it exists, otherwise use default
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
}
else {
    # Use Python icon as fallback
    $PythonPath = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonPath) {
        $Shortcut.IconLocation = $PythonPath.Source
    }
}

$Shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SHORTCUT CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "  1. Double-click the desktop icon to launch" -ForegroundColor White
Write-Host "  2. Pin it to taskbar (right-click → Pin to taskbar)" -ForegroundColor White
Write-Host "  3. Pin to Start menu" -ForegroundColor White
Write-Host ""

# Ask if user wants to customize the icon
Write-Host "TIP: To add a custom icon:" -ForegroundColor Yellow
Write-Host "  1. Save a .ico file as 'icon.ico' in the project folder" -ForegroundColor White
Write-Host "  2. Run this script again" -ForegroundColor White
Write-Host ""
