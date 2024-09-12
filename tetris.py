import time
import board
import displayio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio

display = board.DISPLAY
display.rotation = 90
main_group = displayio.Group()

GRID_WIDTH = 8
GRID_HEIGHT = 11
BLOCK_SIZE = 40

COLORS = [
    0x000000,  # 0 Black (empty)
    0x808080,  # 1 Gray
    0x90EE90,  # 2 LightGreen
    0xFFB6C1,  # 3 Pink
    0x0000FF,  # 4 Blue
    0xFFA500,  # 5 Orange
    0x800080,  # 6 Purple
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
            fill=COLORS[0]     # init black
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
    
# testing
# time.sleep(2)
# update_block_color(0, 0, 1)
# time.sleep(2)
# update_block_color(1, 7, 2)
# time.sleep(2)
# update_block_color(10, 7, 4)
# time.sleep(2)
# update_block_color(10, 1, 6)


display.refresh()