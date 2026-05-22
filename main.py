import pygame

from simulation.match import Match
from rendering.renderer import Renderer


def main():
    renderer = Renderer()
    match = Match()

    clock = pygame.time.Clock()

    running = True

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        match.update(dt)

        renderer.render(match)

    pygame.quit()


if __name__ == "__main__":
    main()