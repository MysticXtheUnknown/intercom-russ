#RUN THIS ON BOTH DEVICES _AFTER_ THE RECEIVER SCRIPT IS RUNNING ON BOTH DEVICES.
#make sure to replace the IP_ADDRESS with the address of the remote device.
#this might work over the internet if you set up port forwarding on your router (and maybe set up your device with a static ip address)


import socket
import pyaudio
from pynput import keyboard

IP_ADDRESS = '192.168.0.2'  # Replace with the IP address of the other device
SEND_PORT = 12345

# PyAudio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Flag for toggling the microphone
mic_enabled = True

def on_press(key):
    global mic_enabled
    if key == keyboard.Key.space:
        mic_enabled = not mic_enabled
        print("Microphone", "enabled" if mic_enabled else "disabled")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

print("Streaming microphone input... (Press spacebar to toggle on/off)")

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    while True:
        if mic_enabled:
            data = stream.read(CHUNK)
            sock.sendto(data, (IP_ADDRESS, SEND_PORT))
        else:
            data = stream.read(CHUNK)  # Clear buffer to avoid lag when re-enabled

except KeyboardInterrupt:
    print("Stopping microphone streaming...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
    listener.stop()


