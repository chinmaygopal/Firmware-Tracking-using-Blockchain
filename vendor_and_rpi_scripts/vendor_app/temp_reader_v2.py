#!/usr/bin/env python3
import socket
import time
def inform_completion():
    # Create a socket object
    s = socket.socket()
    # Define the port on which you want to connect
    port = 12345
    # connect to the server on local computer

    try:
        s.connect(('127.0.0.1', port))
        # close the connection
        s.close()
        time.sleep(5)
    except socket.error:
        print("No Download available")


import gpiozero as gz
cpu_temp = gz.CPUTemperature().temperature
while True:
    time.sleep(3)
    cpu_temp = round(cpu_temp, 1)
    with open("temperature_file.txt", "a+") as file:
        file.write("Hello this is full temp: "+str(cpu_temp)+"\n")
    print("es geht es mir gut!!")
    print(cpu_temp)
    inform_completion()
