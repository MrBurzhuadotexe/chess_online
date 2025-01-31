# dwuosobowa gra w szachy w Pythonie z użyciem Pygame!
# część pierwsza, ustaw zmienne, obrazy i pętlę gry
import socket
import json
import pygame
import threading

pygame.init()  # Inicjalizacja Pygame
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])  # Ustawienie rozmiaru okna gry
pygame.display.set_caption('Two-Player Pygame Chess!')  # Tytuł okna
font = pygame.font.Font('freesansbold.ttf', 20)  # Czcionka dla tekstu
medium_font = pygame.font.Font('freesansbold.ttf', 40)  # Średnia czcionka
big_font = pygame.font.Font('freesansbold.ttf', 50)  # Duża czcionka
timer = pygame.time.Clock()  # Zegar do kontrolowania FPS
fps = 30  # Liczba klatek na sekundę
server_address = ('127.0.0.1', 8080)  # Adres serwera
wait = False  # Flaga oczekiwania na wiadomość
rec_message = None  # Otrzymana wiadomość

# Inicjalizacja pozycji i nazw figur szachowych dla obu graczy
start_enemy_pieces = ('rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                      'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn')
start_enemy_locations = ((7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0),
                         (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1))

start_player_locations = ((0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                          (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6))
start_player_pieces = ('rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                       'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn')

# Zmienne gry i obrazy figur
current_enemy_pieces = list(start_enemy_pieces)
current_enemy_locations = list(start_enemy_locations)
current_player_locations = list(start_player_locations)
current_player_pieces = list(start_player_pieces)

captured_pieces_enemy = []  # Przechwycone figury przez przeciwnika
captured_pieces_player = []  # Przechwycone figury przez gracza
# 0 - tura białych bez wyboru: 1 - tura białych z wybraną figurą: 2 - tura czarnych bez wyboru, 3 - tura czarnych z wybraną figurą
selection = 100
valid_moves = []  # Lista poprawnych ruchów

# Ładowanie obrazów figur szachowych
# Czarne figury
black_queen = pygame.image.load('assets/images/black queen.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))  # Zmiana rozmiaru
black_queen_small = pygame.transform.scale(black_queen, (45, 45))
black_king = pygame.image.load('assets/images/black king.png')
black_king = pygame.transform.scale(black_king, (80, 80))
black_king_small = pygame.transform.scale(black_king, (45, 45))
black_rook = pygame.image.load('assets/images/black rook.png')
black_rook = pygame.transform.scale(black_rook, (80, 80))
black_rook_small = pygame.transform.scale(black_rook, (45, 45))
black_bishop = pygame.image.load('assets/images/black bishop.png')
black_bishop = pygame.transform.scale(black_bishop, (80, 80))
black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
black_knight = pygame.image.load('assets/images/black knight.png')
black_knight = pygame.transform.scale(black_knight, (80, 80))
black_knight_small = pygame.transform.scale(black_knight, (45, 45))
black_pawn = pygame.image.load('assets/images/black pawn.png')
black_pawn = pygame.transform.scale(black_pawn, (65, 65))
black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))

# Białe figury
white_queen = pygame.image.load('assets/images/white queen.png')
white_queen = pygame.transform.scale(white_queen, (80, 80))
white_queen_small = pygame.transform.scale(white_queen, (45, 45))
white_king = pygame.image.load('assets/images/white king.png')
white_king = pygame.transform.scale(white_king, (80, 80))
white_king_small = pygame.transform.scale(white_king, (45, 45))
white_rook = pygame.image.load('assets/images/white rook.png')
white_rook = pygame.transform.scale(white_rook, (80, 80))
white_rook_small = pygame.transform.scale(white_rook, (45, 45))
white_bishop = pygame.image.load('assets/images/white bishop.png')
white_bishop = pygame.transform.scale(white_bishop, (80, 80))
white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
white_knight = pygame.image.load('assets/images/white knight.png')
white_knight = pygame.transform.scale(white_knight, (80, 80))
white_knight_small = pygame.transform.scale(white_knight, (45, 45))
white_pawn = pygame.image.load('assets/images/white pawn.png')
white_pawn = pygame.transform.scale(white_pawn, (65, 65))
white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))

# Listy obrazów figur
white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                      black_rook_small, black_bishop_small]
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']  # Lista typów figur

# Zmienne do sprawdzania i końca gry
winner = ''  # Zmienna do przechowywania zwycięzcy
game_over = False  # Flaga końca gry


# Funkcja do rysowania głównej planszy gry
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        # Rysowanie kwadratów planszy
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])  # Rysowanie dolnego panelu
    pygame.draw.rect(screen, 'black', [0, 800, WIDTH, 100], 5)  # Złota ramka dolnego panelu
    pygame.draw.rect(screen, 'black', [800, 0, 200, HEIGHT], 5)  # Złota ramka prawego panelu

    # Status gry
    status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                   'Black: Select a Piece to Move!', 'Black: Select a Destination!']

    # Rysowanie linii planszy
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)  # Rysowanie poziomych linii planszy
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)  # Rysowanie pionowych linii planszy
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))  # Tekst "FORFEIT" w dolnym prawym rogu


def draw_pieces(enemy_images, player_images):
    # Rysowanie figur przeciwnika
    for i in range(len(current_enemy_pieces)):
        index = piece_list.index(current_enemy_pieces[i])
        if current_enemy_pieces[i] == 'pawn':
            screen.blit(enemy_images[0],
                        (current_enemy_locations[i][0] * 100 + 22, current_enemy_locations[i][1] * 100 + 30))
        else:
            screen.blit(enemy_images[index],
                        (current_enemy_locations[i][0] * 100 + 10, current_enemy_locations[i][1] * 100 + 10))

    # Rysowanie figur gracza
    for i in range(len(current_player_pieces)):
        index = piece_list.index(current_player_pieces[i])
        if current_player_pieces[i] == 'pawn':
            screen.blit(player_images[0],
                        (current_player_locations[i][0] * 100 + 22, current_player_locations[i][1] * 100 + 30))
        else:
            screen.blit(player_images[index],
                        (current_player_locations[i][0] * 100 + 10, current_player_locations[i][1] * 100 + 10))

        # Rysowanie prostokąta zaznaczającego wybraną figurę
        if selection == i:
            pygame.draw.rect(screen, 'blue',
                             [current_player_locations[i][0] * 100 + 1, current_player_locations[i][1] * 100 + 1,
                              100, 100], 2)


# Funkcja sprawdzająca możliwe ruchy figur na planszy
def check_options(pieces, locations):
    moves_list = []  # Lista ruchów dla każdej figury
    all_moves_list = []  # Lista wszystkich ruchów
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        # Sprawdzanie ruchów w zależności od typu figury
        if piece == 'pawn':
            moves_list = check_pawn(location)
        elif piece == 'rook':
            moves_list = check_rook(location)
        elif piece == 'knight':
            moves_list = check_knight(location)
        elif piece == 'bishop':
            moves_list = check_bishop(location)
        elif piece == 'queen':
            moves_list = check_queen(location)
        elif piece == 'king':
            moves_list = check_king(location)
        all_moves_list.append(moves_list)  # Dodanie ruchów do listy
    return all_moves_list  # Zwrócenie wszystkich możliwych ruchów


def check_queen(position):
    moves_list = check_bishop(position)
    second_list = check_rook(position)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


def check_bishop(position):
    moves_list = []
    friends_list = current_player_locations
    enemies_list = current_enemy_locations
    for i in range(4):  # up-right, up-left, down-right, down-left
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


# Funkcje sprawdzające ruchy dla poszczególnych typów figur:
# Sprawdzanie możliwych ruchów królem
def check_king(position):
    moves_list = []  # Lista możliwych ruchów
    friends_list = current_player_locations  # Pozycje przyjaciół (figur gracza)
    enemies_list = current_enemy_locations  # Pozycje wrogów (figur przeciwnika)

    # Możliwe ruchy króla w 8 kierunkach
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        # Sprawdzenie, czy ruch jest możliwy
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list  # Zwrócenie listy możliwych ruchów


# Funkcja sprawdzająca możliwe ruchy wieżą
def check_rook(position):
    moves_list = []  # Lista możliwych ruchów
    friends_list = current_player_locations  # Pozycje przyjaciół (figur gracza)
    enemies_list = current_enemy_locations  # Pozycje wrogów (figur przeciwnika)

    for i in range(4):  # Sprawdzenie kierunków: w dół, w górę, w prawo, w lewo
        path = True  # Flaga do monitorowania, czy ścieżka jest wolna
        chain = 1  # Liczba kroków
        # Ustawienie kierunków
        if i == 0:
            x = 0
            y = 1  # W dół
        elif i == 1:
            x = 0
            y = -1  # W górę
        elif i == 2:
            x = 1
            y = 0  # W prawo
        else:
            x = -1
            y = 0  # W lewo
        # Pętla przeszukująca możliwe ruchy
        while path:
            if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                    0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))  # Dodaj możliwy ruch
                if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                    path = False  # Zatrzymaj szukanie, gdy napotkano figurę przeciwnika
                chain += 1  # Zwiększ liczbę kroków
            else:
                path = False  # Zatrzymaj, gdy napotkano figurę lub wyszedł poza planszę
    return moves_list  # Zwrócenie listy możliwych ruchów

def check_pawn(position):
    moves_list = []  # Lista możliwych ruchów
    # Sprawdzenie ruchu do przodu
    if (position[0], position[1] - 1) not in current_enemy_locations and \
            (position[0], position[1] - 1) not in current_player_locations and position[1] > 0:
        moves_list.append((position[0], position[1] - 1))  # Dodanie ruchu o 1 do przodu
    # Sprawdzenie ruchu o 2 pola do przodu, jeśli pionek znajduje się na pozycji startowej
    if (position[0], position[1] - 2) not in current_enemy_locations and \
            (position[0], position[1] - 2) not in current_player_locations and position[1] == 6:
        moves_list.append((position[0], position[1] - 2))  # Dodanie ruchu o 2 pola do przodu
    # Sprawdzenie ruchów bijących
    if (position[0] + 1, position[1] - 1) in current_enemy_locations:
        moves_list.append((position[0] + 1, position[1] - 1))  # Dodanie ruchu bijącego w prawo
    if (position[0] - 1, position[1] - 1) in current_enemy_locations:
        moves_list.append((position[0] - 1, position[1] - 1))  # Dodanie ruchu bijącego w lewo
    return moves_list  # Zwrócenie listy możliwych ruchów


def check_knight(position):
    moves_list = []  # Lista możliwych ruchów
    friends_list = current_player_locations  # Pozycje przyjaciół
    enemies_list = current_enemy_locations  # Pozycje wrogów

    # Możliwe kierunki skoczka
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])  # Obliczanie potencjalnego celu

        # Sprawdzenie, czy ruch jest możliwy (nie może być na figury przyjaciół oraz musi być w granicach planszy)
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)  # Dodanie możliwego ruchu do listy

    return moves_list


def check_valid_moves():
    options_list = black_options  # Lista opcji ruchów dla czarnych
    valid_options = options_list[selection]  # Zwrócenie opcji dla wybranej figury
    return valid_options

# Funkcja rysująca poprawne ruchy na ekranie
def draw_valid(moves):
    color = 'blue'  # Kolor do wyświetlania
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)  # Rysowanie kółek

# Funkcja rysująca zebrane figury na boku ekranu
def draw_captured():
    # Rysowanie zebranych figur przeciwnika
    for i in range(len(captured_pieces_enemy)):
        captured_piece = captured_pieces_enemy[i]  # Figura przeciwnika
        index = piece_list.index(captured_piece)  # Indeks figury na liście figur
        screen.blit(small_black_images[index], (825, 5 + 50 * i))  # Rysowanie zebranej figury

    # Rysowanie zebranych figur gracza
    for i in range(len(captured_pieces_player)):
        captured_piece = captured_pieces_player[i]  # Figura gracza
        index = piece_list.index(captured_piece)  # Indeks figury na liście figur
        screen.blit(small_white_images[index], (925, 5 + 50 * i))  # Rysowanie zebranej figury

# Funkcja rysująca migający prostokąt wokół króla, jeśli jest w szachu
def draw_check():
    if 'king' in current_enemy_pieces:
        king_index = current_enemy_pieces.index('king')  # Znajdowanie króla
        king_location = current_enemy_locations[king_index]  # Pozycja króla
        for i in range(len(black_options)):
            if king_location in black_options[i]:  # Sprawdzanie opcji
                pygame.draw.rect(screen, 'dark red', [current_enemy_locations[king_index][0] * 100 + 1,
                                                      current_enemy_locations[king_index][1] * 100 + 1, 100, 100], 5)  # Rysowanie prostokąta

# Funkcja rysująca końcowy komunikat o grze
def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])  # Rysowanie prostokąta
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))  # Wyświetlanie zwycięzcy
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))  # Instrukcja restartu

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
    black_options = check_options(current_player_pieces, current_player_locations)

    timer.tick(fps)  # Kontrola klatek na sekundę
    screen.fill('dark gray')  # Wypełnianie tła
    draw_board()  # Rysowanie planszy
    draw_pieces(enemy_images, player_images)  # Rysowanie figur
    draw_captured()  # Rysowanie zebranych figur
    draw_check()  # Sprawdzanie szachów
    if selection != 100:  # Jeśli figura jest wybrana
        valid_moves = check_valid_moves()  # Sprawdzanie poprawnych ruchów
        draw_valid(valid_moves)  # Rysowanie poprawnych ruchów

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
                black_options = check_options(current_player_pieces,
                                              current_player_locations)  # Sprawdzanie opcji ruchów
                if role == 'b':
                    wait = True
                else:
                    wait = Falsecurrent_enemy_pieces = list(start_enemy_pieces)
        if winner != '':  # Jeśli jest zwycięzca
            game_over = True  # Ustawienie flagi końca gry
            draw_game_over()  # Rysowanie komunikatu o zakończeniu gry

        pygame.display.flip()  # Aktualizacja ekranu

pygame.quit()  # Zamykanie Pygame
