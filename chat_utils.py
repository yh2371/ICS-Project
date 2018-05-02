import socket
import time

# use local loop back address by default
#CHAT_IP = '127.0.0.1'
CHAT_IP = socket.gethostbyname(socket.gethostname())
CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

menu = "\n++++ Choose one of the following commands\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        c _peer_: to connect to the _peer_ and chat\n \
        ? _term_: to search your chat logs where _term_ appears\n \
        p _#_: to get number <#> sonnet\n \
        q: to leave the chat system\n \
        m: start MIDI creation\n\n"

music_menu = "\n++++ Choose one of the following commands\n \
        o: to create music on your own\n \
        d: to create music using existing demo melodies\n \
        exit: to leave MIDI creation menu (ALL unsaved data will be deleted!)\n\n"
              
archive = "\n++++ Choose from one of the following existing demo melodies (Song number: Song name, Artist, Instrument)\n \
        1: Firewalking, Idol Producer, Music Box\n \
        2: Wo Huai Nian De, Sun Yanzi, Acoustic Grand Piano\n \
        3: Twinkle Twinkle Little Star, ---, Cello\n \
        4: Thanks, Seventeen, Flute\n \
        5: NYU Shanghai Alma Mater, NYU Shanghai, Voice Oohs\n \
        cancel: to cancel creation\n\n"     
        
original = "\n++++ Choose one of the following commands\n \
        i: view instruments\n \
        k: view keyboard\n \
        w __note names(separated by commas); instrument name; name of melody__: write melody, eg: w C4,D5,D7; Music Box; Test\n \
        back: return to menu\n\n"

instruments = "\n++++Commonly used intruments are shown as following\n \
        ****NOTE: There are a total of 128 instruments available. However, for your convenience, not all are included in the following****\n \
        --> Acoustic Grand Piano\n \
        --> Electric Grand Piano\n \
        --> Electric Piano 1\n \
        --> Electric Piano 2\n \
        --> Music Box\n \
        --> Vibraphone\n \
        --> Xylophone\n \
        --> Church Organ\n \
        --> Reed Organ\n \
        --> Acoustic Guitar (nylon)\n \
        --> Acoustic Guitar (steel)\n \
        --> Electric Guitar (jazz)\n \
        --> Electric Guitar (clean)\n \
        --> Electric Guitar (muted)\n \
        --> Violin\n \
        --> Viola\n \
        --> Cello\n \
        --> Orchestral Harp\n \
        --> Choir Aahs\n \
        --> Voice Oohs\n \
        --> Trumpet\n \
        --> French Horn\n \
        --> Soprano Sax\n \
        --> Alto Sax\n \
        --> Tenor Sax\n \
        --> Baritone Sax\n \
        --> Oboe\n \
        --> English Horn\n \
        --> Clarinet\n \
        --> Flute\n \
        --> Whistle\n\n"
        
keyboard = "\n++++Available notes are shown as following\n \
        ****NOTE: Sharps are written as C#4, flats are written as C!4 or Cb4****\n \
        | C-1| C#-1| D-1| D#-1| E-1| F-1| F#-1| G-1| G#-1| A-1| A#-1| B-1|\n \
        | C0 | C#0 | D0 | D#0 | E0 | F0 | F#0 | G0 | G#0 | A0 | A#0 | B0 |\n \
        | C1 | C#1 | D1 | D#1 | E1 | F1 | F#1 | G1 | G#1 | A1 | A#1 | B1 |\n \
        | C2 | C#2 | D2 | D#2 | E2 | F2 | F#2 | G2 | G#2 | A2 | A#2 | B2 |\n \
        | C3 | C#3 | D3 | D#3 | E3 | F3 | F#3 | G3 | G#3 | A3 | A#3 | B3 |\n \
        | C4 | C#4 | D4 | D#4 | E4 | F4 | F#4 | G4 | G#4 | A4 | A#4 | B4 |\n \
        | C5 | C#5 | D5 | D#5 | E5 | F5 | F#5 | G5 | G#5 | A5 | A#5 | B5 |\n \
        | C6 | C#6 | D6 | D#6 | E6 | F6 | F#6 | G6 | G#6 | A6 | A#6 | B6 |\n \
        | C7 | C#7 | D7 | D#7 | E7 | F7 | F#7 | G7 | G#7 | A7 | A#7 | B7 |\n \
        | C8 | C#8 | D8 | D#8 | E8 | F8 | F#8 | G8 | G#8 | A8 | A#8 | B8 |\n \
        | C9 | C#9 | D9 | D#9 | E9 | F9 | F#9 | G9 |     |    |     |    |\n\n"
        

S_OFFLINE   = 0
S_CONNECTED = 1
S_LOGGEDIN  = 2
S_CHATTING  = 3

SIZE_SPEC = 5

CHAT_WAIT = 0.2

def print_state(state):
    print('**** State *****::::: ')
    if state == S_OFFLINE:
        print('Offline')
    elif state == S_CONNECTED:
        print('Connected')
    elif state == S_LOGGEDIN:
        print('Logged in')
    elif state == S_CHATTING:
        print('Chatting')
    else:
        print('Error: wrong state')

def mysend(s, msg):
    #append size to message and send it
    msg = ('0' * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg) :
        sent = s.send(msg[total_sent:])
        if sent==0:
            print('server disconnected')
            break
        total_sent += sent

def myrecv(s):
    #receive size first
    size = ''
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print('disconnected')
            return('')
        size += text
    size = int(size)
    #now receive message
    msg = ''
    while len(msg) < size:
        text = s.recv(size-len(msg)).decode()
        if text == b'':
            print('disconnected')
            break
        msg += text
    #print ('received '+message)
    return (msg)

def text_proc(text, user):
    ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
    return('(' + ctime + ') ' + user + ' : ' + text) # message goes directly to screen

