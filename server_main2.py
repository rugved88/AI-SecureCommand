import socket
import threading
import csv
from datetime import datetime

def listen_udp(port, stop_event, csv_file, csv_writer):
    """ Listens for UDP messages on the specified port and logs them to a CSV file. """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', port))
        print(f"Listening on port {port}...")

        while not stop_event.is_set():
            try:
                sock.settimeout(1)  # Set timeout to check stop_event periodically
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                if data:
                    try:
                        message = data.decode('utf-8')
                    except UnicodeDecodeError:
                        message = f"Attack: Received non-UTF-8 data: {data.hex()}"
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Received message: {message} from IP {addr[0]}, Port {addr[1]}")
                    # Write to CSV file and flush
                    csv_writer.writerow([current_time, message, addr[0], addr[1]])
                    csv_file.flush()
            except socket.timeout:
                continue  # Just to handle the timeout and check the loop condition again

def monitor_quit(stop_event):
    """ Monitors for the quit command from the user input. """
    print("Press 'q' then Enter to quit:")
    while True:
        if input() == 'q':
            stop_event.set()
            break

if __name__ == "__main__":
    listening_port = 8080
    stop_event = threading.Event()

    # Open a CSV file for writing
    with open('udp_messages.csv', mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        # Write the header if it's a new file and if the file is empty
        if file.tell() == 0:
            csv_writer.writerow(['Time', 'Message', 'Host IP', 'Destination Port'])

        # Start the listener thread
        listener_thread = threading.Thread(target=listen_udp, args=(listening_port, stop_event, file, csv_writer))
        listener_thread.start()

        # Start the monitor thread and wait for 'q' to quit
        monitor_quit(stop_event)

        # Wait for the listener thread to complete before exiting the program
        listener_thread.join()
    print("Stopped listening and exiting the program.")
