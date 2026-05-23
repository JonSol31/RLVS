import math
import random


FIELD_HALF = 72  # center-origin system


def resolve_wall_collision(robot):
    half = robot.SIZE / 2

    robot.x = max(-FIELD_HALF + half, min(FIELD_HALF - half, robot.x))
    robot.y = max(-FIELD_HALF + half, min(FIELD_HALF - half, robot.y))


def resolve_robot_collision(a, b):
    dx = b.x - a.x
    dy = b.y - a.y

    min_dist = (a.SIZE + b.SIZE) / 2

    dist = math.sqrt(dx**2 + dy**2)

    if dist == 0:
        return

    if dist < min_dist:
        overlap = min_dist - dist

        nx = dx / dist
        ny = dy / dist

        # separation
        a.x -= nx * overlap / 2
        a.y -= ny * overlap / 2

        b.x += nx * overlap / 2
        b.y += ny * overlap / 2

        # pushing impulse (mass-based)
        total_mass = a.mass + b.mass

        impulse = (a.push_force - b.push_force) / total_mass

        a.vx -= nx * impulse
        a.vy -= ny * impulse

        b.vx += nx * impulse
        b.vy += ny * impulse
def point_in_rotated_rect(px, py, gx, gy, w, h, angle):
    # translate point into goal space
    dx = px - gx
    dy = py - gy

    rad = math.radians(-angle)

    # rotate point opposite direction of goal
    local_x = dx * math.cos(rad) - dy * math.sin(rad)
    local_y = dx * math.sin(rad) + dy * math.cos(rad)

    return abs(local_x) <= w / 2 and abs(local_y) <= h / 2
def _random_spawn_point_outside_goals(goals, block):
    half = FIELD_HALF - block.SIZE
    for _ in range(100):
        x = random.uniform(-half, half)
        y = random.uniform(-half, half)
        if all(not goal.contains_point(x, y) for goal in goals):
            return x, y
    return x, y


def _eject_goal_blocks(goal, blocks, goals):
    candidates = [
        block for block in blocks
        if block.in_goal and not block.held and goal.contains_point(block.x, block.y)
    ]
    if not candidates:
        return

    count = random.randint(1, min(len(candidates), 3))
    random.shuffle(candidates)
    for block in candidates[:count]:
        block.in_goal = False
        block.held = False
        block.carried_by = None
        block.scored_by = None
        block.x, block.y = _random_spawn_point_outside_goals(goals, block)
        block.vx = random.uniform(-4, 4)
        block.vy = random.uniform(-4, 4)


def resolve_goal_collision(robot, goals, blocks, dt):
    for goal in goals:
        if goal.contains_point(robot.x, robot.y):
            speed = math.hypot(robot.vx, robot.vy)
            crash_penalty = 10.0
            if speed > 4.0:
                crash_penalty += (speed - 4.0) * 4.0
            robot.reward -= crash_penalty

            if speed > 5.0:
                robot.reward -= 10.0
                _eject_goal_blocks(goal, blocks, goals)

            local_x, local_y = goal.world_to_local(robot.x, robot.y)
            half_w = goal.width / 2
            half_h = goal.height / 2

            dx = 0.0
            dy = 0.0
            if abs(local_x) > half_w:
                dx = (half_w - abs(local_x)) * (1 if local_x > 0 else -1)
            if abs(local_y) > half_h:
                dy = (half_h - abs(local_y)) * (1 if local_y > 0 else -1)

            if dx == 0.0 and dy == 0.0:
                # robot inside the goal rectangle, push out along the nearest face
                if abs(local_x) < abs(local_y):
                    dx = (half_w - abs(local_x)) * (1 if local_x > 0 else -1)
                else:
                    dy = (half_h - abs(local_y)) * (1 if local_y > 0 else -1)

            x_axis, y_axis = goal._axes()
            robot.x += dx * x_axis[0] + dy * y_axis[0]
            robot.y += dx * x_axis[1] + dy * y_axis[1]

            robot.vx *= 0.5
            robot.vy *= 0.5
def resolve_block_interaction(robot, blocks):
    pickup_range = robot.SIZE / 2 + 4

    for block in blocks:
        if block.held:
            continue

        dx = block.x - robot.x
        dy = block.y - robot.y

        dist = math.sqrt(dx**2 + dy**2)

        if dist < pickup_range:
            robot_team = getattr(robot, "team", None)

            if block.team is not None and block.team != robot_team:
                dx = block.x - robot.x
                dy = block.y - robot.y

                dist = math.sqrt(dx**2 + dy**2)
                if dist == 0:
                    return

                nx = dx / dist
                ny = dy / dist

                block.x += nx * 6
                block.y += ny * 6

                block.vx = nx * 8
                block.vy = ny * 8

                continue

            if robot.holding < robot.capacity:
                block.held = True
                block.carried_by = robot
                robot.holding += 1
def resolve_block_collisions(blocks):
    for i in range(len(blocks)):
        a = blocks[i]
        if a.held:
            continue

        for j in range(i + 1, len(blocks)):
            b = blocks[j]
            if b.held:
                continue

            dx = b.x - a.x
            dy = b.y - a.y
            min_dist = (a.SIZE + b.SIZE) / 2
            dist = math.hypot(dx, dy)

            if dist == 0 or dist >= min_dist:
                continue

            overlap = min_dist - dist
            nx = dx / dist
            ny = dy / dist

            a.x -= nx * overlap / 2
            a.y -= ny * overlap / 2
            b.x += nx * overlap / 2
            b.y += ny * overlap / 2

            rel_v = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
            if rel_v < 0:
                impulse = -rel_v * 0.5
                a.vx -= impulse * nx
                a.vy -= impulse * ny
                b.vx += impulse * nx
                b.vy += impulse * ny

def update_carried_blocks(blocks):
    carriers = {}

    for block in blocks:
        if block.held and block.carried_by is not None:
            carriers.setdefault(block.carried_by, []).append(block)

    for robot, held_blocks in carriers.items():
        count = len(held_blocks)
        rad_base = math.radians(robot.heading)
        offset = robot.SIZE / 2 + block.SIZE / 2 + 1
        spread = 0.35

        for idx, block in enumerate(held_blocks):
            angle = rad_base + (idx - (count - 1) / 2) * spread
            block.x = robot.x + math.cos(angle) * offset
            block.y = robot.y + math.sin(angle) * offset
            block.vx = robot.vx
            block.vy = robot.vy
def resolve_scoring(blocks, goals):
    for block in blocks:
        if block.held:
            block.in_goal = False
            continue

        block.in_goal = False
        for goal in goals:
            dx = block.x - goal.x
            dy = block.y - goal.y

            rad = math.radians(-goal.angle)
            local_x = dx * math.cos(rad) - dy * math.sin(rad)
            local_y = dx * math.sin(rad) + dy * math.cos(rad)

            if abs(local_y) <= goal.height / 2 and abs(local_x) <= goal.width / 2:
                if goal.current_load(blocks) >= goal.capacity and not block.in_goal:
                    continue
                block.in_goal = True
                break

def clamp_block_in_goal_tube(blocks, goals):
    for block in blocks:
        if block.held or not block.in_goal:
            continue

        for goal in goals:
            dx = block.x - goal.x
            dy = block.y - goal.y

            rad = math.radians(-goal.angle)
            cos_r = math.cos(rad)
            sin_r = math.sin(rad)

            local_x = dx * cos_r - dy * sin_r
            local_y = dx * sin_r + dy * cos_r

            half_height = goal.height / 2 - block.SIZE / 2
            if half_height < 0:
                half_height = 0

            if abs(local_y) > half_height:
                local_y = max(-half_height, min(half_height, local_y))
                block.x = goal.x + local_x * cos_r + local_y * sin_r
                block.y = goal.y - local_x * sin_r + local_y * cos_r

            break
def score_held_blocks(robot, field, dt):
    if robot.holding == 0:
        robot.score_timer = 0.0
        robot.is_scoring = False
        return

    scoring_goal = None
    for goal in field.get_goals():
        if goal.contains_point(robot.x, robot.y, padding=robot.SIZE / 2 + 2):
            scoring_goal = goal
            break

    robot.is_scoring = scoring_goal is not None
    if scoring_goal is None:
        robot.score_timer = 0.0
        return

    robot.score_timer -= dt
    if robot.score_timer > 0:
        return

    robot.score_timer = robot.score_interval

    for block in field.blocks:
        if block.carried_by == robot and block.held:
            release_scored_block(robot, block, scoring_goal)
            break


def release_scored_block(robot, block, goal):
    block.held = False
    block.carried_by = None
    block.scored_by = robot
    robot.holding -= 1

    px, py = goal.closest_point_on_opening(robot.x, robot.y)
    normal_x, normal_y = goal.direction_into_goal(robot.x, robot.y)
    inset = goal.height / 2 - block.SIZE / 2
    offset = max(0.5, min(1.0, inset))

    block.x = px + normal_x * offset
    block.y = py + normal_y * offset

    score_force = 8
    block.vx = normal_x * score_force
    block.vy = normal_y * score_force
def score_blocks(field, score_dict, score_events):
    for block in list(field.blocks):
        if not block.in_goal or block.held:
            continue

        for goal in field.get_goals():
            if goal.contains_point(block.x, block.y):
                if block.scored_by is not None:
                    block.scored_by.reward += goal.value * 5.0
                    block.scored_by = None
                if block.team == "red":
                    score_dict["red"] += goal.value
                    score_events["red"] += 1
                elif block.team == "blue":
                    score_dict["blue"] += goal.value
                    score_events["blue"] += 1

                block.in_goal = False
                block.held = False
                block.carried_by = None
                block.x, block.y = _random_spawn_point_outside_goals(field.get_goals(), block)
                block.vx = random.uniform(-4, 4)
                block.vy = random.uniform(-4, 4)
                break
def enforce_drop(robot, field):
    for block in field.blocks:
        if block.carried_by == robot:
            for goal in field.get_goals():
                if goal.contains_point(robot.x, robot.y):
                    # drop block
                    block.held = False
                    block.carried_by = None

                    robot.holding -= 1