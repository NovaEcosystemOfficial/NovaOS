import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/*!
  Nova Update — foundation stub (Sprint 15).

  Not wired to a full Plasma module yet. Demonstrates the intended surface:
  channel, pending classes, check/apply actions. Runtime data will come from
  nova-updated via system.update.v1.
*/
ApplicationWindow {
    id: root
    width: 720
    height: 480
    visible: true
    title: qsTr("Nova Update")

    // Placeholder bindings — replaced by broker client later.
    property string channel: "stable"
    property string lastCheck: qsTr("never")
    property var pending: [
        { name: "novaos-release", version: "0.2.1", update_class: "os" },
        { name: "novaos-update", version: "0.1.1", update_class: "nova" }
    ]

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            Label {
                text: qsTr("Nova Update")
                font.bold: true
                Layout.leftMargin: 12
            }
            Item { Layout.fillWidth: true }
            Label { text: qsTr("Channel") }
            ComboBox {
                id: channelBox
                model: ["stable", "beta", "developer", "nightly"]
                currentIndex: Math.max(0, model.indexOf(root.channel))
                onActivated: root.channel = currentText
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Label {
            text: qsTr("Last check: %1").arg(root.lastCheck)
            opacity: 0.7
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.pending
            delegate: ItemDelegate {
                width: ListView.view.width
                text: modelData.name + " → " + modelData.version
                      + "  [" + modelData.update_class + "]"
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight
            Button {
                text: qsTr("Check")
                // onClicked: broker.Check()
            }
            Button {
                text: qsTr("Update")
                highlighted: true
                // onClicked: broker.Apply()  // capability system.update.apply
            }
        }

        Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: qsTr("Reboots, when required, are explained and schedulable. "
                     + "AI may summarize changelogs but cannot force Apply.")
            opacity: 0.65
        }
    }
}
