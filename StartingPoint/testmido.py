# Author : Pierre De Loor
# Date : 01/09/2022

import mido
import time
import random
import sys
sys.path.append('C:/Users/sbsim/Documents/ENIB Materias/PRI/musicalcompanion')
from Graphs import Graph
# OPEN OUTPUT PORT

ports_output = mido.get_output_names()
print('output ports: ', ports_output)
portName_output = ports_output[2]
port_output = mido.open_output(portName_output)
print('output port opened : ', port_output)

# OPEN INPUT PORT

ports_input = mido.get_input_names()
print('input ports', ports_input)
portName_input = ports_input[1]
port_input = mido.open_input(portName_input)
print('input port opened : ', port_input)

#port_output.send(mido.Message('note_on', note=94, velocity=100))
#time.sleep(2)

# Define the MIDI input callback function
def on_midi_input(msg):
    # send back received note
    port_output.send(mido.Message(msg.type, note = msg.note, velocity=100))
    # Print the note and velocity
    print(f"Note numéro : {msg.note} jouée avec une vélocité de {msg.velocity}")
    print(f"Channel {msg.channel}\n")
    print(f"Message : {msg.type} ")

# Configurer la fonction de rappel pour recevoir des messages MIDI
port_input.callback = on_midi_input

# Attendre des messages MIDI indéfiniment
while True:
    time.sleep(10)



'''

program_change_message = mido.Message('program_change', channel=2, program=72)
port.send(program_change_message)

'''










'''
#test temps
start_time = 0

#déclarer les notes 
notes_names = {
    0 : 'C',
    1 : 'C#',
    2 : 'D',
    3 : 'D#',
    4 : 'E',
    5 : 'F',
    6 : 'F#',
    7 : 'G',
    8 : 'G#',
    9 : 'A',
    10 : 'A#',
    11 : 'B'
}

#fonction de traduction de note
def note_number_to_name(note_number) :
    octave = (note_number // 12) - 1 #pour choper l'octave -1 car 36 correpsond à 2 
    note = note_number % 12 #modulo 12 pour choper la note après le DO
    return f"{notes_names[note]}{octave}"


#port_output.send(mido.Message('reset'))

# REcevoir des notes
def handle_message(message):
    global start_time
    if message.type == 'note_on' :
        start_time = time.time()
        note_name = note_number_to_name(message.note)
        print(f"Note numéro : {message.note} = {note_name} jouée avec une vélocité de {message.velocity}")
        print(f"Channel {message.channel}\n")

    elif message.type == 'note_off':
        duration = time.time() - start_time
        note_name = note_number_to_name(message.note)
        print(f"Note {note_name} relachée, durée de : {duration:.2f} \n")


#callback et boucle infinie
port_input.callback = handle_message

while True :
    pass

# Fermer la connexion MIDI
port_input.close()
port_output.close()

'''









'''
msg = mido.Message('reset')
port.send(msg)
msg = mido.Message('program_change', channel=5, program=1) #selectionne un son de piano
port.send(msg)
msg = mido.Message('program_change', channel=1, program=113) #selectionne wod block
port.send(msg)

BPM = 100
note = 100
baseTime = time.time()
#Quantification à la double croche 1/16
timeQuantize = 1/BPM*16


subCpt=0


while(True) : 
    while(time.time()<baseTime+timeQuantize) :
        pass
    msg = mido.Message('note_off', channel=1, note=80)
    port.send(msg)
    if subCpt == 3 :
        msg = mido.Message('note_on', channel=1, note=80, velocity=80)
        port.send(msg)
        subCpt=0
    subCpt = subCpt+1
            #print("time : ", time.time())
            #msg = mido.Message('note_on', channel=1, note=100, velocity=80)
            #port.send(msg)
    if random.randint(0,3)==3 :
        note = note + random.randrange(2,6) - 4
        duration = random.randrange(1,3)*60/BPM
        velocity = 50 + random.randrange(1,70)
        msg = mido.Message('note_on', channel=5, note=note, velocity=velocity)
        port.send(msg)
    baseTime = baseTime + timeQuantize
  


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


#envoi
#port_output.send(mido.Message('reset'))
#port_output.send(mido.Message('note_on', note=94, velocity=100)
note_number = 94 
velocity = 64

port_output.send(mido.Message('note_on', note=note_number, velocity=velocity, channel=9))

# Attendre quelques secondes pour permettre à la note de se jouer.
time.sleep(2)

# Envoyer un message MIDI "note off" pour arrêter la note.
port_output.send(mido.Message('note_off', note=note_number))

port_output.close()

'''

