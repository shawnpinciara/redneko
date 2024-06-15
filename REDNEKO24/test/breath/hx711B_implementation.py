# https://swharden.com/blog/2022-11-14-hx710b-arduino/

import board # type: ignore
import digitalio # type: ignore

HX710_OUT = digitalio.DigitalInOut(board.GP4)
HX710_OUT.direction = digitalio.Direction.INPUT 

HX710_SCK = digitalio.DigitalInOut(board.GP5)
HX710_SCK.direction = digitalio.Direction.OUTPUT
# void setup() {
#   pinMode(2, INPUT);   // Connect HX710 OUT to Arduino pin 2
#   pinMode(3, OUTPUT);  // Connect HX710 SCK to Arduino pin 3
#   Serial.begin(9600);
# }


while True:
    val = HX710_OUT.value
#   while (digitalRead(2)) {}
    result: int = 0
    for i in range(24):
        HX710_SCK.value = 1
        HX710_SCK.value = 0
        result = result << 1
        if HX710_OUT.value:
            result += 1
    
#   // read 24 bits
#   long result = 0;
#   for (int i = 0; i < 24; i++) {
#     digitalWrite(3, HIGH);
#     digitalWrite(3, LOW);
#     result = result << 1;
#     if (digitalRead(2)) {
#       result++;
#     }
#   }
    result = result ^ 0x800000
#   // get the 2s compliment
#   result = result ^ 0x800000;
    for i in range(3):
        HX710_SCK.value = 1
        HX710_SCK.value = 0
        
#   // pulse the clock line 3 times to start the next pressure reading
#   for (char i = 0; i < 3; i++) {
#     digitalWrite(3, HIGH);
#     digitalWrite(3, LOW);
#   }
    print(result)
#   // display pressure
#   Serial.println(result);
# }