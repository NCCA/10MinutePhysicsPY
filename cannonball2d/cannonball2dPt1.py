#!/usr/bin/env -S uv run --script

import sys

from nccapy.Math.Vec2 import Vec2
from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow

GRAVITY = Vec2(0.0, -10.0)  # Gravity vector


class Ball:
    """
    Represents a 2D ball with position, velocity, radius, and color.
    Used for simulating projectile motion under gravity.
    """

    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float) -> None:
        """
        Initialize a Ball object.

        Args:
            x (float): Initial x-coordinate of the ball.
            y (float): Initial y-coordinate of the ball.
            vx (float): Initial velocity in the x-direction.
            vy (float): Initial velocity in the y-direction.
            radius (float): Radius of the ball.
        """
        self.pos = Vec2(x, y)
        self.velocity = Vec2(vx, vy)
        self.radius = radius
        self.colour = QColor(255, 0, 0)

    def update(self, dt: float) -> None:
        """
        Update the ball's velocity and position based on elapsed time.

        Args:
            dt (float): Time step in seconds.
        """
        self.velocity += GRAVITY * dt
        self.pos += self.velocity * dt


class Simulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Cannon Ball 2D from 10 Minute Physics")
        self.ball = Ball(0.2, 0.2, 10.0, 15.0, 0.2)
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

    def Simulation_x(self, pos):
        """Convert a position in the simulation to Simulation x-coordinate."""
        return pos.x * self.c_scale

    def Simulation_y(self, pos):
        """Convert a position in the simulation to Simulation y-coordinate."""
        return self.height() - pos.y * self.c_scale

    def update_scale(self):
        """Update the scale based on the current window size."""
        self.ball.radius = 0.2
        self.c_scale = min(self.width() / self.sim_width, self.height() / self.sim_height)
        self.sim_width = self.width() / self.c_scale
        self.sim_height = self.height() / self.c_scale

    def resizeEvent(self, event):
        self.update_scale()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_R:
            # Reset the simulation
            self.ball = Ball(0.2, 0.2, 10.0, 15.0, 0.2)

    def timerEvent(self, event):
        """measure the time elapsed between updates (in seconds), which is essential for time based
        calculations in simulations, animations, or games. It ensures that the simulation progresses
        at a rate consistent with real time, regardless of
        how fast or slow the update loop is running."""
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.ball.update(dt)
        self.check_bounds()
        # call redraw of the Simulation
        self.update()

    def check_bounds(self):
        """Check if the ball is out of bounds and adjust its position and velocity accordingly."""
        # Left edge
        if self.ball.pos.x - self.ball.radius < 0:
            self.ball.pos.x = self.ball.radius
            self.ball.velocity.x *= -1
        # Right edge
        if self.ball.pos.x + self.ball.radius > self.sim_width:
            self.ball.pos.x = self.sim_width - self.ball.radius
            self.ball.velocity.x *= -1
        # Bottom edge
        if self.ball.pos.y - self.ball.radius < 0:
            self.ball.pos.y = self.ball.radius
            self.ball.velocity.y *= -1
        # Top edge
        if self.ball.pos.y + self.ball.radius > self.sim_height:
            self.ball.pos.y = self.sim_height - self.ball.radius
            self.ball.velocity.y *= -1

    def paintEvent(self, event):
        """This is where the drawing is done"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_circle(painter, self.ball)
        self.draw_text(painter, "Cannon Ball 2D Simulation Press R to reset", 10, 20, 16, QColor(0, 0, 0))

    def draw_circle(self, painter, ball):
        """Draw a circle representing the ball on the Simulation."""
        painter.setPen(QPen(ball.colour))
        painter.setBrush(QBrush(ball.colour))
        # Calculate the position and radius of the circle which is different from the simulation coordinates
        x = self.Simulation_x(ball.pos)
        y = self.Simulation_y(ball.pos)
        radius = ball.radius * self.c_scale
        # Draw the circle
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

    def draw_text(self, painter, text, x, y, size, colour, font="Arial"):
        """
        Draw text on the Simulation.

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulation = Simulation()
    simulation.show()
    sys.exit(app.exec())
