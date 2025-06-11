# 10 Minute Physics in Python

This repository is my version of the [10 Minute Physics](https://matthias-research.github.io/pages/tenMinutePhysics/index.html) demos written in Python. The 2D demos use PySide6 for the Canvas, the 3D demos will use PySide6 and WebGPU. Not all the pages on the original site have code so I will only do the ones with a demo.

Each folder has a link to a README.md file with the original demo link as well as descriptions of my versions of it, as well as extras with different versions and methods applied to the demos.

I use uv to package and run the demos, you can install uv by following the instructions [here](https://docs.astral.sh/uv/getting-started/installation/)

Once in the root of the repository, you can run
```bash
uv sync
```

This is using a workspace project structure, so you can run this command from the root of the repository to install all the dependencies for all the demos.

To install the pre-requisites. Each of the individual demos can be run using ./<demo_name> command, for example:

```bash
./cannonball2d.py
```

1. [Cannonball 2D](01-cannonball2d/)
2. [Cannonball 3D](02-cannonball3d/)
3. [Ball collision handling in 2d](03-ballcollision2d/)
4. [Pinball](04-pinball/)
5. [Beads](05-beads/)
6. [Pendulums](06-pendulum)
