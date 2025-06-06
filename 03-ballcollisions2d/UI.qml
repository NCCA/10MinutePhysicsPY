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
                columns: 7
                rowSpacing: 1
                columnSpacing: 7

                ColumnLayout {
                    Layout.alignment: Qt.AlignTop
                    Label {
                        id: label
                        text: qsTr("Num Balls")
                        Layout.alignment: Qt.AlignHCenter
                    }

                    SpinBox {
                        id: num_balls
                        value: 20
                        to: 200
                        from: 1
                        Component.onCompleted: {
                            backend.on_num_balls_changed(value);
                        }
                        onValueChanged: {
                            backend.on_num_balls_changed(value);
                        }
                    }
                }

                // Restitution
                LabeledSlider {
                    label: qsTr("Restitution")
                    from: 0.0
                    to: 1.0
                    value: 1.0
                    stepSize: 0.01
                    decimalPlaces: 2
                    onValueChanged: backend.on_restitution_changed(value)
                    Component.onCompleted: backend.on_restitution_changed(value)
                }
                LabeledRangeSlider {
                    label: qsTr("Radius")
                    minValue: 0.1
                    maxValue: 1.6
                    firstValue: 0.2
                    secondValue: 1.5
                    stepSize: 0.01
                    onRangeChanged: backend.on_radius_range_changed(first, second)
                    Component.onCompleted: backend.on_radius_range_changed(firstValue, secondValue)
                }
                LabeledRangeSlider {
                    label: qsTr("Velocity")
                    minValue: -8.0
                    maxValue: 8.0
                    firstValue: -3.5
                    secondValue: 3.5
                    stepSize: 0.01
                    onRangeChanged: backend.veleocity_changed(first, second)
                    Component.onCompleted: backend.veleocity_changed(firstValue, secondValue)
                }
                ColumnLayout {
                    Layout.alignment: Qt.AlignTop

                    Label {
                        id: label2
                        Layout.alignment: Qt.AlignTop | Qt.AlignHCenter

                        text: qsTr("Integration Method")
                    }

                    ComboBox {
                        id: integration_method
                        Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
                        model: ["Euler", "Semi Implicit", "RK4", "Verlet"]
                        Component.onCompleted: {
                            backend.on_integration_method_changed(currentIndex);
                        }
                        onCurrentIndexChanged: {
                            backend.on_integration_method_changed(currentIndex);
                        }
                    }
                }
                LabeledSlider {
                    label: qsTr("Integration Steps")
                    from: 1
                    to: 1000
                    value: 100
                    stepSize: 0.01
                    decimalPlaces: 0
                    onValueChanged: backend.on_integration_steps_changed(value)
                    Component.onCompleted: backend.on_integration_steps_changed(value)
                }
                // ColumnLayout {
                //     Label {
                //         id: steps_label
                //         text: qsTr("Integration Steps : ") + integration_steps.value.toFixed(0)
                //     }

                //     Slider {
                //         id: integration_steps
                //         value: 100
                //         from: 1
                //         to: 1000
                //         stepSize: 1
                //         Component.onCompleted: {
                //             backend.on_integration_steps_changed(value);
                //         }
                //         onValueChanged: {
                //             backend.on_integration_steps_changed(value);
                //         }
                //     }
                // }
                Button {
                    id: reset
                    text: qsTr("Reset")
                    onClicked: {
                        backend.setup_scene();
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
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onPositionChanged: {
                    if (mouse.buttons & Qt.LeftButton) {
                        backend.on_canvas_mouse_moved(mouse.x, mouse.y);
                    }
                }
            }
            Component.onCompleted: backend.set_canvas_size(width, height)
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);
                ctx.fillStyle = "#fff0f0"; // Set your desired clear color here
                ctx.fillRect(0, 0, width, height); // Fill the background

                for (var i = 0; i < root.balls.length; ++i) {
                    var c = root.balls[i];
                    ctx.beginPath();
                    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
                    ctx.fillStyle = c.color || "blue";
                    ctx.fill();
                }
            }
        }
    }

    onBallsChanged: canvas.requestPaint()
}
