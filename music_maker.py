# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 13:54:52 2018

@author: YH
"""

#Contains all needed functions and modules for MIDI creation

from __future__ import print_function
import pretty_midi
from pylab import *
import librosa             # The librosa library
import librosa.display     # librosa's display module (for plotting features)
import IPython.display     # IPython's display module (for in-line audio)
import matplotlib.pyplot as plt # matplotlib plotting functions
import matplotlib.style as ms   # plotting style
import numpy as np              # numpy numerical functions
ms.use('seaborn-muted')         # fancy plot designs

def show_score(midi_object, fs = 100):
    S = midi_object.get_piano_roll()
    plt.imshow(S, aspect='auto', origin='bottom', interpolation='nearest', cmap=np.cm.gray_r)
    plt.xlabel('Time')
    plt.ylabel('Pitch')
    plt.pc=np.array(['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B'])
    plt.idx = np.tile([0,4,7],13)[:128]
    plt.yticks(np.arange(0,128,4),np.pc[plt.idx], fontsize=5)
    plt.xticks(np.arange(0,S.shape[1],fs),np.arange(0,S.shape[1],fs)/fs, )   
    
def matrix2notes(m):
    #input: m, a N by 4 matrix (4 means starting time, ending time, pitch, velocity)
    # first sort the matrix to make sure starting time is in order
    m = np.array(m)
    m = m[np.argsort(m[:,0]),:] #argsort gives you the index before the sorting
    # transfer the databack to note list
    notes=[pretty_midi.Note(start=m[i,0], end=m[i,1], pitch=int(m[i,2]), velocity= int(m[i,3]) ) 
                            for i in range(np.size(m,0))]
    return notes

def create_note_matrix(start, end, note, vel):
    m = np.matrix(np.zeros((len(note), 4)))
    l = [start, end, note, vel]
    for i in range(4):
        if type(l[i]) != type([]) and type(l[i]) != type(np.array([])):
            m[:,i] = [l[i]]
        else:
            m[:,i] = np.matrix(l[i]).T
    return m

def create_midi(melody, instrument = "Acoustic Grand Piano", music = pretty_midi.PrettyMIDI()):
    program = pretty_midi.instrument_name_to_program(instrument)
    track = pretty_midi.Instrument(program)
    
    start = list(range(0,len(melody)))
    end = np.array(start) + 1
    
    note_number = []
    for note_name in melody:
        note_number.append(pretty_midi.note_name_to_number(note_name))

    note_matrix = create_note_matrix(start, end, note_number, 100)
    
    notes = matrix2notes(note_matrix)
    
    track.notes = notes
    music.instruments.append(track)
    
    return music
 
def create_demo(start, end, note, instrument):
    program = pretty_midi.instrument_name_to_program(instrument)
    track = pretty_midi.Instrument(program)
    
    demo = pretty_midi.PrettyMIDI()
    
    note_matrix = create_note_matrix(start, end, note, 100)
    notes = matrix2notes(note_matrix)
    
    track.notes = notes
    demo.instruments.append(track)
    
    return demo
    
def play_music(midi_object):
    wave = midi_object.synthesize(fs = 44100)
    IPython.display.Audio(data=wave, rate=44100)
    
def save(midi_object, filename):
    midi_object.write(filename)
