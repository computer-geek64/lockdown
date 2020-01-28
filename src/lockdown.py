#!/usr/bin/python3
# lockdown.py

import os
import sys
import cv2
import notify2
import face_recognition
from time import sleep
from subprocess import Popen, PIPE


if len(sys.argv) != 2:
    print("Lockdown v1.1")
    print("Copyright 2020 Ashish D'Souza. All rights reserved.")
    print("Usage: lockdown.py [directory]")
    exit(0)

threshold = 5
sleep_time = 3

known_images = [os.path.join(sys.argv[1], x) for x in next(os.walk(sys.argv[1]))[2]]
known_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(x))[0] for x in known_images]

notify2.init("Lockdown")
unauthorized = 0
while True:
    if unauthorized == threshold - 1:
        notify2.Notification("Lockdown", "Locking in " + str(sleep_time) + " seconds...").show()
    if unauthorized >= threshold:
        Popen(["gnome-screensaver-command", "--lock"], stdout=PIPE, stderr=PIPE)
        unauthorized = 0
        sleep(5)
        while "inactive" not in Popen(["gnome-screensaver-command", "-q"], stdout=PIPE, stderr=PIPE).communicate()[0].decode():
            sleep(10)
    sleep(sleep_time)
    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()
    capture.release()
    frame = cv2.flip(frame, 1)

    unknown_encoding = face_recognition.face_encodings(frame)
    capture.release()
    if len(unknown_encoding) == 0:
        print("No faces")
        unauthorized += 1
        continue

    results = face_recognition.compare_faces(known_encodings, unknown_encoding[0])

    if int(0.6 * len(known_images)) <= sum(results):
        print("Authorized: ", end="")
        unauthorized = 0
    else:
        print("Unauthorized: ", end="")
        unauthorized += 1
    print(results)
