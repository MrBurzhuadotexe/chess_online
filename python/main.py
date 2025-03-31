# dwuosobowa gra w szachy w Pythonie z użyciem Pygame!
# część pierwsza, ustaw zmienne, obrazy i pętlę gry
import socket
import json
import pygame
import threading
from variables import *
import gamelogic as gl


timer = pygame.time.Clock()  # Zegar do kontrolowania FPS
fps = 30  # Liczba klatek na sekundę
server_address = ('127.0.0.1', 8080)  # Adres serwera
wait = False  # Flaga oczekiwania na wiadomość
rec_message = None  # Otrzymana wiadomość

# Funkcja do odbierania wiadomości z serwera
def receive_messages(sock):
    global rec_message, wait  # Deklarowanie używanych zmiennych globalnych
    while True:
        rec_message = json.loads(sock.recv(1024).decode())  # Odbieranie i dekodowanie wiadomości
        wait = False  # Ustawienie flagi na false

# Główna pętla gry
run = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Tworzenie gniazda dla komunikacji sieciowej
sock.connect(server_address)  # Łączenie z serwerem
print("Connected to the server.")  # Wydruki do konsoli

role = sock.recv(1).decode()  # Odbieranie roli (czy gracz jest białymi czy czarnymi)

if role == 'b':  # Jeśli czarne
    wait = True  # Ustawienie flagi oczekiwania na wiadomość
    players = ('black', 'white')
    enemy_images = white_images  # Ustawianie obrazów dla wrogich figur
    player_images = black_images  # Ustawiane obrazów dla swoich figur
else:  # Jeśli białe
    players = ('white', 'black')
    enemy_images = black_images  # Ustawianie obrazów dla wrogich figur
    player_images = white_images  # Ustawiane obrazów dla swoich figur
    small_black_images, small_white_images = small_white_images, small_black_images  # Zamiana małych grafik

# Uruchomienie wątku do odbierania wiadomości z serwera
threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

while run:  # Główna pętla gry
    if rec_message is not None:  # Jeśli ktoś przesłał wiadomość
        if rec_message == 'forfeit':
            winner = players[0]
        else:
            played_figure = rec_message[0]  # Figura, która została zagrana
            click_coords = (7 - rec_message[1][0], 7 - rec_message[1][1])  # Obliczanie współrzędnych kliknięcia
            current_enemy_locations[played_figure] = click_coords  # Aktualizacja pozycji figury przeciwnika

            # Sprawdzenie, czy przeciwnik zbił figurę gracza
            if click_coords in current_player_locations:
                captured_piece = current_player_locations.index(click_coords)  # Indeks zbitej figury
                captured_pieces_enemy.append(current_player_pieces[captured_piece])  # Dodanie zbitej figury do listy
                if current_player_pieces[captured_piece] == 'king':
                    winner = 'black'  # Ustawienie zwycięzcy jako czarny, jeśli zabito króla
                current_player_pieces.pop(captured_piece)  # Usunięcie zbitej figury
                current_player_locations.pop(captured_piece)  # Usunięcie pozycji zbitej figury

        rec_message = None  # Zresetowanie odebranej wiadomości

    # Sprawdzanie opcji ruchów dla czarnych
    black_options = gl.check_options(current_player_pieces, current_player_locations)

    timer.tick(fps)  # Kontrola klatek na sekundę
    screen.fill('dark gray')  # Wypełnianie tła
    gl.draw_board()  # Rysowanie planszy
    gl.draw_pieces(enemy_images, player_images)  # Rysowanie figur
    gl.draw_captured()  # Rysowanie zebranych figur
    gl.draw_check()  # Sprawdzanie szachów
    if selection != 100:  # Jeśli figura jest wybrana
        valid_moves = gl.check_valid_moves()  # Sprawdzanie poprawnych ruchów
        gl.draw_valid(valid_moves)  # Rysowanie poprawnych ruchów

    # Przechodzenie przez zdarzenia Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Jeśli gra zostanie zamknięta
            run = False  # Zatrzymaj pętlę gry
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and not wait:
            x_coord = event.pos[0] // 100  # Obliczanie pozycji na planszy w poziomie
            y_coord = event.pos[1] // 100  # Obliczanie pozycji na planszy w pionie
            click_coords = (x_coord, y_coord)  # Ustawienie współrzędnych kliknięcia

            if click_coords == (8, 8) or click_coords == (9, 8):  # Sprawdzenie, czy gracz zrzekł się
                winner = players[1]
                message = json.dumps('forfeit')
                sock.sendall(message.encode())

            if click_coords in current_player_locations:  # Jeśli kliknięto na figurę gracza
                selection = current_player_locations.index(click_coords)  # Ustawienie wybranej figury

            if click_coords in valid_moves and selection != 100:  # Jeśli kliknięto na poprawny ruch
                current_player_locations[selection] = click_coords  # Zaktualizowanie pozycji figury
                if click_coords in current_enemy_locations:  # Jeśli zbito figurę przeciwnika
                    white_piece = current_enemy_locations.index(click_coords)  # Indeks zbitej figury
                    captured_pieces_player.append(current_enemy_pieces[white_piece])  # Dodawanie do zebranych figur
                    if current_enemy_pieces[white_piece] == 'king':
                        winner = 'black'  # Ustawienie zwycięzcy jako czarny, jeśli zbito króla
                    current_enemy_pieces.pop(white_piece)  # Usunięcie zbitej figury
                    current_enemy_locations.pop(white_piece)  # Usunięcie pozycji zbitej figury

                    # Przesyłanie wiadomości do serwera
                message = json.dumps([selection, click_coords])  # Przygotowanie wiadomości do wysłania
                sock.sendall(message.encode())  # Wysłanie wiadomości
                wait = True  # Ustawienie flagi oczekiwania

                selection = 100  # Resetowanie wyboru figury
                valid_moves = []  # Resetowanie listy poprawnych ruchów
        if event.type == pygame.KEYDOWN and game_over:  # Jeśli gra zakończona, sprawdzanie naciśnięcia klawisza
            if event.key == pygame.K_RETURN:  # Jeśli naciśnięto ENTER
                game_over = False  # Resetowanie flagi końca gry
                winner = ''  # Resetowanie zwycięzcy
                # Resetowanie pozycji i figur
                current_enemy_pieces = list(start_enemy_pieces)
                current_enemy_locations = list(start_enemy_locations)
                current_player_locations = list(start_player_locations)
                current_player_pieces = list(start_player_pieces)
                captured_pieces_enemy = []  # Resetowanie zebranych figur przeciwnika
                captured_pieces_player = []  # Resetowanie zebranych figur gracza
                selection = 100  # Resetowanie wyboru figury
                valid_moves = []  # Resetowanie listy poprawnych ruchów
                black_options = gl.check_options(current_player_pieces,
                                              current_player_locations)  # Sprawdzanie opcji ruchów
                if role == 'b':
                    wait = True
                else:
                    wait = Falsecurrent_enemy_pieces = list(start_enemy_pieces)
        if winner != '':  # Jeśli jest zwycięzca
            game_over = True  # Ustawienie flagi końca gry
            gl.draw_game_over()  # Rysowanie komunikatu o zakończeniu gry

        pygame.display.flip()  # Aktualizacja ekranu

pygame.quit()  # Zamykanie Pygame
