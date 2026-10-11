// Test stand-in for Omarchy's Style singleton: only the type scale, with the
// defaults documented in Omarchy's docs/omarchy-shell.md ([font] base-size 12).
pragma Singleton
import QtQuick

QtObject {
    property QtObject font: QtObject {
        property real caption: 10
        property real bodySmall: 11
        property real body: 12
        property real subtitle: 13
        property real title: 14
        property real heading: 16
        property real display: 24
        property real displayLarge: 28
    }
}
