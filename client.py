# two player chess in python with Pygame!
# part one, set up variables images and game loop
import socket
import json
import pygame
import threading

pygame.init()
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Two-Player Pygame Chess!')
font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 40)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 30
server_address = ('127.0.0.1', 8080)
wait = False
rec_message = None

# game variables and images
enemy_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
enemy_locations = [(7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0),
                   (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1)]

player_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                    (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
player_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
captured_pieces_enemy = []
captured_pieces_player = []
# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
selection = 100
valid_moves = []
# load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
black_queen = pygame.image.load('assets/images/black queen.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))
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
white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                      black_rook_small, black_bishop_small]
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
# check variables/ flashing counter
winner = ''
game_over = False


# draw main game board
def draw_board():
    for i in range(32):
        column = i % 4
        row = i // 4
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
        status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                       'Black: Select a Piece to Move!', 'Black: Select a Destination!']

        for i in range(9):
            pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))


# draw pieces onto board
def draw_pieces(enemy_images, player_images):
    for i in range(len(enemy_pieces)):
        index = piece_list.index(enemy_pieces[i])
        if enemy_pieces[i] == 'pawn':
            screen.blit(enemy_images[0], (enemy_locations[i][0] * 100 + 22, enemy_locations[i][1] * 100 + 30))
        else:
            screen.blit(enemy_images[index], (enemy_locations[i][0] * 100 + 10, enemy_locations[i][1] * 100 + 10))


    for i in range(len(player_pieces)):
        index = piece_list.index(player_pieces[i])
        if player_pieces[i] == 'pawn':
            screen.blit(player_images[0], (player_locations[i][0] * 100 + 22, player_locations[i][1] * 100 + 30))
        else:
            screen.blit(player_images[index], (player_locations[i][0] * 100 + 10, player_locations[i][1] * 100 + 10))

        if selection == i:
            pygame.draw.rect(screen, 'blue', [player_locations[i][0] * 100 + 1, player_locations[i][1] * 100 + 1,
                                              100, 100], 2)


# function to check all pieces valid options on board
def check_options(pieces, locations):
    moves_list = []
    all_moves_list = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
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
        all_moves_list.append(moves_list)
    return all_moves_list


# check king valid moves
def check_king(position):
    moves_list = []

    friends_list = player_locations
    enemies_list = enemy_locations
    # 8 squares to check for kings, they can go one square any direction
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check queen valid moves
def check_queen(position):
    moves_list = check_bishop(position)
    second_list = check_rook(position)
    for i in range(len(second_list)):
        moves_list.append(second_list[i])
    return moves_list


# check bishop moves
def check_bishop(position):
    moves_list = []
    friends_list = player_locations
    enemies_list = enemy_locations
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


# check rook moves
def check_rook(position):
    moves_list = []
    friends_list = player_locations
    enemies_list = enemy_locations
    for i in range(4):  # down, up, right, left
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
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


# check valid pawn moves
def check_pawn(position):
    moves_list = []
    if (position[0], position[1] - 1) not in enemy_locations and \
            (position[0], position[1] - 1) not in player_locations and position[1] > 0:
        moves_list.append((position[0], position[1] - 1))
    if (position[0], position[1] - 2) not in enemy_locations and \
            (position[0], position[1] - 2) not in player_locations and position[1] == 6:
        moves_list.append((position[0], position[1] - 2))
    if (position[0] + 1, position[1] - 1) in enemy_locations:
        moves_list.append((position[0] + 1, position[1] - 1))
    if (position[0] - 1, position[1] - 1) in enemy_locations:
        moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list


# check valid knight moves
def check_knight(position):
    moves_list = []

    friends_list = player_locations
    enemies_list = enemy_locations
    # 8 squares to check for knights, they can go two squares in one direction and one in another
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


# check for valid moves for just selected piece
def check_valid_moves():
    options_list = black_options
    valid_options = options_list[selection]
    return valid_options


# draw valid moves on screen
def draw_valid(moves):
    color = 'blue'
    for i in range(len(moves)):
        pygame.draw.circle(screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)


# draw captured pieces on side of screen
def draw_captured():
    for i in range(len(captured_pieces_enemy)):
        captured_piece = captured_pieces_enemy[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i in range(len(captured_pieces_player)):
        captured_piece = captured_pieces_player[i]
        index = piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


# draw a flashing square around king if in check
def draw_check():

    if 'king' in enemy_pieces:
        king_index = enemy_pieces.index('king')
        king_location = enemy_locations[king_index]
        for i in range(len(black_options)):
            if king_location in black_options[i]:
                pygame.draw.rect(screen, 'dark red', [enemy_locations[king_index][0] * 100 + 1,
                                                      enemy_locations[king_index][1] * 100 + 1, 100, 100], 5)



def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))


def receive_messages(sock):
    global rec_message, wait
    while True:
        rec_message = json.loads(sock.recv(1024).decode())
        wait = False


# main game loop

run = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(server_address)
print("Connected to the server.")

role = sock.recv(1).decode()

if role == 'b':
    wait = True
    enemy_imagies = white_images
    player_imagies = black_images

else:
    enemy_imagies = black_images
    player_imagies = white_images
    small_black_images, small_white_images = small_white_images, small_black_images

threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

while run:
    if rec_message != None:
        enemy_locations[rec_message[0]] = (7 - rec_message[1][0], 7 - rec_message[1][1])
        if (7 - rec_message[1][0], 7 - rec_message[1][1]) in player_locations:
            captured_piece = player_locations.index(click_coords)
            captured_pieces_enemy.append(player_pieces[captured_piece])
            if player_pieces[captured_piece] == 'king':
                winner = 'black'
            player_pieces.pop(captured_piece)
            player_locations.pop(captured_piece)
        rec_message = None

    black_options = check_options(player_pieces, player_locations)

    timer.tick(fps)
    screen.fill('dark gray')
    draw_board()
    draw_pieces(enemy_imagies, player_imagies)
    draw_captured()
    draw_check()
    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and not wait:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)

            if click_coords == (8, 8) or click_coords == (9, 8):
                winner = 'white'
            if click_coords in player_locations:
                selection = player_locations.index(click_coords)

            if click_coords in valid_moves and selection != 100:
                player_locations[selection] = click_coords
                if click_coords in enemy_locations:
                    white_piece = enemy_locations.index(click_coords)
                    captured_pieces_player.append(enemy_pieces[white_piece])
                    if enemy_pieces[white_piece] == 'king':
                        winner = 'black'
                    enemy_pieces.pop(white_piece)
                    enemy_locations.pop(white_piece)

                message = json.dumps([selection, click_coords])
                sock.sendall(message.encode())
                wait = True

                selection = 100
                valid_moves = []

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ''
                enemy_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                enemy_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                player_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                player_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                    (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                captured_pieces_enemy = []
                captured_pieces_player = []
                selection = 100
                valid_moves = []
                black_options = check_options(player_pieces, player_locations)


    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()

pygame.quit()
