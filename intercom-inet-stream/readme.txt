
Local Inet Intercom Solution (LIIS)

Audio Streamer

This folder contains two Python scripts that allow for bi-directional streaming of audio data between two devices over a network. This can be used to set up a simple intercom system or for any other purpose that requires sending live audio data between two devices.
Requirements

    Python 3
    PyAudio
    pynput

You can install the Python dependencies with:

pip install pyaudio pynput

Scripts

The repository contains two main scripts:
1. Receiver Script

The Receiver script binds to a specified port and listens for incoming UDP packets. These packets are interpreted as audio data and played back through the device's speakers.

To use the Receiver script, simply run:

python receiver.py

2. Sender Script

The Sender script captures audio data from the device's microphone and sends it as UDP packets to a specified IP address and port. This script also provides a feature to toggle the microphone on and off by pressing the spacebar.

To use the Sender script, simply run:

python sender.py

Configuration

Both scripts allow you to configure the following parameters:

    IP_ADDRESS: The IP address of the other device (only for Sender script).
    RECEIVE_PORT / SEND_PORT: The port to bind to for receiving audio data / the port to send audio data to.

You can adjust these parameters in the scripts as needed to fit your specific use case.

Network Setup

This setup can work both over a local network and over the internet.

For a local network setup, replace IP_ADDRESS in the Sender script with the local IP address of the other device.

For an internet setup, replace IP_ADDRESS in the Sender script with the external IP address of the other device, and set up port forwarding on both routers to forward incoming traffic on the specified RECEIVE_PORT to the correct local IP address of each device.

Notes

Streaming audio over the internet may introduce latency and quality issues depending on the available bandwidth and network conditions.
