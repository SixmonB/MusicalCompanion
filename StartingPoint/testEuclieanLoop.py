# Author : Pierre De Loor
# Date : 01/09/2022

import mido
import rtmidi
import time
import random
import EuclideanLoop

ports = mido.get_output_names()
print('output ports : ', ports)
portName = ports[0]
port = mido.open_output(portName)
ports = mido.get_input_names()
print('input ports : ', ports)

msg = mido.Message('reset')
port.send(msg)
msg = mido.Message('program_change', channel=5, program=1) #selectionne un son de piano
port.send(msg)
msg = mido.Message('program_change', channel=1, program=113) #selectionne wod block
port.send(msg)
msg = mido.Message('program_change', channel=2, program=3) #selectionne wod block
port.send(msg)



BPM = 100
note = 100
baseTime = time.time()
nbStep = 16
nbOnset = 5
timeQuantize = 1/BPM*nbStep
euclideanLoop = EuclideanLoop.EuclideanLoop(nbStep,nbOnset,1)
sequences = []
sequences.append(euclideanLoop.getSequence())

euclideanLoop = EuclideanLoop.EuclideanLoop(nbStep,2,0)
sequences.append(euclideanLoop.getSequence())

euclideanLoop = EuclideanLoop.EuclideanLoop(nbStep,3,3)
sequences.append(euclideanLoop.getSequence())

print("les sequences : ", sequences)

step = 0
while(True) : 
    while(time.time()<baseTime+timeQuantize) :
        pass
    msg = mido.Message('note_off', channel=1, note=80)
    port.send(msg)
    msg = mido.Message('note_off', channel=5, note=100)
    port.send(msg)

    
    if (sequences[0][step] == 1) :
        msg = mido.Message('note_on', channel=1, note=80, velocity=80)
        port.send(msg)

    if (sequences[1][step] == 1) :
        msg = mido.Message('note_on', channel=5, note=80, velocity=80)
        port.send(msg)

    if (sequences[2][step] == 1) :
        msg = mido.Message('note_on', channel=2, note=100, velocity=80)
        port.send(msg)



    step = step + 1
    if step >= nbStep :
        step = 0   
    baseTime = baseTime + timeQuantize
  
    


'''
msg = mido.Message('note_on', channel=5, note=94, velocity=127)
port.send(msg)
time.sleep(2)
msg = mido.Message('program_change', channel=5, program=50)
port.send(msg)
msg = mido.Message('note_on', channel=5, note=100, velocity=100, time=1)
port.send(msg)
time.sleep(1)
msg = mido.Message('note_on', channel=5, note=94, velocity=100, time=1)
port.send(msg)
time.sleep(2)

'''


