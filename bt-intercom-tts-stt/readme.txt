Overview

This project is an intercom system that allows users to communicate over Bluetooth via speech-to-text and text-to-speech functionality. 
The system triggers when the user speaks the keyword "blueberry". Upon hearing the keyword, the system beeps, begins recording audio, and waits for two seconds of silence before stopping the recording. The audio recording is then converted to text using Google Cloud Speech-to-Text functionality, and the text is transmitted over Bluetooth. The receiving device uses Google Cloud Text-to-Speech to convert the text back to audio, which is played on its connected speaker.

Dependencies

The program relies on multiple Python packages, which include:

    socket for networking
    os and subprocess for OS and shell operations
    getpass for username retrieval
    requests for making HTTP requests
    time for time-related operations
    pygame for audio playback
    google.cloud.texttospeech for Google Cloud functionalities
    sounddevice for audio recording and playback
    numpy for numerical operations
    pvporcupine for hotword detection
    pyaudio for audio streams handling
    struct for data conversions
    threading for threads management
    collections.deque for working with deque data structures
    colorama for terminal output text styling
    sys for system-specific parameters and functions
    bluetooth for Bluetooth communications

Usage

    Set the server_mac_address variable to the MAC address of the device you want to connect to.
    Set my_spp_role to either "host" or "client" depending on whether the device is acting as a host or a client in the connection.
    Run the script. The system will start listening for the keyword "blueberry".
    Speak the keyword to activate the intercom. The system will beep and start recording your speech. Pause for two seconds when you finish speaking to signal the end of your message.
    The system will convert your message to text, send it to the connected device over Bluetooth, convert the text back to speech, and play it on the connected device's speaker.

Note

This system requires a Google Cloud account with Speech-to-Text and Text-to-Speech APIs enabled, and the appropriate credentials file (google-creds.json) available in the project directory. It also requires a Porcupine API key (porcupine-key.txt).

Ensure the MAC address of the connected device is correctly entered and Bluetooth is enabled on both devices. If you're running the script on a machine without a microphone or speaker, you may need to comment out or modify the audio-related sections.
