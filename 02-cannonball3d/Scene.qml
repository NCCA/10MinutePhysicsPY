import QtQuick
import QtQuick.Window
import QtQuick3D
import QtQuick3D.Helpers
import QtQuick.Controls
Window {
    id: win
    width: 1024
    height: 720
    visible: true
    title: "QtQuick3D Physics Ball"
    property real xMin: bounds ? bounds.xMin : -1.5
    property real xMax: bounds ? bounds.xMax : 1.5
    property real zMin: bounds ? bounds.zMin : -2.5
    property real zMax: bounds ? bounds.zMax : 2.5
    property real yMin: bounds ? bounds.yMin : 0
    property int controllerIndex: 0 // 0 = Orbit, 1 = WASD
    property bool running : false
    property bool gridVisible: true
    property bool showPlanes: false
    View3D {
        id: view3d
        objectName : "view3d"
        anchors.fill: parent

        environment: SceneEnvironment {
                 InfiniteGrid {
                    id: grid
                    gridInterval: 10
                    visible: win.gridVisible
                }
            clearColor: "black"
            backgroundMode: SceneEnvironment.Color
            fog: Fog {
                    id: theFog
                    enabled: true
                    depthEnabled: true
                    density : 0.8
                }
        }
        camera : camera

        Node {
            id: originNode
            PerspectiveCamera {
                id: cameraNode
                z: 30
                position: Qt.vector3d(0,5, 20)
                fieldOfView: 60
                clipNear: 0.1
                clipFar: 500
            }
        }

        OrbitCameraController {
            origin: originNode
            camera: cameraNode
             enabled: win.controllerIndex === 0
        }
        WasdController {
                controlledObject: cameraNode
                speed: 0.01
                enabled: win.controllerIndex === 1

            }
        DirectionalLight {
                   color: "#FFFFFF"
                   brightness: 0.1
                   position: Qt.vector3d(0, 3, 0)
                   castsShadow: true
                   shadowMapQuality: Light.ShadowMapQualityHigh
                   shadowBias: 0.005
                   shadowFactor: 10 // not a direct mapping, but controls shadow darkness
                   shadowMapFar: 10

               }


        SpotLight {
            color: "white"
            brightness: 0.5
            y : 5
            z : 10
            coneAngle: 80
            innerConeAngle : 50
            castsShadow: true
            shadowMapQuality: Light.ShadowMapQualityHigh
            shadowBias: 0.5
            shadowFactor: 10 // not a direct mapping, but controls shadow darkness
            shadowMapFar: 1
        }
            Model {
                id : ground
                source: "#Rectangle"
                eulerRotation : Qt.vector3d(-90,0,0)
                scale: Qt.vector3d(1, 1, 0.01)
                x: 0
                y: ball.ball_radius
                z: 0
                materials: DefaultMaterial { diffuseColor: "#ffffff"; opacity: 1 }
            }

            // Left plane (x = xMin)
            Model {
                visible: win.showPlanes
                source: "#Rectangle"
                x: xMin
                y: 0.5
                z: (zMax + zMin) / 2
                scale: Qt.vector3d(0.01, 1, Math.abs(zMax - zMin))
                eulerRotation: Qt.vector3d(0, 90, 0)
                materials: DefaultMaterial { diffuseColor: "#00ff00"; opacity: 0.3 }
            }
            // Right plane (x = xMax)
            Model {
                visible: true // win.showPlanes
                source: "#Rectangle"
                x: xMax
                y: 4
                z: (zMax + zMin) / 2
                scale: Qt.vector3d(0.05, 0.05, 0.05)
                eulerRotation: Qt.vector3d(0, 90, 0)
                materials: DefaultMaterial { diffuseColor: "#ff0000"; opacity: 0.3 }
            }
            // Back plane (z = zMin)
            Model {
                visible:  true //win.showPlanes
                source: "#Rectangle"
                x: (xMax + xMin) / 2
                y: 4
                z: zMin
                scale: Qt.vector3d( 0.05, 0.05, 0.01)
                eulerRotation: Qt.vector3d(0, 0, 0)
                materials: DefaultMaterial { diffuseColor: "#0000ff"; opacity: 0.3 }
            }
            // Front plane (z = zMax)
            Model {
                visible: true // win.showPlanes
                source: "#Rectangle"
                x: (xMax + xMin) / 2
                y: 4
                z: zMax
                scale : Qt.vector3d(0.05,0.05,0.01)
                eulerRotation: Qt.vector3d(0, 0, 0)
                materials: DefaultMaterial { diffuseColor: "#ffff00"; opacity: 0.3 }
            }

        Model {
            id: ball
            objectName : "ball"
            source: "#Sphere"
            materials: DefaultMaterial { diffuseColor: "red" }
            // Position will be set from Python
            property vector3d ballPosition: Qt.vector3d(0,5,0)
            x: ballPosition.x
            y: ballPosition.y
            z: ballPosition.z
            // radius set from python
            property real ball_radius : 0.01
            scale: Qt.vector3d(ball_radius,ball_radius,ball_radius)

        }

}

// UI Overlay
   Row {
       spacing: 16

       Button {
           text: win.running ? "Stop" : "Start"
           onClicked: {
               win.running = !win.running
               if (win.running) {
                   ballSim.start()
               } else {
                   ballSim.stop()
               }
           }
       }
       Button {
           text: "Reset"
           onClicked:
           {
               ballSim.reset()
               win.running = false
           }
       }
       Row {
           spacing: 8
           Switch {
               checked: win.controllerIndex === 1
               onCheckedChanged: win.controllerIndex = checked ? 1 : 0
           }
           Label {
               text: win.controllerIndex === 1 ? "WASD Controller Active" : "Orbit Controller Active"
               color: "white"
               verticalAlignment: Label.AlignVCenter
           }
       }
       Row {
           spacing: 8
           CheckBox {
                  checked: win.gridVisible
                  onCheckedChanged: win.gridVisible = checked
              }
           Label {
               text: "Show Infinite Grid"
               color : "white"
           }
       }
       Button {
           text: win.showPlanes ? "Hide Planes" : "Show Planes"
           onClicked: win.showPlanes = !win.showPlanes
       }

   }
}
