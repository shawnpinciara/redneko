import board # type: ignore
import time

import pwmio # type: ignore

buzzer = pwmio.PWMOut(board.GP16, variable_frequency=True)


DO = 130*2
DO3 = 130*3
SOL = 196*2
OFF = 0
#ON = 2**12 #2^15 default (50% duty cycle)
a = 12
buzzer.duty_cycle = 2**a
time_passaggio = .012
# while True:

    # buzzer.duty_cycle = 2**a
    # time.sleep(1)
    # for slide in range(DO,SOL):
    #     buzzer.frequency = slide
    #     time.sleep(.0008)
    # buzzer.frequency = SOL
    # time.sleep(1)
    # buzzer.duty_cycle = OFF
    # #a-=1
    # print(a)
    # if a==4: a=15

for i in range(1,20000):
        buzzer.frequency = DO
        time.sleep(1/i)
        buzzer.frequency = SOL
        time.sleep(1/i)

#attack:
attack_sleep = .02


buzzer.frequency = DO
buzzer.duty_cycle = OFF
for duty_attack in range(4,12):
    buzzer.duty_cycle = 2**duty_attack
    time.sleep(attack_sleep)

#sustain
time.sleep(1)
#decay
decay_sleep = .03
for duty_decay in range(12,4,-1):
    buzzer.duty_cycle = 2**duty_decay
    time.sleep(decay_sleep)


buzzer.duty_cycle = 2**2
time.sleep(2)
