## This project is under development and not yet ready for release


# Tiltris: A glove and gesture controlled Tetris! 
Created using a modded PyPortal and a custom LoRa Glove Controller

This project is a gesture-controlled version of the classic game Tetris. It uses an **Adafruit PyPortal** for the game display and interaction, along with a glove equipped with sensors and a LoRa wireless connection to detect hand gestures and send commands to control the game.

## Overview

### PyPortal Tetris Game

The game is built using a grid system on the PyPortal's display. The player can interact with the game by moving, rotating, and dropping Tetrimino blocks. 

- **Game Mechanics:**
  - The game follows standard Tetris rules.
  - As the player clears rows, their score increases and the level advances, which increases the game's speed.
  - The game ends when the blocks reach the top of the grid.
  
- **Game Display:**
  - The game grid is displayed on the PyPortal, including the score and level.
  - Borders and flashing effects are shown to indicate level changes.

### Gesture-Controlled Glove

The glove contains sensors (accelerometer, gyroscope, and magnetometer) to detect hand motions. Using LoRa communication, it sends control signals to the PyPortal based on the player's hand gestures.

- **Glove Controls:**
  - **Move Left/Right:** Tilt hand left or right.
  - **Soft Drop/Hard Drop:** Tilt hand forward or backward.
  - **Rotate Block:** Tilt hand upwards.
  
- **Buttons on the Glove:**
  - **Button 1:** Toggles the game on/off or resets the game.
  - **Button 2:** Starts the game or recalibrates the glove sensors.

### Technologies Used

- **Hardware:**
  - PyPortal for the game interface.
  - Glove with LSM6DSOX (accelerometer/gyro) and LIS3MDL (magnetometer) for motion detection.
  - LoRa communication via RFM9x for wireless data transmission between the glove and PyPortal.

- **Software:**
  - Adafruit CircuitPython libraries for display, motion detection, and LoRa communication.
  - Custom gesture recognition logic for controlling the game with hand movements.

## Getting Started

### Hardware Requirements

- Adafruit PyPortal
- Glove with:
  - LSM6DSOX (accelerometer/gyro)
  - LIS3MDL (magnetometer)
  - RFM9x LoRa module
- PyPortal compatible display
- Buttons for the glove (optional for advanced control)

### Installation

1. Clone this repository to your PyPortal device.
2. Install the required Adafruit CircuitPython libraries (listed in `requirements.txt`).
3. Assemble the glove with the required sensors and LoRa module.
4. Upload the game code to the PyPortal and the gesture control code to the glove.

### How to Play

1. Start the game using **Button 2** on the glove.
2. Control the game using gestures:
   - **Tilt Left/Right**: Move Tetrimino left or right.
   - **Tilt Forward/Backward**: Soft drop or hard drop.
   - **Tilt Upwards**: Rotate the Tetrimino.
3. Keep clearing lines to increase your score and advance levels.

## License

This project is open-source and available under the MIT License.
