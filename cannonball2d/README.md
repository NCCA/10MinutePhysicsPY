# Cannonball 2D

This demo is based on the video here https://www.youtube.com/watch?v=oPuSvdBGrpE&ab_channel=TenMinutePhysics The original [web demo](https://matthias-research.github.io/pages/tenMinutePhysics/01-cannonball2d.html) is written in JavaScript and HTML. I have several version of this demo

1. [cannonball2d.py])(cannonball2dPt1.py) - a simple version that uses PySide6 to create a canvas and draw the cannonball the simulation is very close to the original demo. You will notice after a while the simulation will fail and the ball will just move alone the ground. This demonstrates inherent numerical instability in the simulation.

2. [cannonball2dPt2.py](cannonball2dPt2.py) - this version uses Euler integration with sub-stepping (sometimes called "[semi-implicit Euler](https://gafferongames.com/post/integration_basics/) method) to simulate the cannonball. The green ball show the path of the previous simulation, the green ball shows the path of new method (using step updates). After a while you will notice the red ball will start to diverge from the green ball.

3. [cannonball2dRK4.py](cannonball2dRK4.py) - this version uses the Runge-Kutta 4th order method to simulate the cannonball. The green ball shows the path of the previous simulation, the red ball shows the path of new method (using RK4). After a while you will notice the red ball will start to diverge from the green ball.


3. [cannonball2dPt3.py](cannonball2dPt3.py) - this version allows you to change the integration methods used to simulate as well as allowing the mouse to add more balls.

It also add Verlet integration method, which is a symplectic integrator that is used in many physics engines.
