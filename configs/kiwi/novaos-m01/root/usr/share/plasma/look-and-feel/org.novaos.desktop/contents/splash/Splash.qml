import QtQuick 2.15

Rectangle {
    id: root
    color: "#070B12"

    property int stage: 0
    onStageChanged: {
        if (stage === 1)
            introAnimation.running = true
    }

    Image {
        id: mark
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -36
        source: "images/novaos-mark.png"
        sourceSize.width: 96
        sourceSize.height: 96
        opacity: 0.0
    }

    Text {
        id: title
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: mark.bottom
        anchors.topMargin: 20
        text: "NovaOS"
        color: "#E9EEF6"
        font.pixelSize: 22
        font.weight: Font.DemiBold
        opacity: 0.0
    }

    Rectangle {
        id: barBg
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: title.bottom
        anchors.topMargin: 28
        width: 160
        height: 3
        radius: 2
        color: "#1C2738"
        opacity: 0.0

        Rectangle {
            id: bar
            width: parent.width * (root.stage / 6.0)
            height: parent.height
            radius: 2
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#E8A54B" }
                GradientStop { position: 1.0; color: "#3DD6C6" }
            }
            Behavior on width { NumberAnimation { duration: 250; easing.type: Easing.InOutQuad } }
        }
    }

    ParallelAnimation {
        id: introAnimation
        NumberAnimation { target: mark; property: "opacity"; to: 1.0; duration: 450 }
        NumberAnimation { target: title; property: "opacity"; to: 1.0; duration: 450 }
        NumberAnimation { target: barBg; property: "opacity"; to: 1.0; duration: 450 }
    }
}
