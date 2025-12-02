#!/usr/bin/env -S uv run --script

import math
import random
import sys
from enum import Enum

from ncca.ngl import Vec2
from PySide6.QtCore import QElapsedTimer, QFile, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

GRAVITY = Vec2(0.0, 0.0)  # Gravity vector


class IntegrationMode(Enum):
    EULER = 0
    SEMI_IMPLICIT = 1
    RK4 = 2
    VERLET = 3


class Ball:
    """
    Represents a 2D ball with position, velocity, radius, and color.
    Used for simulating projectile motion under gravity.
    """

    def __init__(self, radius: float, mass: float, pos: Vec2, vel: Vec2) -> None:
        self.pos = pos.copy()
        self.velocity = vel.copy()
        self.radius = radius
        self.mass = mass
        self.colour = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self, dt: float, integration_mode: Enum) -> None:
        """
        Update the ball's velocity and position based on elapsed time.

        Args:
            dt (float): Time step in seconds.
            integration_mode (IntegrationMode): The integration method to use for updating the ball's position and velocity.
        """
        match integration_mode:
            case IntegrationMode.EULER:
                self.velocity += GRAVITY * dt
                self.pos += self.velocity * dt
            case IntegrationMode.SEMI_IMPLICIT:
                self.velocity += GRAVITY * dt
                self.pos += self.velocity * dt
            case IntegrationMode.RK4:
                # RK4 for constant acceleration
                v1 = self.velocity
                a1 = GRAVITY
                v2 = self.velocity + a1 * (dt / 2)
                a2 = GRAVITY
                v3 = self.velocity + a2 * (dt / 2)
                a3 = GRAVITY
                v4 = self.velocity + a3 * dt
                a4 = GRAVITY
                self.pos += (v1 + 2 * v2 + 2 * v3 + v4) * (dt / 6)
                self.velocity += (a1 + 2 * a2 + 2 * a3 + a4) * (dt / 6)
            case IntegrationMode.VERLET:
                new_pos = self.pos + self.velocity * dt + 0.5 * GRAVITY * (dt**2)
                self.velocity += GRAVITY * dt
                self.pos = new_pos


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
        # note these values are a good aspect ratio for the simulation
        # when drawing on a 1024x720 canvas
        self.sim_width = 20.0
        self.sim_height = 12.0
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.restitution = 1.0

        self.load_ui()
        self.c_scale = min(self.width(), self.height()) / self.sim_width
        self.setup_scene()

    def load_ui(self) -> None:
        """Load the UI from a .ui file and set up the connections."""
        loader = QUiLoader()
        ui_file = QFile("Part2UI.ui")
        ui_file.open(QFile.ReadOnly)
        # Load the UI into `self` as the parent
        loaded_ui = loader.load(ui_file, self)
        self.setCentralWidget(loaded_ui)
        # add all children with object names to `self`
        for child in loaded_ui.findChildren(QWidget):
            name = child.objectName()
            if name:
                setattr(self, name, child)
        ui_file.close()
        # add signals
        self.reset.clicked.connect(self.setup_scene)
        self.restitution_slider.valueChanged.connect(self.update_restitution)
        self.canvas = SimulationCanvas(self)
        layout = loaded_ui.layout()
        layout.addWidget(self.canvas)
        layout.setStretch(0, 0)
        layout.setStretch(1, 2)

    def update_restitution(self, value) -> None:
        """
        Update the restitution value based on the slider input and update the label.
        Args:
            value (int): The value from the restitution slider (0-100).
        """
        self.restitution = value / 100.0
        self.restitution_label.setText(f"Restitution: {self.restitution:.2f}")

    def setup_scene(self) -> None:
        """Set up the initial scene with a specified number of balls taken from the UI"""
        self.balls.clear()

        num_balls = self.num_balls.value()
        for _ in range(num_balls):
            radius = random.uniform(0.2, 1.0)
            mass = math.pi * radius**2
            pos = Vec2(
                random.uniform(radius, self.sim_width - radius),
                random.uniform(radius, self.sim_height - radius),
            )
            vel = Vec2(random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0))
            self.balls.append(Ball(radius, mass, pos, vel))

    def canvas_x(self, pos) -> float:
        """Convert a position in the simulation to canvas x-coordinate."""
        return pos.x * self.c_scale

    def canvas_y(self, pos) -> float:
        """Convert a position in the simulation to canvas y-coordinate."""
        return self.canvas.height() - pos.y * self.c_scale

    def update_scale(self) -> None:
        """Update the simulation scale based on the current canvas size."""
        # Use the canvas size, not the window size
        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()
        self.c_scale = min(canvas_width / self.sim_width, canvas_height / self.sim_height)

    def keyPressEvent(self, event) -> None:
        """Handle key press events for the simulation."""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_R:
            self.setup_scene()

    def timerEvent(self, event) -> None:
        """Handle the timer event to update the simulation."""
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.simulate(dt)

    def simulate(self, dt):
        """Simulate the motion of the balls in the simulation with per-substep collision handling."""
        mode = list(IntegrationMode)[self.integration_method.currentIndex()]
        num_steps = self.num_steps.value()
        sdt = dt / num_steps if num_steps > 0 else dt

        for step in range(num_steps):
            # Integrate each ball for this substep
            for ball in self.balls:
                ball.update(sdt, mode)

            # After integrating, handle collisions for this substep
            for i in range(len(self.balls)):
                for j in range(i + 1, len(self.balls)):
                    self.handle_ball_collisions(self.balls[i], self.balls[j])

            # Check bounds for each ball after collisions
            self.check_bounds()
        self.canvas.update()

    def check_bounds(self) -> None:
        """
        Check if the ball is out of bounds and adjust its position and velocity accordingly.
        """

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

    def handle_ball_collisions(self, ball1: Ball, ball2: Ball) -> None:
        """
        Handle collisions between two balls by adjusting their positions and velocities.
        Args:
            ball1 (Ball): The first ball involved in the collision.
            ball2 (Ball): The second ball involved in the collision.
        """
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
        """
        Draw the simulation on the canvas.
        Args:
            painter (QPainter): The painter to draw with.
        """
        painter.setRenderHint(QPainter.Antialiasing)
        for ball in self.balls:
            self.draw_circle(painter, ball)

    def draw_circle(self, painter, ball):
        """
        Draw a circle representing a ball on the canvas.
        Args:
            painter (QPainter): The painter to draw with.
            ball (Ball): The ball to draw.
        """
        painter.setPen(QPen(ball.colour))
        painter.setBrush(QBrush(ball.colour))
        x = self.canvas_x(ball.pos)
        y = self.canvas_y(ball.pos)
        radius = ball.radius * self.c_scale
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulation = Simulation()
    simulation.show()
    sys.exit(app.exec())
