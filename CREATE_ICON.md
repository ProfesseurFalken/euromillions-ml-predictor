# 🎯 Create Desktop Icon for EuroMillions ML

## 🚀 Quick Methods

### Method 1: PowerShell Script (Recommended)
**Easiest method with most features**

1. **Double-click**: `create_shortcut.ps1`
   - Creates desktop icon automatically
   - Uses custom icon if available
   - Falls back to Python icon

### Method 2: VBScript
**Works on all Windows versions**

1. **Double-click**: `create_shortcut.vbs`
   - Creates desktop icon
   - Simple and reliable

### Method 3: Manual Creation
**Full control over icon customization**

1. **Right-click on Desktop** → New → Shortcut
2. **Browse to**: `E:\Python\_Ai\Ai_Euromillions v4\launch_quick.bat`
3. **Name it**: "EuroMillions ML"
4. **Click Finish**
5. **Right-click shortcut** → Properties
6. **Click "Change Icon"**
7. **Browse to** your custom .ico file (or use default)
8. **Click OK**

## 🎨 Custom Icon (Optional)

### Download/Create an Icon:
1. **Find a lottery/euro icon** online (.ico format)
2. **Save it as**: `icon.ico` in the project folder
3. **Run** `create_shortcut.ps1` again

### Free Icon Resources:
- https://icons8.com (search "lottery" or "euro")
- https://www.flaticon.com (search "lottery")
- https://iconarchive.com

### Convert PNG to ICO:
- Online: https://convertico.com
- Or use GIMP/Photoshop

## 📌 Pin to Taskbar/Start Menu

Once you have the desktop shortcut:

### Pin to Taskbar:
1. **Right-click** the desktop icon
2. Select **"Pin to taskbar"**

### Pin to Start Menu:
1. **Right-click** the desktop icon
2. Select **"Pin to Start"**

## 🔧 Troubleshooting

### "Cannot run scripts" error:
```powershell
# Run this in PowerShell as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Icon doesn't appear:
- Make sure `icon.ico` is in the project folder
- Right-click shortcut → Properties → Change Icon → Browse

### Shortcut doesn't work:
- Verify the target path is correct
- Make sure `launch_quick.bat` exists
- Try Method 3 (manual creation)

## 🎯 What the Icon Does

When you double-click the icon:
1. ✅ Activates virtual environment
2. ✅ Finds available port (8501-8505)
3. ✅ Launches Streamlit interface
4. ✅ Opens browser automatically
5. ✅ Ready to generate predictions!

---

**Happy predicting! 🍀**
