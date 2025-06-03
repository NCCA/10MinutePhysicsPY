#!/usr/bin/env -S uv run --script

import random
import sys
from enum import Enum

from nccapy import Vec2
from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow

GRAVITY = Vec2(0.0, -9.78)  # Gravity vector


class IntegrationMode(Enum):
    SIMPLE = "simple"
    SEMI_IMPLICIT = "semi-implicit"
    RK4 = "rk4"
    VERLET = "verlet"


class Ball:
    def __init__(self, x, y, vx, vy, radius):
        self.pos = Vec2(x, y)
        self.velocity = Vec2(vx, vy)
        self.radius = radius * random.uniform(0.5, 1.5)  # Randomize radius slightly
        self.gravity = Vec2(0.0, -10.0)
        self.colour = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.num_steps = 100  # Number of steps for more accurate simulation

    def update(self, dt, integration_mode):
        match integration_mode:
            case IntegrationMode.SIMPLE:
                self.velocity += GRAVITY * dt
                self.pos += self.velocity * dt
            case IntegrationMode.SEMI_IMPLICIT:
                sdt = dt / self.num_steps  # Divide the time step into smaller steps for better accuracy
                for _ in range(self.num_steps):
                    self.velocity += GRAVITY * sdt
                    self.pos += self.velocity * sdt
            case IntegrationMode.RK4:
                sdt = dt / self.num_steps  # Divide the time step into smaller steps for better accuracy
                # note this is a simple RK4 as gravity is constant
                for _ in range(self.num_steps):
                    # RK4 for velocity and position
                    # dy/dt = velocity, dv/dt = GRAVITY

                    # k1
                    v1 = self.velocity
                    a1 = GRAVITY

                    # k2
                    v2 = self.velocity + a1 * (sdt / 2)
                    a2 = GRAVITY

                    # k3
                    v3 = self.velocity + a2 * (sdt / 2)
                    a3 = GRAVITY

                    # k4
                    v4 = self.velocity + a3 * sdt
                    a4 = GRAVITY

                    # Update position and velocity
                    self.pos += (v1 + 2 * v2 + 2 * v3 + v4) * (sdt / 6)
                    self.velocity += (a1 + 2 * a2 + 2 * a3 + a4) * (sdt / 6)
            case IntegrationMode.VERLET:
                # Verlet integration
                sdt = dt / self.num_steps
                for _ in range(self.num_steps):
                    # Calculate the new position based on the current position and velocity
                    new_pos = self.pos + self.velocity * sdt + 0.5 * GRAVITY * (sdt**2)
                    # Update velocity based on the average of the current and new positions
                    self.velocity += GRAVITY * sdt
                    # Update position to the new position
                    self.pos = new_pos


class Canvas(QMainWindow):
    def __init__(self):
        super().__init__()

        # var simWidth = canvas.width / cScale;
        # var simHeight = canvas.height / cScale;

        self.setWindowTitle("Simple Cannon Ball 2D from 10 Minute Physics")
        self.balls = []  # Ball(0.2, 0.2, 10.0, 15.0, 0.2)
        self.resize(1024, 720)
        self.sim_width = 20.0
        self.sim_height = 15.0
        self.c_scale = min(self.width(), self.height()) / self.sim_width
        self.sim_width = self.width() / self.c_scale
        self.sim_height = self.height() / self.c_scale
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.integration_mode = IntegrationMode.RK4  # Default integration mode

    def canvas_x(self, pos):
        return pos.x * self.c_scale

    def update_scale(self):
        self.c_scale = min(self.width() / self.sim_width, self.height() / self.sim_height)
        self.sim_width = self.width() / self.c_scale
        self.sim_height = self.height() / self.c_scale

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for i in range(0, 20):
                # Convert mouse position to simulation coordinates
                x = event.position().x() / self.c_scale
                y = (self.height() - event.position().y()) / self.c_scale
                # Create a new ball at the mouse position with a random velocity
                vx = 10.0 * (2.0 * (random.random() - 0.5))  # Random horizontal velocity
                vy = 10.0 * (2.0 * (random.random() - 0.5))  # Random vertical velocity
                new_ball = Ball(x, y, vx, vy, 0.2)
                self.balls.append(new_ball)

    def resizeEvent(self, event):
        self.update_scale()
        super().resizeEvent(event)

    def canvas_y(self, pos):
        return self.height() - pos.y * self.c_scale

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            # Clear all balls when space is pressed
            self.balls.clear()
        elif event.key() == Qt.Key_R:
            # Reset the simulation
            self.balls = [Ball(0.2, 0.2, 10.0, 15.0, 0.2)]
        elif event.key() == Qt.Key_1:
            self.integration_mode = IntegrationMode.SIMPLE

        elif event.key() == Qt.Key_2:
            self.integration_mode = IntegrationMode.SEMI_IMPLICIT
        elif event.key() == Qt.Key_3:
            self.integration_mode = IntegrationMode.RK4
        elif event.key() == Qt.Key_4:
            self.integration_mode = IntegrationMode.VERLET

    def timerEvent(self, event):
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        for ball in self.balls:
            ball.update(dt, self.integration_mode)
        self.update()
        self.check_bounds()

    def check_bounds(self):
        for ball in self.balls:
            # Left edge
            if ball.pos.x - ball.radius < 0:
                ball.pos.x = ball.radius
                ball.velocity.x *= -1
            # Right edge
            if ball.pos.x + ball.radius > self.sim_width:
                ball.pos.x = self.sim_width - ball.radius
                ball.velocity.x *= -1
            # Bottom edge
            if ball.pos.y - ball.radius < 0:
                ball.pos.y = ball.radius
                ball.velocity.y *= -1
            # Top edge
            if ball.pos.y + ball.radius > self.sim_height:
                ball.pos.y = self.sim_height - ball.radius
                ball.velocity.y *= -1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for ball in self.balls:
            self.draw_circle(painter, ball)
        self.draw_text(painter, "Cannon Ball 2D Simulation Press R to reset", 10, 20, 16, QColor(0, 0, 0))
        self.draw_text(painter, "Space to Reset click to add multiple balls", 10, 40, 16, QColor(0, 0, 0))
        self.draw_text(
            painter,
            f"Integration 1 for Euler 2 Semi Implicit Euler 3 RK4  4 Verlet  Current Mode : {self.integration_mode.value}",
            10,
            60,
            16,
            QColor(0, 0, 0),
        )

    def draw_text(self, painter, text, x, y, size, colour, font="Arial"):
        """
        Draw text on the canvas.

        Args:
            painter (QPainter): The painter to draw with.
            text (str): The text to draw.
            x (int): The x-coordinate for the text.
            y (int): The y-coordinate for the text.
            size (int): The font size of the text.
            colour (QColor): The colour of the text.
            font (str): The font family of the text.
        """
        painter.setPen(colour)
        painter.setFont(QFont(font, size))
        painter.drawText(x, y, text)

    def draw_circle(self, painter, ball):
        # Calculate the position and radius of the circle
        painter.setPen(QPen(ball.colour))
        painter.setBrush(QBrush(ball.colour))

        x = self.canvas_x(ball.pos)
        y = self.canvas_y(ball.pos)
        radius = ball.radius * self.c_scale

        # Draw the circle
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    canvas = Canvas()
    canvas.show()
    sys.exit(app.exec())
