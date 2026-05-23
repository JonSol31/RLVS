import random


class RandomAgent:
    def __init__(self, seed=None):
        self.random = random.Random(seed)

    def act(self, robot, field, robots=None, time_remaining=None):
        return self.random.uniform(-1, 1), self.random.uniform(-1, 1)
