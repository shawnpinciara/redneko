
import board
import digitalio
import time

btn = digitalio.DigitalInOut(board.GP29)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

while True:
    button_state = btn.value
    print(button_state)
    time.sleep(0.1) # sleep for debounce