!include "MUI2.nsh"

Name "TestBuddy"
OutFile "TestBuddy-Setup.exe"
InstallDir "$PROGRAMFILES\\TestBuddy"

!define PRODUCT_EXE "TestBuddy.exe"
!define PRODUCT_NAME "TestBuddy"
!define PRODUCT_PUBLISHER "TestBuddy"
!define EXE_SOURCE "Testbuddy\\dist\\TestBuddy.exe"

!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Var StartMenuFolder

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy the executable
  File /oname=${PRODUCT_EXE} "${EXE_SOURCE}"

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\\${PRODUCT_NAME}\\${PRODUCT_NAME}.lnk" "$INSTDIR\\${PRODUCT_EXE}"
  CreateShortCut "$DESKTOP\\${PRODUCT_NAME}.lnk" "$INSTDIR\\${PRODUCT_EXE}"

  ; Optional: register file association for .tbd (TestBuddy session)
  WriteRegStr HKCR ".tbd" "" "${PRODUCT_NAME}.session"
  WriteRegStr HKCR "${PRODUCT_NAME}.session" "" "TestBuddy Session"
  WriteRegStr HKCR "${PRODUCT_NAME}.session\\shell\\open\\command" "" '"$INSTDIR\\${PRODUCT_EXE}"" "%1"'

SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\${PRODUCT_EXE}"
  Delete "$SMPROGRAMS\\${PRODUCT_NAME}\\${PRODUCT_NAME}.lnk"
  Delete "$DESKTOP\\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\\${PRODUCT_NAME}"
  RMDir "$INSTDIR"
  DeleteRegKey HKCR ".tbd"
  DeleteRegKey HKCR "${PRODUCT_NAME}.session"
SectionEnd
