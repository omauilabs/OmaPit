// Loads the real plugin (Widget.qml → Main.qml → Bridge, Chart, Workbench)
// against stand-ins for Quickshell and Omarchy, with the real Python backend
// behind them, and fails on any QML warning: binding errors, undefined
// references and type errors in OmaPit's own code. Run by
// tests/test_qml_runtime.py; this is not native Omarchy acceptance.
import QtQuick
import QtTest
import "../.."

TestCase {
    id: test
    name: "PluginRuntime"
    when: windowShown
    width: 400; height: 60

    // One widget for the whole run, as on Omarchy; it is torn down only after
    // the last test so that teardown cannot hide or cause warnings.
    Widget { id: widget }
    property var panel: findPanel(widget)

    function init() { failOnWarning(/.*/) }

    function findPanel(item) {
        for (var i = 0; i < item.children.length; i++) if (item.children[i].store !== undefined) return item.children[i]
        return null
    }

    function settle() {
        tryVerify(function() { return !panel.store.busy && panel.store.pending.length === 0 }, 10000, "backend request finished")
        wait(50)
    }

    function act(name, payload) {
        panel.action(name, payload)
        settle()
        compare(panel.store.error, "", name + " reported no error")
    }

    function visitEveryView() {
        var views = ["live", "book", "devices", "next", "foods", "alarms", "timeline", "setup", "recipes", "insights"]
        for (var i = 0; i < views.length; i++) { panel.navigate(views[i]); wait(30) }
        panel.navigate("live")
    }

    function test_1_empty_store() {
        verify(panel, "panel found")
        settle()
        compare(panel.store.snapshot.active, null, "no cook yet")
        compare(widget.opened, false)
        widget.togglePanel(); settle()
        compare(widget.opened, true, "panel opens")
        visitEveryView()
        widget.togglePanel()
        compare(widget.opened, false, "panel closes")
    }

    function test_2_cook_lifecycle() {
        verify(panel, "panel found")
        settle()
        widget.open(""); settle()
        act("create", {name: "Runtime test cook", target: "19:00"})
        verify(panel.store.snapshot.active, "cook started")
        act("reading", {meat: "150", pit: "250", unit: panel.store.snapshot.unit})
        compare(panel.store.snapshot.readings.length, 1, "reading recorded")
        act("note", {note: "Wrapped"})
        act("unit", {unit: "C"})
        compare(panel.store.snapshot.unit, "C")
        act("unit", {unit: "F"})
        var modes = ["note", "reading", "finish"]
        for (var i = 0; i < modes.length; i++) { panel.showDialog(modes[i]); wait(30) }
        visitEveryView()
        act("finish", {})
        compare(panel.store.snapshot.active, null, "cook finished")
        widget.close()
    }

    function test_3_demo_and_history() {
        verify(panel, "panel found")
        settle()
        widget.open(""); settle()
        act("demo", {})
        verify(panel.store.snapshot.active, "demo cook active")
        verify(widget.alarm === true || widget.alarm === false)
        visitEveryView()
        var cooks = panel.store.snapshot.cooks
        verify(cooks.length > 0, "history lists cooks")
        act("history", {id: cooks[cooks.length - 1].id})
        verify(panel.store.archive, "saved cook loaded")
        compare(panel.dialogMode, "history")
        wait(50)
        act("finish", {})
        widget.close()
    }
}
