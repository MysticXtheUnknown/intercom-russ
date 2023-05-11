#This script is basically an amplifier. it plays your mic to the connected speakers.
#To use this as an intercom, set up device A's speaker near device B and vice versa.

#There no internet, no bluetooth, and no communication between the devices.  It works by itself as a one way audio stream to the connected speaker.

import pyaudio
from pynput import keyboard

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

recording = False

def on_press(key):
    global recording
    if key == keyboard.Key.space:
        recording = not recording

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Press spacebar to start/stop recording, and ESC to exit")

    try:
        while True:
            data = stream.read(CHUNK)
            if recording:
                stream.write(data, CHUNK)
    except KeyboardInterrupt:
        pass

print("* done")

stream.stop_stream()
stream.close()
p.terminate()

