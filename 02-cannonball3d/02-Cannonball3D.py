#!/usr/bin/env -S uv run --script
import sys

from nccapy import Vec3
from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

GRAVITY = Vec3(0, -10.0, 0)
WORLD_SIZE = Vec3(1.5, 0, 2.5)


class BallSim(QObject):
    ballPositionChanged = Signal()

    def __init__(self, pos: Vec3, radius: float, velocity: Vec3) -> None:
        super().__init__()
        self._pos = pos.clone()
        self._vel = velocity.clone()
        self._initial_pos = pos.clone()
        self._initial_vel = velocity.clone()
        self.radius = radius
        self._running = False

    @Property("QVector3D", notify=ballPositionChanged)
    def ballPosition(self):
        from PySide6.QtGui import QVector3D

        return QVector3D(self._pos.x, self._pos.y, self._pos.z)

    @Slot()
    def start(self):
        self._running = True

    @Slot()
    def reset(self):
        self._running = False
        self._pos = self._initial_pos.clone()
        self._vel = self._initial_vel.clone()
        self.ballPositionChanged.emit()

    @Slot()
    def step(self):
        if not self._running:
            return
        dt = 1.0 / 60.0
        self._vel += GRAVITY * dt
        self._pos += self._vel * dt

        # Collision with world bounds
        if self._pos.x < -WORLD_SIZE.x:
            self._pos.x = -WORLD_SIZE.x
            self._vel.x = -self._vel.x
        if self._pos.x > WORLD_SIZE.x:
            self._pos.x = WORLD_SIZE.x
            self._vel.x = -self._vel.x
        if self._pos.z < -WORLD_SIZE.z:
            self._pos.z = -WORLD_SIZE.z
            self._vel.z = -self._vel.z
        if self._pos.z > WORLD_SIZE.z:
            self._pos.z = WORLD_SIZE.z
            self._vel.z = -self._vel.z
        if self._pos.y < self.radius:
            self._pos.y = self.radius
            self._vel.y = -self._vel.y

        self.ballPositionChanged.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    radius = 0.2
    sim = BallSim(Vec3(radius, radius, radius), radius, Vec3(2.0, 5.0, 3.0))
    engine.rootContext().setContextProperty("ballSim", sim)
    engine.load(QUrl.fromLocalFile("Scene.qml"))

    # Connect simulation to QML
    root_objects = engine.rootObjects()
    if root_objects:
        win = root_objects[0]
        view3d = win.findChild(QObject, "view3d")
        ball = view3d.findChild(QObject, "ball")

        def update_ball():
            ball.setProperty("ballPosition", sim.ballPosition)

        sim.ballPositionChanged.connect(update_ball)

    timer = QTimer()
    timer.timeout.connect(sim.step)
    timer.start(16)  # approx 60 fps

    sys.exit(app.exec())
