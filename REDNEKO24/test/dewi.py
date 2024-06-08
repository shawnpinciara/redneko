


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

def updateBreath():
    breath = getBreath()
    print(breath)
    if (breath > threshold_bottom):
      #lettura valori e manipolazione i bit
      velocity = mapp(breath,threshold_bottom,threshold_top,40,127)
      lastKey = currentKey
      mpr121 = getButtonsState()
      currentKey = (mpr121 & mask_key)>>4
      if (currentKey == 0): currentKey = lastKey
      currentOctave = (mpr121 & mask_octave)>>8 
      #cc = (mpr121 & mask_cc) >>11;
      currentNote = ((octave+octaveArray[currentOctave])*12)+(noteArray[mpr121 & mask_note]+keyArray[currentKey])
      #gestione del fiato vera e propria
      if (breathAttack): #all'inizio della soffiata (va una volta sola)
        breathAttack=false #cambio lo stato cosi non ci entro piu in questo if
        breathRelease = true #accendo la possibilià di entrare nell'if di quando interromperò il fiato
        velocity = mapp(breath,threshold_bottom,threshold_top,40,127)
        noteOn(0,currentNote, velocity)
      else: #durante la soffiata (si ripete continuamente)
        if (currentNote != lastNote):#se il valore letto da sensore è diverso da quello letto in precedenza          
          noteOff(0,lastNote,velocity)    #fai smettere di suonare la nota precedente (perchè siamo in monofonia)
          lastNote = currentNote; #aggiorna valore di nota precedente
          noteOn(0,currentNote, velocity)  #inizia a suonare la nota premuta      
        else:
          channelPressure(0, currentNote, velocity);
    else:
      if (breathRelease==True): #funziona una volta sola solamente quando rilascio il fiato dopo aver soffiato
        breathAttack=True
        breathRelease=False
        noteOff(0,lastNote,velocity) #fai smettere di suonare l'ultima nota suonata
    lastNote = currentNote

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

def getButtonsState() -> int:
    return 0b0111111111111111

def noteOn(ch: int,note: int,vel: int) -> None:
   print("sendNoteOn")

def noteOff(ch: int,note: int,vel: int) -> None:
   print("sendNoteOn")
