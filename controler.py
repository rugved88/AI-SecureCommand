import time
import threading
from scapy.all import *
from datetime import datetime
import keyboard  # Import the keyboard module for capturing key presses

def send_udp_message(ip, port, stop_event):
    """ Sends UDP messages to the specified IP and port based on keyboard inputs. """
    print("Press 'up', 'down', 'left', 'right' to control the bot. Press 'q' to quit.")
    while not stop_event.is_set():
        try:
            if keyboard.is_pressed('up'):
                send_attack_details(ip, port, 'Normal - No Attack', True, 1, "up")
            elif keyboard.is_pressed('down'):
                send_attack_details(ip, port, 'Normal - No Attack', True, 1, "down")
            elif keyboard.is_pressed('left'):
                send_attack_details(ip, port, 'Normal - No Attack', True, 1, "left")
            elif keyboard.is_pressed('right'):
                send_attack_details(ip, port, 'Normal - No Attack', True, 1, "right")
            time.sleep(0.1)  # A short delay to prevent high CPU usage
        except RuntimeError:
            continue  # Handles the exception thrown when the main thread is interrupted

def send_attack_details(ip, port, attack_type, success, num_packets, payload_message):
    """ Sends details of the operation to the target IP using the default source IP, including the original message as part of the payload """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"Attack Type: {attack_type}, Message: {payload_message}"
    packet = IP(dst=ip) / UDP(dport=port, sport=RandShort()) / Raw(load=message.encode())
    send(packet, verbose=0)
    print(f"Details sent to {ip}:{port} - {message}")

def monitor_quit(stop_event):
    """ Monitors for the quit command from the user input. """
    while not stop_event.is_set():
        if keyboard.is_pressed('q'):
            stop_event.set()
            print("Quitting the program...")

if __name__ == "__main__":
    target_ip = "192.168.15.170"
    target_port = 8080
    stop_event = threading.Event()

    # Start the sender thread
    sender_thread = threading.Thread(target=send_udp_message, args=(target_ip, target_port, stop_event))
    sender_thread.start()

    # Use monitor_quit function to handle quit operation
    monitor_quit(stop_event)

    # Wait for the sender thread to complete before exiting the program
    sender_thread.join()
    print("Stopped sending and exiting the program.")
