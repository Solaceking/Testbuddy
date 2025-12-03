# Activity Log Viewer - Test Guide

## ✅ What's New

### **Collapsible Activity Log at Bottom of Window**

```
┌────────────────────────────────────────────┐
│         MAIN APP CONTENT                   │
│                                            │
├────────────────────────────────────────────┤
│ ▶ Show Activity Log  |  Ready  [Copy] [Clear] │  ← Click to expand
└────────────────────────────────────────────┘
```

**When expanded:**
```
┌────────────────────────────────────────────┐
│         MAIN APP CONTENT                   │
├────────────────────────────────────────────┤
│ ▼ Hide Activity Log  | Logs: 45 | Errors: 2  [Copy All] [Clear] │
├────────────────────────────────────────────┤
│ Filter: [ALL ▼]           [Auto-scroll: ON]│
│ ┌──────────────────────────────────────┐  │
│ │ [10:23:15] [INFO    ] OCR: Started   │  │
│ │ [10:23:17] [ERROR   ] OCR: Failed    │  │ ← Color coded!
│ │   error: Tesseract not found         │  │ ← Full details
│ │ [10:23:20] [INFO    ] SESSION: Saved │  │
│ └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

---

## 🎯 Features

### 1. **Auto-Expands on Error**
   - When OCR fails, log viewer automatically opens
   - Shows full error message with all details
   - No more "uncopyable" errors!

### 2. **Copy to Clipboard**
   - Click "Copy All" button
   - All logs copied as plain text
   - Easy to paste into email, support ticket, etc.

### 3. **Color Coding**
   - 🔴 **Red** = ERROR/CRITICAL
   - 🟠 **Orange** = WARNING
   - 🟢 **Green** = INFO
   - ⚪ **Gray** = DEBUG

### 4. **Filter by Level**
   - Dropdown: ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Only show specific types of logs

### 5. **Auto-Scroll**
   - Toggle button: "Auto-scroll: ON/OFF"
   - When ON: automatically scrolls to latest log
   - When OFF: stays at current position

### 6. **Clear Logs**
   - Click "Clear" button
   - Removes all logs from display
   - Starts fresh

---

## 🧪 Test Steps

### Pull Latest Code:
```powershell
cd C:\Users\idavi\Documents\Projects\testbuddy\Testbuddy
git pull origin feature/native-windows-build
```

### Run the App:
```powershell
python app_nosplash.py
```

### Test 1: See the Log Viewer
1. App opens
2. Look at **bottom of window**
3. Should see gray bar: "▶ Show Activity Log"
4. **Click it** to expand

**Expected:**
- Log viewer expands downward
- Shows activity logs
- Button changes to "▼ Hide Activity Log"

---

### Test 2: Test Error Logging (Tesseract Not Installed)

1. Click "+ New Session"
2. Enter name, click OK
3. Click the **BIG BLUE CAPTURE BUTTON**
4. Take a screenshot
5. Wait...

**Expected if Tesseract NOT installed:**
- Error popup appears with message
- **Log viewer AUTO-EXPANDS**
- Shows error in RED with full details
- Can click "Copy All" to copy error

**Expected if Tesseract IS installed:**
- OCR processes normally
- Text appears
- Log shows in GREEN: "OCR complete"

---

### Test 3: Copy Logs

1. Expand log viewer (if not already)
2. Click "**Copy All**" button
3. Button should change to "✓ Copied!" briefly
4. Open Notepad
5. Paste (Ctrl+V)

**Expected:**
- All logs pasted as plain text
- Format:
  ```
  [2025-12-03T10:23:15] [INFO    ] APPLICATION: TestBuddy starting
  [2025-12-03T10:23:17] [ERROR   ] OCR: OCR processing failed
    error_type: TesseractNotFoundError
    error_message: Tesseract not found
  ```

---

### Test 4: Filter Logs

1. Expand log viewer
2. Click "Filter:" dropdown
3. Select "ERROR"

**Expected:**
- Only ERROR and CRITICAL logs shown
- Other logs hidden
- Count updates

Try:
- ALL (shows everything)
- INFO (only info logs)
- WARNING (only warnings)

---

### Test 5: Auto-Scroll

1. Expand log viewer
2. Scroll UP to read older logs
3. Notice "Auto-scroll: ON" button
4. Click it to turn OFF

**Expected:**
- Button turns gray: "Auto-scroll: OFF"
- New logs appear but window doesn't scroll
- You stay at current position

Click again to turn back ON:
- Button turns green: "Auto-scroll: ON"
- Window scrolls to bottom with new logs

---

### Test 6: Clear Logs

1. Expand log viewer
2. See some logs displayed
3. Click "**Clear**" button (red)

**Expected:**
- All logs disappear
- Display is empty
- Counter resets: "Logs: 0 | Errors: 0 | Warnings: 0"

---

## 📊 What Logs Show

### Application Logs:
```
[10:20:00] [INFO] APPLICATION: TestBuddy starting
  version: 3.0
  platform: Windows
```

### Session Logs:
```
[10:21:05] [INFO] SESSION: Session created
  session_id: abc123
  session_name: My Test Session
```

### OCR Logs (Success):
```
[10:22:10] [INFO] OCR: OCR processing started
  image_width: 1920
  image_height: 1080
  language: eng
[10:22:15] [INFO] OCR: OCR processing completed
  text_length: 245
  duration_ms: 4523.5
```

### OCR Logs (Error):
```
[10:23:00] [ERROR] OCR: Dependency check failed
  error: Tesseract OCR binary not found!

Please install Tesseract from:
https://github.com/UB-Mannheim/tesseract/wiki

Expected location: C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## 🎨 Visual Design

### Colors:
- **Background:** Dark terminal (#1C1C1E)
- **Text:** Matrix green (#00FF00)
- **Errors:** Red (#FF3B30)
- **Warnings:** Orange (#FF9500)
- **Info:** Green (#00FF00)
- **Details:** Cyan (#5AC8FA)

### Buttons:
- **Copy All:** Blue (#007AFF)
- **Clear:** Red (#FF3B30)
- **Auto-scroll ON:** Green (#34C759)
- **Auto-scroll OFF:** Gray (#8E8E93)

---

## ✅ Success Checklist

Test and check off:

- [ ] Log viewer bar visible at bottom
- [ ] Clicking "Show" expands it
- [ ] Logs appear in real-time
- [ ] Errors show in RED
- [ ] Can copy all logs to clipboard
- [ ] Filter dropdown works
- [ ] Auto-scroll toggle works
- [ ] Clear button empties logs
- [ ] When OCR errors, viewer auto-expands
- [ ] Full error details visible and copyable

---

## 🐛 Troubleshooting

### Log viewer doesn't show?
- Make sure you pulled latest code
- Check branch: `git branch` (should show `feature/native-windows-build`)
- Check commit: `git log --oneline -1` (should mention "collapsible activity log")

### Logs not updating?
- They update every 500ms
- Try triggering an action (click capture, save, etc.)
- Check if auto-scroll is ON

### Copy button doesn't work?
- Requires `pyperclip` module
- Should be installed in requirements.txt
- Try: `pip install pyperclip`

---

## 📁 Files Created

- `log_viewer.py` - Log viewer widget (400 lines)
- `logger.py` - Activity logger (already created)
- `app.py` - Updated to include log viewer

---

## 🚀 Next Steps

If log viewer works:

1. **Test full workflow:**
   - Create session
   - Capture screenshot
   - If error → logs show details
   - Copy logs
   - Paste and verify

2. **Build executable:**
   ```powershell
   .\build_windows.bat
   ```

3. **Test .exe:**
   ```powershell
   .\dist\TestBuddy.exe
   ```
   - Check if log viewer works in .exe
   - Test copy functionality

4. **Report back:**
   - Does it help with debugging?
   - Can you copy the Tesseract error now?
   - Any improvements needed?

---

**Status:** Ready to test! 🎉  
**Branch:** `feature/native-windows-build`  
**Key Feature:** No more uncopyable errors - full log access!

---

*Log viewer test guide - December 3, 2025*
