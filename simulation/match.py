import math
import random

from simulation.robot import Robot
from simulation.physics import (
    resolve_robot_collision,
    resolve_wall_collision,
    resolve_goal_collision,
    resolve_block_interaction,
    resolve_block_collisions,
    update_carried_blocks,
    resolve_scoring,
    clamp_block_in_goal_tube,
    score_held_blocks,
    score_blocks
)
from simulation.field import Field
from config.robots import DEFAULT_ROBOT


class Match:
    def __init__(self):
        self.initial_robot_configs = [
            (-48, -24, (255, 0, 0), "red"),
            (-48, 24, (255, 0, 0), "red"),
            (48, -24, (0, 0, 255), "blue"),
            (48, 24, (0, 0, 255), "blue"),
        ]

        self.reset()

    def _create_robots(self):
        robots = []
        for x, y, color, team in self.initial_robot_configs:
            robot = Robot(x, y, color, DEFAULT_ROBOT)
            robot.team = team
            robots.append(robot)
        return robots

    def reset(self):
        self.field = Field()
        self.robots = self._create_robots()
        self.score = {
            "red": 0,
            "blue": 0
        }
        self.score_events = {
            "red": 0,
            "blue": 0
        }

    def update(self, dt, controllers=None, time_remaining=None):
        self.time_remaining = time_remaining

        for index, robot in enumerate(self.robots):
            if controllers and index < len(controllers):
                throttle, turn = controllers[index].act(robot, self.field, self.robots, time_remaining=time_remaining)
            else:
                throttle = random.uniform(-1, 1)
                turn = random.uniform(-1, 1)

            robot.update(throttle, turn, dt)

            resolve_wall_collision(robot)
            resolve_goal_collision(robot, self.field.get_goals(), self.field.blocks, dt)
            resolve_block_interaction(robot, self.field.blocks)
            score_held_blocks(robot, self.field, dt)

        update_carried_blocks(self.field.blocks)
        resolve_block_collisions(self.field.blocks)
        resolve_scoring(self.field.blocks, self.field.get_goals())
        clamp_block_in_goal_tube(self.field.blocks, self.field.get_goals())

        for i in range(len(self.robots)):
            for j in range(i + 1, len(self.robots)):
                resolve_robot_collision(self.robots[i], self.robots[j])

        score_blocks(self.field, self.score, self.score_events)
        self.apply_match_rewards(dt)

    def run_episode(self, controllers=None, max_seconds=10.0, dt=0.1):
        self.reset()
        max_steps = int(max_seconds / dt)
        steps = 0
        elapsed = 0.0

        for step in range(max_steps):
            elapsed += dt
            time_remaining = max_seconds - elapsed
            self.update(dt, controllers, time_remaining=time_remaining)
            steps = step + 1

        return {
            "score": dict(self.score),
            "score_events": dict(self.score_events),
            "rewards": [robot.reward for robot in self.robots],
            "steps": steps,
        }

    def _block_in_goal(self, block, goal):
        if block.held:
            return False

        dx = block.x - goal.x
        dy = block.y - goal.y
        rad = math.radians(-goal.angle)
        local_x = dx * math.cos(rad) - dy * math.sin(rad)
        local_y = dx * math.sin(rad) + dy * math.cos(rad)

        return abs(local_y) <= goal.height / 2 and abs(local_x) <= goal.width / 2

    def _is_in_push(self, robot):
        for other in self.robots:
            if other is robot or other.team == robot.team:
                continue
            dx = robot.x - other.x
            dy = robot.y - other.y
            if math.hypot(dx, dy) < robot.SIZE:
                return True
        return False

    def _compute_goal_control(self):
        control = {}
        for goal in self.field.get_goals():
            counts = {"red": 0, "blue": 0}
            for block in self.field.blocks:
                if self._block_in_goal(block, goal) and block.team in counts:
                    counts[block.team] += 1
            control[goal.type] = counts
        return control

    def apply_match_rewards(self, dt):
        if self.score_events["red"] > self.score_events["blue"]:
            leading = "red"
            trailing = "blue"
        elif self.score_events["blue"] > self.score_events["red"]:
            leading = "blue"
            trailing = "red"
        else:
            leading = trailing = None

        goal_control = self._compute_goal_control()
        center_goals = ["center_upper", "center_lower"]
        long_goals = ["long_top", "long_bottom"]

        for robot in self.robots:
            if robot.holding > 2:
                robot.reward += 1.0 * dt

            if leading and robot.team == leading:
                robot.reward += 2.0 * dt
            elif trailing and robot.team == trailing:
                robot.reward -= 1.0 * dt

            # majority control bonus for center and long goals
            center_majority = 0
            for goal_type in center_goals:
                counts = goal_control.get(goal_type, {})
                if counts.get(robot.team, 0) > counts.get("red" if robot.team == "blue" else "blue", 0):
                    center_majority += 1
            long_majority = 0
            for goal_type in long_goals:
                counts = goal_control.get(goal_type, {})
                if counts.get(robot.team, 0) > counts.get("red" if robot.team == "blue" else "blue", 0):
                    long_majority += 1

            robot.reward += 3.0 * center_majority * dt
            robot.reward += 1.5 * long_majority * dt

            # endgame execution reward
            if hasattr(self, "time_remaining") and self.time_remaining is not None and self.time_remaining <= 15.0:
                if robot.is_scoring:
                    robot.reward += 5.0 * dt
                elif robot.holding > 0:
                    robot.reward += 1.0 * dt

            # anti-push penalty for stalled contact situations
            speed = math.hypot(robot.vx, robot.vy)
            if speed < 2.0 and self._is_in_push(robot) and not robot.is_scoring:
                robot.reward -= 5.0 * dt
