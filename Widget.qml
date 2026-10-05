import QtQuick
import qs.Commons

Item {
    id: root
    property var bar
    property var settings: ({})
    property var shell
    property var manifest
    property var pluginRegistry
    property var barWidgetRegistry
    property string omarchyPath: ""
    property string moduleName: "local.omapit"
    implicitWidth: label.implicitWidth + 24
    implicitHeight: bar ? bar.barSize : 30
    readonly property bool alarm: (panel.store.snapshot.alarm_episodes || []).some(e=>e.resolved===null && !e.acknowledged && e.snoozed_until<Date.now()/1000)
    readonly property bool opened: panel.opened
    function open(payloadJson) { panel.open(payloadJson) }
    function close() { panel.close() }
    function togglePanel() { opened ? close() : open("") }
    Main { id: panel }
    Rectangle { anchors.fill:parent; radius:4; color: hover.containsMouse ? Qt.rgba(Color.foreground.r, Color.foreground.g, Color.foreground.b, 0.08) : "transparent" }
    Text {
        id: label
        anchors.centerIn:parent
        color:root.alarm ? Color.urgent : bar ? bar.foreground : Color.foreground
        font.family: bar ? bar.fontFamily : "monospace"
        font.pixelSize:13
        text: {
            var s=panel.store.snapshot, c=s.active
            if(root.alarm) return "PIT · ALARM"
            if (!c) return "PIT · ready"
            var r=s.readings.length ? s.readings[s.readings.length-1] : null
            return "PIT " + (c.source === "demo" ? "DEMO " : "") + (r ? panel.temperature(r.pit) + "° / " + panel.temperature(r.meat) + "°" : "· " + c.name)
        }
    }
    MouseArea { id:hover; anchors.fill:parent; hoverEnabled:true; cursorShape:Qt.PointingHandCursor; onClicked:root.togglePanel() }
}
