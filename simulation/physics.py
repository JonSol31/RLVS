import math


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
def resolve_goal_collision(robot, goals):
    for goal in goals:
        if point_in_rotated_rect(
            robot.x,
            robot.y,
            goal.x,
            goal.y,
            goal.width,
            goal.height,
            goal.angle
        ):
            # simple push-out (minimal vector separation)
            dx = robot.x - goal.x
            dy = robot.y - goal.y

            dist = math.sqrt(dx**2 + dy**2)
            if dist == 0:
                continue

            nx = dx / dist
            ny = dy / dist

            push_strength = 2.0  # tweakable

            robot.x += nx * push_strength
            robot.y += ny * push_strength

            # damp velocity on collision
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
            # ----------------------------
            # TEAM RULE CHECK (NEW)
            # ----------------------------

            robot_team = getattr(robot, "team", None)

            if block.team is not None and block.team != robot_team:
                #  enemy block → SPIT OUT EFFECT
                dx = block.x - robot.x
                dy = block.y - robot.y

                dist = math.sqrt(dx**2 + dy**2)
                if dist == 0:
                    return

                nx = dx / dist
                ny = dy / dist

                # eject block away from robot
                block.x += nx * 6
                block.y += ny * 6

                block.vx = nx * 8
                block.vy = ny * 8

                continue  # cannot pick up enemy block

            # ----------------------------
            # PICKUP (allowed)
            # ----------------------------
            if robot.holding < robot.capacity:
                block.held = True
                block.carried_by = robot
                robot.holding += 1
def update_carried_blocks(blocks):
    for block in blocks:
        if block.held and block.carried_by is not None:
            r = block.carried_by

            # attach block slightly in front of robot
            rad = math.radians(r.heading)

            offset = r.SIZE / 2 + 2

            block.x = r.x + math.cos(rad) * offset
            block.y = r.y + math.sin(rad) * offset
def resolve_scoring(blocks, goals):
    for block in blocks:
        if block.held:
            continue

        for goal in goals:
            dx = block.x - goal.x
            dy = block.y - goal.y

            if abs(dx) < goal.width / 2 and abs(dy) < goal.height / 2:
                block.in_goal = True
def try_drop_blocks(robot):
    # simple rule: robot automatically drops if in goal zone OR random release trigger later
    pass
def score_blocks(field, score_dict):
    for block in field.blocks:
        if block.held:
            continue

        for goal in field.get_goals():
            dx = block.x - goal.x
            dy = block.y - goal.y

            # rotated check
            import math
            rad = math.radians(-goal.angle)

            local_x = dx * math.cos(rad) - dy * math.sin(rad)
            local_y = dx * math.sin(rad) + dy * math.cos(rad)

            if abs(local_x) <= goal.width / 2 and abs(local_y) <= goal.height / 2:

                if block.in_goal:
                    continue  # prevent double scoring

                block.in_goal = True

                # assign score by team ownership
                if block.team == "red":
                    score_dict["red"] += goal.value
                elif block.team == "blue":
                    score_dict["blue"] += goal.value
def enforce_drop(robot, field):
    for block in field.blocks:
        if block.carried_by == robot:
            for goal in field.get_goals():
                dx = robot.x - goal.x
                dy = robot.y - goal.y

                if abs(dx) < goal.width / 2 and abs(dy) < goal.height / 2:
                    # drop block
                    block.held = False
                    block.carried_by = None

                    robot.holding -= 1