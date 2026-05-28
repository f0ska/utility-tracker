#!/usr/bin/env bash
set -euo pipefail

APP_ID="io.github.f0ska.utilitytracker"
APP_NAME="Комуналка"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="${SCRIPT_DIR}/app.py"
ICON_SOURCE="${SCRIPT_DIR}/icon.svg"

APPLICATIONS_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || true)"

if [[ -z "${DESKTOP_DIR}" || ! -d "${DESKTOP_DIR}" ]]; then
    DESKTOP_DIR="${HOME}/Desktop"
fi

DESKTOP_FILE="${APPLICATIONS_DIR}/${APP_ID}.desktop"
DESKTOP_SHORTCUT="${DESKTOP_DIR}/${APP_ID}.desktop"
ICON_TARGET="${ICON_DIR}/${APP_ID}.svg"

mkdir -p "${APPLICATIONS_DIR}" "${ICON_DIR}" "${DESKTOP_DIR}"

install -m 0644 "${ICON_SOURCE}" "${ICON_TARGET}"

cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=Track utility readings, bills, payments, and tariffs
Exec=python3 "${APP_PATH}"
Icon=${ICON_TARGET}
Terminal=false
Categories=Utility;GTK;
StartupNotify=true
StartupWMClass=${APP_ID}
EOF

chmod 0755 "${DESKTOP_FILE}"
cp "${DESKTOP_FILE}" "${DESKTOP_SHORTCUT}"
chmod 0755 "${DESKTOP_SHORTCUT}"

if command -v gio >/dev/null 2>&1; then
    gio set "${DESKTOP_SHORTCUT}" metadata::trusted true 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q "${APPLICATIONS_DIR}" 2>/dev/null || true
fi

echo "Installed desktop entry:"
echo "  ${DESKTOP_FILE}"
echo "Installed desktop shortcut:"
echo "  ${DESKTOP_SHORTCUT}"
