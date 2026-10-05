import QtQuick
import Quickshell
import Quickshell.Io

Item {
    id: root
    property var snapshot: ({active:null, cooks:[], readings:[], events:[], unit:"F"})
    property var archive: null
    property string error: ""
    property bool busy: worker.running
    property var pending: []
    property string operation: "snapshot"
    readonly property string backend: decodeURIComponent(Qt.resolvedUrl("backend/omapit.py").toString().replace(/^file:\/\//, ""))
    signal saved(string action)
    function request(action, payload) {
        pending.push({action:action, payload:payload || {}})
        drain()
    }
    function drain() {
        if (worker.running || pending.length === 0) return
        var job = pending.shift()
        operation = job.action
        worker.command = [Quickshell.env("OMAPIT_PYTHON") || "python3", backend, job.action, JSON.stringify(job.payload)]
        worker.running = true
    }
    Process {
        id: worker
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var value = JSON.parse(text)
                    if (value.error) root.error = value.error
                    else {
                        root.error = ""
                        if (root.operation === "history") root.archive = value
                        else root.snapshot = value
                        root.saved(root.operation)
                    }
                } catch(e) { root.error = "Cannot read the local cook store. Check that Python 3 is installed." }
            }
        }
        stderr: StdioCollector { onStreamFinished: { if (text.trim()) root.error = "Storage helper failed: " + text.slice(0,240) } }
        onExited: (exitCode, exitStatus) => { Qt.callLater(root.drain) }
    }
    Timer { interval:5000; repeat:true; running:true; onTriggered: { if (!root.busy && root.pending.length === 0) root.request("snapshot") } }
    Component.onCompleted: request("snapshot")
}
