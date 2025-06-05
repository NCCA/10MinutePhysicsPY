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
