import cv2 
import socket
import struct 
import pickle
from pynput.keyboard import Key, Listener, Controller
import threading
import sys 


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
streaming = True
break_streaming = False
HOST = socket.gethostname()
PORT = 8081

s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()


data = b""
payload_size = struct.calcsize("L")

keyboard = Controller()

def get_keyboard_input():
    global streaming
    def on_press(key):
        global streaming 
        if key == Key.esc:
            print(streaming)
            streaming = False
            break_streaming = True
            return False
            
    with Listener(on_press=on_press) as listener:
        listener.join()

keypresses = threading.Thread(target=get_keyboard_input)
keypresses.start()

while streaming:
    while len(data) < payload_size and not break_streaming:
        data += conn.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]
    
    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)

    cv2.imshow("frame", frame)
    cv2.waitKey(1)

conn.close()
print("ENDING STREAM")
cv2.destroyAllWindows()
