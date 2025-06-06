# Ball Collisions

This demo is based on this [video](https://www.youtube.com/watch?v=ThhdlMbGT5g&ab_channel=TenMinutePhysics) by Ten Minute Physics.

I have updated the code from the previous demos to allow the use of UI components. This means some of the canvas code has now been moved to it's own class. For simplicity everything is still in the same file.

[billiardPt1.py](billiardPt1.py) This demo shows the basic collision detection and response for multiple balls, it also allows the setting of the restitution coefficient so the balls will eventually come to rest if the coefficient is less than 1.0. It still uses the basic Euler integration method.

[billboardPy2.py](billiardPt2.py) This demo integrates a PySide ui file to make the loading and setup of the user interface easier. We now have the ability via the UI to add the number of balls, set the various simulation parameters and start/stop the simulation.

There is now a choice of integration methods and you can set the number of sub steps, however at present all of the updates are done before the collision detection and response. This means that the simulation is not fully accurate, but it is much faster, this is quite typical in real time simulations and games etc.


[billiardPt3.py](billiardPt3.py) This demo adds a more accurate collision detection and response system by checking the collisions after each sub step. This is a more accurate method, but it is also slower.

[billiardQML.py](billiardQML.py) This demo uses QML to create the user interface. This was an experiment to see how easy it would be to use QML with the existing code. It took a while but works quite well. The design of the system is a little different to the previous demos, but it is still based on the same principles. The QML interface has several re-usable components, to make the UI design easier. There is also a greater reliance on Slots as the QML properties are not directly accessible from Python. 

There is also the ability to use the mouse to drag the balls around, this is done by using a QML MouseArea and sending the position of the mouse to the Python code. The Python code then updates the position of the ball based on the mouse position.

