import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import qs.Commons

Item {
    id: root
    property var shell
    property var manifest
    property var pluginRegistry
    property var barWidgetRegistry
    property string omarchyPath: ""
    property alias store: bridge
    property bool opened: false
    property string view: "live"
    readonly property string navGroup: view==="live"?"cook":view==="book"?"journal":view==="devices"?"":(workbench.section==="timeline" || workbench.section==="setup")?"plan":(workbench.section==="recipes" || workbench.section==="insights")?"journal":"cook"
    function navigate(viewName) { if(viewName==="live" || viewName==="book") view=viewName; else {view="workbench";workbench.section=viewName} }
    property string dialogMode: ""
    readonly property var active: bridge.snapshot.active
    readonly property var readings: bridge.snapshot.readings || []
    readonly property var events: bridge.snapshot.events || []
    readonly property var journalLast: readings.length ? readings[readings.length-1] : null
    readonly property var selected: (bridge.snapshot.devices || []).find(function(d){return d.id===bridge.snapshot.selected_device}) || null
    readonly property bool live: active && active.source==="ble"
    readonly property var last: live ? {meat:selected && selected.channels.food && selected.channels.food.value!==null?selected.channels.food.value*9/5+32:null,pit:selected && selected.channels.ambient && selected.channels.ambient.value!==null?selected.channels.ambient.value*9/5+32:null} : journalLast
    readonly property bool demo: active ? active.source === "demo" : false
    readonly property color bg: Color.background
    readonly property color ink: Color.foreground
    readonly property color accent: "#e0af68"
    readonly property color blue: "#7aa2f7"
    readonly property var stages: ["Smoke","Wrap","Rest","Serve"]
    function open(payloadJson) { opened=true; bridge.request("snapshot") }
    function close() { opened=false }
    function temperature(v) { return v === null || v === undefined ? "—" : String(Math.round(bridge.snapshot.unit === "C" ? (v-32)*5/9 : v)) }
    function timeLabel(t) { return Qt.formatTime(new Date(t*1000),"hh:mm") }
    function action(name,payload) { bridge.request(name,payload || {}) }
    function showDialog(mode) { dialogMode=mode; entry.text=""; meatInput.text=""; pitInput.text=""; modal.open() }
    Bridge { id:bridge; onSaved: action => { if(action !== "snapshot" && action !== "history") modal.close(); if(action === "history") {root.dialogMode="history";modal.open()} } }
    component LabelText: Text { color:root.ink; font.family:"monospace"; font.pixelSize:14; wrapMode:Text.Wrap }
    component ActionButton: Button {
        id: control
        property bool primary: false
        padding:13
        font.family:"monospace"
        font.pixelSize:13
        contentItem: Text {text:control.text;color:control.primary?root.bg:root.ink;font:control.font;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter;opacity:control.enabled?1:0.45}
        background: Rectangle {color:control.primary?root.accent:(control.hovered?Qt.rgba(Color.foreground.r, Color.foreground.g, Color.foreground.b, 0.08):"transparent");border.color:control.primary?root.accent:Color.muted;radius:4;opacity:control.enabled?1:.5}
    }
    FloatingWindow {
        id:window
        visible:root.opened
        title:"OmaPit — cook journal"
        width:1180;height:880
        minimumSize: Qt.size(760,600)
        color:root.bg
        onVisibleChanged: if (!visible) root.opened=false
        ColumnLayout {
            anchors.fill:parent;spacing:0
            Rectangle {
                Layout.fillWidth:true;Layout.preferredHeight:72;color:root.bg;border.color:Color.muted
                RowLayout {
                    anchors.fill:parent;anchors.margins:20;spacing:12
                    LabelText{text:"OmaPit";font.pixelSize:25;font.bold:true;color:root.accent}
                    ActionButton{text:"Cook";primary:root.navGroup==="cook";onClicked:root.view="live"}
                    ActionButton{text:"Plan";primary:root.navGroup==="plan";onClicked:{root.view="workbench";workbench.section="timeline"}}
                    ActionButton{text:"Journal";primary:root.navGroup==="journal";onClicked:root.view="book"}
                    Item{Layout.fillWidth:true}
                    ActionButton{text:"Devices";onClicked:root.view="devices"}
                    ActionButton{text:"°"+bridge.snapshot.unit;onClicked:root.action("unit",{unit:bridge.snapshot.unit==="F"?"C":"F"})}
                }
            }
            RowLayout{Layout.fillWidth:true;Layout.leftMargin:24;Layout.rightMargin:24;visible:root.navGroup!=="";spacing:12
                Repeater{model:root.navGroup==="cook"?[{view:"live",name:"Live cook"},{view:"next",name:"Next actions"},{view:"foods",name:"Foods & probes"},{view:"alarms",name:"Alerts"}]:root.navGroup==="plan"?[{view:"timeline",name:"Timeline"},{view:"setup",name:"New meal"}]:[{view:"book",name:"Cookbook"},{view:"recipes",name:"Recipes"},{view:"insights",name:"Insights"}];delegate:ActionButton{required property var modelData;text:modelData.name;onClicked:root.navigate(modelData.view)}}
                Item{Layout.fillWidth:true}
            }
            ActionButton{Layout.fillWidth:true;visible:(bridge.snapshot.alarm_episodes || []).some(e=>e.resolved===null && !e.acknowledged && e.snoozed_until<Date.now()/1000);text:"A cook alarm needs attention — open alarms";onClicked:{root.view="workbench";workbench.section="alarms"}}
            LabelText { Layout.fillWidth:true;Layout.margins:12;visible:bridge.error!=="";text:bridge.error;color:Color.urgent }
            ScrollView {
                id:scroller
                Layout.fillWidth:true;Layout.fillHeight:true;contentWidth:availableWidth;clip:true
                ColumnLayout {
                    width:scroller.availableWidth;spacing:18
                    Item{Layout.preferredHeight:5}
                    ActionButton{Layout.fillWidth:true;visible:root.view==="live" && root.active!==null;text:"Your next move — open coordinated actions";onClicked:{root.view="workbench";workbench.section="next"}}
                    ColumnLayout {
                        visible:root.view==="live" && root.active!==null
                        Layout.fillWidth:true;Layout.leftMargin:24;Layout.rightMargin:24;spacing:18
                        RowLayout {
                            Layout.fillWidth:true;spacing:20
                            ColumnLayout {
                                Layout.fillWidth:true;spacing:15
                                LabelText{text:root.active?root.active.name:"";font.pixelSize:32;font.bold:true}
                                LabelText{text:root.active?"Started "+root.timeLabel(root.active.started)+" · "+(root.demo?"Sample recording":root.live?"Local Bluetooth · "+(root.selected && root.selected.channels.food && root.selected.channels.food.fresh && root.selected.channels.ambient && root.selected.channels.ambient.fresh?"receiving":"sensor data stale"):"Manual temperatures"):"";opacity:.8}
                                RowLayout {
                                    spacing:35
                                    ColumnLayout { LabelText{text:root.temperature(root.last?root.last.meat:null)+"°"+bridge.snapshot.unit;font.pixelSize:55;color:root.blue;font.bold:true} LabelText{text:"FOOD TEMPERATURE";font.pixelSize:11} }
                                    ColumnLayout { LabelText{text:root.temperature(root.last?root.last.pit:null)+"°"+bridge.snapshot.unit;font.pixelSize:55;color:root.accent;font.bold:true} LabelText{text:root.live?"PROBE AMBIENT":"PIT TEMPERATURE";font.pixelSize:11} }
                                }
                                LabelText{text:root.demo?"Simulated probes · sample recording":root.last?"Last manually recorded "+root.timeLabel(root.last.at):"No readings yet";font.pixelSize:11;opacity:.8}
                                ActionButton {visible:!root.demo && !root.live;text:"Log temperatures";onClicked:root.showDialog("reading")}
                            }
                            Image {Layout.preferredWidth:340;Layout.preferredHeight:250;source:Qt.resolvedUrl("assets/grill.png");fillMode:Image.PreserveAspectFit}
                        }
                        RowLayout {
                            Layout.fillWidth:true;spacing:18
                            Rectangle {
                                Layout.fillWidth:true;Layout.preferredHeight:305;color:"transparent";border.color:Color.muted;radius:4
                                ColumnLayout {anchors.fill:parent;anchors.margins:18
                                    LabelText{text:"Temperature history"}
                                    Chart {Layout.fillWidth:true;Layout.fillHeight:true;readings:root.readings;unit:bridge.snapshot.unit;foodColor:root.blue;pitColor:root.accent;ink:root.ink}
                                }
                            }
                            Rectangle {
                                visible:!(bridge.snapshot.foods || []).length;Layout.preferredWidth:290;Layout.preferredHeight:305;color:"transparent";border.color:Color.muted;radius:4
                                ColumnLayout {anchors.fill:parent;anchors.margins:20;spacing:12
                                    LabelText{text:"NEXT STEP";font.pixelSize:11;opacity:.7}
                                    LabelText{text:root.active?["Wrap when the bark is ready.","Let it cook, then rest.","Rest before you slice.","Bring everyone to the table."][root.active.stage]:"";font.pixelSize:20;font.bold:true;Layout.fillWidth:true}
                                    ActionButton {Layout.fillWidth:true;primary:true;text:root.active?["Log wrap","Start rest","Start serving","Finish cook"][root.active.stage]:"";enabled:!bridge.busy && root.active!==null && (root.active.stage!==0 || (root.active.bark && root.active.dry));onClicked:{if(root.active.stage===3)root.showDialog("finish");else root.action("advance",{expected_stage:root.active.stage})}}
                                    CheckBox {visible:root.active!==null && root.active.stage===0;text:"Bark set";checked:root.active?!!root.active.bark:false;palette.windowText:root.ink;onClicked:root.action("check",{key:"bark",value:checked})}
                                    CheckBox {visible:root.active!==null && root.active.stage===0;text:"Surface dry";checked:root.active?!!root.active.dry:false;palette.windowText:root.ink;onClicked:root.action("check",{key:"dry",value:checked})}
                                    Item{Layout.fillHeight:true}
                                }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth:true;Layout.preferredHeight:195;color:"transparent";border.color:Color.muted;radius:4
                            RowLayout {anchors.fill:parent;anchors.margins:20;spacing:28
                                ColumnLayout {Layout.preferredWidth:300;LabelText{text:"Cook stage"}
                                    RowLayout {spacing:15;Repeater {model:root.stages;delegate:LabelText {required property int index;required property string modelData;text:modelData;color:root.active && index<=root.active.stage?root.accent:root.ink;font.bold:root.active && index===root.active.stage}}}
                                    LabelText{text:root.active?root.stages[root.active.stage]+" active":"";color:root.accent;font.pixelSize:12}
                                }
                                ColumnLayout {Layout.preferredWidth:200;LabelText{text:"Dinner target"} LabelText{text:root.active?root.active.target:"";font.pixelSize:32} LabelText{Layout.fillWidth:true;text:"Your serving goal.\nNo finish-time prediction.";font.pixelSize:11;opacity:.8}}
                                ColumnLayout {Layout.fillWidth:true;LabelText{text:"Event log"}
                                    Repeater {model:root.events.slice(0,3);delegate:LabelText {required property var modelData;Layout.fillWidth:true;text:root.timeLabel(modelData.at)+"  "+modelData.note;font.pixelSize:11;maximumLineCount:2;elide:Text.ElideRight}}
                                    RowLayout {ActionButton{text:"Add note";onClicked:root.showDialog("note")} ActionButton{text:"Fuel added";onClicked:root.action("fuel")}}
                                }
                            }
                        }
                        RowLayout {ActionButton{text:"Open meal workbench";onClicked:root.view="workbench"}LabelText{text:"Saved on this device";font.pixelSize:11;opacity:.7} Item{Layout.fillWidth:true} ActionButton{text:"Finish cook";onClicked:root.showDialog("finish")}}
                    }
                    ActionButton{Layout.fillWidth:true;visible:root.view==="live" && root.active!==null;text:"Your next move — open coordinated actions";onClicked:{root.view="workbench";workbench.section="next"}}
                    ColumnLayout {
                        visible:root.view==="live" && root.active===null;Layout.fillWidth:true;Layout.margins:40;spacing:25
                        LabelText{text:"Your fire. Your notes.\nA better cook every time.";font.pixelSize:36;Layout.alignment:Qt.AlignHCenter}
                        LabelText{text:"Start with manual readings, or explore a clearly labeled demo.";Layout.alignment:Qt.AlignHCenter}
                        RowLayout {Layout.alignment:Qt.AlignHCenter;spacing:20;ActionButton{text:"Start a cook";primary:true;onClicked:{root.view="workbench";workbench.section="setup"}} ActionButton{text:"Explore a demo";onClicked:root.action("demo")}}
                    }
                    ColumnLayout {
                        visible:root.view==="book";Layout.fillWidth:true;Layout.margins:25;spacing:20
                        LabelText{text:"Good cooks are worth keeping.";font.pixelSize:30}
                        Repeater {model:bridge.snapshot.cooks;delegate:ActionButton {required property var modelData;Layout.fillWidth:true;text:modelData.name+"  ·  "+(modelData.finished?"Completed":"Active")+"  ·  "+(modelData.source==="demo"?"Demo":modelData.source==="ble"?"BLE + journal":"Manual");onClicked:root.action("history",{id:modelData.id})}}
                        ActionButton {text:"New cook";enabled:!root.active;onClicked:{root.view="workbench";workbench.section="setup"}}
                    }
                    ColumnLayout {
                        visible:root.view==="devices";Layout.fillWidth:true;Layout.margins:25;spacing:20
                        LabelText{text:"Your thermometers";font.pixelSize:30}
                        LabelText{Layout.fillWidth:true;text:"CHEF iQ CQ50 / CQ60 · experimental local Bluetooth adapter. Wake the probe near this computer."}
                        ActionButton{text:bridge.snapshot.scanner && bridge.snapshot.scanner.status==="scanning"?"Listening for probes…":"Scan for 60 seconds";enabled:!bridge.snapshot.scanner || bridge.snapshot.scanner.status!=="scanning";onClicked:root.action("scan")}
                        LabelText{Layout.fillWidth:true;text:bridge.snapshot.scanner && bridge.snapshot.scanner.error?bridge.snapshot.scanner.error:"";color:Color.urgent}
                        Repeater {model:bridge.snapshot.devices || [];delegate:ColumnLayout {
                            required property var modelData;Layout.fillWidth:true;spacing:12
                            LabelText{Layout.fillWidth:true;text:modelData.name+" · "+modelData.model+" · "+modelData.status;font.pixelSize:20}
                            LabelText{Layout.fillWidth:true;text:"Food "+root.temperature(modelData.channels.food && modelData.channels.food.value!==null?modelData.channels.food.value*9/5+32:null)+"° · Probe ambient "+root.temperature(modelData.channels.ambient && modelData.channels.ambient.value!==null?modelData.channels.ambient.value*9/5+32:null)+"°"}
                            LabelText{Layout.fillWidth:true;text:modelData.source==="replay"?"Recorded replay. Cannot record a live cook.":modelData.evidence==="upstream-verified"?"Upstream verified layout; OmaPit hardware testing pending.":"Experimental layout; owner testing needed.";font.pixelSize:12}
                            ActionButton{text:bridge.snapshot.selected_device===modelData.id?"Recording this cook":"Use for this cook";enabled:root.active && !root.demo && modelData.status==="receiving" && bridge.snapshot.selected_device!==modelData.id;onClicked:root.action("select_device",{id:modelData.id})}
                        }}
                        LabelText{visible:!(bridge.snapshot.devices || []).length;text:"No probes discovered yet. Manual mode remains available."}
                        ActionButton{visible:root.live;text:"Switch to manual readings";onClicked:root.action("manual_mode")}
                    }
                    Workbench{id:workbench;visible:root.view==="workbench";Layout.fillWidth:true;Layout.margins:25;store:bridge;ink:root.ink;bg:root.bg;accent:root.accent}
                    Item{Layout.preferredHeight:20}
                }
            }
        }
        Dialog {
            id:modal
            parent:window.contentItem
            anchors.centerIn:parent
            width:Math.min(600,window.width-60)
            modal:true
            title:({"new":"Start a new cook","note":"Remember this moment","reading":"Log temperatures","finish":"Finish this cook?","history":"Saved cook"})[root.dialogMode]||"OmaPit"
            palette.window:root.bg;palette.windowText:root.ink;palette.text:root.ink;palette.base:root.bg;palette.button:root.bg;palette.buttonText:root.ink
            contentItem:ColumnLayout {
                spacing:15
                LabelText{Layout.fillWidth:true;visible:root.dialogMode==="finish";text:"Your temperatures and notes will stay in the Cookbook."}
                TextField{id:entry;Layout.fillWidth:true;visible:root.dialogMode==="new" || root.dialogMode==="note";placeholderText:root.dialogMode==="new"?"Cook name":"What happened?";maximumLength:root.dialogMode==="new"?80:500}
                TextField{id:target;Layout.fillWidth:true;visible:root.dialogMode==="new";text:"19:00";placeholderText:"Serving time HH:MM"}
                TextField{id:meatInput;Layout.fillWidth:true;visible:root.dialogMode==="reading";placeholderText:"Food temperature °"+bridge.snapshot.unit;inputMethodHints:Qt.ImhFormattedNumbersOnly}
                TextField{id:pitInput;Layout.fillWidth:true;visible:root.dialogMode==="reading";placeholderText:"Pit temperature °"+bridge.snapshot.unit;inputMethodHints:Qt.ImhFormattedNumbersOnly}
                LabelText{Layout.fillWidth:true;visible:root.dialogMode==="history";text:bridge.archive?bridge.archive.cook.name+" · "+bridge.archive.cook.source:"";font.pixelSize:20}
                Chart{Layout.fillWidth:true;Layout.preferredHeight:210;visible:root.dialogMode==="history";readings:bridge.archive?bridge.archive.readings:[];unit:bridge.snapshot.unit;foodColor:root.blue;pitColor:root.accent;ink:root.ink}
                LabelText{Layout.fillWidth:true;visible:root.dialogMode==="history";text:bridge.archive?bridge.archive.events.map(function(e){return root.timeLabel(e.at)+"  "+e.note}).join("\n"):"";font.pixelSize:12;maximumLineCount:9;elide:Text.ElideRight}
                LabelText{Layout.fillWidth:true;visible:bridge.error!=="";text:bridge.error;color:Color.urgent}
                RowLayout {
                    Item{Layout.fillWidth:true}
                    ActionButton{text:"Close";onClicked:modal.close()}
                    ActionButton {
                        visible:root.dialogMode!=="history";text:root.dialogMode==="finish"?"Finish & save":"Save";primary:true;enabled:!bridge.busy
                        onClicked:{
                            if(root.dialogMode==="new")root.action("create",{name:entry.text,target:target.text})
                            if(root.dialogMode==="note")root.action("note",{note:entry.text})
                            if(root.dialogMode==="reading")root.action("reading",{meat:meatInput.text,pit:pitInput.text,unit:bridge.snapshot.unit})
                            if(root.dialogMode==="finish")root.action("finish")
                        }
                    }
                }
            }
        }
    }
}
