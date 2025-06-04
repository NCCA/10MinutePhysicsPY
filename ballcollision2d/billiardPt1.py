#!/usr/bin/env -S uv run --script

import math
import random
import sys

from nccapy.Math.Vec2 import Vec2
from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSlider, QVBoxLayout, QWidget

GRAVITY = Vec2(0.0, 0.0)  # Gravity vector


class Ball:
    """
    Represents a 2D ball with position, velocity, radius, and color.
    Used for simulating projectile motion under gravity.
    """

    def __init__(self, radius: float, mass: float, pos: Vec2, vel: Vec2) -> None:
        self.pos = pos.clone()
        self.velocity = vel.clone()
        self.radius = radius
        self.mass = mass
        self.colour = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self, dt: float) -> None:
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
        self.balls = []
        self.resize(1024, 720)
        self.sim_width = 20.0
        self.sim_height = 15.0
        self.c_scale = min(self.width(), self.height()) / self.sim_width
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.restitution = 1.0
        self.setup_scene()

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

        self.restitution_label = QLabel(f"Restitution: {self.restitution:.2f}")
        controls_layout.addWidget(self.restitution_label)

        restitution = QSlider(Qt.Horizontal)
        restitution.setRange(0, 100)
        restitution.setValue(int(self.restitution * 100))
        restitution.setTickPosition(QSlider.TicksBelow)
        restitution.setTickInterval(10)
        restitution.valueChanged.connect(self.update_restitution)
        controls_layout.addWidget(restitution)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.canvas = SimulationCanvas(self)
        main_layout.addWidget(self.canvas)

        self.setCentralWidget(main_widget)
        # --- End layout code ---

    def update_restitution(self, value):
        self.restitution = value / 100.0
        self.restitution_label.setText(f"Restitution: {self.restitution:.2f}")

    def setup_scene(self):
        self.balls.clear()
        num_balls = 20
        for _ in range(num_balls):
            radius = random.uniform(0.2, 1.0)
            mass = math.pi * radius**2
            pos = Vec2(
                random.uniform(radius, self.sim_width - radius), random.uniform(radius, self.sim_height - radius)
            )
            vel = Vec2(random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0))
            self.balls.append(Ball(radius, mass, pos, vel))

    def canvas_x(self, pos):
        return pos.x * self.c_scale

    def canvas_y(self, pos):
        return self.canvas.height() - pos.y * self.c_scale

    def update_scale(self):
        # Use the canvas size, not the window size
        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()
        self.c_scale = min(canvas_width / self.sim_width, canvas_height / self.sim_height)
        # Optionally, keep sim_width and sim_height fixed, or update them if you want the simulation area to scale
        # For a fixed simulation area, comment out the next two lines:
        # self.sim_width = canvas_width / self.c_scale
        # self.sim_height = canvas_height / self.c_scale

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_R:
            self.balls.clear()
            self.setup_scene()

    def timerEvent(self, event):
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.simulate(dt)
        self.canvas.update()

    def simulate(self, dt):
        for i in range(len(self.balls)):
            ball1 = self.balls[i]
            ball1.update(dt)
            for j in range(i + 1, len(self.balls)):
                ball2 = self.balls[j]
                self.handle_ball_collisions(ball1, ball2)
        self.check_bounds()

    def check_bounds(self):
        for ball in self.balls:
            if ball.pos.x - ball.radius < 0:
                ball.pos.x = ball.radius
                ball.velocity.x *= -1
            if ball.pos.x + ball.radius > self.sim_width:
                ball.pos.x = self.sim_width - ball.radius
                ball.velocity.x *= -1
            if ball.pos.y - +ball.radius < 0:
                ball.pos.y = ball.radius
                ball.velocity.y *= -1
            if ball.pos.y + ball.radius > self.sim_height:
                ball.pos.y = self.sim_height - ball.radius
                ball.velocity.y *= -1

    def handle_ball_collisions(self, ball1, ball2):
        dir = ball2.pos - ball1.pos
        d = dir.length()
        if d == 0 or d > ball1.radius + ball2.radius:
            return
        dir.normalize()
        corr = (ball1.radius + ball2.radius - d) / 2.0
        ball1.pos += dir * -corr
        ball2.pos += dir * corr
        v1 = ball1.velocity.dot(dir)
        v2 = ball2.velocity.dot(dir)
        m1 = ball1.mass
        m2 = ball2.mass
        new_v1 = (m1 * v1 + m2 * v2 - m2 * (v1 - v2) * self.restitution) / (m1 + m2)
        new_v2 = (m1 * v1 + m2 * v2 - m1 * (v2 - v1) * self.restitution) / (m1 + m2)
        ball1.velocity += dir * (new_v1 - v1)
        ball2.velocity += dir * (new_v2 - v2)

    # ---- Drawing logic is here, but only called by SimulationCanvas.paintEvent ----
    def draw_simulation(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        for ball in self.balls:
            self.draw_circle(painter, ball)

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
