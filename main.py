import argparse
import glob
import json
import os
import pygame

from simulation.match import Match
from rendering.renderer import Renderer
from agents.policy_agent import PolicyAgent
from agents.random_agent import RandomAgent


def find_latest_agent(search_dir="."):
    pattern = os.path.join(search_dir, "best_agent_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def load_agent(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PolicyAgent(weights=data.get("weights"), biases=data.get("biases"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default=None, help="Path to agent JSON. If omitted, auto-find latest best_agent_*.json")
    parser.add_argument("--agent-dir", default=".", help="Directory to search for saved agents when --agent is omitted")
    args = parser.parse_args()

    renderer = Renderer()
    match = Match()

    # choose agent
    agent_path = args.agent
    if agent_path is None:
        agent_path = find_latest_agent(args.agent_dir)

    if agent_path:
        print(f"Loading agent from {agent_path}")
        agent = load_agent(agent_path)
        controllers = [agent, agent, agent, agent]
    else:
        print("No saved agent found — using random agents")
        controllers = [RandomAgent(), RandomAgent(), RandomAgent(), RandomAgent()]

    clock = pygame.time.Clock()

    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        match.update(dt, controllers=controllers)

        renderer.render(match)

    pygame.quit()


if __name__ == "__main__":
    main()