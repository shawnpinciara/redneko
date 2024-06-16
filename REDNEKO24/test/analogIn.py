import analogio
import board
import time

pin = analogio.AnalogIn(board.A3)
while True:
    print(pin.value)
    time.sleep(.1)