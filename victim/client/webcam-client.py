import socket
import cv2
import base64
import numpy as np
import pickle 
import struct
import os
import threading
import sys


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostname()
PORT = 8081
streaming = True
s.connect((HOST, PORT))
cap = cv2.VideoCapture(0)

while True:
    try:
        ret, frame=cap.read()
        data = pickle.dumps(frame)
        message_size = struct.pack("L", len(data))
        s.send(message_size + data)
    except:
        break

cap.release()
sys.exit()

    


