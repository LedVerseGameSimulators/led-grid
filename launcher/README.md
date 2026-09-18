# LED Grid launcher

Build the operator `LED Grid.exe` on Windows with PyInstaller:

```bat
pip install pyinstaller
pyinstaller launcher/LED_Grid.spec --noconfirm
```

The executable is written to `dist/LED Grid.exe`. Place it next to `START_GAME.bat` in the release folder (or use the GitHub Actions `Package Windows` workflow on a `v*` tag).
