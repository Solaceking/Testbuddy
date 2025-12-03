Icon File Creation Instructions
================================

Since we're in a Linux environment, we can't create a proper .ico file here.

To create icon.ico for Windows:

OPTION 1: Use an online converter
1. Create a 256x256 PNG image with TestBuddy logo/icon
2. Upload to: https://www.icoconverter.com/ or https://favicon-generator.org
3. Download as icon.ico
4. Place in project root: /home/user/webapp/icon.ico

OPTION 2: Use GIMP (free)
1. Create 256x256 image in GIMP
2. Export As → icon.ico
3. Select ICO format with multiple sizes (16, 32, 48, 256)

OPTION 3: Use ImageMagick (command line)
convert -resize 256x256 logo.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

For now, PyInstaller will build without an icon if icon.ico is missing.
