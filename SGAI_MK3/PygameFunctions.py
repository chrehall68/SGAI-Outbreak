from typing import List, Tuple
import pygame
from constants import *
from Board import Board

# globals
screen = None
font = None
board_like = []


def initScreen(board: Board):
    global font, screen, board_like
    # Initialize pygame
    screen = pygame.display.set_mode(GAME_WINDOW_DIMENSIONS)
    pygame.display.set_caption("Outbreak!")
    pygame.font.init()
    font = pygame.font.SysFont("Comic Sans", 20)
    screen.fill(BACKGROUND)
    board_like = [
        Cell((MARGIN + x * CELL_DIMENSIONS[0], MARGIN + y * CELL_DIMENSIONS[1]))
        for y in range(board.rows)
        for x in range(board.columns)
    ]


class Cell:
    def __init__(
        self,
        top_left: Tuple[int, int],
        width=CELL_DIMENSIONS[0],
        height=CELL_DIMENSIONS[1],
        border_thickness=CELL_BORDER,
        border_color=BLACK,
    ) -> None:
        self.top_left = top_left
        self.width = width
        self.height = height
        self.border_thickness = border_thickness
        self.border_color = border_color

        top_line = pygame.Rect(top_left[0], top_left[1], width, border_thickness)
        bottom_line = pygame.Rect(
            top_left[0],
            top_left[1] + height - border_thickness,
            width,
            border_thickness,
        )
        left_line = pygame.Rect(top_left[0], top_left[1], border_thickness, height)
        right_line = pygame.Rect(
            top_left[0] + width - border_thickness,
            top_left[1],
            border_thickness,
            height,
        )
        self.borders = [top_line, bottom_line, left_line, right_line]
        self.cell_rect = pygame.Rect(top_left[0], top_left[1], width, height)

    def draw(self, screen: pygame.Surface, bgcolor: pygame.Color, **kwargs) -> None:
        """
        Valid kwargs are
        image_path - str - the path to the image
        image_size - Tuple[int, int] - the size to scale the image to
        """
        pygame.draw.rect(screen, bgcolor, self.cell_rect)
        for border in self.borders:
            pygame.draw.rect(screen, self.border_color, border)

        if "image_path" in kwargs:
            img = pygame.image.load(kwargs["image_path"]).convert_alpha()
            if "image_size" in kwargs:
                img = pygame.transform.scale(img, kwargs["image_size"])
            img_dims = img.get_size()
            screen.blit(
                img,
                (
                    self.top_left[0] + (self.width - img_dims[0]) // 2,
                    self.top_left[1] + (self.height - img_dims[1]) // 2,
                ),
            )


def get_action(GameBoard: Board, pixel_x: int, pixel_y: int):
    """
    Get the action that the click represents.
    If the click was on the heal button, returns "heal"
    Else, returns the board coordinates of the click (board_x, board_y) if valid
    Return None otherwise
    """
    # Check if the user clicked on the "heal" or "bite" icon, return "heal" or "bite" if so
    heal_bite_check = (
        pixel_x >= CURE_BITE_COORDS[0]
        and pixel_x <= CURE_BITE_COORDS[0] + CURE_BITE_DIMS[0]
        and pixel_y >= CURE_BITE_COORDS[1]
        and pixel_y <= CURE_BITE_COORDS[1] + CURE_BITE_DIMS[1]
    )
    reset_move_check = (
        pixel_x >= RESET_MOVE_COORDS[0]
        and pixel_x <= RESET_MOVE_COORDS[0] + RESET_MOVE_DIMS[0]
        and pixel_y >= RESET_MOVE_COORDS[1]
        and pixel_y <= RESET_MOVE_COORDS[1] + RESET_MOVE_DIMS[1]
    )
    wall_check = (
        pixel_x >= WALL_BUTTON_COORDS[0]
        and pixel_x <= WALL_BUTTON_COORDS[0] + WALL_BUTTON_DIMS[0]
        and pixel_y >= WALL_BUTTON_COORDS[1]
        and pixel_y <= WALL_BUTTON_COORDS[1] + WALL_BUTTON_DIMS[1]
    )
    board_x = int((pixel_x - MARGIN) / CELL_DIMENSIONS[0])
    board_y = int((pixel_y - MARGIN) / CELL_DIMENSIONS[1])
    move_check = (
        board_x >= 0
        and board_x < GameBoard.columns
        and board_y >= 0
        and board_y < GameBoard.rows
    )

    if heal_bite_check:
        if GameBoard.player_role == "Government":
            return "heal"
        return "bite"
    elif reset_move_check:
        return "reset move"
    elif wall_check:
        if GameBoard.player_role == "Government":
            return "wall"
    elif move_check:
        return board_x, board_y
    return None


def run(GameBoard: Board):
    """
    Draw the screen and return any events.
    """
    screen.fill(BACKGROUND)
    display_grid(GameBoard)  # Draw the grid and the people
    # Draw the heal icon
    if GameBoard.player_role == "Government":
        display_image(screen, "Assets/cure.jpeg", CURE_BITE_DIMS, CURE_BITE_COORDS)
        display_image(screen, "Assets/wall_button.png", WALL_BUTTON_DIMS, WALL_BUTTON_COORDS)
        display_resources(GameBoard.resources)
        display_safe_zone(GameBoard.safeEdge)
    else:
        display_image(screen, "Assets/bite.png", CURE_BITE_DIMS, CURE_BITE_COORDS)
    display_reset_move_button()
    return pygame.event.get()


def display_reset_move_button():
    rect = pygame.Rect(
        RESET_MOVE_COORDS[0],
        RESET_MOVE_COORDS[1],
        RESET_MOVE_DIMS[0],
        RESET_MOVE_DIMS[1],
    )
    pygame.draw.rect(screen, BLACK, rect)
    screen.blit(font.render("Reset move?", True, WHITE), RESET_MOVE_COORDS)


def display_resources(resources):
    screen.blit(
        font.render(f"You have {resources.resources} resources", True, WHITE),
        (800, 700),
    )
    screen.blit(
        font.render(
            f"cures cost {resources.costs['cure']}, vax costs {resources.costs['vaccinate']}, and walls cost {resources.costs['wall']}",
            True,
            WHITE,
        ),
        (800, 750),
    )


def display_safe_zone(zone):
    # Display the safe zone
    SAFE_ZONE_COORDS = (10, 20)
    screen.blit(
        font.render("Safe zone:", True, WHITE),
        SAFE_ZONE_COORDS,
    )
    screen.blit(
        font.render(f"{zone}", True, WHITE),
        (
            SAFE_ZONE_COORDS[0],
            SAFE_ZONE_COORDS[1] + font.size("Safe zone:")[1] * 2,
        ),
    )


def display_image(
    screen: pygame.Surface,
    itemStr: str,
    dimensions: Tuple[int, int],
    position: Tuple[int, int],
):
    """
    Draw an image on the screen at the indicated position.
    """
    v = pygame.image.load(itemStr).convert_alpha()
    v = pygame.transform.scale(v, dimensions)
    screen.blit(v, position)


def display_grid(GameBoard: Board):
    """
    Draw the grid on the screen, as well as any people.
    """
    for idx in range(GameBoard.columns * GameBoard.rows):
        bgcolor = BACKGROUND
        if idx in GameBoard.getSafeEdge():
            bgcolor = VAX_COLOR
        person = GameBoard.personAtIdx(idx)
        if person is not None:
            # there is a person, so draw the person
            image_path = "Assets/"
            if person.isVaccinated:
                image_path += IMAGE_ASSETS[1]
            elif person.isZombie:
                image_path += IMAGE_ASSETS[2]
            else:
                image_path += IMAGE_ASSETS[0]
            board_like[idx].draw(
                screen, bgcolor, image_path=image_path, image_size=PERSON_SIZE
            )
        elif GameBoard.States[idx].wall is not None:
            board_like[idx].draw(
                screen, bgcolor, image_path="Assets/wall.jpg", image_size=CELL_DIMENSIONS
            )
        else:
            # no person, so just draw the cell with the background color
            board_like[idx].draw(screen, bgcolor)


def display_cur_move(cur_move: List):
    # Display the current action
    screen.blit(
        font.render("Your move is currently:", True, WHITE),
        CUR_MOVE_COORDS,
    )
    screen.blit(
        font.render(f"{cur_move}", True, WHITE),
        (
            CUR_MOVE_COORDS[0],
            CUR_MOVE_COORDS[1] + font.size("Your move is currently:")[1] * 2,
        ),
    )


def display_win_screen():
    screen.fill(BACKGROUND)
    screen.blit(
        font.render("You win!", True, WHITE),
        (500, 350),
    )
    screen.blit(
        font.render("There were no possible moves for the computer.", True, WHITE),
        (500, 400),
    )
    pygame.display.update()

    # catch quit event
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


def display_lose_screen():
    screen.fill(BACKGROUND)
    screen.blit(
        font.render("You lose!", True, WHITE),
        (500, 350),
    )
    screen.blit(
        font.render("You had no possible moves...", True, WHITE),
        (500, 400),
    )
    pygame.display.update()

    # catch quit event
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


def direction(coord1: Tuple[int, int], coord2: Tuple[int, int]):
    if coord2[1] > coord1[1]:
        return "moveDown"
    elif coord2[1] < coord1[1]:
        return "moveUp"
    elif coord2[0] > coord1[0]:
        return "moveRight"
    elif coord2[0] < coord1[0]:
        return "moveLeft"

def display_wall(coords):
    dims = (CELL_DIMENSIONS[0] - LINE_WIDTH, CELL_DIMENSIONS[1] - LINE_WIDTH)
    new_coords = (coords[0] + LINE_WIDTH, coords[1] + LINE_WIDTH)
    display_image(screen, "Assets/wall.jpg", dims, new_coords)

