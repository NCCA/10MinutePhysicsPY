# Ball Collisions

This demo is based on this [video](https://www.youtube.com/watch?v=ThhdlMbGT5g&ab_channel=TenMinutePhysics) by Ten Minute Physics.

I have updated the code from the previous demos to allow the use of UI components. This means some of the canvas code has now been moved to it's own class. For simplicity everything is still in the same file.

[billiardPt1.py](billiardPt1.py) This demo shows the basic collision detection and response for multiple balls, it also allows the setting of the restitution coefficient so the balls will eventually come to rest if the coefficient is less than 1.0. It still uses the basic Euler integration method. 

