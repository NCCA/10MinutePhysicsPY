#!/usr/bin/env -S uv run --script

import math
import random
import sys

from ncca.ngl import Vec2
from PySide6.QtCore import QElapsedTimer, QFile, Qt, Slot
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

GRAVITY = Vec2(0.0, -9.87)  # Gravity vector


class Bead:
    def __init__(self, radius: float, mass: float, pos: Vec2) -> None:
        self.radius = radius
        self.mass = mass
        self.pos = pos.copy()
        self.previous_pos = pos.copy()
        self.velocity = Vec2(0, 0)
        self.colour = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def start_step(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        self.previous_pos = self.pos.copy()  # .set(self.pos.x, self.pos.y)
        self.pos += self.velocity * dt

    def keep_on_wire(self, center: Vec2, radius: float) -> float:
        dir = self.pos - center
        len = dir.length()
        if len == 0.0:
            return 0.0
        dir.normalize()

        _lambda = radius - len
        self.pos += dir * _lambda
        return _lambda

    def end_step(self, dt):
        self.velocity = (self.pos - self.previous_pos) * (1.0 / dt)


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
        self.setWindowTitle("Bead from 10 Minute Physics")
        self.sim_min_width = 2.5
        self.wire_center = Vec2(0, 0)
        self.wire_radius = 0.0
        self.load_ui()
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.run_sim = False
        self.beads = []
        self.reset_scene()
        self.resize(1024, 720)

    def load_ui(self) -> None:
        """Load the UI from a .ui file and set up the connections."""
        loader = QUiLoader()
        ui_file = QFile("ManyBead.ui")
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
        self.canvas = SimulationCanvas(self)
        layout = loaded_ui.layout()
        layout.addWidget(self.canvas)
        layout.setStretch(0, 0)
        layout.setStretch(1, 2)
        # connect slots
        self.start_button.toggled.connect(self.start_button_toggled)
        self.step_button.clicked.connect(lambda: self.simulate(1.0 / 60.0))
        self.reset_button.clicked.connect(self.reset_scene)
        self.num_beads.valueChanged.connect(self.reset_scene)
        self.fixed_radius.toggled.connect(self.reset_scene)
        self.radius.valueChanged.connect(self.reset_scene)

    @Slot(bool)
    def start_button_toggled(self, state: bool):
        self.run_sim ^= True
        if state:
            self.start_button.setText("Stop")
        else:
            self.start_button.setText("Start")

    def reset_scene(self):
        self.beads.clear()
        self.update_scale()
        self.wire_center.x = self.sim_width / 2.0
        self.wire_center.y = self.sim_height / 2.0
        self.wire_radius = self.sim_min_width * 0.4
        angle = 0.0
        for _ in range(0, self.num_beads.value()):
            if self.fixed_radius.isChecked():
                r = self.radius.value()
            else:
                r = random.uniform(0.01, 0.25)
            mass = math.pi * r * r
            pos = Vec2(
                self.wire_center.x + self.wire_radius * math.cos(angle),
                self.wire_center.y + self.wire_radius * math.sin(angle),
            )

            self.beads.append(Bead(r, mass, pos))
            angle += math.pi / self.num_beads.value()

    def canvas_x(self, pos):
        """Convert a position in the simulation to Simulation x-coordinate."""
        return pos.x * self.c_scale

    def canvas_y(self, pos):
        """Convert a position in the simulation to Simulation y-coordinate."""
        return self.canvas.height() - pos.y * self.c_scale

    def update_scale(self):
        """Update the scale based on the current window size."""
        self.c_scale = min(self.canvas.width(), self.canvas.height()) / self.sim_min_width

        self.sim_width = self.canvas.width() / self.c_scale
        self.sim_height = self.height() / self.c_scale

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            ...

    def simulate(self, dt):
        num_steps = self.sim_steps.value()
        sdt = dt / num_steps
        for _ in range(0, num_steps):
            for bead in self.beads:
                bead.start_step(sdt)
            for bead in self.beads:
                bead.keep_on_wire(self.wire_center, self.wire_radius)
            for bead in self.beads:
                bead.end_step(sdt)
        for i in range(0, self.num_beads.value()):
            for j in range(0, i):
                self.bead_bead_collision(self.beads[i], self.beads[j])

    def bead_bead_collision(self, ball1, ball2):
        dir = ball2.pos - ball1.pos  # Vec2 subtraction
        restitution = self.restitution.value() / 100.0
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

    def timerEvent(self, event):
        """measure the time elapsed between updates (in seconds), which is essential for time based
        calculations in simulations, animations, or games. It ensures that the simulation progresses
        at a rate consistent with real time, regardless of
        how fast or slow the update loop is running."""
        current_time = self.elapsed_timer.elapsed()  # milliseconds
        dt = (current_time - self.last_time) / 1000.0  # convert ms to seconds
        if self.run_sim:
            self.simulate(dt)
        self.last_time = current_time
        # call redraw of the Simulation
        self.canvas.update()

    def draw_simulation(self, painter):
        """This is where the drawing is done"""
        # self.draw_circle(painter, self.ball)
        self.draw_circle(painter, self.wire_center, self.wire_radius, QColor(0, 0, 0))
        # draw beads

        for bead in self.beads:
            self.draw_circle(painter, bead.pos, bead.radius, bead.colour, True)

    def draw_circle(self, painter, position, radius, colour, filled=False):
        """Draw a circle representing the ball on the Simulation."""
        painter.setPen(QPen(colour))
        if filled:
            painter.setBrush(QBrush(colour))
        else:
            painter.setBrush(Qt.NoBrush)
        x = self.canvas_x(position)
        y = self.canvas_y(position)
        radius = radius * self.c_scale
        # Draw the circle
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulation = Simulation()
    simulation.show()
    sys.exit(app.exec())
