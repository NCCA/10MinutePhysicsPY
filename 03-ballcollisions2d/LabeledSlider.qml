/*
    LabeledSlider.qml

    A reusable QML component that displays a labeled slider with a numeric value display.
    Useful for settings panels or forms where you want a slider with a label and a formatted value.

    Properties:
        - label (string): The text label shown above the slider.
        - value (real): The current value of the slider (read/write).
        - from (real): The minimum value of the slider.
        - to (real): The maximum value of the slider.
        - stepSize (real): The increment step for the slider.
        - decimalPlaces (int): Number of decimal places to display for the value (default: 2).

    Usage Example:
        LabeledSlider {
            label: "Restitution"
            from: 0.0
            to: 1.0
            value: 0.8
            stepSize: 0.01
            decimalPlaces: 2
            // You can bind to 'value' or use onValueChanged in the parent
        }

    Notes:
        - The value is displayed below the slider, formatted to the specified number of decimal places.
        - The label and value are horizontally centered.
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts

ColumnLayout {
    property alias label: label.text
    property alias value: slider.value
    property alias from: slider.from
    property alias to: slider.to
    property alias stepSize: slider.stepSize
    property int decimalPlaces: 2

    Label {
        id: label
        text: "Label"
        Layout.alignment: Qt.AlignHCenter
    }
    Slider {
        id: slider
        from: 0
        to: 1
        stepSize: 0.01
    }
    Label {
        text: slider.value.toFixed(decimalPlaces)
        font.pixelSize: 14
        Layout.alignment: Qt.AlignHCenter
    }
}
