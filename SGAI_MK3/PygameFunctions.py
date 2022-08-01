from asyncio import constants
from typing import List, Tuple
import pygame
from constants import *
from Board import Board
from Person import Person
from Wall import Wall
import csv


# globals
screen = None
font = None
board_like = []


def initScreen(board: Board):
    global font, heading_font, screen, board_like
    # Initialize pygame
    screen = pygame.display.set_mode(GAME_WINDOW_DIMENSIONS)
    pygame.display.set_caption("Outbreak!")
    pygame.font.init()
    font = pygame.font.SysFont("Bahnschrift", 20)
    heading_font = pygame.font.SysFont("Bahnschrift", 40)
    screen.fill(BACKGROUND)
    board_like = [
        Cell(
            (LEFT_MARGIN + x * CELL_DIMENSIONS[0], TOP_MARGIN + y * CELL_DIMENSIONS[1])
        )
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

    def draw(self, screen: pygame.Surface, **kwargs) -> None:
        """
        Valid kwargs are
        image_path - str - the path to the image
        image_size - Tuple[int, int] - the size to scale the image to
        """
        # pygame.draw.rect(screen, bgcolor, self.cell_rect) replaced bgcolor with img
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

    def get_top_left(self):
        return self.top_left


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
    vax_check = (
        pixel_x >= VAX_COORDS[0]
        and pixel_x <= VAX_COORDS[0] + VAX_DIMS[0]
        and pixel_y >= VAX_COORDS[1]
        and pixel_y <= VAX_COORDS[1] + VAX_DIMS[1]
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
    board_x = int((pixel_x - LEFT_MARGIN) / CELL_DIMENSIONS[0])
    board_y = int((pixel_y - TOP_MARGIN) / CELL_DIMENSIONS[1])
    move_check = (
        board_x >= 0
        and board_x < GameBoard.columns
        and board_y >= 0
        and board_y < GameBoard.rows
    )

    if heal_bite_check:
        if GameBoard.player_role == "Government":
            return "cure"
        return "bite"
    elif reset_move_check:
        return "reset move"
    elif wall_check:
        if GameBoard.player_role == "Government":
            return "wall"
    elif vax_check:
        if GameBoard.player_role == "Government":
            return "vaccinate"
    elif move_check:
        return board_x, board_y
    return None


def run(GameBoard: Board):
    """
    Draw the screen and return any events.
    """
    screen.fill(BACKGROUND)
    display_grid(GameBoard)  # Draw the grid and the people
    screen.blit(  # name/action
        heading_font.render(
            "role: " + GameBoard.player_role,
            True,
            WHITE,
        ),
        (40, 25),
    )
    display_options(GameBoard)
    return pygame.event.get()


def display_reset_move_button():
    rect = pygame.Rect(
        RESET_MOVE_COORDS[0],
        RESET_MOVE_COORDS[1],
        RESET_MOVE_DIMS[0],
        RESET_MOVE_DIMS[1],
    )
    pygame.draw.rect(screen, BLACK, rect)
    screen.blit(
        font.render("Reset move?", True, WHITE),
        (RESET_MOVE_COORDS[0] + 45, RESET_MOVE_COORDS[1] + 10),
    )


def display_options(GameBoard):
    # Draw the options and highlight
    if GameBoard.player_role == "Government":
        options = {
            "cure": [CURE_BITE_COORDS, CURE_BITE_DIMS],
            "vaccinate": [VAX_COORDS, VAX_DIMS],
            "wall": [WALL_BUTTON_COORDS, WALL_BUTTON_DIMS],
        }
        for option in options:
            coordsdims = options[option]  # list w/ [coords tuple, dims tuple]
            if GameBoard.resources.resources < GameBoard.resources.costs[option]:
                pygame.draw.rect(
                    screen,
                    IMG_RED,
                    pygame.Rect(
                        coordsdims[0][0],
                        coordsdims[0][1],
                        coordsdims[1][0],
                        coordsdims[1][1],
                    ),
                )
            else:  # elif the move is selected: #** need to work on in separate branch
                pygame.draw.rect(
                    screen,
                    IMG_GREEN,
                    pygame.Rect(
                        coordsdims[0][0],
                        coordsdims[0][1],
                        coordsdims[1][0],
                        coordsdims[1][1],
                    ),
                )
        display_image(screen, "Assets/cure.jpeg", CURE_BITE_DIMS, CURE_BITE_COORDS)
        display_image(screen, "Assets/vax.png", VAX_DIMS, VAX_COORDS)
        display_image(screen, "Assets/wall.png", WALL_BUTTON_DIMS, WALL_BUTTON_COORDS)
        display_resources(GameBoard.resources)
        display_turns_left(GameBoard, GameBoard.count_vax_people())
        # display_safe_zone(GameBoard.safeEdge)
    else:
        display_image(screen, "Assets/bite.png", CURE_BITE_DIMS, CURE_BITE_COORDS)
    display_reset_move_button()


def display_resources(resources):
    resource_coords = (
        1115 - 20 * len(str(resources.resources)),
        25,
    )  # adjusts position based on # of digits
    screen.blit(
        heading_font.render(f"{resources.resources}", True, WHITE),
        resource_coords,
    )
    display_image(screen, "Assets/coin.png", COIN_DIMS, COIN_BALANCE_COORDS)

    costs = [
        ["cure:", f"{resources.costs['cure']}"],
        [f"vax:", f"{resources.costs['vaccinate']}"],
        [f"walls:", f"{resources.costs['wall']}"],
    ]
    for index in range(3):
        screen.blit(  # name/action
            heading_font.render(
                costs[index][0],
                True,
                WHITE,
            ),
            (925, 250 + 50 * index),
        )
        screen.blit(  # price
            heading_font.render(
                costs[index][1],
                True,
                WHITE,
            ),
            (1050, 250 + 50 * index),
        )
        # coin img
        display_image(screen, "Assets/coin.png", (40, 40), (1080, 255 + 50 * index))


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
    imgx, imgy = CELL_DIMENSIONS
    imgx = imgx * 0.95
    imgy = imgy * 0.95
    for idx in range(GameBoard.columns * GameBoard.rows):
        # bgcolor = BACKGROUND
        if idx in GameBoard.getSafeEdge():
            # bgcolor = VAX_COLOR
            board_like[idx].draw(
                screen, image_path="Assets/grass.png", image_size=(imgx, imgy)
            )
        else:
            # bgcolor = CELL_COLOR
            board_like[idx].draw(
                screen, image_path="Assets/grass2.png", image_size=(imgx, imgy)
            )
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
            board_like[idx].draw(screen, image_path=image_path, image_size=PERSON_SIZE)
        elif (  # draw wall depending on how many turnsleft
            GameBoard.States[idx].wall is not None
            and GameBoard.States[idx].wall.turnsLeft >= 0
        ):
            board_like[idx].draw(
                screen,
                image_path=f"Assets/wall3-{min(GameBoard.States[idx].wall.turnsLeft+1, 3)}left.png",
                image_size=(imgx, imgy),
            )
        else:
            # no person, so just draw the cell with the background color
            pass
            # board_like[idx].draw(screen, bgcolor)


def display_cur_move(cur_move: List):
    # Display the current action
    screen.blit(
        font.render("Your move is currently:", True, WHITE),
        (CUR_MOVE_COORDS[0], CUR_MOVE_COORDS[1] + 100),
    )
    screen.blit(
        font.render(f"{cur_move}", True, WHITE),
        (
            CUR_MOVE_COORDS[0],
            CUR_MOVE_COORDS[1] + font.size("Your move is currently:")[1] * 2 + 100,
        ),
    )


def display_telemetry(telemetry: List):
    # display feedback
    screen.blit(
        font.render(telemetry, True, TELEMETRY_RED),
        TELEMETRY_COORDS,
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


def display_turns_left(GameBoard: Board, turns_left):
    if len(turns_left) >= 1:
        for state in turns_left:
            coord = GameBoard.toCoord(state[0])
            screen.blit(
                font.render(f"{state[1]}", True, WHITE),
                (
                    CELL_DIMENSIONS[0] * coord[0] + board_like[0].get_top_left()[0],
                    CELL_DIMENSIONS[1] * coord[1] + board_like[0].get_top_left()[1],
                ),
            )


def direction(coord1: Tuple[int, int], coord2: Tuple[int, int]):
    if coord2[1] > coord1[1]:
        return "moveDown"
    elif coord2[1] < coord1[1]:
        return "moveUp"
    elif coord2[0] > coord1[0]:
        return "moveRight"
    elif coord2[0] < coord1[0]:
        return "moveLeft"


def record_actions(a, d):
    d[a] += 1


def csv_update(file_name, costs, moves):

    header = [
        "cure",
        "vaccinate",
        "wall",
        "movesMade",
        "curesGiven",
        "vaccinationsGiven",
        "wallsCreated",
    ]

    costs.update(moves)
    data = costs

    with open(file_name, "a", newline="") as f:
        w = csv.DictWriter(f, header)

        if f.tell() == 0:
            w.writeheader()

        w.writerow(data)
