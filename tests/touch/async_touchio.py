import asyncio
import board # type: ignore
import touchio # type: ignore
from adafruit_debouncer import Debouncer, Button # type: ignore

#From here:
#https://diyelectromusic.com/2023/06/12/raspberry-pi-pico-capacitive-touch/

THRESHOLD = 1000
# t1 = touchio.TouchIn(board.GP21); t1.threshold = t1.raw_value + THRESHOLD; btn1 = Button(t1, value_when_pressed=True) # type: ignore
t2 = touchio.TouchIn(board.GP20); t2.threshold = t2.raw_value + THRESHOLD; btn2 = Button(t2, value_when_pressed=True)   # type: ignore
t3 = touchio.TouchIn(board.GP19); t3.threshold = t3.raw_value + THRESHOLD; btn3 = Button(t3, value_when_pressed=True)   # type: ignore
t4 = touchio.TouchIn(board.GP18); t4.threshold = t4.raw_value + THRESHOLD; btn4 = Button(t4, value_when_pressed=True)   # type: ignore

class Buttons:
    def __init__(self,arr: list[bool]) -> None:
        self.arrPresent = arr
        self.arrPast = arr
        self.note_byte = 0b0000000000000000
    def setButton(self,i,state):
        self.arrPast = self.arrPresent
        self.arrPresent[i] = state
        if state: #push
            self.note_byte = self.note_byte  | state<<i #note on get shifted so representation of all buttons is 0bXXXX
        else: #release
            self.note_byte = self.note_byte  & ~(1<<i)
    def getButtonsArr(self) -> list[bool]:
        return self.arrPresent
    def getButtonsState(self) -> int:
        return self.note_byte
    def getArrs(self) ->list[list]:
        return [self.arrPresent,self.arrPast]

buttons = Buttons([False,False,False,False])

async def handleBtnPressing(sleep_time,btn, n_string,i):
    while True:
        btn.update()
        if btn.rose:
            buttons.setButton(i,True)
        if btn.fell:
            buttons.setButton(i,False)
        await asyncio.sleep(sleep_time)

async def getBTNSS(sleep_time):
   global buttons
   while True:
      print(buttons.getButtonsState())
      await asyncio.sleep(sleep_time)


async def main():
    # asyncio.create_task(handleBtnPressing(0.005,btn1,"btn1",0))
    asyncio.create_task(handleBtnPressing(0.005,btn2,"btn2",1))
    asyncio.create_task(handleBtnPressing(0.005,btn3,"btn3",2))
    asyncio.create_task(handleBtnPressing(0.005,btn4,"btn4",3))

    
    asyncio.create_task(getBTNSS(0.1))
    while True: #if not the program end
       await asyncio.sleep(1)

asyncio.run(main())