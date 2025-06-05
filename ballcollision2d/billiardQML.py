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
        self.min_radius = 0.1
        self.max_radius = 1.0
        self.min_velocity = -5.0
        self.max_velocity = 5.0
        self.setup_scene()
        self.num_steps = 1  # Number of substeps for collision handling
        self.integration_method = 0  # Default integration method
        self.mouse_ball = Ball(1.0, math.pi * 2**2, Vec2(0, 0), Vec2(0, 0))

    def _create_ball(self) -> Ball:
        """Create a new ball with random properties."""
        radius = random.uniform(self.min_radius, self.max_radius)
        mass = math.pi * radius**2
        pos = Vec2(random.uniform(radius, self.sim_width - radius), random.uniform(radius, self.sim_height - radius))
        vel = Vec2(
            random.uniform(self.min_velocity, self.max_velocity), random.uniform(self.min_velocity, self.max_velocity)
        )
        return Ball(radius, mass, pos, vel)

    @Slot()
    def setup_scene(self) -> None:
        """Set up the initial scene with a specified number of balls taken from the UI"""
        self.balls.clear()

        for _ in range(self.num_balls):
            self.balls.append(self._create_ball())

    @Slot(int, int)
    def set_canvas_size(self, w, h):
        print(f"Canvas size: {w} x {h}")
        self.canvas_width = w
        self.canvas_height = h
        self.update_scale()

    @Slot(float, float)
    def veleocity_changed(self, min, max):
        self.min_velocity = min
        self.max_velocity = max

    @Slot(int, int)
    def on_canvas_mouse_moved(self, x, y):
        """Handle canvas click events to create a new ball at the clicked position."""
        print(f"Canvas clicked at: {x}, {y}")
        # Convert canvas coordinates to simulation coordinates
        # also calculate a new velocity based on the position
        last_pos = self.mouse_ball.pos
        new_pos = Vec2(x / self.c_scale, (self.canvas_height - y) / self.c_scale)

        sim_x = x / self.c_scale
        sim_y = (self.canvas_height - y) / self.c_scale
        self.mouse_ball.pos = Vec2(sim_x, sim_y)
        # Calculate a new velocity based on the position
        self.mouse_ball.velocity = (last_pos - new_pos) * 10  # Scale the velocity for better interaction
        print(self.mouse_ball.velocity)

    @Slot(int)
    def on_num_balls_changed(self, count):
        self.num_balls = count
        ball_count = len(self.balls)
        if ball_count < self.num_balls:
            for _ in range(self.num_balls - ball_count):
                self.balls.append(self._create_ball())
        elif ball_count > self.num_balls:
            self.balls = self.balls[: self.num_balls]

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

    @Slot(float, float)
    def on_radius_range_changed(self, min, max):
        self.min_radius = min
        self.max_radius = max
        print(f"Radius range changed to: {self.min_radius} - {self.max_radius}")

    def push_to_qml(self):
        # Only the data needed for drawing
        values = []
        for ball in self.balls:
            x = self.canvas_x(ball.pos)
            y = self.canvas_y(ball.pos)
            radius = ball.radius * self.c_scale
            values.append({"x": x, "y": y, "r": radius, "color": ball.colour.name()})
        if self.mouse_ball:
            x = self.canvas_x(self.mouse_ball.pos)
            y = self.canvas_y(self.mouse_ball.pos)
            radius = self.mouse_ball.radius * self.c_scale
            values.append({"x": x, "y": y, "r": radius, "color": self.mouse_ball.colour.name()})
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
        if self.mouse_ball:
            # Check for collisions with other balls
            self.mouse_ball.update(dt, mode[self.integration_method], self.num_steps)
            for ball in self.balls:
                self.handle_ball_collisions(self.mouse_ball, ball)

    def check_bounds(self) -> None:
        """
        Check if the ball is out of bounds and adjust its position and velocity accordingly.
        """

        def check_ball(ball: Ball) -> None:
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

        for ball in self.balls:
            check_ball(ball)
        if self.mouse_ball:
            check_ball(self.mouse_ball)

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

    engine.load(QUrl("UI.qml"))
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    backend.root = root

    # Animation loop
    timer = QTimer()
    timer.timeout.connect(backend.animate)
    timer.start(16)  # Approximately 60 FPS

    sys.exit(app.exec())
