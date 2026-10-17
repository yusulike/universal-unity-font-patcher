# Universal Unity Korean Font Plugin Compiler Script
$scriptDir = $PSScriptRoot
$managedDir = "E:\SteamLibrary\steamapps\common\House Flipper\HouseFlipper_Data\Managed"
$bepInExCore = "$scriptDir\template\BepInEx\core"
$pluginDir = "$scriptDir\template\BepInEx\plugins"
$outputDll = "$pluginDir\UniversalFontPlugin.dll"
$sourceFile = "$scriptDir\src\UniversalFontPlugin.cs"
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

if (-not (Test-Path $pluginDir)) {
    New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
}

Write-Host "Compiling UniversalFontPlugin.dll..." -ForegroundColor Cyan

& $csc /noconfig /target:library /nostdlib `
  /out:"$outputDll" `
  /r:"$managedDir\mscorlib.dll" `
  /r:"$managedDir\netstandard.dll" `
  /r:"$managedDir\System.dll" `
  /r:"$managedDir\System.Core.dll" `
  /r:"$bepInExCore\BepInEx.dll" `
  /r:"$managedDir\UnityEngine.dll" `
  /r:"$managedDir\UnityEngine.CoreModule.dll" `
  /r:"$managedDir\UnityEngine.TextRenderingModule.dll" `
  /r:"$managedDir\UnityEngine.UI.dll" `
  /r:"$managedDir\UnityEngine.InputLegacyModule.dll" `
  /r:"$managedDir\Unity.TextMeshPro.dll" `
  "$sourceFile"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Compilation SUCCESS -> $outputDll" -ForegroundColor Green
} else {
    Write-Host "Compilation FAILED with code $LASTEXITCODE" -ForegroundColor Red
}
