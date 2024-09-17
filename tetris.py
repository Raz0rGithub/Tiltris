import time
import board
import displayio
import digitalio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
import random
from adafruit_debouncer import Debouncer
pyportal = PyPortal()

display = board.DISPLAY
display.rotation = 90
main_group = displayio.Group()

GRID_WIDTH = 14
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
            col * BLOCK_SIZE + 20,  # x pos
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
    text='Score: 0',
    color=0xFFFFFF,
    x=5,
    y=GRID_HEIGHT * BLOCK_SIZE + 10
)

level_text = label.Label(
    terminalio.FONT,
    text='Level: 1',
    color=0xFFFFFF,
    x=GRID_WIDTH * BLOCK_SIZE - 15,
    y=GRID_HEIGHT * BLOCK_SIZE + 10
)

# Left border
main_group.append(Rect(
    0,  # x pos
    0,  # y pos
    BLOCK_SIZE,  # w
    GRID_HEIGHT * BLOCK_SIZE,  # h
    fill=0xF4C2C2)  # baby pink
)

# Right border
main_group.append(Rect(
    GRID_WIDTH + 286,  # x pos
    0,  # y pos
    BLOCK_SIZE,  # w
    GRID_HEIGHT * BLOCK_SIZE,  # h
    fill=0xF4C2C2)  # baby pink
)

# Bottom border
main_group.append(Rect(
    0,  # x pos
    22 * BLOCK_SIZE,  # y pos
    GRID_WIDTH * BLOCK_SIZE + 40,        # w
    BLOCK_SIZE,        # h
    fill=0xF4C2C2)  # baby pink
)

main_group.append(score_text)
main_group.append(level_text)

# Update score and level
def update_score(new_score):
    global score
    score = new_score
    score_text.text = f'Score: {score}'

def update_level(new_level):
    global level
    level = new_level
    level_text.text = f'Level: {level}'

# Update color of a block at row, col
def update_block_color(row, col, color_index):
    grid[row][col].fill = COLORS[color_index]


score = 0
level = 0
total_lines_eliminated = 0
game_over = False
tetromino = []
tetromino_color = 0
tetromino_offset = [-1, GRID_WIDTH // 2 - 2]


def reset_tetromino():
    global tetromino, tetromino_color, tetromino_offset, game_over
    tetromino = random.choice(TETROMINOS)[:]
    tetromino_index = TETROMINOS.index(tetromino)
    tetromino_color = COLORS[tetromino_index]
    tetromino_offset = [-1, GRID_WIDTH // 2 - 2]
    game_over = any(not is_cell_free(row, col)
                    for (row, col) in get_tetromino_coords())


def get_tetromino_coords():
    # Return coords of current tetromino as a list
    return [(row + tetromino_offset[0], col + tetromino_offset[1] + 1) for (row, col) in tetromino]


def apply_tetromino():
    # Add tetromino to tetris board and check for line elims
    global score, total_lines_eliminated, level, grid, tetromino_color, score
    for (row, col) in get_tetromino_coords():
        grid[row][col].fill = tetromino_color
    time.sleep(1)

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

    print(cleared_rows)

    lines_eliminated = len(cleared_rows)
    total_lines_eliminated += lines_eliminated
    update_score(score + lines_eliminated)
    
    # Check level update
    new_level = total_lines_eliminated // 10 + 1
    if new_level > level:
        print("Next level")
        update_level(new_level)

    # need to shift down above rows
    if cleared_rows:
        for row_to_clear in cleared_rows:
            # Shift down all rows above cleared row by one
            for row in range(row_to_clear, 0, -1):
                for col in range(GRID_WIDTH):
                    grid[row][col].fill = grid[row - 1][col].fill
            # Clear top row
            for col in range(GRID_WIDTH):
                grid[0][col].fill = 0x000000

    reset_tetromino()


def is_cell_free(row, col):
    return row < GRID_HEIGHT and 0 <= col < GRID_WIDTH and (row < 0 or grid[row][col].fill == 0)


def clear_tetromino():
    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = 0


def move_right():
    move(0, 1)


def move_left():
    move(0, -1)

def drop():
    global game_over, tetromino_offset
    clear_tetromino()
    not_applied = True

    while not_applied:
                
        # If right below is free, update offset
        if all(is_cell_free(row + 1, col) for (row, col) in get_tetromino_coords()):
            tetromino_offset = [tetromino_offset[0] + 1, tetromino_offset[1]]
        # If not free, apply directly
        else:
            game_over = any(row < 0 for (row, col) in get_tetromino_coords())
            if not game_over:
                apply_tetromino()
                not_applied = False
                
    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = tetromino_color

def move(d_row, d_col):
    global game_over, tetromino_offset

    # Clear prev position
    clear_tetromino()

    # If free, move
    if all(is_cell_free(row + d_row, col + d_col) for (row, col) in get_tetromino_coords()):
        tetromino_offset = [tetromino_offset[0] +
                            d_row, tetromino_offset[1] + d_col]
    elif d_row == 1 and d_col == 0:
        game_over = any(row < 0 for (row, col) in get_tetromino_coords())
        if not game_over:
            apply_tetromino()

    # Update the tetromino at the new position
    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = tetromino_color


def rotate():
    global game_over, tetromino, tetromino_offset
    if game_over:
        return
    clear_tetromino()

    ys = [row for (row, col) in tetromino]
    xs = [col for (row, col) in tetromino]
    size = max(max(ys) - min(ys), max(xs) - min(xs))
    rotated_tetromino = [(col, size - row) for (row, col) in tetromino]
    wallkick_offset = tetromino_offset[:]
    tetromino_coord = [(row + wallkick_offset[0], col + wallkick_offset[1])
                       for (row, col) in rotated_tetromino]

    min_x = min(col for row, col in tetromino_coord)
    max_x = max(col for row, col in tetromino_coord)
    max_y = max(row for row, col in tetromino_coord)
    wallkick_offset[1] -= min(0, min_x)
    wallkick_offset[1] += min(0, GRID_WIDTH - (1 + max_x))
    wallkick_offset[0] += min(0, GRID_HEIGHT - (1 + max_y))

    tetromino_coord = [(row + wallkick_offset[0], col + wallkick_offset[1])
                       for (row, col) in rotated_tetromino]
    if all(is_cell_free(row, col) for (row, col) in tetromino_coord):
        tetromino, tetromino_offset = rotated_tetromino, wallkick_offset

    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = tetromino_color


# ---- Buttons ----
pin1 = digitalio.DigitalInOut(board.D3)
pin1.direction = digitalio.Direction.INPUT
pin1.pull = digitalio.Pull.UP
switch1 = Debouncer(pin1)

pin2 = digitalio.DigitalInOut(board.D4)
pin2.direction = digitalio.Direction.INPUT
pin2.pull = digitalio.Pull.UP
switch2 = Debouncer(pin2)

S1Timer = 0
S2Timer = 0

# ---- Application ----

for row in range(10, GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        if col != 8 and col != 9:
            grid[row][col].fill = 0xf0f000

reset_tetromino()
first_move_time = time.monotonic()
last_move_time = time.monotonic()
pyportal.peripherals.play_file("Tetris.wav", wait_to_finish=False)

while (not game_over):
    if (time.monotonic() > last_move_time + 0.35):
        last_move_time = time.monotonic()
        move(1, 0)
        
    switch1.update()
    if switch1.fell:
        S1Timer = time.monotonic()
    if switch1.rose:
        if time.monotonic() > S1Timer + 0.3:
            move_left()
        else:
            move_right()

    switch2.update()
    if switch2.fell:
        S2Timer = time.monotonic()
    if switch2.rose:
        if time.monotonic() > S2Timer + 0.3:
            drop()
        else:
            rotate()

print('game over!')