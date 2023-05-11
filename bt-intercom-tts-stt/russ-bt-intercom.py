
#This intercom works by, you say 'blueberry', and it beeps, and it records audio, waits for two seconds of silence, then turns the audio to text, transmits the text over bluetooth socket, then the other device turns the text to speech and plays it on it's connected speaker.

my_threshold = -40  #edutige eim 003

# Used to work with sockets, for example, to get the hostname
import socket

# Used for file and folder operations
import os

# Used to run a shell command, for example, to set the background image
import subprocess

# Used to get the current user's username
import getpass

# Used for making HTTP requests, for example, to generate images and get weather information
import requests

# Used to calculate the time difference between two network speed measurements
import time

import time as t
# Used to work with the Pygame library for playing sounds
import pygame

# Used for Google Cloud Text-to-Speech functionality
from google.cloud import texttospeech

# Used for Google Cloud Speech-to-Text functionality
from google.cloud import speech_v1p1beta1 as speech

# Used to record and play audio with the sounddevice library
import sounddevice as sd

# Used for working with numpy arrays, for example, when processing audio data
import numpy as np

# Used for the Porcupine hotword detection library
import pvporcupine

# Used for working with audio streams using the PyAudio library
import pyaudio

# Used for converting between different data types, for example, when processing audio data
import struct

# Used for creating and managing threads
import threading

# Used for creating and working with deque data structures
from collections import deque

# Used for changing the color and style of terminal output text
from colorama import Fore, Style

#to exit the script
import sys

from threading import Lock
recording_lock = Lock()

import bluetooth
from bluetooth import BluetoothSocket, RFCOMM

#SPP-----------
# Replace these with the MAC address and port number of the client device.
server_mac_address = "XX:XX:XX:XX:XX:XX"
port = 1

my_spp_role = "host"
#my_spp_role = "client"



#END SPP--------

# Create a lock for the hotword detection
hotword_lock = threading.Lock()

processing_speech = False


#Initialize the text to speech, speech to text, maps credential json file.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-creds.json"

# Initialize recording variables
recording = False
recorded_audio = []
silence_count = 0
silence_buffer = deque(maxlen=44100)  # Buffer to store the last second of audio samples

# Initialize global voice_enabled variable
voice_enabled = True

# Initialize recording variables
recording = False
recorded_audio = []

found_voice = 0
has_internet = True #for connection status

paused = False # for audio playback

# Initialize global stop_output variable to cease play of mp3 completely. cuts off the ai's speech.
stop_output = False

#LOAD API KEYS#################

# Load pvporcupine API key
with open('porcupine-key.txt', 'r') as f:
   PORCUPINE_API_KEY = f.read().strip()

# Initialize global stop_hotword_detection variable for blueberry, etc.
stop_hotword_detection = threading.Event()

#AS HOST
def handle_client_connections(): #reestablish spp connection if dropped
    global client_sock, server_sock
    while True:
        print("Waiting for a new connection on RFCOMM channel 1...")
        # Accept a new connection
        client_sock, _ = server_sock.accept()
        print(f"Accepted connection from {client_sock.getpeername()}")

        try:
            spp_receive_messages()
        except bluetooth.btcommon.BluetoothError as e:
            print(f"Failed to receive data from SPP client: {e}")

        # Close the client socket
        client_sock.close()
        print("Client disconnected. Ready for a new connection.")

#AS HOST
def spp_receive_messages():
    while True:
        # Receive data from the SPP client
        received_data = client_sock.recv(1024)
        if not received_data:
            break

        print(f"Received data: {received_data}")
        text_to_speech(received_data.decode(), "output.mp3")
        play_mp3_file("output.mp3")

#sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)


#I AM CLIENT CONNECT AND RECIEVE FROM MAC ADDRESS
def connect_to_spp_server(server_mac_address, port):
    global sock
    while True:
        # Create a socket for RFCOMM communication
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            # Connect to the SPP server
            sock.connect((server_mac_address, port))
            print(f"Connected to SPP server at {server_mac_address} on port {port}")

            # Communicate with the SPP server
            while True:
                received_data = sock.recv(1024)
                if not received_data:
                    break

                print(f"Received data: {received_data}")
                text_to_speech(received_data, "output.mp3")
                play_mp3_file("output.mp3")  # Assuming you have a play_mp3_file function

        except bluetooth.btcommon.BluetoothError as e:
            print(f"Failed to connect to SPP server: {e}")

        finally:
            sock.close()

        print("Waiting 0 seconds before attempting to reconnect...")
        time.sleep(5)




def send_message(message):

    if my_spp_role == "host":
        global client_sock
        try:
            client_sock.send(message)
            print(f"Sent message: {message}")
        except bluetooth.BluetoothError as e:
            print(f"Bluetooth Error: {e}")
    if my_spp_role == "client":
        sock.send(message)

def start_spp_server():
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", 1))  # Bind to channel 1
    server_sock.listen(1)  # Listen for incoming connections

    print("Waiting for a connection on RFCOMM channel 1...")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    return client_sock, server_sock


#detect silence
def is_silent(audio_data, threshold):
    threshold = my_threshold
    global found_voice
    rms = np.sqrt(np.mean(audio_data**2))
    audio_data_dB = 20 * np.log10(rms + np.finfo(float).eps)

    if audio_data_dB < threshold:  # Silence
        print(Fore.GREEN + f"Decibals: {audio_data_dB}" + Style.RESET_ALL)
    else:  # Sound
        print(Fore.YELLOW + f"Decibals: {audio_data_dB}" + Style.RESET_ALL)

    return audio_data_dB < threshold


def recording_thread_function(hotword_activated):
 #   global recording, recorded_audio, record_button
    with sd.InputStream(callback=record_callback, channels=1, samplerate=44100, blocksize=4096):
        if hotword_activated:
            while recording:
                time.sleep(0.1)
            #record_button.config(text="Start Recording")
            sd.stop()
            record_and_transcribe(hotword_activated)
        else:
            while recording:
                time.sleep(0.1)


#PORCUPINE WORD Recognition

global current_task
current_task = ""
audio_playing=False

def hotword_listen(): #Listen for the activation hotwords, blueberry, terminator, and look-up.
    global current_task
    global audio_playing
    hotword_lock.acquire()
    while not stop_hotword_detection.is_set():
        porcupine = None
        pa = None
        audio_stream = None

        try:
            porcupine = pvporcupine.create(
                keyword_paths=[pvporcupine.KEYWORD_PATHS["blueberry"]],
                sensitivities=[0.5],
                access_key=PORCUPINE_API_KEY,
            )
            pa = pyaudio.PyAudio()

            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length,
                input_device_index=None,
            )

            print("Listening for hotword...'blueberry' for ai chat or 'look up' for wikipedia")


            while not stop_hotword_detection.is_set():
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0 and not recording and not audio_playing:  # Add condition to check if not recording
                    if keyword_index == 0:  # "blueberry" detected
                        print("Blueberry detected!")
                        beep()
                        if my_spp_role == "client":
                            t.sleep(1)
                            beep()
                        current_task = "chat"
                        toggle_recording(True)
                        break

        except KeyboardInterrupt:
            print("Stopping hotword listening...")
        finally:
            if audio_stream is not None:
                audio_stream.close()
            if pa is not None:
                pa.terminate()
            if porcupine is not None:
                porcupine.delete()



#STT
def record_callback(indata, frames, time, status):
    global recording, silence_count, silence_buffer
    if status:
        print(status, file=sys.stderr)
    if recording:
        recorded_audio.append(indata.copy())

        # Add the incoming audio data to the silence buffer
        silence_buffer.extend(indata.flatten())

        # Check if the entire buffer is silent
        if is_silent(np.array(silence_buffer), threshold=-37.4):  #-40 for the etm 001 microphone # -37.4 for EIM 003
            silence_count += frames
            print(f"Silence count: {silence_count}")
            if silence_count >= 88200:  # 2 second of silence
                recording = False
                beep()
        else:
            silence_count = 0




#STT also
def transcribe_audio(audio_data):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    if response.results:
        transcript = response.results[0].alternatives[0].transcript
        print(f"Transcription: {transcript}")  # Debug print statement
        return transcript
    else:
        print("No transcription results found.")  # Debug print statement
        return None

def save_string_to_file(text,file_name):
    with open(file_name, 'w') as file:
        file.write(text)

#stt
def record_and_transcribe(hotword_activated):
    global recorded_audio, recording_lock
    print("Current task:", current_task)
    # Acquire the lock before processing the audio data
    with recording_lock:

        if len(recorded_audio) > 0:
            audio_data = np.concatenate(recorded_audio, axis=0)
            audio_data = (audio_data * 32767).astype(np.int16).tobytes()

            transcript = transcribe_audio(audio_data)
            if transcript:
                if hotword_activated:
                    if current_task == "chat":
                        print("chatting")
                        send_message(transcript)

                else:
                    send_message(transcript)
        else:
            # If recorded_audio is empty, return immediately
            return

#more stt
def toggle_recording(hotword_activated):
    print("Toggling")
    global recording, recorded_audio, silence_count, silence_buffer, recording_lock
    silence_count = 0
    silence_buffer = deque(maxlen=44100)  # Buffer to store the last second of audio samples

    with recording_lock:
        if not recording:
            recorded_audio = []
            recording = True
            input_device_index = sd.default.device[0]  # Get the default input device index

            recording_thread = threading.Thread(target=recording_thread_function, args=(hotword_activated,))
            recording_thread.start()

        else:
            recording = False
            sd.stop()
            if hotword_activated:
                hotword_activated = False  # Reset hotword_activated to False after processing

            # Acquire the lock before calling record_and_transcribe
            # Check if hotword_activated is True and restart hotword listening
            if hotword_activated:
                hotword_activated = False  # Reset hotword_activated to False after processing
                hotword_listen()  # Restart hotword listening after processing


def play_mp3_file(file_path):
    global stop_output, paused
    stop_output = False
    paused = False
    global audio_playing
    audio_playing = True
    print("playing audio")
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() and not stop_output:
        if not paused:
            time.sleep(0.1)
        else:
            pygame.mixer.music.pause()
            while paused:
                time.sleep(0.1)
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    stop_output = False
    audio_playing = False



def text_to_speech(text, output_file):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    #voice = texttospeech.VoiceSelectionParams(
    #    language_code="en-US",
    #    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    #)
    if my_spp_role == "host":
        voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Wavenet-F"
    )
    if my_spp_role == "client":
        voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-News-M"
    )


    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Save the synthesized audio to a file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')



#computer beep when detect hotword
def beep():
    os.system(f"play -n synth 0.11 sin 880 vol 0.1 ")

def beep_vol(volume):
    os.system(f"play -n synth 0.11 sin 880 vol {volume}")


#start listening for keywords LOOK UP and BLUEBERRY and TERMINATOR for change name.
hotword_thread = threading.Thread(target=hotword_listen, daemon=True)
hotword_thread.start()

# Start the Bluetooth SPP server
if my_spp_role == "host":
    client_sock, server_sock = start_spp_server()
    spp_receive_thread = threading.Thread(target=handle_client_connections, daemon=True)
    spp_receive_thread.start()

if my_spp_role == "client":
    connection_thread = threading.Thread(target=connect_to_spp_server, args=(server_mac_address, port))
    connection_thread.daemon = True
    connection_thread.start()


# Main function
def main():

    #true or false
    global recording

    print("Starting terminal application...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting terminal application...") #dunno why i have to ctrl-c twice to exit but whatever.
        sys.exit(0)

if __name__ == "__main__":
    main()
