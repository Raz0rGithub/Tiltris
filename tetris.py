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
import adafruit_rfm9x
import busio

# pyportal = PyPortal()

display = board.DISPLAY
display.rotation = 90
main_group = displayio.Group()

# LORA
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
reset = digitalio.DigitalInOut(board.D4)
rfm9x = adafruit_rfm9x.RFM9x(
    spi=spi, cs=cs, reset=reset, frequency=915.0, baudrate=1000000)

GRID_WIDTH = 12
GRID_HEIGHT = 20
BLOCK_SIZE = 23

score = 0
level = 1
base_drop_delay = 0.5
drop_delay = 0.5
total_lines_eliminated = 0
game_over = False
tetromino = []
tetromino_color = 0
tetromino_offset = [-1, GRID_WIDTH // 2 - 2]

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
    x=GRID_WIDTH * BLOCK_SIZE - 20,
    y=GRID_HEIGHT * BLOCK_SIZE + 10
)

# Rect 1 (Left)
left_border = Rect(
    0,  # x pos
    0,  # y pos
    BLOCK_SIZE,  # w
    GRID_HEIGHT * BLOCK_SIZE,  # h
    fill=0xF4C2C2  # baby pink
)
main_group.append(left_border)

# Rect 2 (Right)
right_border = Rect(
    (GRID_WIDTH + 1) * BLOCK_SIZE - 3,  # x pos
    0,  # y pos
    BLOCK_SIZE + 3,  # w
    GRID_HEIGHT * BLOCK_SIZE,  # h
    fill=0xF4C2C2  # baby pink
)
main_group.append(right_border)

# Rect 3 (Bottom)
bottom_border = Rect(
    0,  # x pos
    GRID_HEIGHT * BLOCK_SIZE,  # y pos
    (GRID_WIDTH + 2) * BLOCK_SIZE,  # w
    BLOCK_SIZE,  # h
    fill=0xF4C2C2  # baby pink
)
main_group.append(bottom_border)

main_group.append(score_text)
main_group.append(level_text)


# Update score and level
def update_score(new_score):
    global score
    score = new_score
    score_text.text = f'Score: {score}'


def update_level(new_level):
    global level, base_drop_delay
    level = new_level
    level_text.text = f'Level: {level}'
    base_drop_delay = 0.5 * pow(0.75, level - 1)
    start_flashing()


def start_flashing():
    border_rects = [
        left_border,  # Left border
        right_border,  # Right border
        bottom_border   # Bottom border
    ]

    # Flash borders 5 times
    for _ in range(5):
        for rect in border_rects:
            rect.fill = 0xFFFFFF  # White
            rect.fill = 0x808080  # Gray
        display.refresh()
        time.sleep(0.1)

        # Set borders back to OG color
        for rect in border_rects:
            rect.fill = 0xF4C2C2
        display.refresh()
        time.sleep(0.1)


# Update color of a block at row, col
def update_block_color(row, col, color_index):
    grid[row][col].fill = COLORS[color_index]


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

    # Update lines and score
    lines_eliminated = len(cleared_rows)
    total_lines_eliminated += lines_eliminated
    update_score(score + lines_eliminated)

    # Check level update
    new_level = total_lines_eliminated // 10 + 1
    if new_level > level:
        print("Next level")
        update_level(new_level)

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


# def soft_drop():
    # Empty


def hard_drop():
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
    wallkick_offset[1] += min(0, GRID_WIDTH - (2 + max_x))
    wallkick_offset[0] += min(0, GRID_HEIGHT - (1 + max_y))

    tetromino_coord = [(row + wallkick_offset[0], col + wallkick_offset[1])
                       for (row, col) in rotated_tetromino]
    if all(is_cell_free(row, col) for (row, col) in tetromino_coord):
        tetromino, tetromino_offset = rotated_tetromino, wallkick_offset

    for (row, col) in get_tetromino_coords():
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            grid[row][col].fill = tetromino_color


def game_over_screen():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            # Make the screen all black
            grid[row][col].fill = 0x000000

    # Show "Game Over!" message
    game_over_text = label.Label(
        terminalio.FONT,
        text='Game Over!',
        color=0xFF0000,  # Red
        x=(GRID_WIDTH * BLOCK_SIZE - 15) // 2,
        y=(GRID_HEIGHT * BLOCK_SIZE) // 2
    )
    main_group.append(game_over_text)

    # Show final score
    final_score_text = label.Label(
        terminalio.FONT,
        text=f'Final Score: {score}',
        color=0xFFFFFF,  # Red
        x=(GRID_WIDTH * BLOCK_SIZE - 50) // 2,
        y=(GRID_HEIGHT * BLOCK_SIZE) // 2 + 20
    )
    main_group.append(final_score_text)

    # Show final level
    final_level_text = label.Label(
        terminalio.FONT,
        text=f'Final Level: {level}',
        color=0xFFFFFF,  # Red
        x=(GRID_WIDTH * BLOCK_SIZE - 50) // 2,
        y=(GRID_HEIGHT * BLOCK_SIZE) // 2 + 40
    )
    main_group.append(final_level_text)


# ---- Application ----

for row in range(19, GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        if col != 8 and col != 9:
            grid[row][col].fill = 0xf0f000

reset_tetromino()
last_move_time = time.monotonic()
# pyportal.peripherals.play_file("Tetris.wav", wait_to_finish=False)
print("listening...")
on = True

while not game_over:
    packet = rfm9x.receive(timeout=0.4)
    packet_text = ""
    if not packet is None:
        packet_text = str(packet, 'ascii')
        print("Received: {0}".format(packet_text))

    if packet_text == "on_off()":
        on = not on

    # elif packet_text == "reset()":
#         game_over_screen()
#         time.sleep(1)
#         return

    if on:
        if packet_text == "move_left()":
            move_left()
            drop_delay = base_drop_delay

        elif packet_text == "move_right()":
            move_right()
            drop_delay = base_drop_delay

        elif packet_text == "soft_drop()":
            drop_delay = base_drop_delay/4

        elif packet_text == "hard_drop()":
            hard_drop()
            drop_delay = base_drop_delay

        elif packet_text == "rotation()":
            rotate()
            drop_delay = base_drop_delay

        if time.monotonic() > last_move_time + drop_delay:
            print(drop_delay)
            last_move_time = time.monotonic()
            move(1, 0)

game_over_screen()

time.sleep(100)

print('game over!')