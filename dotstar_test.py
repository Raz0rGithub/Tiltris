import board
import adafruit_dotstar as dotstar
import time

dots = dotstar.DotStar(board.SCK, board.MOSI, 2, brightness=0.1, pixel_order = "RGB")
#print("turning all off")
#dots.fill((0,0,0))

#time.sleep(1)
print("turning first on")
while True:
    dots[0] = (0, 100, 0)
    dots.show()
    print("running.")
    time.sleep(1)