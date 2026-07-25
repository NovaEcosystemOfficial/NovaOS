import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#070B12"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#070B12" }
            GradientStop { position: 1.0; color: "#0C121C" }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24
        width: 380

        Image {
            Layout.alignment: Qt.AlignHCenter
            source: "novaos-mark.png"
            sourceSize.width: 96
            sourceSize.height: 96
            fillMode: Image.PreserveAspectFit
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "NovaOS"
            color: "#E9EEF6"
            font.pixelSize: 28
            font.weight: Font.DemiBold
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 12
            color: "#141C2A"
            border.color: "#1C2738"
            border.width: 1
            implicitHeight: column.implicitHeight + 40

            ColumnLayout {
                id: column
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Text {
                    text: "Username"
                    color: "#9AA8BA"
                    font.pixelSize: 12
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 40
                    radius: 8
                    color: "#0C121C"
                    border.color: nameInput.activeFocus ? "#E8A54B" : "#1C2738"

                    TextInput {
                        id: nameInput
                        anchors.fill: parent
                        anchors.margins: 10
                        text: userModel.lastUser
                        color: "#E9EEF6"
                        font.pixelSize: 15
                        clip: true
                        selectByMouse: true
                        KeyNavigation.tab: passwordInput
                        onAccepted: passwordInput.forceActiveFocus()
                    }
                }

                Text {
                    text: "Password"
                    color: "#9AA8BA"
                    font.pixelSize: 12
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 40
                    radius: 8
                    color: "#0C121C"
                    border.color: passwordInput.activeFocus ? "#E8A54B" : "#1C2738"

                    TextInput {
                        id: passwordInput
                        anchors.fill: parent
                        anchors.margins: 10
                        echoMode: TextInput.Password
                        color: "#E9EEF6"
                        font.pixelSize: 15
                        clip: true
                        selectByMouse: true
                        focus: true
                        KeyNavigation.tab: loginButton
                        onAccepted: loginButton.clicked()
                    }
                }

                Rectangle {
                    id: loginButton
                    Layout.fillWidth: true
                    Layout.topMargin: 6
                    height: 42
                    radius: 8
                    color: loginMa.pressed ? "#C4892F" : "#E8A54B"
                    signal clicked()
                    onClicked: sddm.login(nameInput.text, passwordInput.text, sessionModel.lastIndex)

                    Text {
                        anchors.centerIn: parent
                        text: "Sign in"
                        color: "#070B12"
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                    }
                    MouseArea {
                        id: loginMa
                        anchors.fill: parent
                        onClicked: loginButton.clicked()
                    }
                    Keys.onReturnPressed: loginButton.clicked()
                    Keys.onEnterPressed: loginButton.clicked()
                }

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 4
                    text: "Nova Shell"
                    color: "#5A6B80"
                    font.pixelSize: 12
                }
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            passwordInput.selectAll()
            passwordInput.forceActiveFocus()
        }
    }

    Component.onCompleted: {
        if (nameInput.text === "")
            nameInput.forceActiveFocus()
        else
            passwordInput.forceActiveFocus()
    }
}
