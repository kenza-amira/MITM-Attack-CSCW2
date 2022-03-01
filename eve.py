import sys
import os
import argparse
from common import *
from const import *

# Getting the flags sorted out and making sure they're correctly used
if len(sys.argv) > 2:
    print('You have specified too many arguments, Eve can\'t multitask. Try "python3 eve.py -h" to see all the options.')
    sys.exit()

if len(sys.argv) < 2:
    print('You need to specify the kind of attack you wish to execute. Try "python3 eve.py -h" to see all the options.')
    sys.exit()
    
parser = argparse.ArgumentParser(description='Man in the Middle Attack')
parser.add_argument('--relay', help='Eve relays the messages', action='store_true')
parser.add_argument('--break-heart', help= 'Eve changes the messages', action='store_true')
parser.add_argument('--custom', help = 'Eve prompts user to input a message', action='store_true')
args = parser.parse_args()
#print(args)

dialog = Dialog('print')

# Creating fake identities
asAlice = 'alice'
asBob = 'bob'
socket_B, aes_B = setup(asBob, BUFFER_DIR, BUFFER_FILE_NAME)
os.rename(BUFFER_DIR+BUFFER_FILE_NAME, BUFFER_DIR + "mitm_buffer")
dialog.prompt("Nice, getting there...")
socket_A, aes_A = setup(asAlice, BUFFER_DIR, BUFFER_FILE_NAME)
dialog.prompt("Hehe, it\'s working!")


# Alice starts the process so we start by getting the initial message sent to her by Bob
received_B = receive_and_decrypt(aes_A, socket_A)

# Mostly the same code as the one in alice.py and bob.py slightly modified

# No changes made here, just a mixture of bob.py and alice.py as Alice only relays the messages
if args.relay:
    encrypt_and_send(received_B, aes_B, socket_B)
    dialog.chat('Bob said: "{}"'.format(received_B))
    dialog.info('Message sent!')
    dialog.info("Waiting for message...")
    received_A = receive_and_decrypt(aes_B, socket_B)
    dialog.chat('Alice said: "{}"'.format(received_A))
    encrypt_and_send(received_A,aes_A, socket_A)

# As noticed in bob.py and alice.py we can send a BAD_MSG instead of a NICE_MSG which is what we do here.
# This will automatically trigger alice.py if/else condition and break her heart...
elif args.break_heart:
    sent_B = BAD_MSG[asBob]
    encrypt_and_send(sent_B, aes_B, socket_B)
    dialog.chat('Bob said: "{}"'.format(sent_B))
    dialog.info('Message sent!')
    dialog.info("Waiting for message...")
    received_A = receive_and_decrypt(aes_B, socket_B)
    dialog.chat('Alice said: "{}"'.format(received_A))
    encrypt_and_send(received_A,aes_A, socket_A)

# In here we prompt the attacker to write Bob's and Alice's messages and allow them to see the actual messages.
# Bob and Alice on the other hand only get the fake messages.
elif args.custom:
    dialog.chat('Bob said: "{}"'.format(received_B))
    dialog.prompt('Please input what Bob (or at least that\'s what Alice thinks) has to say')
    sent_B = input()
    encrypt_and_send(sent_B, aes_B, socket_B)
    dialog.chat('Bob slurred: "{}"'.format(sent_B))
    received_A = receive_and_decrypt(aes_B, socket_B)
    dialog.chat('Alice slurred: "{}"'.format(received_A))
    dialog.prompt('Please input what Alice (or at least that\'s what Bob thinks) has to say')
    sent_A = input()
    encrypt_and_send(sent_A, aes_A, socket_A)

tear_down(socket_B, BUFFER_DIR, "mitm_buffer")
tear_down(socket_A, BUFFER_DIR, BUFFER_FILE_NAME)