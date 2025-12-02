#!/usr/bin/env -S uv run --script
import sys

from ncca.ngl import Vec3
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


class Ball:
    """
    Represents a 2D ball with position, velocity, radius, and color.
    Used for simulating projectile motion under gravity.
    """

    def __init__(self, radius: float, pos: Vec3, vel: Vec3) -> None:
        self.pos = pos.copy()
        self.velocity = vel.copy()
        self.radius = radius

    def update(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        self.pos += self.velocity * dt

    def wall_collide(self):
        # Collision with world bounds
        if self.pos.x < -WORLD_SIZE.x:
            self.pos.x = -WORLD_SIZE.x
            self.velocity.x = -self.velocity.x
        if self.pos.x > WORLD_SIZE.x:
            self.pos.x = WORLD_SIZE.x
            self.velocity.x = -self.velocity.x
        if self.pos.z < -WORLD_SIZE.z:
            self.pos.z = -WORLD_SIZE.z
            self.velocity.z = -self.velocity.z
        if self.pos.z > WORLD_SIZE.z:
            self.pos.z = WORLD_SIZE.z
            self.velocity.z = -self.velocity.z
        if self.pos.y < self.radius:
            self.pos.y = self.radius
            self.velocity.y = -self.velocity.y


class BallSim(QObject):
    ballPositionChanged = Signal()

    def __init__(self, pos: Vec3, radius: float, velocity: Vec3) -> None:
        super().__init__()
        self._initial_position = pos.copy()
        self._initial_velocity = velocity.copy()

        self.ball = Ball(radius, pos, velocity)
        self._running = False

    @Property("QVector3D", notify=ballPositionChanged)
    def ballPosition(self):
        return QVector3D(self.ball.pos.x, self.ball.pos.y, self.ball.pos.z)

    @Slot()
    def start(self):
        self._running = True

    @Slot()
    def stop(self):
        self._running = False

    @Slot()
    def reset(self):
        self._running = False
        self.ball.pos = self._initial_position.copy()
        self.ball.velocity = self._initial_velocity.copy()
        self.ballPositionChanged.emit()

    @Slot()
    def step(self):
        if not self._running:
            return

        dt = 1.0 / 60.0
        self.ball.update(dt)
        self.ball.wall_collide()
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
            ball.setProperty("ball_radius", sim.ball.radius)

        sim.ballPositionChanged.connect(update_ball)

    timer = QTimer()
    timer.timeout.connect(sim.step)
    timer.start(8)  # approx 60 fps

    sys.exit(app.exec())
