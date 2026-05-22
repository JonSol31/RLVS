import math

from simulation.block import Block
import random


class Goal:
    def __init__(self, x, y, width, height, angle_deg, goal_type):
        self.x = x
        self.y = y

        self.width = width
        self.height = height
        self.angle = angle_deg
        self.type = goal_type

        # scoring value
        if "long" in goal_type:
            self.value = 1
        else:
            self.value = 1

class Field:
    SIZE = 144  # inches
    HALF = SIZE / 2  # 72

    def __init__(self):
        self.goals = self._build_goals()
        self.blocks = self._spawn_blocks()

    def _build_goals(self):
        goals = []

        # --------------------------
        # LONG GOALS (horizontal)
        # --------------------------

        goals.append(
            Goal(
                x=0,
                y=48,
                width=54,   # -24 to 24
                height=5,   # goal opening thickness
                angle_deg=0,
                goal_type="long_top"
            )
        )

        goals.append(
            Goal(
                x=0,
                y=-48,
                width=54,
                height=5,
                angle_deg=0,
                goal_type="long_bottom"
            )
        )

        # --------------------------
        # CENTER GOALS (rotated)
        # --------------------------

        goals.append(
            Goal(
                x=0,
                y=0,
                width=40,
                height=5,
                angle_deg=-45,
                goal_type="center_upper"
            )
        )

        goals.append(
            Goal(
                x=0,
                y=0,
                width=40,
                height=5,
                angle_deg=45,
                goal_type="center_lower"
            )
        )

        return goals

    def get_goals(self):
        return self.goals


    def _spawn_blocks(self):
        blocks = []

        def add(x, y, color, team):
            blocks.append(Block(x, y, color, team))

        # neutral center blocks

        # red team blocks
        for i in range(22):
            add(-30 + i * 6, 20, (255, 80, 80), "red")

        # blue team blocks
        for i in range(22):
            add(-30 + i * 6, -20, (80, 120, 255), "blue")

        return blocks