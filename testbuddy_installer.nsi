; TestBuddy Windows Installer Script
; ====================================
; NSIS (Nullsoft Scriptable Install System) script for creating
; a professional Windows installer for TestBuddy.
;
; Requirements:
;   - NSIS installed: https://nsis.sourceforge.io/Download
;   - TestBuddy.exe built in dist/ folder
;
; Usage:
;   Right-click this file → "Compile NSIS Script"
;   Output: TestBuddy-Setup.exe

!include "MUI2.nsh"

; ===== General Configuration =====
Name "TestBuddy"
OutFile "TestBuddy-Setup.exe"
InstallDir "$PROGRAMFILES\TestBuddy"
InstallDirRegKey HKCU "Software\TestBuddy" ""
RequestExecutionLevel admin

; ===== Version Information =====
VIProductVersion "3.0.0.0"
VIAddVersionKey "ProductName" "TestBuddy"
VIAddVersionKey "CompanyName" "TestBuddy Development Team"
VIAddVersionKey "LegalCopyright" "Copyright 2025"
VIAddVersionKey "FileDescription" "TestBuddy OCR Workbench Installer"
VIAddVersionKey "FileVersion" "3.0.0.0"

; ===== Modern UI Configuration =====
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; If you have a custom icon, replace above with:
; !define MUI_ICON "icon.ico"
; !define MUI_UNICON "icon.ico"

; ===== Installer Pages =====
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"  ; Create LICENSE.txt if needed
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; ===== Uninstaller Pages =====
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ===== Language =====
!insertmacro MUI_LANGUAGE "English"

; ===== Installation Section =====
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy main executable
  File "dist\TestBuddy.exe"
  
  ; Copy additional files if needed (config templates, docs, etc.)
  ; File "testbuddy.ini.template"
  ; File "README_V2.md"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\TestBuddy"
  CreateShortcut "$SMPROGRAMS\TestBuddy\TestBuddy.lnk" "$INSTDIR\TestBuddy.exe" "" "$INSTDIR\TestBuddy.exe" 0
  CreateShortcut "$SMPROGRAMS\TestBuddy\Uninstall TestBuddy.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\TestBuddy.lnk" "$INSTDIR\TestBuddy.exe" "" "$INSTDIR\TestBuddy.exe" 0
  
  ; Write registry keys for uninstaller
  WriteRegStr HKCU "Software\TestBuddy" "" "$INSTDIR"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add to Windows Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                   "DisplayName" "TestBuddy - OCR Workbench"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                   "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                   "DisplayIcon" "$INSTDIR\TestBuddy.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                   "Publisher" "TestBuddy Development Team"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                   "DisplayVersion" "3.0.0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                     "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy" \
                     "NoRepair" 1
  
  ; File associations (optional - uncomment to associate .testbuddy files)
  ; WriteRegStr HKCR ".testbuddy" "" "TestBuddyFile"
  ; WriteRegStr HKCR "TestBuddyFile" "" "TestBuddy Session File"
  ; WriteRegStr HKCR "TestBuddyFile\DefaultIcon" "" "$INSTDIR\TestBuddy.exe,0"
  ; WriteRegStr HKCR "TestBuddyFile\shell\open\command" "" '"$INSTDIR\TestBuddy.exe" "%1"'
  
SectionEnd

; ===== Uninstallation Section =====
Section "Uninstall"
  ; Remove executable and files
  Delete "$INSTDIR\TestBuddy.exe"
  Delete "$INSTDIR\Uninstall.exe"
  ; Delete "$INSTDIR\testbuddy.ini.template"
  ; Delete "$INSTDIR\README_V2.md"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\TestBuddy\TestBuddy.lnk"
  Delete "$SMPROGRAMS\TestBuddy\Uninstall TestBuddy.lnk"
  RMDir "$SMPROGRAMS\TestBuddy"
  Delete "$DESKTOP\TestBuddy.lnk"
  
  ; Remove installation directory
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\TestBuddy"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TestBuddy"
  
  ; Remove file associations (if enabled)
  ; DeleteRegKey HKCR ".testbuddy"
  ; DeleteRegKey HKCR "TestBuddyFile"
  
SectionEnd

; ===== Post-Installation Messages =====
Function .onInstSuccess
  MessageBox MB_OK "TestBuddy has been successfully installed!$\n$\nYou can now launch it from the Start Menu or Desktop shortcut.$\n$\nIMPORTANT: TestBuddy requires Tesseract OCR to be installed separately.$\nDownload from: https://github.com/UB-Mannheim/tesseract/wiki"
FunctionEnd
