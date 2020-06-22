import wave
from contextlib import closing
import threading
from urllib.request import urlopen
import pyaudio
import numpy as np
import audioop

volume_pc = []
volume_phone = []
player = None

# get the phone audio streams loudness
def getPhoneAudio(audio_input):
    global player
    global volume_phone
    record_seconds = 5
    chunk = 1024

    # start computer audio function at the same time
    threading.Thread(target=getComputerAudio()).start()

    if player is None:
        player = pyaudio.PyAudio()
    with closing(wave.open(audio_input, 'rb')) as wavfile, \
         closing(player.open(
             format=player.get_format_from_width(wavfile.getsampwidth()),
             channels=wavfile.getnchannels(),
             rate=wavfile.getframerate(),
             output=True)) as stream:
        frames = []
        print("Recording...")
        for i in range(int(44100 / chunk * record_seconds)):
            data = wavfile.readframes(chunk) # read 1024 frames at once
            rms = audioop.rms(data, 2)
            # calculating Decibel from rood-mean-squared measure
            db = 20 * np.log10(rms)
            if db >= 0.0:
                volume_phone.append(db)
            if not data: # EOF
                break
            frames.append(data)
        print("Finished recording.")
        # stop and close stream
        stream.stop_stream()
        stream.close()
        # terminate pyaudio object
        player.terminate()

# get the computers audio loudness
def getComputerAudio():
    global volume_pc

    chunk = 1024
    FORMAT = pyaudio.paInt16
    channels = 1
    sample_rate = 44100
    record_seconds = 5
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    frames = []
    print("Recording...")
    for i in range(int(44100 / chunk * record_seconds)):
        data = stream.read(chunk)
        # calculate Decibel from root-mean-squared measure
        rms = audioop.rms(data, 2)
        db = 20 * np.log10(rms)
        if db >= 0.0:
            volume_pc.append(db)
        frames.append(data)
    print("Finished recording.")
    # stop and close stream
    stream.stop_stream()
    stream.close()
    # terminate pyaudio object
    p.terminate()

# calculate if the loudness of audio files of phone and computer are close enough
def audio_confidence(url):
    getPhoneAudio(urlopen(url))

    sum = 0
    for i in range(len(volume_pc)):
        sum += volume_pc[i]
    avg_volume_pc = sum/len(volume_pc)

    sum = 0
    for i in range(len(volume_phone)):
        sum += volume_phone[i]
    avg_volume_phone = sum/len(volume_phone)

    # loudness of phone audio must be within +/- 30% of computer audio, can be adjusted later
    if (avg_volume_phone > 0.7*avg_volume_pc and avg_volume_phone < 1.3*avg_volume_pc):
        return "Audio okay"
    else:
        return "Audio off"
