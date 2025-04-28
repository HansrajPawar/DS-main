# server.py

'''
Berkeley Algorithm Theory:

- Goal: Synchronize all the clocks in a distributed system to have almost the same time.
- Unlike NTP (where clients adjust based on a known good server), Berkeley assumes all clocks (even server's) are equally unreliable.
- Process:
    1. Server polls all clients for their current time.
    2. Each client sends back its local time.
    3. Server computes the time differences.
    4. Server calculates an average difference.
    5. Server sends an adjustment to all clients (and itself) based on this average.
'''

from functools import reduce
from dateutil import parser
import threading
import socket
import time
import datetime

# Global data structure to store client details:
# Each client has: {address: {"clock_time": ..., "time_difference": ..., "connector": ...}}
client_data = {}

# Function to receive the clock time from a connected client
def startReceivingClockTime(connector, address):
    while True:
        try:
            # Receive client's current time as string
            clock_time_string = connector.recv(1024).decode()
            if not clock_time_string:
                break  # if nothing received, connection is closed

            # Parse string to datetime object
            clock_time = parser.parse(clock_time_string)
            
            # Calculate the time difference: (Server time - Client time)
            clock_time_diff = datetime.datetime.now() - clock_time
            
            # Update client_data dictionary
            client_data[address] = {
                "clock_time": clock_time,
                "time_difference": clock_time_diff,
                "connector": connector
            }
            print(f"[{datetime.datetime.now()}] Client {address} time updated.")
            time.sleep(5)  # wait 5 seconds before next time reading
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error receiving from {address}: {e}")
            connector.close()
            if address in client_data:
                del client_data[address]
            break

# Function to accept incoming client connections
def startConnecting(master_server):
    while True:
        # Accept new client connection
        master_slave_connector, addr = master_server.accept()
        slave_address = f"{addr[0]}:{addr[1]}"
        print(f"[{datetime.datetime.now()}] {slave_address} connected.")

        # Start a separate thread for each client to receive time
        current_thread = threading.Thread(
            target=startReceivingClockTime,
            args=(master_slave_connector, slave_address),
            daemon=True
        )
        current_thread.start()

# Function to compute average clock difference among all clients
def getAverageClockDiff():
    if not client_data:
        return datetime.timedelta(0)  # if no clients, return zero

    # Get the list of all time differences
    time_difference_list = [
        client['time_difference'] for client in client_data.values()
    ]

    # Sum all the differences
    sum_of_clock_difference = reduce(
        lambda x, y: x + y, time_difference_list, datetime.timedelta()
    )

    # Average = sum / number of clients
    return sum_of_clock_difference / len(client_data)

# Function to synchronize all connected clients periodically
def synchronizeAllClocks():
    while True:
        if client_data:
            print(f"\n[{datetime.datetime.now()}] New synchronization cycle started.")
            print(f"Number of clients to synchronize: {len(client_data)}")

            # Calculate the average clock difference
            average_clock_difference = getAverageClockDiff()

            for client_addr, client in list(client_data.items()):
                try:
                    # Adjust server's time by the average difference
                    synchronized_time = datetime.datetime.now() + average_clock_difference

                    # Send the synchronized time back to the client
                    client['connector'].send(str(synchronized_time).encode())
                    print(f"Sent synchronized time to {client_addr}")
                except Exception as e:
                    print(f"Error sending time to {client_addr}: {e}")
                    client['connector'].close()
                    del client_data[client_addr]
        else:
            print(f"[{datetime.datetime.now()}] No clients to synchronize.")

        time.sleep(10)  # wait 10 seconds before next synchronization cycle

# Function to start the server
def initiateClockServer(port=8080):
    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master_server.bind(('', port))
    master_server.listen(10)  # Server ready to accept clients
    print(f"[{datetime.datetime.now()}] Clock server started on port {port}.\n")
    
    # Start threads to connect clients and synchronize clocks
    threading.Thread(target=startConnecting, args=(master_server,), daemon=True).start()
    threading.Thread(target=synchronizeAllClocks, daemon=True).start()

    # Keep the main server thread running forever
    while True:
        time.sleep(1)

# Entry point
if __name__ == '__main__':
    initiateClockServer(port=8080)
