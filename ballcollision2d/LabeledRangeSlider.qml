import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

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
