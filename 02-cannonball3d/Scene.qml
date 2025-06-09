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

    View3D {
        id: view3d
        objectName : "view3d"
        anchors.fill: parent

        environment: SceneEnvironment {
            clearColor: theFog.color
            backgroundMode: SceneEnvironment.Color
            fog: Fog {
                    id: theFog
                    enabled: true
                    depthEnabled: true
                    density : 0.8
                }
        }
        camera: camera


        Node {
            id: originNode
            PerspectiveCamera {
                id: cameraNode
                position: Qt.vector3d(0, 2, 8)
                fieldOfView: 70
                clipNear: 0.01
                clipFar: 100
            }
        }

        OrbitCameraController {
            origin: originNode
            camera: camera
        }
        DirectionalLight {
                   color: "#55505a"
                   brightness: 1
                   position: Qt.vector3d(0, 3, 0)
                   castsShadow: true
                   shadowMapQuality: Light.ShadowMapQualityHigh
                   shadowBias: 0.005
                   shadowFactor: 10 // not a direct mapping, but controls shadow darkness
                   shadowMapFar: 10

               }



        // DirectionalLight {
        //    // worldDirection: Qt.vector3d(-1, -1, -1)
        //     eulerRotation: Qt.vector3d(-45, -45, 0)
        //     brightness: 2
        // }
        SpotLight {
            color: "white"
            brightness: 1
            position: Qt.vector3d(2, 3, 3)
            eulerRotation: Qt.vector3d(-30, 0, -30)
            coneAngle: 80 //Math.PI/5
            castsShadow: true
            shadowMapQuality: Light.ShadowMapQualityHigh
            shadowBias: 0.05
            shadowFactor: 10 // not a direct mapping, but controls shadow darkness
            shadowMapFar: 1
        }
        Model {
                    id : "ground"
                   source: "#Rectangle"
                   position: Qt.vector3d(0.0, -0.2, 0.0)
                   scale: Qt.vector3d(20, 1, 20)
                   eulerRotation : Qt.vector3d(-90,0,0)
                   y: -0.1
                   materials: DefaultMaterial {
                       diffuseColor: "#a0adaf"
                       specularAmount: 1.0
                       specularRoughness: 0.1
                   }
                   receivesShadows: true
               }


        Model {
            id: ball
            objectName : "ball"
            source: "#Sphere"
            scale: Qt.vector3d(0.01, 0.01, 0.01)
            materials: DefaultMaterial { diffuseColor: "red" }
            // Position will be set from Python
            property vector3d ballPosition: Qt.vector3d(0.01, 0.01, 0.01)
            x: ballPosition.x
            y: ballPosition.y
            z: ballPosition.z
        }
    }


// UI Overlay
   Row {
       spacing: 16
       anchors {
           top: parent.top
           right: parent.right
           topMargin: 24
           rightMargin: 24
       }

       Button {
           text: "Start"
           onClicked: ballSim.start()
       }
       Button {
           text: "Reset"
           onClicked: ballSim.reset()
       }
   }
}
