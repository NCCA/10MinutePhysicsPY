import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 1024
    height: 720
    title: "10 Minute Physics - QML Edition"

    // This is updated from Python
    property var balls: []
      ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        uniformCellSizes: false
        spacing: 1

        GroupBox {
            id: groupBox
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            title: qsTr("Controls")

            GridLayout {
                id: gridLayout
                property string property: "This is a string"
                anchors.fill: parent
                columns: 5
                rowSpacing: 1
                columnSpacing: 6
                Label {
                    id: label
                    text: qsTr("Num Items")
                }

                SpinBox {
                    id: num_balls
                    value: 20
                    to: 200
                    from: 1
                    Component.onCompleted: {
                        backend.on_num_balls_changed(value)
                    }
                    onValueChanged: {
                        backend.on_num_balls_changed(value)
                    }
                }

                Label {
                    id: restitution_label
                    text: qsTr("Restitution: ") + restitution.value.toFixed(2)
                }

                Slider {
                    id: restitution
                    value: 1
                    stepSize: 0.01
                    from: 0.0
                    to: 1.0
                    Component.onCompleted: {
                        backend.on_restitution_changed(value)
                    }
                    onValueChanged: {
                        backend.on_restitution_changed(value)
                    }
                }

                Button {
                    id: reset
                    text: qsTr("Reset")
                    onClicked: {
                        backend.reset_simulation()
                    }
                }

                Label {
                    id: label2
                    text: qsTr("Label")
                }

                ComboBox {
                    id: integration_method
                    model: ["Euler", "Semi Implicit", "RK4", "Verlet"]
                    Component.onCompleted: {
                        backend.on_integration_method_changed(currentIndex)
                    }
                    onCurrentIndexChanged: {
                        backend.on_integration_method_changed(currentIndex)
                    }
                }

                Label {
                    id: steps_label
                    text: qsTr("Integration Steps : ") + integration_steps.value.toFixed(0)
                }

                Slider {
                    id: integration_steps
                    value: 100
                    from: 1
                    to: 1000
                    stepSize: 1
                    Component.onCompleted: {
                        backend.on_integration_steps_changed(value)
                    }
                    onValueChanged: {
                        backend.on_integration_steps_changed(value)
                    }
                }
            }
        }
        Canvas {
        id: canvas
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.preferredWidth: 1024
        Layout.preferredHeight: 720
        onWidthChanged: backend.set_canvas_size(width, height)
        onHeightChanged: backend.set_canvas_size(width, height)
        Component.onCompleted: backend.set_canvas_size(width, height)
        onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = "#fff0f0" // Set your desired clear color here
                ctx.fillRect(0, 0, width, height) // Fill the background

                for (var i = 0; i < root.balls.length; ++i) {
                    var c = root.balls[i]
                    ctx.beginPath()
                    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2)
                    ctx.fillStyle = c.color || "blue"
                    ctx.fill()
                }
            }
        }
    }

    onBallsChanged: canvas.requestPaint()
}
