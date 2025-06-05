#!/usr/bin/env -S uv run --script
import math
import random
import sys
from enum import Enum
from typing import List, Optional

from nccapy import Vec2
from PySide6.QtCore import QElapsedTimer, QObject, QTimer, QUrl, Slot
from PySide6.QtGui import QColor
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

GRAVITY = Vec2(0, 0)


class IntegrationMode(Enum):
    """Enumeration of available integration methods for ball motion."""

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
        """
        Initialize a Ball instance.

        Args:
            radius (float): The radius of the ball.
            mass (float): The mass of the ball.
            pos (Vec2): The initial position of the ball.
            vel (Vec2): The initial velocity of the ball.
        """
        self.pos: Vec2 = pos.clone()
        self.velocity: Vec2 = vel.clone()
        self.radius: float = radius
        self.mass: float = mass
        self.colour: QColor = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self, dt: float, integration_mode: Enum, num_steps: int) -> None:
        """
        Update the ball's velocity and position based on elapsed time.

        Args:
            dt (float): Time step in seconds.
            integration_mode (IntegrationMode): The integration method to use for updating the ball's position and velocity.
            num_steps (int): Number of substeps for integration.
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
    """
    Backend class for managing the simulation state and communication with QML.
    """

    def __init__(self, root: Optional[QObject]) -> None:
        """
        Initialize the Backend.

        Args:
            root (QObject or None): The root QML object, or None at startup.
        """
        super().__init__()
        self.root: Optional[QObject] = root
        self.num_circles: int = 5
        self.positions: List[Vec2] = []
        self.balls: List[Ball] = []
        self.sim_width: float = 20.0
        self.sim_height: float = 12.0
        self.num_balls: int = 20
        self.canvas_width: int = 1024
        self.canvas_height: int = 720
        self.elapsed_timer: QElapsedTimer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time: int = self.elapsed_timer.elapsed()  # milliseconds
        self.restitution: float = 1.0
        self.c_scale: float = min(self.canvas_width, self.canvas_height) / self.sim_width
        self.min_radius: float = 0.1
        self.max_radius: float = 1.0
        self.min_velocity: float = -5.0
        self.max_velocity: float = 5.0
        self.setup_scene()
        self.num_steps: int = 1  # Number of substeps for collision handling
        self.integration_method: int = 0  # Default integration method
        self.mouse_ball: Ball = Ball(1.0, math.pi * 2**2, Vec2(0, 0), Vec2(0, 0))

    def _create_ball(self) -> Ball:
        """
        Create a new ball with random properties.

        Returns:
            Ball: The created Ball instance.
        """
        radius = random.uniform(self.min_radius, self.max_radius)
        mass = math.pi * radius**2
        pos = Vec2(random.uniform(radius, self.sim_width - radius), random.uniform(radius, self.sim_height - radius))
        vel = Vec2(
            random.uniform(self.min_velocity, self.max_velocity), random.uniform(self.min_velocity, self.max_velocity)
        )
        return Ball(radius, mass, pos, vel)

    @Slot()
    def setup_scene(self) -> None:
        """
        Set up the initial scene with a specified number of balls taken from the UI.
        """
        self.balls.clear()
        for _ in range(self.num_balls):
            self.balls.append(self._create_ball())

    @Slot(int, int)
    def set_canvas_size(self, w: int, h: int) -> None:
        """
        Set the canvas size and update the simulation scale.

        Args:
            w (int): Canvas width in pixels.
            h (int): Canvas height in pixels.
        """
        print(f"Canvas size: {w} x {h}")
        self.canvas_width = w
        self.canvas_height = h
        self.update_scale()

    @Slot(float, float)
    def veleocity_changed(self, min: float, max: float) -> None:
        """
        Update the minimum and maximum velocity for new balls.

        Args:
            min (float): Minimum velocity.
            max (float): Maximum velocity.
        """
        self.min_velocity = min
        self.max_velocity = max

    @Slot(int, int)
    def on_canvas_mouse_moved(self, x: int, y: int) -> None:
        """
        Handle canvas mouse move events to update the mouse_ball's position and velocity.

        Args:
            x (int): X coordinate in canvas pixels.
            y (int): Y coordinate in canvas pixels.
        """
        print(f"Canvas clicked at: {x}, {y}")
        # Convert canvas coordinates to simulation coordinates
        last_pos = self.mouse_ball.pos
        new_pos = Vec2(x / self.c_scale, (self.canvas_height - y) / self.c_scale)

        sim_x = x / self.c_scale
        sim_y = (self.canvas_height - y) / self.c_scale
        self.mouse_ball.pos = Vec2(sim_x, sim_y)
        # Calculate a new velocity based on the position
        self.mouse_ball.velocity = (last_pos - new_pos) * 10  # Scale the velocity for better interaction
        print(self.mouse_ball.velocity)

    @Slot(int)
    def on_num_balls_changed(self, count: int) -> None:
        """
        Update the number of balls in the simulation.

        Args:
            count (int): The new number of balls.
        """
        self.num_balls = count
        ball_count = len(self.balls)
        if ball_count < self.num_balls:
            for _ in range(self.num_balls - ball_count):
                self.balls.append(self._create_ball())
        elif ball_count > self.num_balls:
            self.balls = self.balls[: self.num_balls]

    @Slot(int)
    def on_integration_method_changed(self, index: int) -> None:
        """
        Update the integration method.

        Args:
            index (int): Index of the integration method (see IntegrationMode).
        """
        print(f"Integration method changed to: {IntegrationMode(index).name}")
        self.integration_method = index

    @Slot(int)
    def on_integration_steps_changed(self, steps: int) -> None:
        """
        Update the number of integration steps.

        Args:
            steps (int): Number of integration steps.
        """
        print(f"Integration steps changed to: {steps}")
        self.num_steps = steps

    @Slot(float)
    def on_restitution_changed(self, value: float) -> None:
        """
        Update the restitution coefficient for collisions.

        Args:
            value (float): Restitution coefficient.
        """
        print(f"Restitution: {value}")
        self.restitution = value

    @Slot(float, float)
    def on_radius_range_changed(self, min: float, max: float) -> None:
        """
        Update the minimum and maximum radius for new balls.

        Args:
            min (float): Minimum radius.
            max (float): Maximum radius.
        """
        self.min_radius = min
        self.max_radius = max
        print(f"Radius range changed to: {self.min_radius} - {self.max_radius}")

    def push_to_qml(self) -> None:
        """
        Push the current state of all balls to the QML frontend for rendering.
        """
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

    def animate(self) -> None:
        """
        Advance the simulation by one frame and update the QML frontend.
        """
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        self.last_time = current_time
        self.simulate(dt)
        self.push_to_qml()

    def simulate(self, dt: float) -> None:
        """
        Simulate the motion and collisions of all balls for a given time step.

        Args:
            dt (float): Time step in seconds.
        """
        for i in range(len(self.balls)):
            ball1 = self.balls[i]
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
        Check if the balls are out of bounds and adjust their positions and velocities accordingly.
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

    def canvas_x(self, pos: Vec2) -> float:
        """
        Convert a position in the simulation to canvas x-coordinate.

        Args:
            pos (Vec2): The simulation position.

        Returns:
            float: The x-coordinate on the canvas.
        """
        return pos.x * self.c_scale

    def canvas_y(self, pos: Vec2) -> float:
        """
        Convert a position in the simulation to canvas y-coordinate.

        Args:
            pos (Vec2): The simulation position.

        Returns:
            float: The y-coordinate on the canvas.
        """
        return self.canvas_height - pos.y * self.c_scale

    def update_scale(self) -> None:
        """
        Update the simulation scale based on the current canvas size.
        """
        self.c_scale = min(self.canvas_width / self.sim_width, self.canvas_height / self.sim_height)


if __name__ == "__main__":
    """
    Main entry point for the simulation application.
    Sets up the QApplication, QML engine, backend, and animation loop.
    """
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
