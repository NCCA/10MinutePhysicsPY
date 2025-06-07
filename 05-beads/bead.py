#!/usr/bin/env -S uv run --script

import math
import sys

from nccapy.Math.Vec2 import Vec2
from PySide6.QtCore import QElapsedTimer, QFile, Qt, Slot
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

GRAVITY = Vec2(0.0, -9.87)  # Gravity vector


class Bead:
    def __init__(self, radius: float, mass: float, pos: Vec2) -> None:
        self.radius = radius
        self.mass = mass
        self.pos = pos.clone()
        self.previous_pos = pos.clone()
        self.velocity = Vec2(0, 0)

    def start_step(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        self.previous_pos = self.pos.clone()  # .set(self.pos.x, self.pos.y)
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


class AnalyticBead:
    def __init__(self, radius: float, bead_radius: float, mass: float, angle: float) -> None:
        self.radius = radius
        self.bead_radius = bead_radius
        self.mass = mass
        self.angle = angle
        self.omega = 0.0

    def simulate(self, dt: float, gravity_y: float) -> None:
        acc = -gravity_y / self.radius * math.sin(self.angle)
        self.omega += acc * dt
        self.angle += self.omega * dt
        centrifugal_force = self.omega * self.omega * self.radius
        force = centrifugal_force + math.cos(self.angle) * math.fabs(gravity_y)
        return force

    def get_pos(self) -> Vec2:
        return Vec2(math.sin(self.angle) * self.radius, -math.cos(self.angle) * self.radius)


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
        self.sim_min_width = 2.0
        self.wire_center = Vec2(0, 0)
        self.wire_radius = 0.0
        self.resize(1024, 720)
        self.load_ui()
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.last_time = self.elapsed_timer.elapsed()  # milliseconds
        self.startTimer(1.0 / 60.0)
        self.num_steps = 1000
        self.bead = None
        self.analytic_bead = None
        self.run_sim = False
        self.resize(1024, 720)
        self.reset_scene()

    def load_ui(self) -> None:
        """Load the UI from a .ui file and set up the connections."""
        loader = QUiLoader()
        ui_file = QFile("Bead.ui")
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
        # set colours
        self.pdb_label.setStyleSheet("color: #FF0000")
        self.analytic_label.setStyleSheet("color: #00FF00")

    @Slot(bool)
    def start_button_toggled(self, state: bool):
        self.run_sim ^= True
        if state:
            self.start_button.setText("Stop")
        else:
            self.start_button.setText("Start")

    def reset_scene(self):
        self.update_scale()
        self.wire_center.x = self.sim_width / 2.0
        self.wire_center.y = self.sim_height / 2.0
        self.wire_radius = self.sim_min_width * 0.4
        pos = Vec2(self.wire_center.x + self.wire_radius, self.wire_center.y)
        self.bead = Bead(0.1, 1.0, pos)
        self.analytic_bead = AnalyticBead(self.wire_radius, 0.1, 1.0, 0.5 * math.pi)

    def Simulation_x(self, pos):
        """Convert a position in the simulation to Simulation x-coordinate."""
        return pos.x * self.c_scale

    def Simulation_y(self, pos):
        """Convert a position in the simulation to Simulation y-coordinate."""
        return self.height() - pos.y * self.c_scale

    def update_scale(self):
        """Update the scale based on the current window size."""
        self.c_scale = min(self.canvas.width(), self.canvas.height()) / self.sim_min_width

        self.sim_width = self.canvas.width() / self.c_scale
        self.sim_height = self.height() / self.c_scale

    def resizeEvent(self, event):
        self.update_scale()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            ...

    def simulate(self, dt):
        sdt = dt / self.num_steps
        for _ in range(0, self.num_steps):
            self.bead.start_step(sdt)
            _lambda = self.bead.keep_on_wire(self.wire_center, self.wire_radius)
            force = math.fabs(_lambda / sdt / sdt)
            self.pdb_label.setText(f"PDB {force:02.3f}")
            self.bead.end_step(sdt)
            force = self.analytic_bead.simulate(sdt, -GRAVITY.y)
            self.analytic_label.setText(f"Analytic {force:02.3f}")

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
        pos = self.analytic_bead.get_pos()
        pos += self.wire_center

        self.draw_circle(painter, self.bead.pos, self.bead.radius, QColor(255, 0, 0), True)
        self.draw_circle(painter, pos, self.analytic_bead.bead_radius, QColor(0, 255, 0), True)

    def draw_circle(self, painter, position, radius, colour, filled=False):
        """Draw a circle representing the ball on the Simulation."""
        painter.setPen(QPen(colour))
        if filled:
            painter.setBrush(QBrush(colour))
        else:
            painter.setBrush(Qt.NoBrush)
        x = self.Simulation_x(position)
        y = self.Simulation_y(position)
        radius = radius * self.c_scale
        # Draw the circle
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulation = Simulation()
    simulation.show()
    sys.exit(app.exec())
