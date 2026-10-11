// Test stand-in for Quickshell's singleton: env() asks the test helper.
pragma Singleton
import QtQuick
import "Io/endpoint.js" as Endpoint

QtObject {
    function env(name) {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", Endpoint.url + "/env?name=" + encodeURIComponent(name), false)
        xhr.send()
        return xhr.status === 200 && xhr.responseText !== "" ? xhr.responseText : null
    }
}
