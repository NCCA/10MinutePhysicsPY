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
    View3D {
        id: view3d
        objectName : "view3d"
        anchors.fill: parent

        environment: SceneEnvironment {
            Node {
                position: Qt.vector3d(0, 1, 0)
                InfiniteGrid {
                    id: grid
                    gridInterval: 10
                    visible: win.gridVisible
                }
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
        // // Left plane (x = -1.5)
        // Model {
        //     source: "#Rectangle"
        //     position: Qt.vector3d(-1.5, 1.0, 0.0)
        //     eulerRotation : Qt.vector3d(0,90,0)
        //     scale: Qt.vector3d(0.05, 0.05, 0.05) // Thin in X, tall in Y, wide in Z
        //     materials: DefaultMaterial {
        //         diffuseColor: "#00ff00"
        //         opacity: 0.3
        //     }
        // }

        // // // Right plane (x = 1.5)
        // Model {
        //     source: "#Rectangle"
        //     position: Qt.vector3d(1.7, 1.0, 0.0)
        //     eulerRotation : Qt.vector3d(0,90,0)
        //     scale: Qt.vector3d(0.05, 0.05, 0.05) // Thin in X, tall in Y, wide in Z
        //     materials: DefaultMaterial {
        //         diffuseColor: "#00ff00"
        //         opacity: 0.3
        //     }
        // }

        // Model {
        //     source: "#Rectangle"
        //     position: Qt.vector3d(0, 1.0, 2.7)
        //     eulerRotation : Qt.vector3d(0,0,0)
        //     scale: Qt.vector3d(0.05, 0.05, 0.05) // Thin in X, tall in Y, wide in Z
        //     materials: DefaultMaterial {
        //         diffuseColor: "#00ff00"
        //         opacity: 0.3
        //     }
        // }
        // Model {
        //     source: "#Rectangle"
        //     position: Qt.vector3d(0, 1.0, -2.7)
        //     eulerRotation : Qt.vector3d(0,0,0)
        //     scale: Qt.vector3d(0.05, 0.05, 0.05) // Thin in X, tall in Y, wide in Z
        //     materials: DefaultMaterial {
        //         diffuseColor: "#00ff00"
        //         opacity: 0.3
        //     }
        // }


        // // Front plane (z = 2.5)
        // Model {
        //     source: "#Rectangle"
        //     position: Qt.vector3d(0.5, 0.5, 0.0)
        //     scale: Qt.vector3d(3, 1, 0.01)
        //     x: 0
        //     y: 0.5
        //     z: 2.5
        //     materials: DefaultMaterial {
        //         diffuseColor: "#0000ff"
        //         opacity: 0.3
        //     }
        // }


        // Model {
        //     id : ground
        //     source: "#Rectangle"
        //     position: Qt.vector3d(0.0, -0.4, 0.0)
        //     eulerRotation : Qt.vector3d(-90,0,0)
        //     scale: Qt.vector3d(3, 5, 0.01)
        //     x: 0
        //     y: 0
        //     z: 0
        //     materials: DefaultMaterial {
        //         diffuseColor: "#252525"
        //         opacity: 1.0
        //     }
        // }

        // Model {
        //             id : "ground"
        //            source: "#Rectangle"
        //            position: Qt.vector3d(0.0, -0.2, 0.0)
        //            scale: Qt.vector3d(20, 1, 20)
        //            eulerRotation : Qt.vector3d(-90,0,0)
        //            y: -0.1
        //            materials: DefaultMaterial {
        //                diffuseColor: Qt.rgba(0.2, 0.2, 0.2, 0.3)
        //                specularAmount: 1.0
        //                specularRoughness: 0.1
        //            }
        //            receivesShadows: true
        //        }
        // Left plane (x = xMin)
            // Model {
            //     source: "#Rectangle"
            //     //position: Qt.vector3d(0.5, 0.5, 0.0)
            //     //scale: Qt.vector3d(0.1, 0.1,0.5) // Math.abs(zMax - zMin))
            //     //eulerRotation : Qt.vector3d(0,90,0)
            //     x: xMin
            //     y: 0.5
            //     z: (zMax + zMin) / 2
            //     materials: DefaultMaterial { diffuseColor: "#00ff00"; opacity: 0.3 }
            // }
            // // Right plane (x = xMax)
            // Model {
            //     source: "#Rectangle"
            //     position: Qt.vector3d(0.5, 0.5, 0.0)
            //     scale: Qt.vector3d(0.01, 1, Math.abs(zMax - zMin))
            //     x: xMax
            //     y: 0.5
            //     z: (zMax + zMin) / 2
            //     materials: DefaultMaterial { diffuseColor: "#00ff00"; opacity: 0.3 }
            // }
            // // Back plane (z = zMin)
            // Model {
            //     source: "#Rectangle"
            //     position: Qt.vector3d(0.5, 0.5, 0.0)
            //     scale: Qt.vector3d(Math.abs(xMax - xMin), 1, 0.01)
            //     x: (xMax + xMin) / 2
            //     y: 0.5
            //     z: zMin
            //     materials: DefaultMaterial { diffuseColor: "#0000ff"; opacity: 0.3 }
            // }
            // // Front plane (z = zMax)
            // Model {
            //     source: "#Rectangle"
            //     position: Qt.vector3d(0.5, 0.5, 0.0)
            //     scale: Qt.vector3d(Math.abs(xMax - xMin), 1, 0.01)
            //     x: (xMax + xMin) / 2
            //     y: 0.5
            //     z: zMax
            //     materials: DefaultMaterial { diffuseColor: "#0000ff"; opacity: 0.3 }
            // }
            // // Floor (y = yMin)
            Model {

                id : ground
                source: "#Rectangle"
                position: Qt.vector3d(0.0, -0.4, 0.0)
                eulerRotation : Qt.vector3d(-90,0,0)
                scale: Qt.vector3d(3, 5, 0.01)
                x: 0
                y: 0
                z: 0
                materials: DefaultMaterial { diffuseColor: "#ffffff"; opacity: 1 }
                // source: "#Rectangle"
                // position: Qt.vector3d(0.0, 0.0, 0.0)
                // //scale: Qt.vector3d(Math.abs(xMax - xMin), Math.abs(zMax - zMin), 0.01)
                // scale : Qt.vector3d(20.0,1.0,20.0)
                // eulerRotation : Qt.vector3d(-90,0,0)
                // x: (xMax + xMin) / 2
                // y: yMin
                // z: (zMax + zMin) / 2
                // materials: DefaultMaterial { diffuseColor: "#000000"; opacity: 0.3 }
                // PrincipledMaterial {
                //         id: commonMaterial
                //         baseColor: "grey"
                //     }
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
       // anchors {
       //     top: parent.top
       //     right: parent.left
       //     topMargin: 24
       //     rightMargin: 24
       // }

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

   }
}
