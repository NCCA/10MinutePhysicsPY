#!/usr/bin/env -S uv run --script
import sys

from nccapy import Vec3
from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QVector3D
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

GRAVITY = Vec3(0, -10.0, 0)
WORLD_SIZE = Vec3(1.5, 0, 2.5)


class Bounds(QObject):
    xMinChanged = Signal()
    xMaxChanged = Signal()
    zMinChanged = Signal()
    zMaxChanged = Signal()
    yMinChanged = Signal()

    def __init__(self, xMin, xMax, zMin, zMax, yMin):
        super().__init__()
        self._xMin = xMin
        self._xMax = xMax
        self._zMin = zMin
        self._zMax = zMax
        self._yMin = yMin

    @Property(float, notify=xMinChanged)
    def xMin(self):
        return self._xMin

    @xMin.setter
    def xMin(self, v):
        if self._xMin != v:
            self._xMin = v
            self.xMinChanged.emit()

    @Property(float, notify=xMaxChanged)
    def xMax(self):
        return self._xMax

    @xMax.setter
    def xMax(self, v):
        if self._xMax != v:
            self._xMax = v
            self.xMaxChanged.emit()

    @Property(float, notify=zMinChanged)
    def zMin(self):
        return self._zMin

    @zMin.setter
    def zMin(self, v):
        if self._zMin != v:
            self._zMin = v
            self.zMinChanged.emit()

    @Property(float, notify=zMaxChanged)
    def zMax(self):
        return self._zMax

    @zMax.setter
    def zMax(self, v):
        if self._zMax != v:
            self._zMax = v
            self.zMaxChanged.emit()

    @Property(float, notify=yMinChanged)
    def yMin(self):
        return self._yMin

    @yMin.setter
    def yMin(self, v):
        if self._yMin != v:
            self._yMin = v
            self.yMinChanged.emit()


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
        return QVector3D(self._pos.x, self._pos.y, self._pos.z)

    @Slot()
    def start(self):
        self._running = True

    @Slot()
    def stop(self):
        self._running = False

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
    radius = 0.01
    sim = BallSim(Vec3(0, 5, 0), radius, Vec3(2.0, 5.0, 3.0))
    engine.rootContext().setContextProperty("ballSim", sim)
    bounds = Bounds(-1.5, 1.5, -2.5, 2.5, 0)
    engine.rootContext().setContextProperty("bounds", bounds)
    engine.load(QUrl.fromLocalFile("Scene.qml"))

    # Connect simulation to QML
    root_objects = engine.rootObjects()
    if root_objects:
        win = root_objects[0]
        view3d = win.findChild(QObject, "view3d")
        ball = view3d.findChild(QObject, "ball")

        def update_ball():
            ball.setProperty("ballPosition", sim.ballPosition)
            ball.setProperty("ball_radius", sim.radius)

        sim.ballPositionChanged.connect(update_ball)

    timer = QTimer()
    timer.timeout.connect(sim.step)
    timer.start(8)  # approx 60 fps

    sys.exit(app.exec())
