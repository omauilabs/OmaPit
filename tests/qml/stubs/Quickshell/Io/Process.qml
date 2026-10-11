// Test stand-in for Quickshell.Io.Process. The test helper runs the command
// (only the OmaPit backend) and returns its exit code, stdout and stderr.
import QtQuick
import "endpoint.js" as Endpoint

QtObject {
    id: process
    property var command: []
    property bool running: false
    property var stdout: null
    property var stderr: null
    signal exited(int exitCode, int exitStatus)
    onRunningChanged: if (running) Qt.callLater(run)
    function run() {
        var xhr = new XMLHttpRequest()
        xhr.open("POST", Endpoint.url + "/run", false)
        xhr.send(JSON.stringify(command))
        var result = xhr.status === 200 ? JSON.parse(xhr.responseText) : {code: 127, stdout: "", stderr: "test helper refused: " + xhr.responseText}
        if (stdout) { stdout.text = result.stdout; stdout.streamFinished() }
        if (stderr) { stderr.text = result.stderr; stderr.streamFinished() }
        running = false
        exited(result.code, 0)
    }
}
