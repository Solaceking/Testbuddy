TestBuddy - Distribution & Signing Guide
========================================

Purpose
-------
This guide explains exactly how to produce signed, installable Windows artifacts for TestBuddy and how to configure the CI pipeline to produce release builds and signed installers.

What we added for you
---------------------
- `build_windows.ps1` / `build_windows.bat` — build the EXE (PyInstaller) and compile NSIS installer (if `makensis` is available).
- `testbuddy_installer.nsi` — NSIS installer script (references `dist/TestBuddy.exe`).
- GitHub Actions workflow: `.github/workflows/windows_build.yml` that:
  - Installs dependencies
  - Runs tests
  - Builds EXE and runs NSIS (on Windows runner)
  - Generates `CHECKSUMS.txt` (SHA256)
  - Uploads artifacts
  - Optionally signs artifacts if signing secrets are present
  - Creates a GitHub Release and attaches artifacts

Requirements before distribution
--------------------------------
1. Windows code signing certificate (PFX) with private key.
   - Obtain from a CA (DigiCert, Sectigo, GlobalSign). EV certificates are recommended for broad trust.
2. GitHub repo-level secrets (to enable automatic signing):
   - `SIGN_CERT_PFX` — base64-encoded contents of the PFX file
   - `SIGN_CERT_PASSWORD` — password for the PFX

How to create the base64 PFX secret (PowerShell)
------------------------------------------------
Run locally and copy the output into the `SIGN_CERT_PFX` secret value in GitHub:

```powershell
$bytes = [System.IO.File]::ReadAllBytes('C:\path\to\your-cert.pfx')
$base64 = [Convert]::ToBase64String($bytes)
# Save temporarily
Set-Content -Path C:\tmp\cert.pfx.b64 -Value $base64
# Open the file and copy-paste the single-line content into the repo secret
notepad C:\tmp\cert.pfx.b64
```

Add the PFX password as `SIGN_CERT_PASSWORD` in GitHub Secrets.

Signing options supported in the workflow
----------------------------------------
- `osslsigncode` (open-source): used on Windows runner (installed via Chocolatey). Works with PFX.
- `signtool` (Microsoft): preferred for EV certs / MS recommended signing. If you prefer `signtool`, you can modify the workflow to call `signtool` instead; it requires the Windows SDK or a runner that has `signtool.exe` available.

How to trigger a release build
------------------------------
- Option A: Push a commit to `main` branch (workflow runs automatically)
- Option B: Run `Build Windows` workflow manually from the Actions UI (workflow_dispatch)

How the workflow produces artifacts
-----------------------------------
1. `pyinstaller` creates `dist/TestBuddy.exe` (one-file, windowed).
2. NSIS compiles `TestBuddy-Setup.exe` if `makensis` is available on the runner.
3. `CHECKSUMS.txt` is produced with SHA256 lines for each artifact.
4. Optional signing step (if secrets present) produces `*-signed.exe` variants.
5. The release flow creates a tag like `vYYYYMMDD-<run_number>` and publishes a Release, attaching artifacts and `CHECKSUMS.txt`.

Manual verification steps (recommended)
--------------------------------------
- Download artifacts from the workflow run or Release.
- Verify SHA256 matches the values in `CHECKSUMS.txt`:
  ```powershell
  Get-FileHash .\TestBuddy-Setup.exe -Algorithm SHA256
  Get-Content CHECKSUMS.txt
  ```
- Install on a clean VM (Windows 10/11) and verify:
  - App launches
  - Sessions load
  - Export features work (PDF, DOCX, CSV, HTML, Markdown, JSON, TXT)
  - Document Intelligence analyze works (with Tesseract installed)
  - Uninstall removes program files

If you want to use `signtool` instead of `osslsigncode`
------------------------------------------------------
- Upload PFX as repo secret as above.
- Modify the workflow step `Optional: Sign artifacts` to call `signtool.exe sign /f cert.pfx /p <password> /tr http://timestamp.digicert.com /td sha256 /fd sha256 <file>`
- On hosted runners, `signtool` may not be present. You'll need either to install Windows SDK in the runner (adds time), or use a self-hosted Windows runner that has `signtool` installed and your signing cert available.

Recommended post-release steps
------------------------------
- Sign all binaries and installer before publishing to avoid "Unknown Publisher" warnings.
- Consider using an official code-signing service or HSM for private key security.
- Publish checksums on the website and in the release notes.
- For automated distribution, consider pushing artifacts to a CDN or S3 bucket and use the installer to fetch updates.

Support and troubleshooting
-------------------------
If a workflow fails:
- Open the Actions run and expand logs for the failing step.
- For signing issues, ensure the PFX is valid and not password-protected with non-ASCII characters that could break environment handling.
- For NSIS errors, ensure makensis is available and the path to the EXE referenced in `testbuddy_installer.nsi` matches the build output.

Contact
-------
If you'd like, I can:
- Switch the workflow to use `signtool` and/or a self-hosted signing runner.
- Add automatic changelog generation using Conventional Commits or `release-drafter`.
- Add an auto-update server or mechanism.

*** End of guide ***
