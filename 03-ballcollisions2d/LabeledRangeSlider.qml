/*
    LabeledRangeSlider.qml

    A reusable QML component that displays a labeled RangeSlider with a formatted display
    of the current range selection. Useful for selecting a numeric range (e.g., min/max radius)
    in a settings panel or form.

    Properties:
        - label (string): The text label shown above the RangeSlider.
        - minValue (real): The minimum value of the range (default: 0.1).
        - maxValue (real): The maximum value of the range (default: 1.6).
        - firstValue (real): The initial value of the first handle (default: 0.2).
        - secondValue (real): The initial value of the second handle (default: 1.5).
        - stepSize (real): The increment step for the slider (default: 0.01).

    Signals:
        - rangeChanged(real first, real second): Emitted whenever either handle of the RangeSlider changes,
          or when the component is first completed.

    Usage Example:
        LabeledRangeSlider {
            label: "Radius Range"
            minValue: 0.1
            maxValue: 2.5
            firstValue: 0.2
            secondValue: 1.5
            stepSize: 0.01
            onRangeChanged: backend.on_radius_range_changed(first, second)
        }

    Notes:
        - The current range is displayed as text below the slider, formatted to three decimal places.
        - The label and value display are horizontally centered.
        - The component emits the rangeChanged signal on startup and whenever the user moves either handle.
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts

ColumnLayout {
    id: root
    property alias label: label.text
    property real minValue: 0.1
    property real maxValue: 1.6
    property real firstValue: 0.2
    property real secondValue: 1.5
    property real stepSize: 0.01
    signal rangeChanged(real first, real second)

    spacing: 10

    Label {
        id: label
        Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
        text: qsTr("Radius Range")
    }

    RangeSlider {
        id: radius_range
        from: root.minValue
        to: root.maxValue
        first.value: root.firstValue
        second.value: root.secondValue
        stepSize: root.stepSize

        Component.onCompleted: {
            root.rangeChanged(first.value, second.value);
        }
        first.onValueChanged: {
            root.rangeChanged(first.value, second.value);
        }
        second.onValueChanged: {
            root.rangeChanged(first.value, second.value);
        }
    }

    Text {
        text: radius_range.first.value.toFixed(3) + "→ " + radius_range.second.value.toFixed(3)
        Layout.alignment: Qt.AlignCenter
    }
}
