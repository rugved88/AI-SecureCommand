import time
import threading
from scapy.all import *
from datetime import datetime

def send_udp_message(ip, port, spoofed_ip, stop_event):
    """ Sends UDP messages every 30 seconds to the specified IP and port, including normal operation details. """
    while not stop_event.is_set():
        # The message is now included in the attack details
        send_attack_details(ip, port, 'Normal - No Attack', spoofed_ip, True, 1, "Bot go up")
        time.sleep(3)  # Sleep for 3 seconds in this example, adjust as needed

def send_attack_details(ip, port, attack_type, spoofed_ip, success, num_packets, payload_message):
    """ Sends details of the "attack" (normal operation) to main2.py using a spoofed IP, including the original message as part of the payload """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"Attack Type: {attack_type}, Message: {payload_message}"
    packet = IP(src=spoofed_ip, dst=ip) / UDP(dport=port, sport=RandShort()) / Raw(load=message.encode())
    send(packet, verbose=0)
    print(f"Details sent from spoofed IP {spoofed_ip} to {ip}:{port} - {message}")

def monitor_quit(stop_event):
    """ Monitors for the quit command from the user input. """
    print("Press 'q' then Enter to quit:")
    while not stop_event.is_set():
        if input() == 'q':
            stop_event.set()

if __name__ == "__main__":
    target_ip = "192.168.42.170"
    target_port = 8080
    spoofed_ip = "192.168.1.170"  # The IP address to use for spoofing
    stop_event = threading.Event()

    # Start the sender thread
    sender_thread = threading.Thread(target=send_udp_message, args=(target_ip, target_port, spoofed_ip, stop_event))
    sender_thread.start()

    # Start the monitor thread and wait for 'q' to quit
    monitor_quit(stop_event)

    # Wait for the sender thread to complete before exiting the program
    sender_thread.join()
    print("Stopped sending and exiting the program.")
