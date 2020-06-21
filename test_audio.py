import wave
from contextlib import closing
import threading
from urllib.request import urlopen
import pyaudio
import numpy as np
import audioop
from subprocess import Popen, PIPE

volume_pc = []
volume_phone = []
player = None

def getPhoneAudio(audio_input):
    global player
    global volume_phone
    record_seconds = 5
    chunk = 1024
    channels = 1
    sample_rate = 44100
    FORMAT = pyaudio.paInt16

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
            db = 20 * np.log10(rms)
            # print(db)
            if db >= 0.0:
                volume_phone.append(db)
            if not data: # EOF
                break
            #stream.write(data)
            frames.append(data)
        print("Finished recording.")
        # stop and close stream
        stream.stop_stream()
        stream.close()

        player.terminate()
        # # save audio file
        # # open the file in 'write bytes' mode
        # wf = wave.open(filename, "wb")
        # # set the channels
        # wf.setnchannels(channels)
        # # set the sample format
        # wf.setsampwidth(player.get_sample_size(FORMAT))
        # # set the sample rate
        # wf.setframerate(sample_rate)
        # # write the frames as bytes
        # wf.writeframes(b"".join(frames))
        # # close the file
        # wf.close()



def getIpAdress():
    return None

def getComputerAudio():
    global volume_pc

    chunk = 1024
    FORMAT = pyaudio.paInt16
    # mono, change to 2 if you want stereo
    channels = 1
    # 44100 samples per second
    sample_rate = 44100
    record_seconds = 5
    # initialize PyAudio object
    p = pyaudio.PyAudio()
    # open stream object as input & output
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
        # if you want to hear your voice while recording
        rms = audioop.rms(data, 2)
        db = 20 * np.log10(rms)
        # print(db)
        if db >= 0.0:
            volume_pc.append(db)
        frames.append(data)
    print("Finished recording.")
    # stop and close stream
    stream.stop_stream()
    stream.close()
    # terminate pyaudio object
    p.terminate()
    # save audio file
    # open the file in 'write bytes' mode
    # wf = wave.open(filename, "wb")
    # # set the channels
    # wf.setnchannels(channels)
    # # set the sample format
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # # set the sample rate
    # wf.setframerate(sample_rate)
    # # write the frames as bytes
    # wf.writeframes(b"".join(frames))
    # # close the file
    # wf.close()

# possibly optimize offset in the future

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

    if (avg_volume_phone > 0.7*avg_volume_pc and avg_volume_phone < 1.3*avg_volume_pc):
        return "Audio okay"
    else:
        return "Audio off"

# # calculate fingerprints
# def calculate_fingerprints(filename):
#     sample_time = 4
#     process = Popen(['fpcalc', '-raw', '-length', f'{sample_time}', f'{filename}'], cwd=r'C:\Users\Admin', shell=True, stdout=PIPE, stderr=PIPE)
#     stdout, stderr = process.communicate()
#     stdout = stdout.decode('utf-8')
#     # get byte position of all the fingerprints
#     fingerprint_index = stdout.find('FINGERPRINT=') + 12
#     # put all the fingerprints in a list
#     fingerprints = list(map(lambda x: int(x), stdout[fingerprint_index:-2].split(',')))
#     return fingerprints
#
# # listx = phone audio, listy = pc audio
# def correlation(listx, listy, offset):
#     if len(listx) == 0 or len(listy) == 0:
#         raise Exception('Empty lists cannot be correlated.')
#
#     listx = listx[offset:]
#     listy = listy[:len(listx)]
#
#     covariance = 0
#     for i in range(len(listx)):
#         covariance += 32 - bin(listx[i] ^ listy[i]).count("1")
#     covariance = covariance / float(len(listx))
#
#     return covariance / 32
#
# # possibly optimize offset in the future
#
# def audio_confidence(url):
#     getPhoneAudio(urlopen(url), 'output/phone-recorded.wav')
#
#     offset = 0
#     root_dir = r'C:/Users/Admin/PycharmProjects/onlineExam/'
#
#     fingerprints_phone = calculate_fingerprints(root_dir + 'output/phone-recorded.wav')
#     fingerprints_pc = calculate_fingerprints(root_dir + 'output/pc-recorded.wav')
#     print(fingerprints_phone)
#     print(fingerprints_pc)
#
#     confidence = correlation(fingerprints_phone, fingerprints_pc, offset)
#     print(confidence)
#     yield(confidence)