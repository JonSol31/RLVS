import random

from simulation.robot import Robot
from simulation.physics import (
    resolve_robot_collision,
    resolve_wall_collision,
)
from config.robots import DEFAULT_ROBOT


class Match:
    def __init__(self):
        self.robots = [
            Robot(30, 30, (255, 0, 0), DEFAULT_ROBOT),
            Robot(30, 110, (255, 0, 0), DEFAULT_ROBOT),
            Robot(110, 30, (0, 0, 255), DEFAULT_ROBOT),
            Robot(110, 110, (0, 0, 255), DEFAULT_ROBOT),
        ]

    def update(self, dt):
        for robot in self.robots:
            throttle = random.uniform(-1, 1)
            turn = random.uniform(-1, 1)

            robot.update(throttle, turn, dt)

            resolve_wall_collision(robot)

        # robot collisions
        for i in range(len(self.robots)):
            for j in range(i + 1, len(self.robots)):
                resolve_robot_collision(
                    self.robots[i],
                    self.robots[j]
                )