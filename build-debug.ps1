$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$env:ANDROID_HOME = 'C:\Users\doli\Downloads\android-sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME

if (-not (Get-Command java -ErrorAction SilentlyContinue)) { throw 'Java is not available.' }
if (-not (Get-Command gradle -ErrorAction SilentlyContinue)) { throw 'Gradle is not installed. Install Gradle 8.x matching Android Gradle Plugin 8.13.0.' }
if (-not (Test-Path (Join-Path $env:ANDROID_HOME 'platforms\android-36\android.jar'))) { throw 'Android SDK Platform 36 is missing.' }

java -version
gradle --version
gradle --no-daemon :app:assembleDebug
if ($LASTEXITCODE -ne 0) { throw 'Debug APK build failed.' }

$Apk = Join-Path $ProjectRoot 'app\build\outputs\apk\debug\app-debug.apk'
if (-not (Test-Path $Apk)) { throw 'Debug APK was not created.' }

$Signer = Join-Path $env:ANDROID_HOME 'build-tools\35.0.0\apksigner.bat'
if (-not (Test-Path $Signer)) { throw 'apksigner is missing.' }
& $Signer verify --verbose --print-certs $Apk
if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed.' }

Get-FileHash $Apk -Algorithm SHA256 | Format-List
Get-Item $Apk | Select-Object FullName, Length, LastWriteTime | Format-List
