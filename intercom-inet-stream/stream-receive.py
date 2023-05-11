#Run this file without changing it to be ready to receive a connection for the mic stream.

import socket
import pyaudio

IP_ADDRESS = ''  # Empty string to bind to all available interfaces
RECEIVE_PORT = 12345

# PyAudio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_ADDRESS, RECEIVE_PORT))

try:
    print("Receiving audio stream...")
    while True:
        data, addr = sock.recvfrom(CHUNK * CHANNELS * 2)
        stream.write(data)
except KeyboardInterrupt:
    print("Stopping audio stream...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()

