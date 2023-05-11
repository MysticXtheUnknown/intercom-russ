Audio Amplifier

This script acts as an audio amplifier, capturing audio from the device's microphone and playing it directly through the connected speakers.

This can be used as a simple intercom setup by placing device A's speaker near device B and vice versa. It operates as a standalone one-way audio stream to the connected speaker.
Requirements

    Python 3
    PyAudio
    pynput

You can install the Python dependencies with:

pip install pyaudio pynput

To use the script, simply run:

python amplifier.py

After starting the script, press the spacebar to start and stop recording. The recorded audio will be played back through the connected speakers in real time.  Press space again to pause input.

Press ESC to exit the script.

Note: There is no communication between devices, and no internet or Bluetooth connection is required for operation.
