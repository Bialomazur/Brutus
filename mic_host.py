import pyaudio
import socket
import select
from pynput.keyboard import Key, Listener, Controller
import threading


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
HOST = socket.gethostname()
PORT = 8082

streaming = True

audio = pyaudio.PyAudio()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)


def get_keyboard_input():
    global streaming
    def on_press(key):
        global streaming
        if key == Key.esc:
            streaming = False
            return False

    with Listener(on_press=on_press) as listener:
        listener.join()

keypresses = threading.Thread(target=get_keyboard_input)
keypresses.start()

try:
    while streaming:
        data = conn.recv(CHUNK)
        stream.write(data)
except KeyboardInterrupt:
    print("Killing connection")


s.close()
stream.close()
audio.terminate()
    

