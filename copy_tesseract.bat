@echo off
REM Copy Tesseract from system installation to project bundle
REM Run this on Windows after installing Tesseract

echo ========================================
echo TestBuddy - Bundle Tesseract Setup
echo ========================================
echo.

set "TESSERACT_SRC=C:\Program Files\Tesseract-OCR"
set "TESSERACT_DEST=%~dp0tesseract"

if not exist "%TESSERACT_SRC%" (
    echo ERROR: Tesseract not found at %TESSERACT_SRC%
    echo.
    echo Please install Tesseract first:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

echo Creating bundle directory...
mkdir "%TESSERACT_DEST%" 2>nul
mkdir "%TESSERACT_DEST%\tessdata" 2>nul

echo.
echo Copying Tesseract files...
copy "%TESSERACT_SRC%\tesseract.exe" "%TESSERACT_DEST%\" /Y
copy "%TESSERACT_SRC%\tessdata\eng.traineddata" "%TESSERACT_DEST%\tessdata\" /Y
copy "%TESSERACT_SRC%\tessdata\osd.traineddata" "%TESSERACT_DEST%\tessdata\" /Y

echo.
echo Copying DLL dependencies...
for %%F in (
    libtesseract-5.dll
    libleptonica-1.84.1.dll
    libarchive-13.dll
    libbrotlicommon.dll
    libbrotlidec.dll
    libbz2-1.dll
    libcrypto-3-x64.dll
    libcurl-4.dll
    libdeflate.dll
    libgif-7.dll
    libiconv-2.dll
    libintl-8.dll
    libjbig-0.dll
    libjpeg-8.dll
    liblzma-5.dll
    liblzo2-2.dll
    libnettle-8.dll
    libopenjp2-7.dll
    libpng16-16.dll
    libsharpyuv-0.dll
    libssh2-1.dll
    libssl-3-x64.dll
    libtiff-6.dll
    libwebp-7.dll
    libwebpdemux-2.dll
    libwebpmux-3.dll
    libxml2-2.dll
    libzstd.dll
    zlib1.dll
) do (
    if exist "%TESSERACT_SRC%\%%F" (
        copy "%TESSERACT_SRC%\%%F" "%TESSERACT_DEST%\" /Y
    )
)

echo.
echo ========================================
echo Bundle created successfully!
echo ========================================
echo.
echo Location: %TESSERACT_DEST%
echo.
echo Next steps:
echo 1. Verify files exist in tesseract/ folder
echo 2. Run: python app_nosplash.py
echo 3. Test OCR functionality
echo 4. Build .exe: build_windows.bat
echo.
pause
