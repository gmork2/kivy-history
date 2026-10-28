#!/usr/bin/env bash
# Build a kivy-history sample AppImage from the PyInstaller onefile binary.
set -euo pipefail

BIN="${1:-dist/kivy-history-sample}"
OUT="${2:-kivy-history-sample-x86_64.AppImage}"
APP="kivy-history-sample"
WORK="build/appdir"

rm -rf "$WORK"
mkdir -p "$WORK/usr/bin"

cp "$BIN" "$WORK/usr/bin/$APP"
cp assets/icon.png "$WORK/$APP.png"

cat > "$WORK/$APP.desktop" <<EOF
[Desktop Entry]
Name=kivy-history sample
Comment=Demo reader of the kivy-history API
Exec=$APP
Icon=$APP
Type=Application
Categories=Development;Utility;
EOF

cat > "$WORK/AppRun" <<EOF
#!/bin/sh
HERE="\$(dirname "\$(readlink -f "\$0")")"
exec "\$HERE/usr/bin/$APP" "\$@"
EOF
chmod +x "$WORK/AppRun" "$WORK/usr/bin/$APP"

TOOL="build/appimagetool.AppImage"
if [ ! -f "$TOOL" ]; then
    curl -fL -o "$TOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$TOOL"
fi

ARCH=x86_64 "$TOOL" --appimage-extract-and-run "$WORK" "$OUT"
echo "Built $OUT"
