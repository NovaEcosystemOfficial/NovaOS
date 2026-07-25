/* NovaOS Calamares slideshow — minimal, no promo clutter */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: root

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            color: "#0B1F2A"
        }

        Column {
            anchors.centerIn: parent
            spacing: 16
            width: parent.width * 0.8

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "NovaOS"
                color: "#E8F1F5"
                font.pixelSize: 42
                font.bold: true
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("Installing to disk. Other operating systems are preserved when you choose Alongside or Manual partitioning.")
                color: "#A8C5D1"
                font.pixelSize: 16
            }
        }
    }

    Slide {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            color: "#0B1F2A"
        }

        Column {
            anchors.centerIn: parent
            spacing: 12
            width: parent.width * 0.8

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("After reboot")
                color: "#E8F1F5"
                font.pixelSize: 28
                font.bold: true
            }
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("Log in with the account you created. NetworkManager, Plasma, and development tools are ready.")
                color: "#A8C5D1"
                font.pixelSize: 16
            }
        }
    }
}
