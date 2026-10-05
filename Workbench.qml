import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id:root
    property var store
    property color ink: "#c0caf5"
    property color bg: "#151922"
    property color accent: "#e0af68"
    property string section: "foods"
    property var data: store.snapshot
    property var foods: data.foods || []
    property var grills: data.plan ? (data.plan.resources || []) : []
    property var nextTask: tasks.filter(t=>!t.completed && t.ready).sort((a,b)=>(a.started?0:1)-(b.started?0:1) || a.planned_start-b.planned_start)[0] || null
    property var urgentAlarm: (data.alarm_episodes || []).find(e=>e.resolved===null && !e.acknowledged && e.snoozed_until<=Date.now()/1000) || null
    property var tasks: data.plan ? data.plan.tasks : []
    property var liveDevices: (data.devices || []).filter(d=>d.source==="ble" || d.source==="bridge")
    spacing:18
    function send(command,payload) { store.request(command,payload || {}) }
    function temperature(value) { return value===null || value===undefined?"—":Math.round(data.unit==="C"?(value-32)*5/9:value) }
    function when(value) { return value?new Date(value*1000).toLocaleString():"No goal set" }
    component Copy: Text {color:root.ink;font.family:"monospace";font.pixelSize:13;wrapMode:Text.Wrap;Layout.fillWidth:true}
    component Entry: TextField {Layout.fillWidth:true;palette.text:root.ink;palette.base:root.bg;font.family:"monospace";selectByMouse:true}
    component Choice: ComboBox {Layout.fillWidth:true;palette.text:root.ink;palette.buttonText:root.ink;palette.button:root.bg}
    component Press: Button {palette.buttonText:root.ink;palette.button:root.bg;enabled:!root.store.busy}
    Copy{text:"Meal workbench";font.pixelSize:28;color:root.accent}
    Copy{text:"Targets are personal preferences. Experimental trends do not assess food safety. Native controls require Linux acceptance.";opacity:.8}
    ColumnLayout {visible:root.section==="next";Layout.fillWidth:true;spacing:14
        Copy{text:"Your next move";font.pixelSize:24;color:root.accent}
        Copy{text:root.urgentAlarm?root.urgentAlarm.label:root.nextTask?(root.nextTask.started?"Check progress: ":"Up next: ")+root.nextTask.name:"Add a meal plan for coordinated actions."}
        Copy{text:root.nextTask?root.when(root.nextTask.planned_start)+" · "+root.nextTask.duration/60+"m estimate":""}
        RowLayout {
            Press{visible:!!root.urgentAlarm;text:"Acknowledge";onClicked:root.send("alarm_ack",{id:root.urgentAlarm.id})}
            Press{visible:!!root.urgentAlarm;text:"Snooze 5m";onClicked:root.send("alarm_snooze",{id:root.urgentAlarm.id,seconds:300})}
            Press{visible:!root.urgentAlarm && !!root.nextTask;text:root.nextTask && root.nextTask.started?"Confirm done":"Start step";onClicked:root.send(root.nextTask.started?"task_done":"task_start",{id:root.nextTask.id,done:true})}
            Press{text:"Review timeline";onClicked:root.section="timeline"}
        }
        Copy{text:"Completion needs your confirmation. Elapsed estimates do not establish doneness."}
    }
    ColumnLayout {visible:root.section==="setup";Layout.fillWidth:true;spacing:14
        Copy{text:root.data.active?"Finish and save your active cook before creating a guided meal.":"Guided meal · one grill, main and optional side";font.pixelSize:20;color:root.accent}
        Entry{id:mealName;placeholderText:"Meal name";text:"Sunday dinner"}
        Entry{id:mealDate;placeholderText:"Serving date/time with offset";text:new Date(Date.now()+7200000).toISOString()}
        RowLayout{Entry{id:setupGrill;text:"Main grill";placeholderText:"Grill name"}Entry{id:setupCapacity;text:"2";placeholderText:"Space units"}}
        Entry{id:setupPreheat;text:"15";placeholderText:"Preheat minutes"}
        Entry{id:mainFood;placeholderText:"Main food name"}
        Choice{id:setupCategory;model:["quick","poultry","vegetables","smoke","manual"]}
        RowLayout{Entry{id:setupTarget;placeholderText:"Personal target °"+root.data.unit}Entry{id:setupPit;placeholderText:"Pit temperature °"+root.data.unit}}
        RowLayout{Entry{id:setupCook;text:"30";placeholderText:"Cook minutes"}Entry{id:setupRest;text:"10";placeholderText:"Rest minutes"}Entry{id:setupSlots;text:"1";placeholderText:"Space units used"}}
        Entry{id:sideFood;placeholderText:"Optional side name"}
        RowLayout{Entry{id:sideTarget;placeholderText:"Side target °"+root.data.unit}Entry{id:sidePit;placeholderText:"Side pit °"+root.data.unit}Entry{id:sideMinutes;text:"15";placeholderText:"Side cook minutes"}}
        Copy{text:"Creates prep, preheat, cook and rest tasks plus target reminders. Personal targets require independent confirmation. Review the timeline before starting."}
        Press{text:"Create meal & plan";enabled:!root.store.busy && !root.data.active;onClicked:{
            var items=[{name:mainFood.text,category:setupCategory.currentText,target:setupTarget.text,pit:setupPit.text,minutes:setupCook.text,prep:10,rest:setupRest.text,slots:setupSlots.text,resource:"main"}]
            if(sideFood.text.trim()) items.push({name:sideFood.text,category:"vegetables",target:sideTarget.text,pit:sidePit.text,minutes:sideMinutes.text,prep:10,rest:0,slots:1,resource:"main"})
            root.send("guided_setup",{name:mealName.text,serve_at:mealDate.text,unit:root.data.unit,preheat:setupPreheat.text,resources:[{id:"main",name:setupGrill.text,capacity:Number(setupCapacity.text)}],foods:items})
        }}
    }
    ColumnLayout {visible:root.section==="foods";Layout.fillWidth:true;spacing:16
        Entry{id:foodName;placeholderText:"Food name";maximumLength:100}
        RowLayout{Layout.fillWidth:true;Entry{id:foodZone;text:"Main grill";placeholderText:"Grill / zone"}Entry{id:foodTarget;placeholderText:"Personal target °"+root.data.unit;inputMethodHints:Qt.ImhFormattedNumbersOnly}}
        Choice{id:foodCategory;model:["quick","poultry","vegetables","smoke","manual"]}
        TextArea{id:foodSteps;Layout.fillWidth:true;placeholderText:"Optional steps, one per line";palette.text:root.ink;palette.base:root.bg}
        Press{text:"Add food";enabled:!root.store.busy && root.data.active && root.data.active.source!=="demo";onClicked:root.send("food_add",{name:foodName.text,zone:foodZone.text,target:foodTarget.text,unit:root.data.unit,category:foodCategory.currentText,steps:foodSteps.text})}
        Repeater{model:root.foods;delegate:ColumnLayout{
            required property var modelData
            Layout.fillWidth:true;spacing:10
            Copy{text:modelData.name+" · "+modelData.zone;font.pixelSize:20;color:root.accent}
            Copy{text:(modelData.finished?"Completed":modelData.steps[modelData.stage])+" · target "+root.temperature(modelData.target_f)+"°"+root.data.unit+" · "+(modelData.reading?root.temperature(modelData.reading.value_f)+"° · "+(modelData.reading.fresh?"recent":"stale")+" "+modelData.reading.source:"no reading")}
            RowLayout{visible:!modelData.finished;Layout.fillWidth:true
                Choice{id:probeChoice;model:["Manual"].concat(root.liveDevices.map(d=>d.name));currentIndex:modelData.device?root.liveDevices.findIndex(d=>d.id===modelData.device)+1:0}
                Press{text:"Map food channel";onClicked:root.send("food_map",{id:modelData.id,device:probeChoice.currentIndex>0?root.liveDevices[probeChoice.currentIndex-1].id:null,role:"food"})}
                Entry{id:foodReading;placeholderText:"Reading °"+root.data.unit;visible:!modelData.device;inputMethodHints:Qt.ImhFormattedNumbersOnly}
                Press{text:"Log";visible:!modelData.device;onClicked:root.send("food_reading",{id:modelData.id,value:foodReading.text,unit:root.data.unit})}
            }
            RowLayout{visible:!modelData.finished
                Press{text:"Target alarm";onClicked:root.send("food_alarm",{id:modelData.id})}
                Press{text:modelData.stage<modelData.steps.length-1?"Next: "+modelData.steps[modelData.stage+1]:"Finish food";onClicked:root.send(modelData.stage<modelData.steps.length-1?"food_advance":"food_finish",{id:modelData.id,expected_stage:modelData.stage})}
            }
        }}
    }
    ColumnLayout{visible:root.section==="alarms";Layout.fillWidth:true;spacing:16
        Copy{text:"Snapshots evaluate alarms. For independent monitoring and notify-send delivery, run backend/omapit.py --monitor with OMAPIT_DESKTOP_NOTIFY=1. A sleeping receiver cannot monitor temperatures."}
        Entry{id:alarmName;placeholderText:"Alarm label";maximumLength:100}
        Choice{id:alarmKind;model:["high","low","stale","timer"]}
        Choice{id:alarmRole;model:["food","ambient"]}
        Entry{id:alarmValue;placeholderText:alarmKind.currentText==="timer"?"Minutes":alarmKind.currentText==="stale"?"Maximum age in seconds":"Temperature °"+root.data.unit}
        Press{text:"Save alarm";onClicked:root.send("alarm_add",{label:alarmName.text,kind:alarmKind.currentText,role:alarmRole.currentText,threshold:alarmValue.text,seconds:Number(alarmValue.text)*60,unit:root.data.unit})}
        Repeater{model:(root.data.alarm_episodes || []).filter(e=>e.resolved===null);delegate:RowLayout{
            required property var modelData;Layout.fillWidth:true
            Copy{text:modelData.label+" · "+(modelData.acknowledged?"acknowledged":"needs attention");color:root.accent}
            Press{text:"Acknowledge";visible:!modelData.acknowledged;onClicked:root.send("alarm_ack",{id:modelData.id})}
            Press{text:"Snooze 5m";visible:!modelData.acknowledged;onClicked:root.send("alarm_snooze",{id:modelData.id,seconds:300})}
        }}
        Repeater{model:root.data.alarm_rules || [];delegate:RowLayout{required property var modelData;Layout.fillWidth:true;Copy{text:modelData.label+" · "+modelData.kind}Press{text:modelData.enabled?"Disable":"Enable";onClicked:root.send("alarm_rule",{id:modelData.id,enabled:!modelData.enabled})}}}
    }
    ColumnLayout{visible:root.section==="timeline";Layout.fillWidth:true;spacing:16
        Copy{text:"Serving goal: "+root.when(root.data.plan ? root.data.plan.serve_at:null)}
        Entry{id:serveDate;placeholderText:"Date/time with offset, e.g. 2026-10-04T19:00:00-07:00"}
        Press{text:"Save serving goal";onClicked:root.send("meal_goal",{serve_at:serveDate.text})}
        Entry{id:taskName;placeholderText:"Step name";maximumLength:100}
        Entry{id:taskMinutes;placeholderText:"Estimated minutes";inputMethodHints:Qt.ImhFormattedNumbersOnly}
        Entry{id:grillName;placeholderText:"New grill / zone name"}
        Entry{id:grillCapacity;text:"2";placeholderText:"Space units"}
        Press{text:"Add grill";onClicked:root.send("grill_config",{resources:root.grills.concat([{id:String(Date.now()),name:grillName.text,capacity:Number(grillCapacity.text)}])})}
        Choice{id:taskGrill;model:["Off grill"].concat(root.grills.map(g=>g.name))}
        Entry{id:taskSlots;text:"1";placeholderText:"Space units used"}
        Entry{id:taskPit;placeholderText:"Optional cooking temperature °"+root.data.unit}
        Choice{id:dependency;model:["Independent"].concat(root.tasks.map(t=>t.name))}
        Press{text:"Add step";onClicked:root.send("task_add",{name:taskName.text,minutes:taskMinutes.text,resource:taskGrill.currentIndex>0?root.grills[taskGrill.currentIndex-1].id:"",slots:taskSlots.text,pit_f:taskPit.text?root.data.unit==="C"?Number(taskPit.text)*9/5+32:Number(taskPit.text):null,depends:dependency.currentIndex>0?[root.tasks[dependency.currentIndex-1].id]:[]})}
        Repeater{model:root.tasks;delegate:ColumnLayout{required property var modelData;Layout.fillWidth:true
            Copy{text:modelData.name+" · "+modelData.duration/60+"m · "+(modelData.completed?"done":root.when(modelData.planned_start)+" → "+root.when(modelData.planned_finish))}
            RowLayout{Press{text:"Start";visible:!modelData.completed && !modelData.started;enabled:!root.store.busy && modelData.ready;onClicked:root.send("task_start",{id:modelData.id})}Press{text:modelData.completed?"Reopen":"Mark done";onClicked:root.send("task_done",{id:modelData.id,done:!modelData.completed})}Entry{id:durationEdit;placeholderText:"New estimated minutes"}Press{text:"Adjust";onClicked:root.send("task_edit",{id:modelData.id,name:modelData.name,food:modelData.food,depends:modelData.depends,minutes:durationEdit.text})}}
        }}
    }
    ColumnLayout{visible:root.section==="recipes";Layout.fillWidth:true;spacing:16
        Entry{id:recipeName;placeholderText:"Recipe name";maximumLength:100}
        Entry{id:recipeServings;text:"4";placeholderText:"Servings"}
        TextArea{id:ingredients;Layout.fillWidth:true;placeholderText:"Ingredients, one per line";palette.text:root.ink;palette.base:root.bg}
        TextArea{id:instructions;Layout.fillWidth:true;placeholderText:"Instructions, one per line";palette.text:root.ink;palette.base:root.bg}
        Press{text:"Save recipe";onClicked:root.send("recipe_save",{name:recipeName.text,servings:recipeServings.text,ingredients:ingredients.text,steps:instructions.text})}
        TextArea{id:importText;Layout.fillWidth:true;placeholderText:"Paste Recipe JSON / JSON-LD / page HTML";palette.text:root.ink;palette.base:root.bg}
        Press{text:"Import recipe";onClicked:root.send("recipe_import",{text:importText.text})}
        Repeater{model:root.data.recipes || [];delegate:ColumnLayout{required property var modelData;Layout.fillWidth:true;Copy{text:modelData.name+" · "+modelData.servings+" servings";color:root.accent;font.pixelSize:20}Copy{text:modelData.ingredients.join("\n")}Copy{text:modelData.steps.map((s,i)=>(i+1)+". "+s).join("\n")}}}
    }
    ColumnLayout{visible:root.section==="insights";Layout.fillWidth:true;spacing:16
        Repeater{model:root.foods.filter(f=>!f.finished);delegate:ColumnLayout{required property var modelData;property var forecast:root.data.predictions ? root.data.predictions[modelData.id]:null;Layout.fillWidth:true
            Copy{text:modelData.name+" · "+(forecast && forecast.status==="estimate"?root.when(forecast.earliest)+" – "+root.when(forecast.latest):forecast?forecast.status:"Waiting for data");color:root.accent;font.pixelSize:19}
            Copy{text:forecast?forecast.reason:""}
        }}
        Copy{text:"Experimental local trend ranges. Photos, per-food comparison charts, backup downloads and prediction evaluation are available in the browser companion. No calibrated confidence or hardware reliability claim is made."}
    }
}
