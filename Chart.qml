import QtQuick

Canvas {
    id: root
    property var readings: []
    property string unit: "F"
    property color foodColor: "#7aa2f7"
    property color pitColor: "#e0af68"
    property color ink: "#a9b1d6"
    onReadingsChanged: requestPaint()
    onUnitChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onFoodColorChanged: requestPaint()
    onPitColorChanged: requestPaint()
    onInkChanged: requestPaint()
    onPaint: {
        var ctx=getContext("2d"); ctx.reset()
        var left=42, top=12, w=width-left-14, h=height-top-30, max=unit==="F"?300:150
        var min=0
        for(var n=0;n<readings.length;n++) for(var key of ["meat","pit"]) {
            var v=unit==="F"?readings[n][key]:(readings[n][key]-32)*5/9
            max=Math.max(max,Math.ceil(v/50)*50);min=Math.min(min,Math.floor(v/50)*50)
        }
        var range=max-min
        ctx.font="11px monospace"; ctx.fillStyle=ink
        for(var tick=0; tick<=6; tick++) {
            var y=top+h-tick*h/6
            ctx.strokeStyle="#30384c"; ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(left+w,y);ctx.stroke()
            ctx.fillText(String(Math.round(min+tick*range/6)),3,y+4)
        }
        if (!readings.length) {ctx.fillText("Log your first temperatures to start the chart.",left+18,top+h/2);return}
        var t0=readings[0].at,t1=readings[readings.length-1].at,span=Math.max(1,t1-t0)
        var keys=["meat","pit"],colors=[foodColor,pitColor]
        for(var j=0;j<2;j++) {
            ctx.strokeStyle=colors[j];ctx.lineWidth=2.5;ctx.beginPath()
            for(var i=0;i<readings.length;i++) {
                var r=readings[i],v=unit==="F"?r[keys[j]]:(r[keys[j]]-32)*5/9
                var x=left+(r.at-t0)/span*w, yy=top+h-(v-min)/range*h
                if(i===0)ctx.moveTo(x,yy);else ctx.lineTo(x,yy)
            }
            ctx.stroke()
            if(readings.length===1){ctx.fillStyle=colors[j];ctx.beginPath();ctx.arc(left,yy,3,0,Math.PI*2);ctx.fill()}
        }
        ctx.fillStyle=ink
        for(var k=0;k<4;k++) {
            var when=new Date((t0+span*k/3)*1000)
            ctx.fillText(Qt.formatTime(when,"hh:mm"),left+k*w/3-10,height-4)
        }
    }
}
