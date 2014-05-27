#!/usr/bin/python3

extensions = ["*.mp3", "*.ogg"]

import serial, argparse, time
from datetime import datetime,timedelta
import random
import os
import glob
from pygame import mixer

parser = argparse.ArgumentParser(description='Woxoun Interface')
parser.add_argument('-p', '--port', help='Sets the port you wish to communicate through. For Windows you max use COM* and for Linux you may use /dev/ttyS* whereas the asterisk stands for the port number.', required=True)
parser.add_argument('-i', '--interval', help='Defines an interval in seconds the program should wait between messages. If no argument is given, the program assumes 60 seconds', required=False, default=60)
parser.add_argument('-d', '--directory', help='Sets the directory you stored the soundfiles.',required=True)
parser.add_argument('-s', '--silence', help='Required length in seconds of silence before PTT is asserted. Default is 10 seconds.', required=False, default=10.0)
parser.add_argument('-n', '--noise', help='Maximum ADC Value to accept as silence. Default is 128/1024', required=False, default=128)
parser.add_argument('-r', '--randomize', help='Randomize interval by +- n seconds. Default is 10.', required=False, default=10);

args = vars(parser.parse_args())
interval = float(args['interval'])
silence = float(args['silence'])
randomize = float(args['randomize'])

os.chdir(args['directory'])
files = []
for ext in extensions:
    files.extend(glob.glob(ext))

random.shuffle(files)

mixer.init()

#ser = serial.Serial(args['port'],9600)
    
def LogAction(message, duration=None):
    if duration == None:
        print("[{0}]               {1}".format(time.strftime("%H:%M:%S"), message))
    else:
        print("[{0}] -> [{2}] {1}".format(time.strftime("%H:%M:%S"), message, (datetime.now()+timedelta(seconds=duration)).strftime("%H:%M:%S")))

def PlaySample():
    global files
    #ser.write(b'H')               # Key on
    time.sleep(.5)
    file = files.pop()
    LogAction("playing {0}".format(file));

    mixer.music.load(files.pop())
    mixer.music.play()
    time.sleep(.5)
    #ser.write(b'L')               # Key off
    if not files: #list is empty
        LogAction("  reloading files")
        for ext in extensions:
            files.extend(glob.glob(ext))
        random.shuffle(files)

def GetADCVal():
    #ser.write(b'A')
    time.sleep(.2)
    return random.randint(0, 136)
    #return ser.readline()     # Returns a value from 0 to 1023 

def WaitForSilence():
    LogAction("waiting for {0:.1f}s of silence".format(silence))
    waited = 0.0;
    while waited < silence:
        noise = GetADCVal();
        #print("  2a-Noise {0}, Timer {1}".format(noise, waited))
        if noise > args['noise']:
            waited = 0.0
        else:
            waited += 0.2

def WaitForInterval():
    pause = random.uniform(-randomize, randomize)
    if interval + pause < 0:
        pause = -interval + 1
    LogAction("Waiting {0:.1f} + {1:.1f} = {2:.1f} seconds for next action".format(interval, pause, interval+pause), interval+pause)
    time.sleep(interval+pause)

if __name__ == '__main__':
    LogAction("Starting random sample player")
    running = True
    while running:
        WaitForInterval()
        WaitForSilence()
        PlaySample()

        
