#!/usr/bin/env bash
set -e

export MSYS2_ARG_CONV_EXCL="*"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANAGED="E:\\SteamLibrary\\steamapps\\common\\House Flipper\\HouseFlipper_Data\\Managed"
BEPINEX_CORE=$(cygpath -w "$SCRIPT_DIR/template/BepInEx/core")
PLUGIN_DIR=$(cygpath -w "$SCRIPT_DIR/template/BepInEx/plugins")
OUT_DLL="$PLUGIN_DIR\\UniversalFontPlugin.dll"
SRC=$(cygpath -w "$SCRIPT_DIR/src/UniversalFontPlugin.cs")
CSC="/c/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe"

mkdir -p "$SCRIPT_DIR/template/BepInEx/plugins"

echo "Compiling UniversalFontPlugin.dll..."
"$CSC" -noconfig -target:library -nostdlib \
  -out:"$OUT_DLL" \
  -r:"$MANAGED\\mscorlib.dll" \
  -r:"$MANAGED\\netstandard.dll" \
  -r:"$MANAGED\\System.dll" \
  -r:"$MANAGED\\System.Core.dll" \
  -r:"$BEPINEX_CORE\\BepInEx.dll" \
  -r:"$MANAGED\\UnityEngine.dll" \
  -r:"$MANAGED\\UnityEngine.CoreModule.dll" \
  -r:"$MANAGED\\UnityEngine.TextRenderingModule.dll" \
  -r:"$MANAGED\\UnityEngine.UI.dll" \
  -r:"$MANAGED\\UnityEngine.InputLegacyModule.dll" \
  -r:"$MANAGED\\Unity.TextMeshPro.dll" \
  "$SRC"

if [ -f "$SCRIPT_DIR/template/BepInEx/plugins/UniversalFontPlugin.dll" ]; then
  echo "Compilation SUCCESS! Output:"
  ls -lh "$SCRIPT_DIR/template/BepInEx/plugins/UniversalFontPlugin.dll"
else
  echo "Compilation FAILED!"
  exit 1
fi
