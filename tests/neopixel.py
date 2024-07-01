import board # type: ignore
import neopixel
import time

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False) # type: ignore


while True:
    pixels[0] = (10, 100, 20)
    pixels.show() # type: ignore
    time.sleep(1)
    pixels[0] = (255, 0, 0)
    pixels.show() # type: ignore
    time.sleep(1)

