import board
import digitalio
import time


#buzzer GP2
#encoder: GP3,GP4 GP5(button)
#Button: GP29
#PCM5102:
# LCK - 28
# DIN - 27
# BCK - 26

import thisbutton as tb
# https://github.com/elliotmade/This-Button

myButton = tb.thisButton(board.GP5, True)

def btnPushed():
    print("Boop")

myButton.assignClick(btnPushed)
while True:
    myButton.tick()