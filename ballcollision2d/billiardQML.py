#!/usr/bin/env -S uv run --script
import math
import random
import sys
from enum import Enum

from nccapy import Vec2
from PySide6.QtCore import QElapsedTimer, QObject, QTimer, QUrl, Slot
from PySide6.QtGui import QColor
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

GRAVITY = Vec2(0, 0)


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
        self.pos = pos.clone()
        self.velocity = vel.clone()
        self.radius = radius
        self.mass = mass
        self.colour = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self, dt: float, integration_mode: Enum, num_steps: int) -> None:
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
                sdt = dt / num_steps  # Divide the time step into smaller steps for better accuracy
                for _ in range(num_steps):
                    self.velocity += GRAVITY * sdt
                    self.pos += self.velocity * sdt
            case IntegrationMode.RK4:
                sdt = dt / num_steps  # Divide the time step into smaller steps for better accuracy
                # note this is a simple RK4 as gravity is constant
                for _ in range(num_steps):
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
                sdt = dt / num_steps
                for _ in range(num_steps):
                    # Calculate the new position based on the current position and velocity
                    new_pos = self.pos + self.velocity * sdt + 0.5 * GRAVITY * (sdt**2)
                    # Update velocity based on the average of the current and new positions
                    self.velocity += GRAVITY * sdt
                    # Update position to the new position
                    self.pos = new_pos


class Backend(QObject):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.num_circles = 5
        self.positions = []
        self.balls = []
        self.sim_width = 20.0
        self.sim_height = 12.0
        self.num_balls = 20
        self.canvas_width = 1024
        self.canvas_height = 720
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.restitution = 1.0
        self.c_scale = min(self.canvas_width, self.canvas_height) / self.sim_width
        self.setup_scene()
        self.num_steps = 1  # Number of substeps for collision handling
        self.integration_method = 0  # Default integration method

    def setup_scene(self) -> None:
        """Set up the initial scene with a specified number of balls taken from the UI"""
        self.balls.clear()

        for _ in range(self.num_balls):
            radius = random.uniform(0.2, 1.0)
            mass = math.pi * radius**2
            pos = Vec2(
                random.uniform(radius, self.sim_width - radius), random.uniform(radius, self.sim_height - radius)
            )
            vel = Vec2(random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0))
            self.balls.append(Ball(radius, mass, pos, vel))

    @Slot()
    def onButtonClicked(self):
        print("Button clicked!")

    @Slot()
    def reset_simulation(self):
        print("Reset clicked!")
        self.setup_scene()

    @Slot(int, int)
    def set_canvas_size(self, w, h):
        print(f"Canvas size: {w} x {h}")
        self.canvas_width = w
        self.canvas_height = h
        self.update_scale()

    @Slot(int)
    def on_num_balls_changed(self, count):
        print(f"Circle count: {int(count)}")
        self.num_balls = count

    @Slot(int)
    def on_integration_method_changed(self, index):
        print(f"Integration method changed to: {IntegrationMode(index).name}")
        self.integration_method = index

    @Slot(int)
    def on_integration_steps_changed(self, int):
        print(f"Integration steps changed to: {int}")
        self.num_steps = int

    @Slot(float)
    def on_restitution_changed(self, value):
        print(f"Restitution: {value}")
        self.restitution = value

    def push_to_qml(self):
        # Only the data needed for drawing
        values = []
        for ball in self.balls:
            x = self.canvas_x(ball.pos)
            y = self.canvas_y(ball.pos)
            radius = ball.radius * self.c_scale
            values.append({"x": x, "y": y, "r": radius, "color": ball.colour.name()})

        self.root.setProperty("balls", values)

    def animate(self):
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.simulate(dt)

        self.push_to_qml()

    def simulate(self, dt):
        for i in range(len(self.balls)):
            ball1 = self.balls[i]

            # Update the ball's position and velocity based on the integration methodmo
            mode = list(IntegrationMode)

            ball1.update(dt, mode[self.integration_method], self.num_steps)

            for j in range(i + 1, len(self.balls)):
                ball2 = self.balls[j]
                self.handle_ball_collisions(ball1, ball2)
        self.check_bounds()

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

    def canvas_x(self, pos) -> float:
        """Convert a position in the simulation to canvas x-coordinate."""
        return pos.x * self.c_scale

    def canvas_y(self, pos) -> float:
        """Convert a position in the simulation to canvas y-coordinate."""
        return self.canvas_height - pos.y * self.c_scale

    def update_scale(self) -> None:
        """Update the simulation scale based on the current canvas size."""
        # Use the canvas size, not the window size
        self.c_scale = min(self.canvas_width / self.sim_width, self.canvas_height / self.sim_height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = Backend(None)
    engine.rootContext().setContextProperty("backend", backend)

    engine.load(QUrl("main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    backend.root = root

    # Animation loop
    timer = QTimer()
    timer.timeout.connect(backend.animate)
    timer.start(16)  # Approximately 60 FPS

    sys.exit(app.exec())
