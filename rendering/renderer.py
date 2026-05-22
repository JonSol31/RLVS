import pygame
import math


WINDOW_SIZE = 1000
FIELD_SIZE = 144

SCALE = WINDOW_SIZE / FIELD_SIZE


class Renderer:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_SIZE, WINDOW_SIZE)
        )

        pygame.display.set_caption("RLVS")

    def draw_robot(self, robot):
        x = int(robot.x * SCALE)
        y = int(robot.y * SCALE)

        radius = int(robot.RADIUS * SCALE)

        pygame.draw.circle(
            self.screen,
            robot.color,
            (x, y),
            radius
        )

        # heading line
        radians = math.radians(robot.heading)

        hx = x + math.cos(radians) * radius
        hy = y + math.sin(radians) * radius

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (x, y),
            (hx, hy),
            3
        )

    def draw_field(self):
        self.screen.fill((40, 40, 40))

        # tiles
        tile_size = WINDOW_SIZE / 6

        for i in range(7):
            pygame.draw.line(
                self.screen,
                (70, 70, 70),
                (i * tile_size, 0),
                (i * tile_size, WINDOW_SIZE),
            )

            pygame.draw.line(
                self.screen,
                (70, 70, 70),
                (0, i * tile_size),
                (WINDOW_SIZE, i * tile_size),
            )

    def render(self, match):
        self.draw_field()

        for robot in match.robots:
            self.draw_robot(robot)

        pygame.display.flip()