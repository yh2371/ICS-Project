"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
import music_maker
from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        self.out_msg += 'New fundtion : Music Sharing\n'
                        self.out_msg += 'Enter "share original" to share original music in the group;\n'
                        self.out_msg += 'Enter "share demo" to share demo music in the group;\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                
                #MIDI creation action
                elif my_msg == "m":
                    self.state = S_MUSIC
                    self.out_msg += original
                    
                    #while my_msg != "back":
                    #    print(original)
                    #    my_msg = input()

                    
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                elif my_msg == "share original":
                    self.state = S_CHATTING_O
                    
                elif my_msg == "share demo":
                    self.state = S_CHATTING_D
                    
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == "original":
                    if peer_msg["status"] == "success":
                        info = peer_msg["info"]
                        midi = music_maker.create_midi(info[4], info[3])
                        save(midi, info[0])
                        self.out_msg += "You have successfully recieved " + info[0] + ".mid created by " + info[1] + " from " + peer_msg["from"] + "! Please check your directory!"
                    else:
                        self.out_msg += "Error: MIDI file was not successfully recieved!"
                elif peer_msg["action"] == "demo":
                    if peer_msg["status"] == "success":
                        info = peer_msg["info"]
                        midi = music_maker.create_demo(info[1], info[2], info[3], info[3])
                        save(midi, info[0])
                        self.out_msg += "You have successfully recieved " + info[0] + ".mid from " + peer_msg["from"] + "! Please check your directory!"
                    else:
                        self.out_msg += "Error: MIDI file was not successfully recieved!"
                else:
                    self.out_msg += peer_msg["from"] + ": " + peer_msg["message"]
                   

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
        
        
        elif self.state == S_MUSIC:
            
            if len(my_msg) > 0:
                if my_msg == "i":
                    self.out_msg += instruments
                elif my_msg == "k":
                    self.out_msg += keyboard
                elif my_msg[0] == "w":
                    try:
                        l = my_msg[1:].split(";")
                        melody = l[0].strip()
                        instrument = l[1].strip()
                        name = l[2].strip()
                        mysend(self.s, json.dumps({"action":"create", "melody" : melody, "instrument": instrument, "name": name}))
                        if json.loads(myrecv(self.s))["status"] == "failure":
                            self.out_msg +="ERROR: Unable to create MIDI. Please try again.\n"
                        else:
                            self.out_msg +="Success! MIDI saved!"
                            self.out_msg +=("New creation:", json.loads(myrecv(self.s)["info"]))
                    except:
                        self.out_msg += "Enter in required format."
                        self.out_msg += original
                elif my_msg == 'back':
                    self.state =S_LOGGEDIN
                else:
                    self.out_msg += original
            
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
            
        elif self.state == S_CHATTING_O:
            f = open("creations.txt", r)
            self.out_msg += "++++++Archive of original music is shown below:\n"
            self.out_msg += f.read()
            f.close()
            if my_msg.isdigit():
                mysend(self.s, json.dumps({"action": "original", "from": "[" + self.me + "]", "number": number}))
                if json.loads(myrecv(self.s))["status"] == "failure":
                    self.out_msg += "ERROR. Unable to send the original music. Try again.\n"
                else:
                    self.out_msg += "Success! Original sent!"
                
                
        elif self.state == S_CHATTING_D:
            self.out_msg +="++++++Archive of demo music is shown below:\n"
            self.out_msg += archive
            if my_msg.isdigit():
                mysend(self.s, json.dumps({"action": "original", "from": "[" + self.me + "]", "number": number}))
                if json.loads(myrecv(self.s))["status"] == "failure":
                    self.out_msg += "ERROR. Unable to send the demo music. Try again.\n"
                else:
                    self.out_msg += "Success! Demo sent!"

#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
