from variables import *


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
    options_list = player_options  # Lista opcji ruchów dla czarnych
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
        for i in range(len(player_options)):
            if king_location in player_options[i]:  # Sprawdzanie opcji
                pygame.draw.rect(screen, 'dark red', [current_enemy_locations[king_index][0] * 100 + 1,
                                                      current_enemy_locations[king_index][1] * 100 + 1, 100, 100], 5)  # Rysowanie prostokąta

# Funkcja rysująca końcowy komunikat o grze
def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])  # Rysowanie prostokąta
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))  # Wyświetlanie zwycięzcy
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))  # Instrukcja restartu
