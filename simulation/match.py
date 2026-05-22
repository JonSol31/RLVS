import random

from simulation.robot import Robot
from simulation.physics import (
    enforce_drop,
    resolve_robot_collision,
    resolve_wall_collision,
    resolve_goal_collision,
    resolve_block_interaction,
    update_carried_blocks,
    resolve_scoring,
    score_blocks
)
from simulation.field import Field
from config.robots import DEFAULT_ROBOT


class Match:
    def __init__(self):
        self.field = Field()

        self.robots = [
            Robot(-48, -24, (255, 0, 0), DEFAULT_ROBOT),
            Robot(-48, 24, (255, 0, 0), DEFAULT_ROBOT),
            Robot(48, -24, (0, 0, 255), DEFAULT_ROBOT),
            Robot(48, 24, (0, 0, 255), DEFAULT_ROBOT),
        ]
        self.robots[0].team = "red"
        self.robots[1].team = "red"
        self.robots[2].team = "blue"
        self.robots[3].team = "blue"

        self.score = {
            "red": 0,
            "blue": 0
        }

    def update(self, dt):
        for robot in self.robots:
            throttle = random.uniform(-1, 1)
            turn = random.uniform(-1, 1)

            robot.update(throttle, turn, dt)

            resolve_wall_collision(robot)
            resolve_goal_collision(robot, self.field.get_goals())
            resolve_block_interaction(robot, self.field.blocks)

        update_carried_blocks(self.field.blocks)
        resolve_scoring(self.field.blocks, self.field.get_goals())

        for i in range(len(self.robots)):
            for j in range(i + 1, len(self.robots)):
                resolve_robot_collision(self.robots[i], self.robots[j])
        score_blocks(self.field, self.score)
        enforce_drop(robot, self.field)
        print(f"Red: {self.score['red']} | Blue: {self.score['blue']}")
