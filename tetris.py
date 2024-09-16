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


# Check if space is free
def is_free_space(tetromino, x_offset, y_offset):
    for (x, y) in tetromino:
        # Update new position
        new_x = x + x_offset
        new_y = y + y_offset
         
        # Ensure within grid bounds
        if new_y < 0 or new_y >= GRID_HEIGHT or new_x < 0 or new_x >= GRID_WIDTH:
            return False
            
            if  grid[new_x][new_y].fill != 0: #0 for black
                return False
            
    return True


# Ensure random tetrominos
def get_random_block():
    return random.choice(TETROMINOS)
    

# Set up for tetrominos
for i in range(len(grid)):
    tetromino = get_random_block()
    color = random.randint(0, len(COLORS) - 1)
    # Ensure block starts in the middle
    x_offset = 6
    # Prevent overlap
    y_offset = i * 2 
    
    # Check for free and in bounds space
    if is_free_space(tetromino, x_offset, y_offset) and in_bounds(tetromino, x_offset, y_offset):
        print('Good to go!')
        # Place the tetromino
        for (x, y) in tetromino:
            update_block_color( y + y_offset, x + x_offset, color)
    else:
        print(f"Tetromino {i} is out of bounds!")
        
        break

    time.sleep(1)

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
    tetromino_color = random.randint(1, len(COLORS) - 1)
    tetromino_offset = [-2, GRID_WIDTH // 2]
    game_over = any(not is_cell_free(row, col) for (row, col) in get_tetromino_coords())

def get_tetromino_coords():
    # Return coords of current tetromino as a list
    return [(row + tetromino_offset[0], col + tetromino_offset[1]) for (row, col) in tetromino]

def apply_tetromino():
    # Add tetromino to tetris board and check for line elims
    global score, total_lines_eliminated, level, grid
    for (row, col) in get_tetromino_coords():
        grid[row][col].fill = tetromino_color
    
    # If any row is full, eliminate
    new_rows = []
    for row in grid:
        n_filled_tiles = 0
        for tile in row:
            if tile:
                n_filled_tiles += 1
        if n_filled_tiles == GRID_WIDTH:
            new_rows.append(row)

    lines_eliminated = len(grid) - len(new_rows)
    total_lines_eliminated += lines_eliminated
    
    # NEXT: need to shift down above rows

    reset_tetromino()

display.refresh()
