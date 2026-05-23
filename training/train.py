import random
import time
import os
import sys

# Ensure project root is on sys.path so imports like `simulation.match`
# work even when running this file directly from the `training/` folder.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from simulation.match import Match
from agents.policy_agent import PolicyAgent
from agents.random_agent import RandomAgent


POPULATION_SIZE = 20
GENERATIONS = 30
EVAL_EPISODES = 6
EPISODE_SECONDS = 8.0
DT = 0.1


import argparse
import json
from datetime import datetime


def evaluate_policy(policy, episodes=EVAL_EPISODES, episode_seconds=EPISODE_SECONDS, dt=DT):
    total_reward = 0.0

    for _ in range(episodes):
        match = Match()
        controllers = [policy, policy, RandomAgent(), RandomAgent()]
        episode_info = match.run_episode(controllers=controllers, max_seconds=episode_seconds, dt=dt)
        total_reward += sum(robot.reward for robot in match.robots if robot.team == "red")

    return total_reward / max(1, episodes)


def evolve(population, eval_episodes=EVAL_EPISODES, episode_seconds=EPISODE_SECONDS, dt=DT):
    scored = [(evaluate_policy(agent, episodes=eval_episodes, episode_seconds=episode_seconds, dt=dt), agent) for agent in population]
    scored.sort(key=lambda item: item[0], reverse=True)
    survivors = [agent for _, agent in scored[: max(2, POPULATION_SIZE // 4)]]

    children = []
    while len(children) < POPULATION_SIZE:
        parent = random.choice(survivors)
        child = parent.clone()
        child.mutate()
        children.append(child)

    return children, scored[0]



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=GENERATIONS, help="Number of generations to run")
    parser.add_argument("--population", type=int, default=POPULATION_SIZE, help="Population size")
    parser.add_argument("--episodes", type=int, default=EVAL_EPISODES, help="Evaluation episodes per agent")
    parser.add_argument("--seconds", type=float, default=EPISODE_SECONDS, help="Seconds per episode")
    parser.add_argument("--dt", type=float, default=DT, help="Physics dt")
    parser.add_argument("--fast", action="store_true", help="Run with faster, lower-fidelity settings")
    parser.add_argument("--save-dir", type=str, default=".", help="Directory to save best agent and history")

    args = parser.parse_args()

    # apply overrides
    generations = args.generations
    population_size = args.population
    eval_episodes = args.episodes
    episode_seconds = args.seconds
    dt = args.dt

    if args.fast:
        # lower-fidelity but much faster defaults for running many generations
        eval_episodes = max(1, eval_episodes // 3)
        episode_seconds = max(1.0, episode_seconds / 4.0)
        dt = min(0.25, dt * 2.0)

    # initialize population using requested size
    population = [PolicyAgent() for _ in range(population_size)]
    best_score = None
    best_agent = None

    history = []
    start = time.time()
    for generation in range(1, generations + 1):
        population, top = evolve(population, eval_episodes, episode_seconds, dt)
        score, agent = top

        if best_score is None or score > best_score:
            best_score = score
            best_agent = agent
            # save best agent whenever we get a new champion
            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            save_path = os.path.join(args.save_dir, f"best_agent_{timestamp}.json")
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump({"weights": best_agent.weights, "biases": best_agent.biases, "score": best_score}, f)

        history.append({"generation": generation, "score": score, "best_score": best_score})

        # print summary less verbosely for large runs
        if generation % max(1, generations // 50) == 0 or generation <= 5:
            print(f"Generation {generation:04d} | best average reward: {score:.2f} | best ever: {best_score:.2f}")

    duration = time.time() - start
    print(f"Training finished in {duration:.1f}s | best average reward: {best_score:.2f}")

    # write history
    history_path = os.path.join(args.save_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f)


if __name__ == "__main__":
    main()
