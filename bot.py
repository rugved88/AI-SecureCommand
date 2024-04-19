import socket
import threading
import pygame
import queue
import csv
import random
from datetime import datetime

def listen_udp(port, stop_event, command_queue, csv_file, csv_writer):
    """ Listens for UDP messages on the specified port and adds commands to a queue while logging them to a CSV file. """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('', port))
        print(f"Listening on port {port}...")

        while not stop_event.is_set():
            try:
                sock.settimeout(1)
                data, addr = sock.recvfrom(1024)
                if data:
                    command = data.decode('utf-8').strip().lower()
                    print(f"Received command: {command} from {addr}")
                    command_queue.put(command)  # Put command in queue
                    # Log to CSV
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    csv_writer.writerow([current_time, command, addr[0], addr[1]])
                    csv_file.flush()
            except socket.timeout:
                continue

def game_loop(command_queue, stop_event):
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Bot Game')

    # Load font for text rendering
    font = pygame.font.Font(None, 36)

    # Define variables at this level so they're accessible in reset_game
    step_size = 10
    bot = pygame.Rect(300, 220, 50, 50)
    destination = pygame.Rect(random.randint(0, 590), random.randint(0, 430), 50, 50)
    min_steps = (abs(destination.x - bot.x) + abs(destination.y - bot.y)) // step_size
    steps_taken = 0

    def reset_game():
        """ Resets the game with new destination and counters. """
        nonlocal bot, destination, min_steps, steps_taken
        bot = pygame.Rect(300, 220, 50, 50)
        destination = pygame.Rect(random.randint(0, 590), random.randint(0, 430), 50, 50)
        min_steps = (abs(destination.x - bot.x) + abs(destination.y - bot.y)) // step_size
        steps_taken = 0

    clock = pygame.time.Clock()
    score_display_time = 0

    while not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()

        while not command_queue.empty():
            command = command_queue.get()
            if 'up' in command and bot.y > 0:
                bot.move_ip(0, -step_size)
                steps_taken += 1
            elif 'down' in command and bot.y < 430:
                bot.move_ip(0, step_size)
                steps_taken += 1
            elif 'left' in command and bot.x > 0:
                bot.move_ip(-step_size, 0)
                steps_taken += 1
            elif 'right' in command and bot.x < 590:
                bot.move_ip(step_size, 0)
                steps_taken += 1

        screen.fill((0, 0, 0))  # Clear screen with black
        pygame.draw.rect(screen, (255, 255, 255), bot)  # Draw bot
        pygame.draw.rect(screen, (0, 255, 0), destination)  # Draw destination

        if bot.colliderect(destination):
            if score_display_time == 0:
                score_display_time = pygame.time.get_ticks()
            text = font.render(f"Reached in {steps_taken} steps, minimum was {min_steps}.", True, (255, 0, 0))
            screen.blit(text, (10, 50))
            if pygame.time.get_ticks() - score_display_time > 5000:  # Display score for 5 seconds
                reset_game()
                score_display_time = 0
        else:
            text = font.render(f"Steps: {steps_taken} | Min Steps: {min_steps}", True, (255, 255, 255))
            screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()

if __name__ == "__main__":
    listening_port = 8080
    stop_event = threading.Event()
    command_queue = queue.Queue()

    # Open a CSV file for writing
    with open('udp_commands.csv', mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        # Write the header if it's a new file and if the file is empty
        if file.tell() == 0:
            csv_writer.writerow(['Time', 'Command', 'Host IP', 'Destination Port'])
            file.flush()

        # Start the listener thread
        listener_thread = threading.Thread(target=listen_udp, args=(listening_port, stop_event, command_queue, file, csv_writer))
        listener_thread.start()

        # Start game loop in main thread
        game_loop(command_queue, stop_event)

        # Wait for the listener thread to complete before exiting
        listener_thread.join()
    print("Game has been stopped.")
