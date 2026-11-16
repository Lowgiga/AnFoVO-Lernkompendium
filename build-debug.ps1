# Build- und Pruefskript fuer das Lern-Kompendium (Android WebView-Wrapper).
#
# Aufruf:   .\build-debug.ps1
# Ergebnis:  Debug-APKs, Signaturpruefung, SHA256 je Datei und der Vergleich
#            der Web-Assets zwischen Quelle und Build-Merge-Verzeichnis.
#
# Das Skript richtet JAVA_HOME und ANDROID_HOME selbst ein, falls sie fehlen,
# und nutzt den Projekt-Wrapper (gradlew.bat) statt einer globalen Gradle-Installation.

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# ---------- Java ----------
if (-not ($env:JAVA_HOME -and (Test-Path (Join-Path $env:JAVA_HOME 'bin\java.exe')))) {
    $found = $null
    foreach ($c in @('C:\Tools\jdk-21\jdk-21.0.13+9')) {
        if (Test-Path (Join-Path $c 'bin\java.exe')) { $found = $c; break }
    }
    if (-not $found) {
        foreach ($base in @('C:\Tools', 'C:\Program Files\Java', 'C:\Program Files\Eclipse Adoptium')) {
            if (Test-Path $base) {
                $hit = Get-ChildItem $base -Directory -ErrorAction SilentlyContinue |
                    Where-Object { Test-Path (Join-Path $_.FullName 'bin\java.exe') } |
                    Select-Object -First 1 -ExpandProperty FullName
                if ($hit) { $found = $hit; break }
            }
        }
    }
    if (-not $found) { throw 'Kein JDK gefunden. JAVA_HOME auf ein JDK 21 setzen.' }
    $env:JAVA_HOME = $found
}
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# ---------- Android SDK ----------
if (-not ($env:ANDROID_HOME -and (Test-Path (Join-Path $env:ANDROID_HOME 'platforms\android-36\android.jar')))) {
    $sdk = $null
    foreach ($c in @('C:\Android', 'C:\Users\doli\Downloads\android-sdk')) {
        if (Test-Path (Join-Path $c 'platforms\android-36\android.jar')) { $sdk = $c; break }
    }
    if (-not $sdk) { throw 'Kein Android SDK mit Plattform android-36 gefunden. ANDROID_HOME setzen.' }
    $env:ANDROID_HOME = $sdk
}
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:PATH = "$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:ANDROID_HOME\platform-tools;$env:PATH"

Write-Host '=== Umgebung ==='
Write-Host ("  JAVA_HOME    : " + $env:JAVA_HOME)
Write-Host ("  ANDROID_HOME : " + $env:ANDROID_HOME)
& java -version

# ---------- Build ----------
Write-Host '=== Build (:app:assembleDebug) ==='
& .\gradlew.bat :app:assembleDebug
if ($LASTEXITCODE -ne 0) { throw 'Debug-APK-Build fehlgeschlagen.' }

# ---------- APKs pruefen ----------
$outDir = Join-Path $ProjectRoot 'app\build\outputs\apk\debug'
$signer = Join-Path $env:ANDROID_HOME 'build-tools\35.0.0\apksigner.bat'
if (-not (Test-Path $signer)) { throw ('apksigner fehlt: ' + $signer) }

$names = @('app-universal-debug.apk', 'app-arm64-v8a-debug.apk', 'app-x86_64-debug.apk')
foreach ($name in $names) {
    $apk = Join-Path $outDir $name
    if (-not (Test-Path $apk)) { Write-Host ("  FEHLT: " + $name); continue }
    & $signer verify --print-certs $apk | Out-Null
    $sig = ($LASTEXITCODE -eq 0)
    $item = Get-Item $apk
    Write-Host ("  {0,-26} {1,9} Bytes  Signatur {2}" -f $name, $item.Length, $(if ($sig) { 'OK' } else { 'FEHLER' }))
    Write-Host ("      SHA256 " + (Get-FileHash $apk -Algorithm SHA256).Hash)
}

# ---------- Web-Assets: Quelle gegen Build-Vergleich ----------
$src = Join-Path $ProjectRoot 'app\src\main\assets'
$merge = Join-Path $ProjectRoot 'app\build\intermediates\assets\debug\mergeDebugAssets'
Write-Host '=== Asset-Vergleich (Quelle gegen Merge-Verzeichnis) ==='
foreach ($f in @('index.html', 'style.css', 'app.js', 'assistent.js', 'robot-navigation.js', 'sw.js', 'manifest.json')) {
    $a = Join-Path $src $f
    $b = Join-Path $merge $f
    if ((Test-Path $a) -and (Test-Path $b)) {
        $ha = (Get-FileHash $a -Algorithm SHA256).Hash
        $hb = (Get-FileHash $b -Algorithm SHA256).Hash
        Write-Host ("  {0,-22} {1}" -f $f, $(if ($ha -eq $hb) { 'identisch' } else { 'ABWEICHUNG' }))
    }
}

Write-Host '=== Fertig ==='