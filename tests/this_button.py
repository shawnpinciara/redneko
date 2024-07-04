import thisbutton as tb
import board
# https://github.com/elliotmade/This-Button

myButton = tb.thisButton(board.GP5, True)

def boop():
    print("Boop")

myButton.assignClick(boop)
while True:
    myButton.tick()