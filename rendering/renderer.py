import pygame
import math

from simulation import robot


WINDOW_SIZE = 1000
FIELD_SIZE = 144  # inches


class Renderer:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("RLVS - Push Back Simulator")

        # scaling + coordinate transform
        self.SCALE = WINDOW_SIZE / FIELD_SIZE
        self.center_offset = WINDOW_SIZE / 2

    # -----------------------------
    # Coordinate transform helpers
    # -----------------------------
    def world_to_screen(self, x, y):
        px = x * self.SCALE
        py = y * self.SCALE

        # flip Y axis (math → pygame)
        py = -py

        # center origin
        sx = px + self.center_offset
        sy = py + self.center_offset

        return int(sx), int(sy)
    def draw_field(self):
        self.screen.fill((30, 30, 30))

        tile = WINDOW_SIZE / 6

        for i in range(7):
            pygame.draw.line(
                self.screen,
                (60, 60, 60),
                (i * tile, 0),
                (i * tile, WINDOW_SIZE),
            )
            pygame.draw.line(
                self.screen,
                (60, 60, 60),
                (0, i * tile),
                (WINDOW_SIZE, i * tile),
            )

        # center crosshair
        pygame.draw.line(
            self.screen,
            (120, 120, 120),
            (WINDOW_SIZE / 2, 0),
            (WINDOW_SIZE / 2, WINDOW_SIZE),
            2,
        )
        pygame.draw.line(
            self.screen,
            (120, 120, 120),
            (0, WINDOW_SIZE / 2),
            (WINDOW_SIZE, WINDOW_SIZE / 2),
            2,
        )

    # -----------------------------
    # Robot rendering (square)
    # -----------------------------
    def draw_robot(self, robot):
        corners = []

        half = robot.SIZE / 2

        radians = math.radians(robot.heading)
        cos_h = math.cos(radians)
        sin_h = math.sin(radians)

        # local square corners
        local = [
            (-half, -half),
            (half, -half),
            (half, half),
            (-half, half),
        ]

        for dx, dy in local:
            rx = dx * cos_h - dy * sin_h
            ry = dx * sin_h + dy * cos_h

            x, y = self.world_to_screen(robot.x + rx, robot.y + ry)
            corners.append((x, y))

        pygame.draw.polygon(self.screen, robot.color, corners)

        # heading indicator
        cx, cy = self.world_to_screen(robot.x, robot.y)

        hx = cx + math.cos(radians) * 15
        hy = cy - math.sin(radians) * 15

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (cx, cy),
            (hx, hy),
            2,
        )
        print(robot.x, robot.y, self.world_to_screen(robot.x, robot.y))

    # -----------------------------
    # Goal rendering (rotated rectangles)
    # -----------------------------
    def draw_goal(self, goal):
        cx, cy = self.world_to_screen(goal.x, goal.y)

        w = goal.width * self.SCALE
        h = goal.height * self.SCALE

        if "long" in goal.type:
            color = (255, 200, 0)
        else:
            color = (0, 200, 255)

        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        surface.fill(color)

        rotated = pygame.transform.rotate(surface, goal.angle)

        rect = rotated.get_rect(center=(cx, cy))

        self.screen.blit(rotated, rect.topleft)

    def draw_goals(self, field):
        for goal in field.get_goals():
            self.draw_goal(goal)
    def draw_blocks(self, field):
        for block in field.blocks:
            x, y = self.world_to_screen(block.x, block.y)

            size = block.SIZE * self.SCALE

            color = block.color

            pygame.draw.rect(
                self.screen,
                color,
                pygame.Rect(
                    x - size / 2,
                    y - size / 2,
                    size,
                    size
                )
            )

    # -----------------------------
    # Main render call
    # -----------------------------
    def render(self, match):
        self.draw_field()

        # goals
        self.draw_goals(match.field)
        self.draw_blocks(match.field)
        # robots
        for robot in match.robots:
            self.draw_robot(robot)

        pygame.display.flip()