// Test stand-in for Quickshell's FloatingWindow, backed by a plain Window.
import QtQuick
import QtQuick.Window

Window {
    property size minimumSize: Qt.size(0, 0)
    minimumWidth: minimumSize.width
    minimumHeight: minimumSize.height
}
