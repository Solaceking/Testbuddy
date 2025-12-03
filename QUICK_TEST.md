# Quick Test Guide - Prominent Capture Button

## ✅ What Changed

### 1. **Big Round Capture Button**
- **Size:** 300px wide × 70px tall
- **Color:** Apple Blue (#007AFF)
- **Shape:** Fully rounded (35px border radius)
- **Position:** Top of workbench, centered
- **Text:** "CAPTURE SCREENSHOT" in white, bold, 16px

### 2. **Clean Toolbar** (No Emojis)
- Undo, Redo, Save, Export, Zoom +, Zoom -, Fit
- All text-only, professional appearance

### 3. **Better OCR Errors**
- Checks if Tesseract is installed
- Shows helpful error messages with instructions
- Tells you exactly where to download Tesseract
- Activity log tracks everything

---

## 🧪 Test On Windows

### Step 1: Pull Latest
```powershell
cd C:\Users\idavi\Documents\Projects\testbuddy\Testbuddy
git pull origin feature/native-windows-build
```

### Step 2: Run App
```powershell
python app_nosplash.py
```

### Step 3: Test The Button

1. **Click "+ New Session"**
   - Enter name: "Test Capture"
   - Click OK

2. **Look for the BIG BLUE BUTTON**
   - Should be at the top, impossible to miss
   - Says "CAPTURE SCREENSHOT"
   - Blue, round, prominent

3. **Click the Capture Button**
   - Windows Snipping Tool should launch
   - Take a screenshot of some text
   - It auto-copies to clipboard

4. **Wait for OCR**
   - If Tesseract is installed: Text appears
   - If Tesseract is NOT installed: Error popup with instructions

---

## 🔧 If OCR Fails

You'll see a detailed error message like:

```
Tesseract OCR binary not found!

Please install Tesseract from:
https://github.com/UB-Mannheim/tesseract/wiki

Expected location: C:\Program Files\Tesseract-OCR\tesseract.exe

After installation, restart TestBuddy.
```

### Fix:
1. Click the link in the error message
2. Download Tesseract installer
3. Install to default location
4. Restart TestBuddy
5. Try again

---

## 📸 What You Should See

### Home Page:
```
┌────────────────────────────────────┐
│  [+ New Session]                   │
├────────────────────────────────────┤
│  Search: [.................]        │
│  Filter: [All Categories ▼]        │
├────────────────────────────────────┤
│  Recent Sessions                    │
│  ┌──────────────────────────────┐ │
│  │                              │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

### Workbench Page:
```
┌─────────────────────────────────────────┐
│                                         │
│        ┌─────────────────────┐         │
│        │  CAPTURE SCREENSHOT │  ← BIG! │
│        └─────────────────────┘         │
│                                         │
│  [Undo] [Redo]  [Save] [Export]       │
│  [Zoom +] [Zoom -] [Fit]              │
├─────────────────────────────────────────┤
│  Image Panel   │   Text Editor         │
│                │                        │
│                │                        │
└─────────────────────────────────────────┘
```

---

## ✅ Success Criteria

### The button should be:
- ✅ Large and impossible to miss
- ✅ Blue and professional
- ✅ Round and modern
- ✅ At the top, centered
- ✅ Changes color on hover (darker blue)

### OCR should:
- ✅ Give clear error if Tesseract missing
- ✅ Tell you where to download it
- ✅ Work normally if Tesseract installed

---

## 📝 Test Checklist

Run through this:

- [ ] App launches without errors
- [ ] Home page shows
- [ ] Can create new session
- [ ] BIG BLUE BUTTON is visible and prominent
- [ ] Button turns darker blue on hover
- [ ] Clicking button launches Snipping Tool
- [ ] After screenshot, either:
  - [ ] Text appears in editor (Tesseract working)
  - [ ] Error popup with instructions (Tesseract missing)
- [ ] Activity log file created: `testbuddy_activity.log`

---

## 🐛 If Something's Wrong

### Button not showing?
- Make sure you pulled latest code
- Check you're on `feature/native-windows-build` branch
- Run: `git log --oneline -1` (should show "feat: Add prominent round capture button")

### App crashes?
- Run: `python app_debug.py`
- Check output for errors

### OCR still just says "failed"?
- Check `testbuddy_activity.log` file
- Should have detailed error info

---

## 🚀 Next Steps

If everything works:

1. **Build the .exe:**
   ```powershell
   .\build_windows.bat
   ```

2. **Test the executable:**
   ```powershell
   .\dist\TestBuddy.exe
   ```

3. **Create installer** (if you have NSIS):
   - Right-click `testbuddy_installer.nsi`
   - Compile NSIS Script

---

## 📊 What Changed (Technical)

```python
# OLD:
self.btn_capture = QPushButton("📷 Capture")

# NEW:
self.btn_capture = QPushButton("CAPTURE SCREENSHOT")
self.btn_capture.setStyleSheet("""
    QPushButton {
        background-color: #007AFF;  /* Apple Blue */
        color: white;
        border-radius: 35px;        /* Fully round */
        min-width: 300px;
        min-height: 70px;
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0051D5;  /* Darker on hover */
    }
""")
```

```python
# OLD OCR:
self.worker = OCRWorker()  # Basic, no error handling

# NEW OCR:
self.worker = OCRWorkerFixed(config)  # Robust error handling
```

---

**Status:** Ready to test! 🎉  
**Branch:** `feature/native-windows-build`  
**Files Changed:** `app.py`, `logger.py`, `ocr_fixed.py`, `design_system.py`

---

*Quick test guide - December 3, 2025*
