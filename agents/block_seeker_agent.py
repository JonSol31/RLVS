import math
import random


class BlockSeekerAgent:
    def __init__(self, seed=None):
        self.random = random.Random(seed)

    def act(self, robot, field, robots=None, time_remaining=None):
        # If the robot is already carrying a block, drive toward the nearest goal.
        if robot.holding > 0:
            target = min(field.get_goals(), key=lambda goal: self._distance_to_goal(robot, goal))
            target_x, target_y = target.closest_point_on_opening(robot.x, robot.y)
            return self._drive_towards(robot, target_x, target_y, slow_when_close=True)

        # Otherwise seek the nearest free block.
        target_block = self._closest_free_block(robot, field.blocks)
        if target_block:
            return self._drive_towards(robot, target_block.x, target_block.y)

        # No block found: slow down and hold heading.
        return 0.0, 0.0

    def _closest_free_block(self, robot, blocks):
        available = [
            block for block in blocks
            if not block.held and not block.in_goal and block.team == robot.team
        ]
        if not available:
            return None

        return min(available, key=lambda block: math.hypot(block.x - robot.x, block.y - robot.y))

    def _distance_to_goal(self, robot, goal):
        dx = robot.x - goal.x
        dy = robot.y - goal.y
        return math.hypot(dx, dy)

    def _drive_towards(self, robot, target_x, target_y, slow_when_close=False):
        dx = target_x - robot.x
        dy = target_y - robot.y
        distance = math.hypot(dx, dy)
        desired = math.atan2(dy, dx)
        heading_rad = math.radians(robot.heading)
        angle_delta = self._normalize_angle(desired - heading_rad)

        turn = max(-1.0, min(1.0, angle_delta / 1.5))

        if abs(angle_delta) > math.pi / 2:
            throttle = 0.0
        else:
            throttle = max(0.0, min(1.0, distance / 24.0))
            if slow_when_close and distance < 12.0:
                throttle *= 0.35

        return throttle, turn

    @staticmethod
    def _normalize_angle(angle):
        while angle <= -math.pi:
            angle += 2 * math.pi
        while angle > math.pi:
            angle -= 2 * math.pi
        return angle
