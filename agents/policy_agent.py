import math
import random


class PolicyAgent:
    FEATURE_COUNT = 10

    def __init__(self, weights=None, biases=None):
        if weights is None:
            self.weights = [random.gauss(0, 0.5) for _ in range(self.FEATURE_COUNT * 2)]
        else:
            self.weights = list(weights)

        if biases is None:
            self.biases = [random.gauss(0, 0.1) for _ in range(2)]
        else:
            self.biases = list(biases)

    def act(self, robot, field, robots=None, time_remaining=None):
        features = self._build_features(robot, field, robots=robots, time_remaining=time_remaining)

        throttle = sum(features[i] * self.weights[i] for i in range(self.FEATURE_COUNT)) + self.biases[0]
        turn = sum(features[i] * self.weights[self.FEATURE_COUNT + i] for i in range(self.FEATURE_COUNT)) + self.biases[1]

        return math.tanh(throttle), math.tanh(turn)

    def _has_goal_majority(self, robot, field, goal_types):
        own = 0
        opp = 0
        opponent = "blue" if robot.team == "red" else "red"

        for goal in field.get_goals():
            if goal.type not in goal_types:
                continue
            for block in field.blocks:
                if block.held or block.team not in {robot.team, opponent}:
                    continue
                dx = block.x - goal.x
                dy = block.y - goal.y
                rad = math.radians(-goal.angle)
                local_x = dx * math.cos(rad) - dy * math.sin(rad)
                local_y = dx * math.sin(rad) + dy * math.cos(rad)
                if abs(local_y) <= goal.height / 2 and abs(local_x) <= goal.width / 2:
                    if block.team == robot.team:
                        own += 1
                    else:
                        opp += 1

        if own > opp:
            return 1.0
        if opp > own:
            return -1.0
        return 0.0

    def _closest_opponent(self, robot, robots):
        if not robots:
            return None, None

        opponents = [other for other in robots if other.team != robot.team]
        if not opponents:
            return None, None

        nearest = min(opponents, key=lambda other: math.hypot(robot.x - other.x, robot.y - other.y))
        dx = nearest.x - robot.x
        dy = nearest.y - robot.y
        return math.hypot(dx, dy), math.atan2(dy, dx)

    def _build_features(self, robot, field, robots=None, time_remaining=None):
        # internal robot state
        holding = robot.holding / max(robot.capacity, 1)
        speed = math.hypot(robot.vx, robot.vy) / max(robot.max_speed, 1)

        # goal control and zone dominance
        center_control = self._has_goal_majority(robot, field, ["center_upper", "center_lower"])
        long_control = self._has_goal_majority(robot, field, ["long_top", "long_bottom"])

        # nearest opponent vector
        opp_dist, opp_angle = self._closest_opponent(robot, robots)
        if opp_dist is None:
            opp_dist = 144.0
            opp_angle = 0.0

        opp_dist = min(opp_dist / 144.0, 1.0)
        opp_cos = math.cos(opp_angle)
        opp_sin = math.sin(opp_angle)

        # reward critical timing and endgame behavior
        time_norm = 0.0
        if time_remaining is not None:
            time_norm = max(0.0, min(1.0, time_remaining / 60.0))

        # simple field distribution proxy
        free_blocks = sum(
            1
            for block in field.blocks
            if not block.held and not block.in_goal and block.team == robot.team
        )
        total_blocks = max(1, len(field.blocks))
        block_distribution = free_blocks / total_blocks

        nearest_goal = min(field.get_goals(), key=lambda goal: math.hypot(robot.x - goal.x, robot.y - goal.y))
        goal_dx = nearest_goal.x - robot.x
        goal_dy = nearest_goal.y - robot.y
        goal_dist = math.hypot(goal_dx, goal_dy) + 1e-6

        return [
            holding,
            center_control,
            long_control,
            opp_dist,
            opp_cos,
            opp_sin,
            time_norm,
            block_distribution,
            (goal_dx / goal_dist),
            (goal_dy / goal_dist),
        ]

    def clone(self):
        return PolicyAgent(weights=self.weights, biases=self.biases)

    def mutate(self, rate=0.25, scale=0.6):
        for i in range(len(self.weights)):
            if random.random() < rate:
                self.weights[i] += random.gauss(0, scale)
        for i in range(len(self.biases)):
            if random.random() < rate:
                self.biases[i] += random.gauss(0, scale)
