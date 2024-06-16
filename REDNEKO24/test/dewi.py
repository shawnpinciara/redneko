import asyncio
import board # type: ignore
import touchio # type: ignore
from adafruit_debouncer import Debouncer, Button # type: ignore
import time
import board # type: ignore
import digitalio # type: ignore
import audiomixer# type: ignore
import synthio # type: ignore
# for PWM audio with an RC filter
import audiopwmio # type: ignore
import analogio # type: ignore
from adafruit_simplemath import map_range #type: ignore


mixer = audiomixer.Mixer(channel_count=1, sample_rate=22050, buffer_size=2048)
#From here:
#https://diyelectromusic.com/2023/06/12/raspberry-pi-pico-capacitive-touch/

THRESHOLD = 1000
t1 = touchio.TouchIn(board.GP21); t1.threshold = t1.raw_value + THRESHOLD; btn1 = Button(t1, value_when_pressed=True) # type: ignore
t2 = touchio.TouchIn(board.GP20); t2.threshold = t2.raw_value + THRESHOLD; btn2 = Button(t2, value_when_pressed=True)# type: ignore
t3 = touchio.TouchIn(board.GP19); t3.threshold = t3.raw_value + THRESHOLD; btn3 = Button(t3, value_when_pressed=True)# type: ignore
t4 = touchio.TouchIn(board.GP18); t4.threshold = t4.raw_value + THRESHOLD; btn4 = Button(t4, value_when_pressed=True)# type: ignore

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

def mapp(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def getBreath() -> int:
    return 9

def noteOn(ch: int,note: int,vel: int) -> None:
   synth.release_all_then_press(note)
  #  print("Note on: "+str(note))

def noteOff(ch: int,note: int,vel: int) -> None:
   synth.release(note)
  #  print("Note off: "+str(note))

# def channelPressure(ch: int,note: int,vel: int) -> None:
#   #  synth.release_all_then_press(note)
#   print("channelPressure: " +str(note))



async def updateBreath(sleep_time):
    #binary no midi note map es: binary:0001 -> decimal: 1 -->note: D (1 in midi value)
    noteArray: list[int] = [0,2,11,4,12,9,5,7,1,3,12,5,16,10,6,8]
    keyArray: list =  [0,2,11,4,0,9,5,7,1,3,0,5,16,10,6,8]
    octaveArray: list = [0,1,-1,0,-2,-1,-3,0,0,0,0,0,0,0,0,0] #missing button is X000, change octave is 0X00, -1 (X) e +1 (Y) octave is 00XY
    octave: int = 5
    velocity: int = 60
    threshold_bottom: int = 9736143
    threshold_top: int = 14000000
    breath: int = 0 #16689194 base, 8595203 piano,10305762 forte (breath sensor data)
    mask_key: int = 0b0000000011110000
    mask_note: int = 0b0000000000001111
    mask_octave: int = 0b0000111100000000
    mask_cc: int = 0b0000100000000000
    currentNote: int = 0
    lastNote: int = 0b0111111111111111
    sendNote: int = 0
    currentKey: int = 0
    lastKey: int = 1
    currentOctave: int = 0
    lastOctave: int = 0
    mpr121: int = 0
    breathAttack: bool = True
    breathRelease: bool = False
    cc: int = 0
    cc_debounce: int = 1
    bank: int = 0
    global buttons

    while True:
      # breath = getBreath()
      breath = 9936143
      #print(breath)
      if (breath > threshold_bottom):
        #lettura valori e manipolazione i bit
        velocity = int(mapp(breath,threshold_bottom,threshold_top,40,127))
        lastKey = currentKey
        mpr121 = buttons.getButtonsState()
        print(mpr121)
        currentKey = (mpr121 & mask_key)>>4
        if (currentKey == 0): currentKey = lastKey
        currentOctave = (mpr121 & mask_octave)>>8 
        #cc = (mpr121 & mask_cc) >>11;
        currentNote = ((octave+octaveArray[currentOctave])*12)+(noteArray[mpr121 & mask_note]+keyArray[currentKey])
        #gestione del fiato vera e propria
        if (breathAttack): #all'inizio della soffiata (va una volta sola)
          breathAttack=False #cambio lo stato cosi non ci entro piu in questo if
          breathRelease = True #accendo la possibilià di entrare nell'if di quando interromperò il fiato
          velocity = int(mapp(breath,threshold_bottom,threshold_top,40,127))
          noteOn(0,currentNote, int(velocity))
        else: #durante la soffiata (si ripete continuamente)
          if (currentNote != lastNote):#se il valore letto da sensore è diverso da quello letto in precedenza          
            noteOff(0,lastNote,velocity)    #fai smettere di suonare la nota precedente (perchè siamo in monofonia)
            lastNote = currentNote #aggiorna valore di nota precedente
            noteOn(0,currentNote, velocity)  #inizia a suonare la nota premuta      
          # else:
          #   channelPressure(0, currentNote, velocity)
      else:
        if (breathRelease==True): #funziona una volta sola solamente quando rilascio il fiato dopo aver soffiato
          breathAttack=True
          breathRelease=False
          noteOff(0,lastNote,int(velocity)) #fai smettere di suonare l'ultima nota suonata
      lastNote = currentNote
      await asyncio.sleep(sleep_time)

async def handleBtnPressing(sleep_time,btn, n_string,i):
    global buttons
    while True:
        btn.update()
        if btn.rose:
            buttons.setButton(i,1)
        if btn.fell:
            buttons.setButton(i,0)
        await asyncio.sleep(sleep_time)

async def handlePotChange(sleep_time):
   pot = analogio.AnalogIn(board.A3)
   global mixer
   while True:
      mixer.voice[0].level = map_range(pot,400,1024,0,2)
      await asyncio.sleep(sleep_time)


async def playSynth(sleep_time):
    #SYNTH
    global mixer
    audio = audiopwmio.PWMAudioOut(board.GP1)
    amp_env_slow = synthio.Envelope(attack_time=0.01,sustain_level=1.0,release_time=0.1)
    synth = synthio.Synthesizer(channel_count=1, sample_rate=22050,envelope=amp_env_slow)
    synth.envelope = amp_env_slow
    audio.play(mixer)
    mixer.voice[0].play(synth)
    mixer.voice[0].level = 1
    #     #mixer.voice[0].level = (mixer.voice[0].level - 0.1) % 0.4  # reduce volume each pass
    noteArray: list[int] = [0,2,11,4,12,9,5,7,1,3,12,5,16,10,6,8]
    global buttons
    while True:
       synth.release_all_then_press(noteArray[buttons.getButtonsState()]+(12*5))
    #    synth.press(60)
       await asyncio.sleep(sleep_time)


async def main():
    asyncio.create_task(handleBtnPressing(0.005,btn1,"btn1",0))
    asyncio.create_task(handleBtnPressing(0.005,btn2,"btn2",1))
    asyncio.create_task(handleBtnPressing(0.005,btn3,"btn3",2))
    asyncio.create_task(handleBtnPressing(0.005,btn4,"btn4",3))
    # asyncio.create_task(updateBreath(0.05))
    asyncio.create_task(playSynth(0.01))
    while True: #if not the program end
       #print(buttons.getButtonsState())
       await asyncio.sleep(1)

asyncio.run(main())