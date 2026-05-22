import math


FIELD_SIZE = 144  # inches


def resolve_wall_collision(robot):
    r = robot.RADIUS

    robot.x = max(r, min(FIELD_SIZE - r, robot.x))
    robot.y = max(r, min(FIELD_SIZE - r, robot.y))


def resolve_robot_collision(robot1, robot2):
    dx = robot2.x - robot1.x
    dy = robot2.y - robot1.y

    distance = math.sqrt(dx**2 + dy**2)

    min_distance = robot1.RADIUS + robot2.RADIUS

    if distance == 0:
        return

    if distance < min_distance:
        overlap = min_distance - distance

        nx = dx / distance
        ny = dy / distance

        # separate robots
        robot1.x -= nx * overlap / 2
        robot1.y -= ny * overlap / 2

        robot2.x += nx * overlap / 2
        robot2.y += ny * overlap / 2

        # pushing impulse
        push_strength = (
            robot1.push_force + robot2.push_force
        ) / (robot1.mass + robot2.mass)

        robot1.vx -= nx * push_strength
        robot1.vy -= ny * push_strength

        robot2.vx += nx * push_strength
        robot2.vy += ny * push_strength