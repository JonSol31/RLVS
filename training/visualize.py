import argparse
import json
import os
import time

from simulation.match import Match
from agents.policy_agent import PolicyAgent
from agents.block_seeker_agent import BlockSeekerAgent
from rendering.renderer import Renderer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, help="Path to saved agent JSON")
    parser.add_argument("--seconds", type=float, default=100.0, help="Seconds to simulate")
    parser.add_argument("--dt", type=float, default=0.1, help="Physics dt")
    args = parser.parse_args()

    with open(args.agent, "r", encoding="utf-8") as f:
        data = json.load(f)

    agent = PolicyAgent(weights=data.get("weights"), biases=data.get("biases"))

    match = Match()
    renderer = Renderer()

    controllers = [agent, BlockSeekerAgent(), BlockSeekerAgent(), BlockSeekerAgent()]

    match.reset()
    steps = int(args.seconds / args.dt)
    for _ in range(steps):
        match.update(args.dt, controllers=controllers)
        renderer.render(match)
        time.sleep(args.dt * 0.25)


if __name__ == "__main__":
    main()
