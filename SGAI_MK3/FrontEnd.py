from typing import List, Tuple
import pygame
from constants import *
from Board import Board


class FrontEnd:
    def __init__(
        self,
        columns: int,
        rows: int,
    ):
        self.columns = columns
        self.rows = rows
        self.init_window()

    def init_window(self):
        """
        Initialize the window and the font that will be used in the game
        """
        pygame.init()
        self.screen = pygame.display.set_mode(GAME_WINDOW_DIMENSIONS)
        pygame.display.set_caption("Outbreak!")
        pygame.font.init()
        self.font = pygame.font.SysFont("Impact", 30)
        self.screen.fill(BACKGROUND)

    def get_action(self, pixel_x: int, pixel_y: int):
        """
        Get the action that the click represents.
        If the click was on the heal button, returns "heal"
        Else, returns the board coordinates of the click (board_x, board_y) if valid
        Return None otherwise
        """
        # Check if the user clicked on the "heal" icon, return "heal" if so
        heal_check = (
            pixel_x >= CURE_COORDS[0]
            and pixel_x <= CURE_COORDS[0] + CURE_DIMS[0]
            and pixel_y >= CURE_COORDS[1]
            and pixel_y <= CURE_COORDS[1] + CURE_DIMS[1]
        )
        reset_move_check = (
            pixel_x >= RESET_MOVE_COORDS[0]
            and pixel_x <= RESET_MOVE_COORDS[0] + RESET_MOVE_DIMS[0]
            and pixel_y >= RESET_MOVE_COORDS[1]
            and pixel_y <= RESET_MOVE_COORDS[1] + RESET_MOVE_DIMS[1]
        )
        board_x = int((pixel_x - BORDER) / CELL_DIMENSIONS[0])
        board_y = int((pixel_y - BORDER) / CELL_DIMENSIONS[1])
        move_check = (
            board_x >= 0
            and board_x < self.columns
            and board_y >= 0
            and board_y < self.rows
        )

        if heal_check:
            return "heal"
        elif reset_move_check:
            return "reset move"
        elif move_check:
            return board_x, board_y
        return None

    def handle_user_input(self):
        """
        Returns False if the user quit (pressed the close button), else returns the requested actions
        """
        ret = []
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = self.get_action(x, y)
                ret.append(action)
            if event.type == pygame.QUIT:
                return [False]
        return ret

    def render(self, GameBoard: Board, cur_moves: List):
        """
        Draw the screen
        """
        self.screen.fill(BACKGROUND)
        self.build_grid()  # Draw the grid
        # Draw the heal icon
        self.display_image("Assets/cure.jpeg", CURE_DIMS, CURE_COORDS)
        self.display_people(GameBoard)
        self.display_reset_move_button()
        self.display_cur_moves(cur_moves)

        pygame.display.update()

    def display_cur_moves(self, cur_moves: List):
        # Display the current action
        self.screen.blit(
            self.font.render("Your move is currently:", True, WHITE),
            (800, 400),
        )
        self.screen.blit(self.font.render(f"{cur_moves}", True, WHITE), (800, 450))

    def display_reset_move_button(self):
        """
        Display the button that allows for resetting the user's move
        """
        rect = pygame.Rect(
            RESET_MOVE_COORDS[0],
            RESET_MOVE_COORDS[1],
            RESET_MOVE_DIMS[0],
            RESET_MOVE_DIMS[1],
        )
        pygame.draw.rect(self.screen, BLACK, rect)
        self.screen.blit(
            self.font.render("Reset move?", True, WHITE), RESET_MOVE_COORDS
        )

    def display_image(
        self,
        itemStr: str,
        dimensions: Tuple[int, int],
        position: Tuple[int, int],
    ):
        """
        Draw an image on the screen at the indicated position.
        """
        v = pygame.image.load(itemStr).convert_alpha()
        v = pygame.transform.scale(v, dimensions)
        self.screen.blit(v, position)

    def build_grid(self):
        """
        Draw the grid on the screen.
        """
        grid_width = self.columns * CELL_DIMENSIONS[0]
        grid_height = self.rows * CELL_DIMENSIONS[1]

        # left
        pygame.draw.rect(
            self.screen,
            BLACK,
            [
                BORDER - LINE_WIDTH,
                BORDER - LINE_WIDTH,
                LINE_WIDTH,
                grid_height + (2 * LINE_WIDTH),
            ],
        )
        # right
        pygame.draw.rect(
            self.screen,
            BLACK,
            [
                BORDER + grid_width,
                BORDER - LINE_WIDTH,
                LINE_WIDTH,
                grid_height + (2 * LINE_WIDTH),
            ],
        )
        # bottom
        pygame.draw.rect(
            self.screen,
            BLACK,
            [
                BORDER - LINE_WIDTH,
                BORDER + grid_height,
                grid_width + (2 * LINE_WIDTH),
                LINE_WIDTH,
            ],
        )
        # top
        pygame.draw.rect(
            self.screen,
            BLACK,
            [
                BORDER - LINE_WIDTH,
                BORDER - LINE_WIDTH,
                grid_width + (2 * LINE_WIDTH),
                LINE_WIDTH,
            ],
        )
        # Fill the inside wioth the cell color
        pygame.draw.rect(
            self.screen,
            CELL_COLOR,
            [
                BORDER,
                BORDER,
                grid_width,
                grid_height,
            ],
        )

        # Draw the vertical lines
        i = BORDER + CELL_DIMENSIONS[0]
        while i < BORDER + grid_width:
            pygame.draw.rect(self.screen, BLACK, [i, BORDER, LINE_WIDTH, grid_height])
            i += CELL_DIMENSIONS[0]
        # Draw the horizontal lines
        i = BORDER + CELL_DIMENSIONS[1]
        while i < BORDER + grid_height:
            pygame.draw.rect(self.screen, BLACK, [BORDER, i, grid_width, LINE_WIDTH])
            i += CELL_DIMENSIONS[1]

    def display_people(self, GameBoard: Board):
        """
        Draw the people (government, vaccinated, and zombies) on the grid.
        """
        for x in range(len(GameBoard.States)):
            if GameBoard.States[x].person != None:
                p = GameBoard.States[x].person
                char = "Assets/" + IMAGE_ASSETS[0]
                if p.isVaccinated:
                    char = "Assets/" + IMAGE_ASSETS[1]
                elif p.isZombie:
                    char = "Assets/" + IMAGE_ASSETS[2]
                coords = (
                    int(x % GameBoard.rows) * CELL_DIMENSIONS[0] + BORDER + 35,
                    int(x / GameBoard.columns) * CELL_DIMENSIONS[1] + BORDER + 20,
                )
                self.display_image(char, (35, 60), coords)

    def display_win_screen(self):
        """
        A blocking function that displays the win screen
        """
        self.screen.fill(BACKGROUND)
        self.screen.blit(
            self.font.render("You win!", True, WHITE),
            (500, 400),
        )
        pygame.display.update()

        # catch quit event
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

    def display_lose_screen(self):
        """
        A blocking function that displays the lose screen
        """
        self.screen.fill(BACKGROUND)
        self.screen.blit(
            self.font.render("You lose!", True, WHITE),
            (500, 400),
        )
        pygame.display.update()

        # catch quit event
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
