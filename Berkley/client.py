# client.py

'''
Client Behavior in Berkeley Algorithm:

- Each client:
    1. Sends its local clock time to the server.
    2. Waits to receive the new synchronized time from the server.
    3. (In a real system, it would adjust its clock based on synchronized time.)
'''

from dateutil import parser
import threading
import datetime
import socket
import time

# Function to send local time to server periodically
def startSendingTime(slave_client):
    while True:
        try:
            # Send current local datetime as a string
            slave_client.send(str(datetime.datetime.now()).encode())
            print(f"[{datetime.datetime.now()}] Local time sent to server.")
            time.sleep(5)  # wait 5 seconds before sending again
        except Exception as e:
            print(f"Error sending local time: {e}")
            slave_client.close()
            break

# Function to receive synchronized time from server
def startReceivingTime(slave_client):
    while True:
        try:
            # Receive synchronized time from server
            synchronized_time_string = slave_client.recv(1024).decode()
            if not synchronized_time_string:
                break  # server closed connection

            # Parse synchronized time and display
            synchronized_time = parser.parse(synchronized_time_string)
            print(f"[{datetime.datetime.now()}] Synchronized time: {synchronized_time}")
        except Exception as e:
            print(f"Error receiving synchronized time: {e}")
            slave_client.close()
            break

# Function to start the client and connect to server
def initiateSlaveClient(port=8080):
    slave_client = socket.socket()
    try:
        # Connect to the clock server (localhost)
        slave_client.connect(('127.0.0.1', port))
        print(f"[{datetime.datetime.now()}] Connected to Clock Server.\n")
    except Exception as e:
        print(f"Connection to server failed: {e}")
        return
    
    # Start separate threads for sending and receiving time
    threading.Thread(target=startSendingTime, args=(slave_client,), daemon=True).start()
    threading.Thread(target=startReceivingTime, args=(slave_client,), daemon=True).start()

    # Keep client main thread alive
    while True:
        time.sleep(1)

# Entry point
if __name__ == '__main__':
    initiateSlaveClient(port=8080)
