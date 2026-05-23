import math

from simulation.block import Block
import random


class Goal:
    def __init__(self, x, y, width, height, angle_deg, goal_type, capacity=15):
        self.x = x
        self.y = y

        self.width = width
        self.height = height
        self.angle = angle_deg
        self.type = goal_type
        self.capacity = capacity

        # scoring value
        if "long" in goal_type:
            self.value = 1
        else:
            self.value = 1

    def current_load(self, blocks):
        return sum(
            1
            for block in blocks
            if block.in_goal and self.contains_point(block.x, block.y)
        )

    def _axes(self):
        rad = math.radians(self.angle)
        x_axis = (math.cos(rad), math.sin(rad))
        y_axis = (-math.sin(rad), math.cos(rad))
        return x_axis, y_axis

    def world_to_local(self, px, py):
        dx = px - self.x
        dy = py - self.y
        x_axis, y_axis = self._axes()
        local_x = dx * x_axis[0] + dy * x_axis[1]
        local_y = dx * y_axis[0] + dy * y_axis[1]
        return local_x, local_y

    def local_to_world(self, lx, ly):
        x_axis, y_axis = self._axes()
        return (
            self.x + lx * x_axis[0] + ly * y_axis[0],
            self.y + lx * x_axis[1] + ly * y_axis[1],
        )

    def contains_point(self, px, py, padding=0.0):
        local_x, local_y = self.world_to_local(px, py)
        return (
            abs(local_x) <= self.width / 2 + padding
            and abs(local_y) <= self.height / 2 + padding
        )

    def opening_endpoints(self):
        return (
            self.local_to_world(-self.width / 2, 0),
            self.local_to_world(self.width / 2, 0),
        )

    def closest_point_on_opening(self, px, py):
        local_x, _ = self.world_to_local(px, py)
        local_x = max(-self.width / 2, min(self.width / 2, local_x))
        return self.local_to_world(local_x, 0)

    def direction_into_goal(self, px, py):
        _, local_y = self.world_to_local(px, py)
        _, y_axis = self._axes()
        sign = -1.0 if local_y > 0 else 1.0
        return y_axis[0] * sign, y_axis[1] * sign

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
                goal_type="long_top",
                capacity=15,
            )
        )

        goals.append(
            Goal(
                x=0,
                y=-48,
                width=54,
                height=5,
                angle_deg=0,
                goal_type="long_bottom",
                capacity=15,
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
                goal_type="center_upper",
                capacity=15,
            )
        )

        goals.append(
            Goal(
                x=0,
                y=0,
                width=40,
                height=5,
                angle_deg=45,
                goal_type="center_lower",
                capacity=15,
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