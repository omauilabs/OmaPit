// Test stand-in for Omarchy's palette singleton, limited to the roles
// documented in Omarchy's docs/omarchy-shell.md, so an undocumented role fails.
pragma Singleton
import QtQuick

QtObject {
    property color background: "#1a1b26"
    property color foreground: "#c0caf5"
    property color accent: "#7aa2f7"
    property color urgent: "#f7768e"
}
