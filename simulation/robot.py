import math


class Robot:
    SIZE = 15  # inches (18x18 VEX-ish footprint)

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

        self.capacity = 9
        self.holding =  0   

        self.team = None     

    def get_corners(self):
        """Return approximate square corners (for rendering + collision)."""
        half = self.SIZE / 2

        radians = math.radians(self.heading)

        cos_h = math.cos(radians)
        sin_h = math.sin(radians)

        corners = []

        for dx, dy in [
            (-half, -half),
            (half, -half),
            (half, half),
            (-half, half),
        ]:
            rx = dx * cos_h - dy * sin_h
            ry = dx * sin_h + dy * cos_h

            corners.append((self.x + rx, self.y + ry))

        return corners

    def update(self, throttle, turn, dt):
        # rotation
        self.heading += turn * self.turn_speed * dt

        radians = math.radians(self.heading)

        ax = math.cos(radians) * throttle * self.acceleration
        ay = math.sin(radians) * throttle * self.acceleration

        self.vx += ax * dt
        self.vy += ay * dt

        speed = math.sqrt(self.vx**2 + self.vy**2)

        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        self.x += self.vx * dt
        self.y += self.vy * dt

        # friction
        self.vx *= 0.96
        self.vy *= 0.96