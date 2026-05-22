import math


class Robot:
    RADIUS = 9  # inches (~18 inch robot)

    def __init__(self, x, y, color, config):
        self.x = x
        self.y = y

        self.heading = 0

        self.vx = 0
        self.vy = 0

        self.color = color

        self.mass = config["mass"]
        self.push_force = config["push_force"]

        self.max_speed = config["max_speed"]
        self.acceleration = config["acceleration"]
        self.turn_speed = config["turn_speed"]

    def update(self, throttle, turn, dt):
        # turning
        self.heading += turn * self.turn_speed * dt

        radians = math.radians(self.heading)

        # acceleration
        ax = math.cos(radians) * throttle * self.acceleration
        ay = math.sin(radians) * throttle * self.acceleration

        self.vx += ax * dt
        self.vy += ay * dt

        # clamp speed
        speed = math.sqrt(self.vx**2 + self.vy**2)

        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        # movement
        self.x += self.vx * dt
        self.y += self.vy * dt

        # friction
        self.vx *= 0.96
        self.vy *= 0.96