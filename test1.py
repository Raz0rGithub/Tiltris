import time
import board
import displayio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
import random

display = board.DISPLAY
display.rotation = 90
main_group = displayio.Group()

GRID_WIDTH = 16
GRID_HEIGHT = 22
BLOCK_SIZE = 20

COLORS = [
    0xf0f000,  # 0 Yellow
    0xf0a000,  # 1 Orange
    0x0000f0,  # 2 Navy
    0x00f000,  # 3 Green
    0xa000f0,  # 4 Purple
    0xf00000,  # 5 Red
    0x00f0f0,  # 6 Cyan
]

TETROMINOS = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # 0 O Yellow
    [(0, 0), (0, 1), (1, 1), (2, 1)],  # 1 L Orange
    [(0, 1), (1, 1), (2, 1), (2, 0)],  # 2 J Navy
    [(0, 1), (1, 0), (1, 1), (2, 0)],  # 3 Z Green
    [(0, 1), (1, 0), (1, 1), (2, 1)],  # 4 T Purple
    [(0, 0), (1, 0), (1, 1), (2, 1)],  # 5 S Red
    [(0, 1), (1, 1), (2, 1), (3, 1)],  # 6 I Cyan
]

# Create the Tetris grid
grid = []
for row in range(GRID_HEIGHT):
    grid_row = []
    for col in range(GRID_WIDTH):
        # Create a rectangle for each block
        block = Rect(
            col * BLOCK_SIZE,  # x pos
            row * BLOCK_SIZE,  # y pos
            BLOCK_SIZE,        # w
            BLOCK_SIZE,        # h
            fill=0x000000
        )
        main_group.append(block)
        grid_row.append(block)
    grid.append(grid_row)

display.root_group = main_group

score_text = label.Label(
    terminalio.FONT,
    text="Score: 0",
    color=0xFFFFFF,
    x=5,
    y=GRID_HEIGHT * BLOCK_SIZE + 10
)
main_group.append(score_text)


# Update color of a block at row, col
def update_block_color(row, col, color_index):
    grid[row][col].fill = COLORS[color_index]

score = 0
level = 0
total_lines_eliminated = 0
game_over = False
tetromino = []
tetromino_color = 0
tetromino_offset = [-2, GRID_WIDTH // 2]


def reset_tetromino():
    global tetromino, tetromino_color, tetromino_offset, game_over
    tetromino = random.choice(TETROMINOS)[:]
    tetromino_index = TETROMINOS.index(tetromino)
    tetromino_color = COLORS[tetromino_index]
    tetromino_offset = [-2, GRID_WIDTH // 2]
    game_over = any(not is_cell_free(row, col)
                    for (row, col) in get_tetromino_coords())


def get_tetromino_coords():
    # Return coords of current tetromino as a list
    return [(row + tetromino_offset[0], col + tetromino_offset[1]) for (row, col) in tetromino]


def apply_tetromino():
    # Add tetromino to tetris board and check for line elims
    global score, total_lines_eliminated, level, grid, tetromino_color
    for (row, col) in get_tetromino_coords():
        grid[row][col].fill = tetromino_color
    time.sleep(2)

    # If any row is full, eliminate
    cleared_rows = []
    for row in range(len(grid)):
        n_filled_tiles = 0
        for tile in grid[row]:
            cur_color = tile.fill
            if cur_color != 0:
                n_filled_tiles += 1
        if n_filled_tiles == GRID_WIDTH:
            cleared_rows.append(row)

    lines_eliminated = len(cleared_rows)
    total_lines_eliminated += lines_eliminated
    time.sleep(2)

    # need to shift down above rows
    if cleared_rows:
        for row_to_clear in reversed(cleared_rows):
            # Shift down all rows above cleared row by one
            for row in range(row_to_clear, 0, -1):
                for col in range(GRID_WIDTH):
                    grid[row][col].fill = grid[row - 1][col].fill
            # Clear top row
            for col in range(GRID_WIDTH):
                grid[0][col].fill = 0x000000

    time.sleep(5)
    reset_tetromino()


def is_cell_free(row, col):
    return row < GRID_HEIGHT and 0 <= col < GRID_WIDTH and (row < 0 or grid[row][col].fill == 0)

def clear_tetromino():
    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = 0
    
def move(d_row, d_col):
    global game_over, tetromino_offset

    # Clear the previous position
    clear_tetromino()

    if all(is_cell_free(row + d_row, col + d_col) for (row, col) in get_tetromino_coords()):
        tetromino_offset = [tetromino_offset[0] + d_row, tetromino_offset[1] + d_col]

    # Update the tetromino at the new position
    for (row, col) in get_tetromino_coords():
        print((row, col))
        if -1 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = tetromino_color

    # If going down by 1 is not free and game not over, set block down. Otherwise, game over
    if d_row == 1 and d_col == 0 and not all(is_cell_free(row + d_row, col + d_col) for (row, col) in get_tetromino_coords()):
        game_over = any(row < 0 for (row, col) in get_tetromino_coords())
        if not game_over:
            apply_tetromino()
        else:
            print('GAME OVER!')

# ---- Application ----

reset_tetromino()
first_move_time = time.monotonic()
last_move_time = time.monotonic()
while (time.monotonic() < first_move_time + 10.0):
    if (time.monotonic() > last_move_time + 1.0):
        last_move_time = time.monotonic()
        print(tetromino_offset)
        move(1, 0)
clear_tetromino()

# display.refresh()