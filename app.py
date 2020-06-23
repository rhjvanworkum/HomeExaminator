import shutil
from face_encoding import save_faces
from flask import Flask, Response, request, render_template, after_this_request, flash, redirect
from flask_apscheduler import APScheduler
from imutils.video import VideoStream
from face import FaceDetector
from yolo import YoloDetector
from test_audio import audio_confidence
import requests
import argparse
import threading
from ctypes import *
import numpy as np
import imutils
import cv2
import simplejson as json
import time
import os
import subprocess

app = Flask(__name__)

def start_browser(chromium_path):
    subprocess.Popen([chromium_path, '--kiosk', 'http://localhost:5000'])

def kill_processes():
    subprocess.Popen(['taskkill', '/IM', 'chrome.exe', '/F'])

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# function to start capturing pc camera frames
def start_pc_camera():
    global pc_camera_frame, vs

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        pc_camera_frame = frame.copy()

# function to start capturing phone camera frames
def start_phone_camera():
    global url, phone_camera_frame

    while True:
        img_response = requests.get(url + '/shot.jpg')
        img_array = np.array(bytearray(img_response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, 1)
        phone_camera_frame = frame.copy()

# listener function for events on pc camera
def pc_camera_listener(student):
    global pc_camera_frame

    print("In pc listener")

    faceDetector = FaceDetector()
    phoneDetector = YoloDetector('./yoloColoV3')
    file_lines = []

    while True:
        # first handle the face recognition
        image, names = faceDetector.detect(pc_camera_frame)
        if (not names):
            print("no person present")
        else:
            for i in range(len(names)):
                if (names[i] != student):
                    # make log of this
                    file_lines.append("A person different from the actual is present: " + names[i] + ",")

        # now handle the phone detection
        frame, objects = phoneDetector.detect(pc_camera_frame)
        for i in range(len(objects)):
            if (objects[i] == 'cell phone'):
                # make log of this
                file_lines.append("use of cell phone detected,")

        with open('static/log.txt', 'a') as f:
            f.writelines(file_lines)

# listener function for events on phone camera
def phone_camera_listener():
    global phone_camera_frame

    print("In phone listener")

    handDetector = YoloDetector('./yoloHandsTiny')
    phoneDetector = YoloDetector('./yoloColoV3')
    file_lines = []
    hands_gone_period = 0

    while True:
        # first handle the hand detection
        frame, objects = handDetector.detect(pc_camera_frame)
        print(objects)
        if (len(objects) == 1):
            hands_gone_period += 0.5
        elif (not objects):
            hands_gone_period += 1
        elif (len(objects) >= 2):
            hands_gone_period = 0

        if (hands_gone_period > 10):
            hands_gone_period = 0
            # make log of this
            file_lines.append("Hands  were out of sight for longer than 10 seconds,")

        frame, objects = phoneDetector.detect(pc_camera_frame)
        for i in range(len(objects)):
            if (objects[i] == 'cell phone'):
                # make log of this
                file_lines.append("use of cell phone detected,")

        with open('static/log.txt', 'a') as f:
            f.writelines(file_lines)

def freeze_input(duration):
    print("I am freezing")
    ok = windll.user32.BlockInput(True)

    time.sleep(duration)
    ok = windll.user32.BlockInput(False)

@app.route('/')
def index():
    with open('static/students.txt', 'r') as f:
        students = f.read().split(',')

    return render_template('index.html', students=students)

def gen_faces():
    global pc_camera_frame
    faceDetector = FaceDetector()

    timeout = time.time() + 6
    while time.time() < timeout:
        #get camera frame
        frame = pc_camera_frame.copy()
        image, names = faceDetector.detect(frame)
        if not names:
            names.append('No_face_detected')
        yield (names)

def gen_hands():
    global phone_camera_frame
    yoloDetector = YoloDetector('./yoloHandsTiny')

    timeout = time.time() + 6
    while time.time() < timeout:
        #get camera frame
        frame = phone_camera_frame.copy()
        frame, objects = yoloDetector.detect(frame)
        yield (objects)

def gen_logfile():
    with open('static/log.txt', 'r') as file:
        data = file.read()
        yield(data)

# for first time users - demo only
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name'].replace(" ", "_")
        image_path = 'dataset/faces_dataset/' + name
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            with open('static/students.txt', 'a') as f:
                f.write(request.form['name'] + ',')
        else:
            os.rmdir(image_path)
            os.makedirs(image_path)

        file = request.files['image']
        file.save(image_path + '/' + name + '.jpg')

        save_faces()

        return "Succesful upload"
    else:
        return "mwoh just a get request"

# only for demo and develop purposes
@app.route('/video_feed_pc')
def video_feed_pc():
    return Response(gen_pc_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_pc_cam():
    global pc_camera_frame

    while True:
        #get camera frame
        frame = pc_camera_frame.copy()
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# only for demo and develop purposes
@app.route('/video_feed_phone')
def video_feed_phone():
    return Response(gen_phone_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_phone_cam():
    global phone_camera_frame

    while True:
        #get camera frame
        frame = phone_camera_frame.copy()
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# verify pc cam
@app.route('/verify_pc_cam')
def verify_pc_cam():
    global vs

    vs = VideoStream(src=0).start()
    cap = vs.read()

    return Response(json.dumps(cap.tolist()))

# verify phone cam
@app.route('/verify_phone_cam')
def verify_phone_cam():
    img_response = requests.get(url + '/shot.jpg')
    img_array = np.array(bytearray(img_response.content), dtype=np.uint8)
    cap = cv2.imdecode(img_array, 1)

    return Response(json.dumps(cap.tolist()))

# face verification
@app.route('/verify_face', methods=['GET'])
def verify_face():
    # now we actually start storing the pc and phone camera frames
    app.apscheduler.add_job(func=start_pc_camera, trigger='date', id="pc_camera")
    app.apscheduler.add_job(func=start_phone_camera, trigger='date', id="phone_camera")
    time.sleep(2.0)

    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    return Response(json.dumps(gen_faces(), iterable_as_array=True))

# hands verification
@app.route('/verify_hands', methods=['GET'])
def verify_hands():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    return Response(json.dumps(gen_hands(), iterable_as_array=True))

# audio verification
@app.route('/verify_audio', methods=['GET'])
def verify_audio():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    return Response(json.dumps(audio_confidence(url + "/audio.wav"), iterable_as_array=True))

# starting exam
@app.route('/start_exam')
def start_exam():
    student = request.args.get('student')
    print(request.args)

    app.apscheduler.add_job(func=freeze_input, args=[190.0], trigger='date', id="freeze_input")
    app.apscheduler.add_job(func=pc_camera_listener, args=[student], trigger='date', id="pc_camera_listener")
    app.apscheduler.add_job(func=phone_camera_listener, trigger='date', id="phone_camera_listener")

    return Response(json.dumps("Exam started"))

    # send exam here ->

@app.route('/logfile')
def logfile():
    return Response(json.dumps(gen_logfile(), iterable_as_array=True, indent=2))

@app.route('/collect_answers')
def collect_answers():
    global pc_camera_frame

    cv2.imwrite('output/answers.jpg', pc_camera_frame)

    return Response(json.dumps("succesfull upload"))

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return "Server shutting down"

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--ipadress', required=True)
    parser.add_argument('--chromium', required=True)
    parser.add_argument('--killchrome', required=True)
    args = parser.parse_args()

    if (args.killchrome == True):
        t = threading.Thread(target=kill_processes())
        t.start()

    t = threading.Thread(target=start_browser(args.chromium))
    t.start()

    pc_camera_frame = None
    phone_camera_frame = None
    url = "http://" + args.ipadress + ':8080'
    ok = None
    vs = None

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', port=5000, debug=True)

    vs.stop()