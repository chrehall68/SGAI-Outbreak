# constants

# frontend constants
BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CELL_COLOR = (233, 222, 188)
LINE_WIDTH = 5
IMAGE_ASSETS = [
    "person_normal.png",
    "person_vax.png",
    "person_zombie.png",
]
GAME_WINDOW_DIMENSIONS = (1200, 800)
RESET_MOVE_COORDS = (800, 600)
RESET_MOVE_DIMS = (200, 50)
BORDER = 150  # Number of pixels to offset grid to the top-left side
CELL_DIMENSIONS = (100, 100)  # Number of pixels (x,y) for each cell
CURE_COORDS = (950, 200)
CURE_DIMS = (100, 100)

# game, board constants
ROWS = 6
COLUMNS = 6
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite"]
ROLE_TO_ROLE_NUM = {"Government": 1, "Zombie": -1}
ROLE_TO_ROLE_BOOLEAN = {"Government": False, "Zombie": True}
