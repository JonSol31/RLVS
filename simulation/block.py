class Block:
    SIZE = 3.5  # inches

    def __init__(self, x, y, color, team=None):
        self.x = x
        self.y = y

        self.color = color
        self.team = team  # "red", "blue"

        self.vx = 0
        self.vy = 0

        self.held = False
        self.carried_by = None

        self.in_goal = False
        self.scored = False
        self.scored_by = None
        self.scored = False