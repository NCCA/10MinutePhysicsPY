#!/usr/bin/env -S uv run --script

import math
import sys

from nccapy.Math.Vec2 import Vec2
from PySide6.QtCore import QElapsedTimer, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

GRAVITY = Vec2(0.0, 0.0)  # Gravity vector


def closest_point_on_segment(p, a, b):
    ab = b - a
    ab_dot_ab = ab.dot(ab)
    if ab_dot_ab == 0.0:
        return a.clone()
    t = (p.dot(ab) - a.dot(ab)) / ab_dot_ab
    t = max(0.0, min(1.0, t))
    closest = a + ab * t
    return closest


class Obstacle:
    def __init__(self, radius: float, pos: Vec2, push_velocity: float) -> None:
        self.radius = radius
        self.pos = pos.clone()
        self.push_velocity = push_velocity
        self.colour = QColor("#FF8000")


class Flipper:
    def __init__(
        self,
        radius: float,
        pos: Vec2,
        length: float,
        rest_angle: float,
        max_rotation: float,
        angular_velocity: float,
        restitution: float,
    ) -> None:
        # fix flipper values
        self.radius = radius
        self.pos = pos.clone()
        self.length = length
        self.rest_angle = rest_angle
        self.max_rotation = math.fabs(max_rotation)
        self.sign = self._sign(max_rotation)
        self.angular_velocity = angular_velocity
        # updated values
        self.rotation = 0.0
        self.current_angular_velocity = 0.0
        self.touch_id = -1

    def _sign(self, x):
        """Equivalent of Javascript Math.sign"""
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    def simulate(self, dt: float):
        previous_rotation = self.rotation
        pressed = self.touch_id >= 0
        if pressed:
            self.rotation = min(self.rotation + dt * self.angular_velocity, self.max_rotation)
        else:
            self.rotation = max(self.rotation - dt * self.angular_velocity, 0.0)
        try:
            self.current_angular_velocity = self.sign * (self.rotation - previous_rotation) / dt
        except ZeroDivisionError:
            pass

    def select(self, pos: Vec2): ...

    def get_tip(self):
        angle = self.rest_angle + self.sign + self.rotation
        dir = Vec2(math.cos(angle), math.sin(angle))
        tip = self.pos.clone()
        return tip + dir * self.length


class Ball:
    """
    Represents a 2D ball with position, velocity, radius, and color.
    Used for simulating projectile motion under gravity.
    """

    def __init__(
        self, radius: float, mass: float, pos: Vec2, vel: Vec2, restitution: float, colour: QColor = QColor(0, 0, 0)
    ) -> None:
        self.pos = pos.clone()
        self.velocity = vel.clone()
        self.radius = radius
        self.mass = mass
        self.colour = colour
        self.restitution = restitution

    def simulate(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        self.pos += self.velocity * dt


class SimulationCanvas(QWidget):
    """
    A QWidget subclass that serves as the drawing canvas for the billiard simulation.
    Delegates painting and resizing logic to the Simulation instance.
    """

    def __init__(self, simulation: "Simulation") -> None:
        """
        Initialize the SimulationCanvas.

        Args:
            simulation (Simulation): The simulation logic/controller instance.
        """
        super().__init__()
        self.simulation = simulation

    def paintEvent(self, event) -> None:
        """
        Handle the paint event for the canvas.

        Args:
            event (QPaintEvent): The paint event object.
        """
        painter = QPainter(self)
        self.simulation.draw_simulation(painter)
        painter.end()

    def resizeEvent(self, event) -> None:
        """
        Handle the resize event for the canvas and update the simulation scale.

        Args:
            event (QResizeEvent): The resize event object.
        """
        self.simulation.update_scale()
        super().resizeEvent(event)


class Simulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billard Ball 2D from 10 Minute Physics")
        self.resize(1024, 720)
        # note these values are a good aspect ratio for the simulation
        # when drawing on a 1024x720 canvas
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.score = 0
        self.border = []
        self.balls = []
        self.obstacles = []
        self.flippers = []
        self.flipper_height = 1.7
        self.setup_scene()
        self.create_ui()
        self.c_scale = self.canvas.height() / self.flipper_height
        self.sim_width = self.canvas.width() / self.c_scale
        self.sim_height = self.canvas.height() / self.c_scale

    def create_ui(self) -> None:
        # --- Layout with controls above canvas ---
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 0)
        controls_layout.setSpacing(10)

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.setup_scene)
        controls_layout.addWidget(reset_button)

        self.score_label = QLabel(f"Score: {self.score}")
        controls_layout.addWidget(self.score_label)

        main_layout.addLayout(controls_layout)

        self.canvas = SimulationCanvas(self)
        main_layout.addWidget(self.canvas)
        main_layout.setStretch(0, 0)  # controls_widget
        main_layout.setStretch(1, 2)  # canvas
        self.setCentralWidget(main_widget)

    def _create_boarder(self):
        offset = 0.02
        # border points
        self.border.append(Vec2(0.74, 0.25))
        self.border.append(Vec2(1.0 - offset, 0.4))
        self.border.append(Vec2(1.0 - offset, self.flipper_height - offset))
        self.border.append(Vec2(offset, self.flipper_height - offset))
        self.border.append(Vec2(offset, 0.4))
        self.border.append(Vec2(0.26, 0.25))
        self.border.append(Vec2(0.26, 0.0))
        self.border.append(Vec2(0.74, 0.0))

    def _create_balls(self):
        # Pinballs
        radius = 0.03
        mass = math.pi * radius**2
        pos = Vec2(0.92, 0.5)
        vel = Vec2(-0.2, 3.5)
        self.balls.append(Ball(radius, mass, pos, vel, 0.2))
        pos = Vec2(0.08, 0.5)
        vel = Vec2(0.2, 3.5)
        self.balls.append(Ball(radius, mass, pos, vel, 0.2))

    def _create_obstacles(self):
        self.obstacles.append(Obstacle(0.1, Vec2(0.25, 0.6), 2.0))
        self.obstacles.append(Obstacle(0.1, Vec2(0.75, 0.5), 2.0))
        self.obstacles.append(Obstacle(0.12, Vec2(0.7, 1.0), 2.0))
        self.obstacles.append(Obstacle(0.1, Vec2(0.2, 1.2), 2.0))

    def _create_flippers(self):
        radius = 0.03
        length = 0.2
        max_rotation = 1.0
        rest_angle = 0.5
        angular_velocity = 10.0
        restitution = 0.0
        pos1 = Vec2(0.25, 0.22)
        pos2 = Vec2(0.74, 0.22)
        self.flippers.append(Flipper(radius, pos1, length, -rest_angle, max_rotation, angular_velocity, restitution))
        self.flippers.append(
            Flipper(radius, pos2, length, math.pi + rest_angle, -max_rotation, angular_velocity, restitution)
        )

    def setup_scene(self):
        self._create_boarder()
        self._create_balls()
        self._create_obstacles()
        self._create_flippers()

    def canvas_x(self, pos):
        return pos.x * self.c_scale

    def canvas_y(self, pos):
        return self.canvas.height() - pos.y * self.c_scale

    def update_scale(self):
        # Use the canvas size, not the window size
        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()
        self.c_scale = min(canvas_width / self.sim_width, canvas_height / self.sim_height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_R:
            self.setup_scene()

        elif event.key() == Qt.Key_Left:
            self.flippers[0].touch_id = 1
        elif event.key() == Qt.Key_Right:
            self.flippers[1].touch_id = 1

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.flippers[0].touch_id = -1
        elif event.key() == Qt.Key_Right:
            self.flippers[1].touch_id = -1

    def timerEvent(self, event):
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.simulate(dt)
        self.canvas.update()

    def simulate(self, dt):
        for flipper in self.flippers:
            flipper.simulate(dt)
        for i in range(len(self.balls)):
            ball = self.balls[i]
            ball.simulate(dt)
            for j in range(i + 1, len(self.balls)):
                ball2 = self.balls[j]
                self.handle_ball_ball_collision(ball, ball2)
            for j in range(0, len(self.obstacles)):
                self.ball_obstacle_collisions(ball, self.obstacles[j])
            for j in range(0, len(self.flippers)):
                self.ball_flipper_collisions(ball, self.flippers[j])
            self.handle_ball_border_collision(ball)

    def ball_flipper_collisions(self, ball, flipper):
        closest = closest_point_on_segment(ball.pos, flipper.pos, flipper.get_tip())
        dir = ball.pos - closest
        d = dir.length()
        if d == 0.0 or d > ball.radius + flipper.radius:
            return

        dir = dir * (1.0 / d)  # Normalize

        corr = ball.radius + flipper.radius - d
        ball.pos += dir * corr

        # Update velocity
        radius = closest + dir * flipper.radius
        radius = radius - flipper.pos
        rad_perp = Vec2(-radius.y, radius.x)
        surface_vel = rad_perp * flipper.current_angular_velocity

        v = ball.velocity.dot(dir)
        vnew = surface_vel.dot(dir)

        ball.velocity += dir * (vnew - v)

    def ball_obstacle_collisions(self, ball, obstacle):
        dir = ball.pos - obstacle.pos
        d = dir.length()
        if d == 0 or d > ball.radius + obstacle.radius:
            return
        dir.normalize()
        corr = ball.radius + obstacle.radius - d
        ball.pos += dir * corr
        v = ball.velocity.dot(dir)
        ball.velocity += dir * (obstacle.push_velocity - v)
        self.score += 1

    def handle_ball_ball_collision(self, ball1, ball2):
        dir = ball2.pos - ball1.pos  # Vec2 subtraction
        restitution = min(ball1.restitution, ball2.restitution)
        d = dir.length()
        if d == 0.0 or d > ball1.radius + ball2.radius:
            return

        dir = dir * (1.0 / d)  # Normalize

        corr = (ball1.radius + ball2.radius - d) / 2.0
        ball1.pos -= dir * corr
        ball2.pos += dir * corr

        v1 = ball1.velocity.dot(dir)
        v2 = ball2.velocity.dot(dir)

        m1 = ball1.mass
        m2 = ball2.mass

        newV1 = (m1 * v1 + m2 * v2 - m2 * (v1 - v2) * restitution) / (m1 + m2)
        newV2 = (m1 * v1 + m2 * v2 - m1 * (v2 - v1) * restitution) / (m1 + m2)

        ball1.velocity += dir * (newV1 - v1)
        ball2.velocity += dir * (newV2 - v2)

    def handle_ball_border_collision(self, ball):
        border = self.border
        if len(border) < 3:
            return

        min_dist = None
        closest = None
        normal = None

        for i in range(len(border)):
            a = border[i]
            b = border[(i + 1) % len(border)]
            c = closest_point_on_segment(ball.pos, a, b)
            d = ball.pos - c
            dist = d.length()
            if min_dist is None or dist < min_dist:
                min_dist = dist
                closest = c
                ab = b - a
                normal = Vec2(-ab.y, ab.x)  # perp

        # push out
        d = ball.pos - closest
        dist = d.length()
        if dist == 0.0:
            d = normal
            dist = normal.length()
        d = d * (1.0 / dist)

        if d.dot(normal) >= 0.0:
            if dist > ball.radius:
                return
            ball.pos += d * (ball.radius - dist)
        else:
            ball.pos += d * -(dist + ball.radius)

        # update velocity
        v = ball.velocity.dot(d)
        vnew = abs(v) * ball.restitution

        ball.velocity += d * (vnew - v)

    # ---- Drawing logic is here, but only called by SimulationCanvas.paintEvent ----
    def draw_simulation(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_border(painter)
        for ball in self.balls:
            self.draw_circle(painter, ball)
        for obstacle in self.obstacles:
            self.draw_circle(painter, obstacle)
        self.draw_flippers(painter)

    def draw_flippers(self, painter):
        def draw_disc(painter, x, y, radius):
            painter.drawEllipse(QPointF(x, y), radius, radius)

        painter.setBrush(QColor("#FF0000"))
        painter.setPen(Qt.NoPen)
        cScale = self.c_scale

        for flipper in self.flippers:
            painter.save()
            # Translate to flipper position
            painter.translate(self.canvas_x(flipper.pos), self.canvas_y(flipper.pos))
            # QPainter rotates counterclockwise, so we convert radians to degrees and negate
            angle_deg = -math.degrees(flipper.rest_angle + flipper.sign * flipper.rotation)
            painter.rotate(angle_deg)
            # Draw the flipper rectangle
            rect = QRectF(0.0, -flipper.radius * self.c_scale, flipper.length * cScale, 2.0 * flipper.radius * cScale)
            painter.drawRect(rect)
            # Draw the discs at each end
            draw_disc(painter, 0, 0, flipper.radius * cScale)
            draw_disc(painter, flipper.length * cScale, 0, flipper.radius * cScale)
            painter.restore()

    def draw_border(self, painter):
        if len(self.border) >= 2:
            pen = QPen(QColor("#000000"))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            # # Convert border points to canvas coordinates
            points = [QPointF(self.canvas_x(v), self.canvas_y(v)) for v in self.border]

            # # Draw the closed polygon
            if points:
                painter.drawPolygon(QPolygonF(points))

            # Optionally reset pen width if needed elsewhere
            pen.setWidth(1)
            painter.setPen(pen)

    def draw_circle(self, painter, ball):
        painter.setPen(QPen(ball.colour))
        painter.setBrush(QBrush(ball.colour))
        x = self.canvas_x(ball.pos)
        y = self.canvas_y(ball.pos)
        radius = ball.radius * self.c_scale
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

    def draw_text(self, painter, text, x, y, size, colour, font="Arial"):
        painter.setPen(colour)
        painter.setFont(QFont(font, size))
        painter.drawText(x, y, text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulation = Simulation()
    simulation.show()
    sys.exit(app.exec())
