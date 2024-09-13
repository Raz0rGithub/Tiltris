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
    0x808080,  # 0 Gray
    0x90EE90,  # 1 LightGreen
    0xFFB6C1,  # 2 Pink
    0x0000FF,  # 3 Blue
    0xFFA500,  # 4 Orange
    0x800080,  # 5 Purple
]

TETROMINOS = [
    [(0, 0), (0, 1), (1, 0), (1,1)], # 0 O
    [(0, 0), (0, 1), (1, 1), (2,1)], # 1 L
    [(0, 1), (1, 1), (2, 1), (2,0)], # 2 J 
    [(0, 1), (1, 0), (1, 1), (2,0)], # 3 Z
    [(0, 1), (1, 0), (1, 1), (2,1)], # 4 T
    [(0, 0), (1, 0), (1, 1), (2,1)], # 5 S
    [(0, 1), (1, 1), (2, 1), (3,1)], # 6 I
]

# Create the Tetris grid (8x8 grid of blocks)
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


# Check to see if block is in bounds
def in_bounds(tetromino, x_offset, y_offset):
    for (x, y) in tetromino:
        # Check for horizontal bounds
        if x_offset < 0 or x_offset >= GRID_WIDTH - 1:
            return False
        # Check for vertical bounds
        if y_offset < 0 or y_offset >= GRID_HEIGHT - 1:
            return False
    return True


# Ensure random tetrominos
def get_random_block():
    return random.choice(TETROMINOS)

# Place tetrominos on the grid
for i in range(len(grid)):
    tetromino = get_random_block()
    color = random.randint(0, len(COLORS) - 1)
    # Ensure block starts in the middle
    x_offset = 6
    # Prevent overlap
    y_offset = i * 2 

    # Check if the tetromino is within bounds before drawing
    if in_bounds(tetromino, x_offset, y_offset):
        for (x, y) in tetromino:
            update_block_color( y + y_offset, x + x_offset, color)
    else:
        print(f"Tetromino {i} is out of bounds!")

    time.sleep(1)

display.refresh()
