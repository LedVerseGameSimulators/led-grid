# Build the Grid operator package with Nuitka on Windows (CI: windows-latest).
# ONE exe with roles: supervisor / --role api|bridge / --selftest / --stop.
# usage:  powershell -File packaging\build_nuitka_windows.ps1 [-Tag v1.2.3]
param([string]$Tag = "dev")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ExeName = "LED Grid"
python -m pip install -q -U pip wheel
python -m pip install -q nuitka ordered-set zstandard
python -m pip install -q -r api/requirements.txt

Push-Location frontend
npm ci --silent
npm run build
Pop-Location

$Out = Join-Path $Root "dist\nuitka"
if (Test-Path $Out) { Remove-Item -Recurse -Force $Out }
New-Item -ItemType Directory -Force $Out | Out-Null

$env:PYTHONPATH = "$Root;$Root\games"

# api.game_manager mocks these via sys.modules (GUI, dongle check, mysql, ...): never bundle.
$NoFollow = @("tkinter","numpy","PIL","cv2","moviepy","pynput","rsa","Crypto","mysql","encryption","gui","gui2","ui_design","net")
$NuitkaArgs = @(
  "--standalone", "--assume-yes-for-downloads",
  "--output-dir=$Out", "--output-filename=$ExeName",
  "--include-package=api", "--include-package=floor_launcher",
  "--include-module=ws_bridge",
  "--include-package=fastapi", "--include-package=starlette", "--include-package=uvicorn",
  "--include-package=pydantic", "--include-package=pydantic_core", "--include-package=websockets",
  "--include-package=httpx", "--include-package=httpcore", "--include-package=anyio",
  "--include-package=h11", "--include-package=loguru", "--include-package=dotenv",
  "--include-package=serial", "--include-package=pygame",
  "--include-package=game_play", "--include-package=led", "--include-package=model",
  "--include-package=model_in", "--include-package=audio_play", "--include-package=database",
  "--include-package=util", "--include-module=shelve", "--include-module=dbm.dumb", "--nofollow-import-to=pygame.tests"
)
foreach ($m in $NoFollow) { $NuitkaArgs += "--nofollow-import-to=$m" }
$NuitkaArgs += "floor_launcher/entry.py"

python -m nuitka @NuitkaArgs
if ($LASTEXITCODE -ne 0) { throw "Nuitka failed" }

$Stage = Join-Path $Root "dist\release\LED-Grid-$Tag-windows"
python packaging/stage_release.py $Stage (Join-Path $Out "entry.dist")
if ($LASTEXITCODE -ne 0) { throw "staging failed" }

$Zip = "$Stage-nuitka.zip"
if (Test-Path $Zip) { Remove-Item $Zip }
Compress-Archive -Path $Stage -DestinationPath $Zip
Write-Host "Wrote $Zip"
