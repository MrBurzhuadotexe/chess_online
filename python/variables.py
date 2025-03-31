import pygame

pygame.init()  # Inicjalizacja Pygame
WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])  # Ustawienie rozmiaru okna gry
pygame.display.set_caption('Two-Player Pygame Chess!')  # Tytuł okna
font = pygame.font.Font('freesansbold.ttf', 20)  # Czcionka dla tekstu
medium_font = pygame.font.Font('freesansbold.ttf', 40)  # Średnia czcionka
big_font = pygame.font.Font('freesansbold.ttf', 50)  # Duża czcionka


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

player_options = []
