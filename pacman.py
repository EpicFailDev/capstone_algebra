import pygame
import sys
import os
import math
import copy
import heapq
from assets.board import boards

def a_star_path(start, goal, level):
    # start, goal: (x, y) em pixels
    # level: matriz do tabuleiro
    num1, num2 = _tile_sizes()
    def to_tile(pos):
        return (int(pos[0] // num2), int(pos[1] // num1))
    def to_center(tile):
        return _tile_center(tile[0], tile[1])
    start_tile = to_tile(start)
    goal_tile = to_tile(goal)
    w, h = 30, 32
    def neighbors(tile):
        x, y = tile
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<w and 0<=ny<h:
                if level[ny][nx] < 3 or level[ny][nx]==9:
                    yield (nx, ny)
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_set = [(0+heuristic(start_tile,goal_tile), 0, start_tile, None)]
    came_from = {}
    cost_so_far = {start_tile: 0}
    while open_set:
        _, cost, current, prev = heapq.heappop(open_set)
        if current == goal_tile:
            # reconstrói caminho
            path = [current]
            while prev:
                path.append(prev)
                prev = came_from.get(prev)
            path.reverse()
            return [to_center(t) for t in path]
        if current in came_from:
            continue
        came_from[current] = prev
        for n in neighbors(current):
            new_cost = cost + 1
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                heapq.heappush(open_set, (new_cost+heuristic(n,goal_tile), new_cost, n, current))
    # Se não encontrou caminho, retorna lista vazia
    return []

def draw_matrix_overlay(level, screen, WIDTH, HEIGHT, _tile_sizes):
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 120)) # Semi-transparent black background

    num1, num2 = _tile_sizes()

    for i in range(len(level)):
        for j in range(len(level[i])):
            tile_type = level[i][j]
            color = None
            if tile_type == 1: # Pellet
                color = (255, 255, 255, 100) # White, semi-transparent
            elif tile_type == 2: # Power-up
                color = (0, 255, 0, 150) # Green, semi-transparent
            elif tile_type == 0: # Empty space
                color = (50, 50, 50, 50) # Dark gray, very transparent
            elif tile_type >= 3 and tile_type <= 8: # Walls
                color = (0, 0, 255, 100) # Blue, semi-transparent
            elif tile_type == 9: # Ghost house gate
                color = (255, 0, 0, 100) # Red, semi-transparent

            if color:
                pygame.draw.rect(overlay_surface, color, (j * num2, i * num1, num2, num1))

    screen.blit(overlay_surface, (0, 0))

def draw_hacker_overlay(ghosts, targets, player_center, player_dir, level):
    # 1. Cria um fundo escuro e translúcido para destacar as linhas
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 30, 220))  # Azul escuro, bem transparente
    screen.blit(overlay, (0, 0))

    # 2. Exibe o banner na parte superior da tela
    banner_font = pygame.font.Font('freesansbold.ttf', 32)
    banner = banner_font.render('HACKER VISION ATIVADA (S para sair)', True, (0, 255, 180))
    banner_rect = banner.get_rect(center=(WIDTH // 2, 36))
    screen.blit(banner, banner_rect)

    # 3. Define as cores para cada fantasma (Blinky, Inky, Pinky, Clyde)
    colors = [(255, 0, 0), (0, 180, 255), (255, 105, 180), (255, 165, 0)]

    # 4. Itera sobre cada fantasma para desenhar sua linha de alvo
    for idx, g in enumerate(ghosts):
        # Posição inicial da linha (centro do fantasma)
        start_pos = (g.center_x, g.center_y)
        
        # Posição final da linha (alvo do fantasma)
        end_pos = targets[idx]
        
        # Cor correspondente ao fantasma
        color = colors[idx]

        # --- LÓGICA PRINCIPAL ---
        # Desenha uma linha reta e sólida do fantasma até o alvo
        pygame.draw.line(screen, color, start_pos, end_pos, 3)

        # Desenha um círculo no alvo para destacá-lo
        pygame.draw.circle(screen, color, end_pos, 8, 2)


dirpath = os.getcwd()
sys.path.append(dirpath)
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


try:
    import numpy as np
except Exception:  # fallback lightweight shim if NumPy isn't available
    class _NPShim:
        def array(self, it):
            return list(it)

        def linalg_norm(self, v):
            return math.sqrt(sum((x * x for x in v)))

    np = _NPShim()

pygame.init()

WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)
color = 'blue'
PI = math.pi
player_images = []
for i in range(1, 5):
    caminho_imagem = resource_path(f'assets/player_images/{i}.png')
    player_images.append(pygame.transform.scale(pygame.image.load(caminho_imagem), (45, 45)))

blinky_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/red.png')), (45, 45))
pinky_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/pink.png')), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/blue.png')), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/orange.png')), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/powerup.png')), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(resource_path(f'assets/ghost_images/dead.png')), (45, 45))
player_x = 450
player_y = 663
direction = 0
blinky_x = 56
blinky_y = 58
blinky_direction = 0
inky_x = 440
inky_y = 388
inky_direction = 2
pinky_x = 440
pinky_y = 438
pinky_direction = 2
clyde_x = 440
clyde_y = 438
clyde_direction = 2
counter = 0
flicker = False
# R, L, U, D
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False
moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False
debug_mode = False  # Modo Vetorial (toggle com tecla D)
hacker_mode = False  # Modo Hacker Visual (toggle com tecla S)
matrix_mode = False # MODO MATRIZ (toggle com tecla A)

# Pellets e modos de fantasmas
pellets_eaten = 0
inky_released = False
blinky_elroy = False
ELROY_PELLETS = 60
INKY_RELEASE_PELLETS = 15
CLYDE_RELEASE_PELLETS = 30
clyde_released = False
# Clyde fica menos agressivo quando está mais próximo que este raio (em tiles)
CLYDE_SCATTER_RADIUS_TILES = 8.0


# Scheduler de scatter/chase (s)
current_mode = 'scatter'
mode_index = 0
mode_timer_frames = 0
mode_schedule = [
    ('scatter', 5), ('chase', 25),
    ('scatter', 5), ('chase', 25),
    ('scatter', 3), ('chase', 30),
    ('scatter', 1), ('chase', 9999),
]

def _reverse_dir(d):
    return {0:1, 1:0, 2:3, 3:2}.get(d, d)


class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self):
    # R, L, U, D
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self):
    # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
    # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # inky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction


def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    # Janela moderna para Game Over e Win (sem emoji, sem borda amarela, mostra score)
    if game_over or game_won:
        # Gradiente de fundo
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            cor = (30, 30, 30 + int(80 * y / HEIGHT), 220)
            pygame.draw.line(overlay, cor, (0, y), (WIDTH, y))
        screen.blit(overlay, (0, 0))

        # Caixa central com sombra
        box_rect = pygame.Rect(WIDTH//2-260, HEIGHT//2-130, 520, 260)
        shadow = pygame.Surface((box_rect.width+16, box_rect.height+16), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,100), shadow.get_rect(), border_radius=18)
        screen.blit(shadow, (box_rect.x+8, box_rect.y+8))
        pygame.draw.rect(screen, (255,255,255,240), box_rect, border_radius=18)
        pygame.draw.rect(screen, (200,200,200,180), box_rect.inflate(-20,-20), border_radius=14)

        # Título com sombra
        bigfont = pygame.font.Font('freesansbold.ttf', 54)
        if game_over:
            title = 'GAME OVER'
            color = (220,0,0)
        else:
            title = 'VITÓRIA!'
            color = (0,180,0)
        # Sombra
        title_img_shadow = bigfont.render(title, True, (0,0,0))
        title_img = bigfont.render(title, True, color)
        title_rect = title_img.get_rect(center=(WIDTH//2, HEIGHT//2-30))
        screen.blit(title_img_shadow, title_rect.move(3,3))
        screen.blit(title_img, title_rect)

        # Score centralizado
        scorefont = pygame.font.Font('freesansbold.ttf', 32)
        score_text = scorefont.render(f'Score: {score}', True, (40,40,40))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2+20))
        screen.blit(score_text, score_rect)

        # Mensagem de reinício (sem borda amarela)
        btn_rect = pygame.Rect(WIDTH//2-140, HEIGHT//2+70, 280, 54)
        pygame.draw.rect(screen, (40,40,40), btn_rect, border_radius=12)
        msgfont = pygame.font.Font('freesansbold.ttf', 28)
        msg = msgfont.render('Pressione ESPAÇO', True, (255,255,0))
        msg_rect = msg.get_rect(center=btn_rect.center)
        screen.blit(msg, msg_rect)


def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
            global pellets_eaten
            pellets_eaten += 1
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
            pellets_eaten += 1
    return scor, power, power_count, eaten_ghosts


def draw_board():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)


def draw_player():
    # 0:R, 1:L, 2:U, 3:D
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


def _tile_sizes():
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    return num1, num2


def _tile_center(col, row):
    num1, num2 = _tile_sizes()
    return int(col * num2 + (0.5 * num2)), int(row * num1 + (0.5 * num1))


def _euclid(a, b):
    # distância euclidiana
    try:
        va = np.array([a[0], a[1]])
        vb = np.array([b[0], b[1]])
        v = vb - va
        # se usando shim
        if hasattr(np, 'linalg'):
            return float(np.linalg.norm(v))
        return float(np.linalg_norm(v))
    except Exception:
        return math.dist(a, b)


def draw_vector_overlay(ghosts, targets, player_center, player_dir):
    colors = [(255, 0, 0), (0, 180, 255), (255, 105, 180), (255, 165, 0)]  # blinky, inky, pinky, clyde
    names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
    num1, num2 = _tile_sizes()

    # Fundo escurecido para destacar overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    # banner
    banner_font = pygame.font.Font('freesansbold.ttf', 28)
    banner = banner_font.render('MODO DEBUG ATIVO (D para sair)', True, 'yellow')
    banner_rect = banner.get_rect(center=(WIDTH//2, 30))
    screen.blit(banner, banner_rect)

    for idx, g in enumerate(ghosts):
        target = targets[idx]
        gx, gy = g.center_x, g.center_y
        tx, ty = target
        color = colors[idx]

        # Nome do fantasma
        name_font = pygame.font.Font('freesansbold.ttf', 22)
        name_label = name_font.render(names[idx], True, color)
        name_rect = name_label.get_rect(center=(gx, gy-32))
        screen.blit(name_label, name_rect)

        # Vetor g->alvo com seta curta e grossa (sem tracejado nem ponto final)
        vec_len = _euclid((gx, gy), (tx, ty))
        if vec_len > 0:
            dx = (tx - gx) / vec_len
            dy = (ty - gy) / vec_len
            arrow_len = min(60, vec_len-20)
            endx = int(gx + dx * arrow_len)
            endy = int(gy + dy * arrow_len)
            pygame.draw.line(screen, color, (gx, gy), (endx, endy), 5)
            # Seta
            angle = math.atan2(dy, dx)
            arrow_size = 16
            for a in [-0.5, 0.5]:
                ax = int(endx - arrow_size * math.cos(angle + a))
                ay = int(endy - arrow_size * math.sin(angle + a))
                pygame.draw.line(screen, color, (endx, endy), (ax, ay), 5)

        # Destacar fantasma
        pygame.draw.circle(screen, color, (gx, gy), 24, 2)

        # Distância
        dist = int(vec_len)
        dist_label = name_font.render(f'dist: {dist}', True, color)
        screen.blit(dist_label, (gx + 28, gy - 18))

        # Direções possíveis (setas pequenas)
        col = int(g.center_x // num2)
        row = int(g.center_y // num1)
        next_by_dir = {
            0: _tile_center(min(col + 1, 29), row),
            1: _tile_center(max(col - 1, 0), row),
            2: _tile_center(col, max(row - 1, 0)),
            3: _tile_center(col, min(row + 1, 31)),
        }
        for d, allowed in enumerate(getattr(g, 'turns', [False, False, False, False])):
            if not allowed:
                continue
            nx, ny = next_by_dir[d]
            # Pequena seta
            adx = nx - gx
            ady = ny - gy
            alen = math.sqrt(adx*adx + ady*ady)
            if alen > 0:
                adx = adx / alen
                ady = ady / alen
                sx = int(gx + adx * 32)
                sy = int(gy + ady * 32)
                pygame.draw.line(screen, color, (gx, gy), (sx, sy), 3)
                # ponta
                angle = math.atan2(ady, adx)
                for a in [-0.4, 0.4]:
                    px = int(sx - 8 * math.cos(angle + a))
                    py = int(sy - 8 * math.sin(angle + a))
                    pygame.draw.line(screen, color, (sx, sy), (px, py), 2)
            # Valor da distância
            dval = int(_euclid((nx, ny), (tx, ty)))
            text = name_font.render(f'{dval}', True, color)
            screen.blit(text, (nx - 12, ny - 12))



def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 15
    # check collisions based on center x and center y of player +/- fudge number
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns


def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)

    # tamanhos de tile
    num1, num2 = _tile_sizes()
    # 2 tiles à frente (Pinky)
    if direction == 0:
        pink_ahead = (player_x + 4 * num2, player_y)
    elif direction == 1:
        pink_ahead = (player_x - 4 * num2, player_y)
    elif direction == 2:
        pink_ahead = (player_x, player_y - 4 * num1)
    else:
        pink_ahead = (player_x, player_y + 4 * num1)

    # 2 tiles à frente (Inky)
    if direction == 0:
        two_ahead = (player_x + 2 * num2, player_y)
    elif direction == 1:
        two_ahead = (player_x - 2 * num2, player_y)
    elif direction == 2:
        two_ahead = (player_x, player_y - 2 * num1)
    else:
        two_ahead = (player_x, player_y + 2 * num1)

    # alvo de Inky a partir do vetor
    vx = two_ahead[0] - blink_x
    vy = two_ahead[1] - blink_y
    ink_vector_target = (blink_x + 2 * vx, blink_y + 2 * vy)

    # distância de Clyde em tiles
    clyde_center = (clyd_x + 22, clyd_y + 22)
    pac_center = (player_x + 23, player_y + 24)
    dx_tiles = abs(pac_center[0] - clyde_center[0]) / float(num2)
    dy_tiles = abs(pac_center[1] - clyde_center[1]) / float(num1)
    clyde_dist_tiles = math.sqrt(dx_tiles * dx_tiles + dy_tiles * dy_tiles)
    clyde_scatter_corner = _tile_center(1, 31)
    corner_top_left = _tile_center(1, 1)
    corner_top_right = _tile_center(28, 1)
    corner_bottom_right = _tile_center(28, 31)
    if powerup:
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        if not inky.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead and not eaten_ghost[2]:
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead and not eaten_ghost[3]:
            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        # Scatter/Chase com exceção de Elroy
        if not blinky.dead:
            blink_target = (player_x, player_y) if (current_mode == 'chase' or blinky_elroy) else (corner_top_right)
        else:
            blink_target = return_target

        if not inky.dead:
            ink_target = (ink_vector_target if current_mode == 'chase' else corner_bottom_right)
        else:
            ink_target = return_target

        if not pinky.dead:
            pink_target = (pink_ahead if current_mode == 'chase' else corner_top_left)
        else:
            pink_target = return_target

        if not clyde.dead:
            clyd_target = (clyde_scatter_corner if clyde_dist_tiles <= CLYDE_SCATTER_RADIUS_TILES else (player_x, player_y)) if current_mode == 'chase' else clyde_scatter_corner
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]


def draw_matrix_overlay(level, screen, WIDTH, HEIGHT, _tile_sizes):
    """
    Desenha uma sobreposição visual da matriz do tabuleiro, mostrando os números
    que compõem o nível, com um estilo visual aprimorado e fundo translúcido.
    """
    # Cria uma superfície para a sobreposição com um fundo azul escuro e translúcido
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill((10, 10, 30, 190))

    # Pega as dimensões de cada tile do tabuleiro
    tile_height, tile_width = _tile_sizes()

    # Define uma fonte para os números. O tamanho é calculado para caber no tile.
    # Usamos try/except para garantir que o jogo não quebre se a fonte não for encontrada.
    try:
        font_size = int(min(tile_height, tile_width) * 0.7) # 70% do menor lado do tile
        matrix_font = pygame.font.Font('freesansbold.ttf', font_size)
    except FileNotFoundError:
        font_size = int(min(tile_height, tile_width) * 0.8)
        matrix_font = pygame.font.Font(None, font_size)  # Usa a fonte padrão do Pygame

    # Itera sobre cada tile da matriz 'level'
    for i in range(len(level)):
        for j in range(len(level[i])):
            tile_type = level[i][j]
            number_str = str(tile_type)
            color = (80, 80, 80, 150)  # Cor padrão (cinza escuro para espaços vazios '0')

            # Define cores vibrantes baseadas no tipo de tile para um visual incrível
            if tile_type == 1:  # Pellets
                color = (255, 255, 180, 200)  # Amarelo claro
            elif tile_type == 2:  # Power-ups
                color = (100, 255, 100, 255)  # Verde brilhante
            elif 3 <= tile_type <= 8:  # Paredes
                color = (0, 200, 255, 220)    # Ciano/Azul-claro
            elif tile_type == 9:  # Portão dos fantasmas
                color = (255, 0, 180, 255)    # Magenta

            # Renderiza o número como uma imagem de texto
            text_surface = matrix_font.render(number_str, True, color)

            # Calcula a posição central do tile para centralizar o número
            center_pos = (j * tile_width + tile_width // 2,
                          i * tile_height + tile_height // 2)
            
            # Pega o retângulo do texto e define sua posição central
            text_rect = text_surface.get_rect(center=center_pos)
            
            # Desenha o número na superfície de sobreposição
            overlay_surface.blit(text_surface, text_rect)

    # Por fim, desenha a superfície de sobreposição completa na tela principal
    screen.blit(overlay_surface, (0, 0))


def show_start_screen():
    screen.fill((10, 10, 30))
    title_font = pygame.font.Font('freesansbold.ttf', 64)
    title = title_font.render('PACMAN', True, (255, 255, 0))
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    screen.blit(title, title_rect)
    # Pacman e fantasmas
    pac_img = pygame.transform.scale(player_images[0], (80, 80))
    screen.blit(pac_img, (WIDTH//2 - 40, HEIGHT//2 - 30))
    ghost_imgs = [blinky_img, inky_img, pinky_img, clyde_img]
    for i, img in enumerate(ghost_imgs):
        gimg = pygame.transform.scale(img, (60, 60))
        screen.blit(gimg, (WIDTH//2 - 120 + i*60, HEIGHT//2 + 60))
    # Texto de instrução
    instr_font = pygame.font.Font('freesansbold.ttf', 28)
    instr = instr_font.render('Pressione qualquer tecla para começar', True, (0,255,180))
    instr_rect = instr.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))
    screen.blit(instr, instr_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        timer.tick(30)

show_start_screen()
run = True
while run:
    # PAUSA TOTAL se game_over ou game_won
    if game_over or game_won:
        screen.fill('black')
        draw_board()
        draw_player()
        blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
        inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead, inky_box, 1)
        pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
        clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
        draw_misc()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Reset total já está implementado abaixo
                    powerup = False
                    power_counter = 0
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    direction = 0
                    direction_command = 0
                    blinky_x = 56
                    blinky_y = 58
                    blinky_direction = 0
                    inky_x = 440
                    inky_y = 388
                    inky_direction = 2
                    pinky_x = 440
                    pinky_y = 438
                    pinky_direction = 2
                    clyde_x = 440
                    clyde_y = 438
                    clyde_direction = 2
                    eaten_ghost = [False, False, False, False]
                    blinky_dead = False
                    inky_dead = False
                    clyde_dead = False
                    pinky_dead = False
                    score = 0
                    lives = 3
                    level = copy.deepcopy(boards)
                    game_over = False
                    game_won = False
                    pellets_eaten = 0
                    inky_released = False
                    clyde_released = False
                    blinky_elroy = False
                    current_mode = 'scatter'
                    mode_index = 0
                    mode_timer_frames = 0
        continue

    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 60 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')

    # scheduler de modos
    if not powerup and not game_over and not game_won:
        mode_timer_frames += 1
        mode_name, secs = mode_schedule[mode_index]
        if mode_timer_frames >= secs * fps:
            # troca
            mode_timer_frames = 0
            mode_index = (mode_index + 1) % len(mode_schedule)
            prev_mode = current_mode
            current_mode = mode_schedule[mode_index][0]
            # reverter direções
            blinky_direction = _reverse_dir(blinky_direction)
            pinky_direction = _reverse_dir(pinky_direction)
            inky_direction = _reverse_dir(inky_direction)
            clyde_direction = _reverse_dir(clyde_direction)

    # Elroy
    if not blinky_elroy and pellets_eaten >= ELROY_PELLETS:
        blinky_elroy = True
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24
    if powerup:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    # Elroy: blinky ligeiramente mais rápido
    if blinky_elroy and not powerup and not blinky_dead:
        ghost_speeds[0] = 3
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if blinky_dead:
        ghost_speeds[0] = 4
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead,
                   blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead,
                 inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead,
                  pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead,
                  clyde_box, 3)
    draw_misc()
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)
    # alvo de saída quando na box (tile 9)
    gate_target = (400, 100)
    if blinky.in_box and not blinky_dead:
        targets[0] = gate_target
    if pinky.in_box and not pinky_dead:
        targets[2] = gate_target
    # Inky: só libera após INKY_RELEASE_PELLETS
    if pellets_eaten >= INKY_RELEASE_PELLETS:
        inky_released = True
    if inky.in_box and not inky_dead:
        targets[1] = gate_target if inky_released else (inky_x, inky_y)
    # Clyde: só libera após CLYDE_RELEASE_PELLETS
    if pellets_eaten >= CLYDE_RELEASE_PELLETS:
        clyde_released = True
    if clyde.in_box and not clyde_dead:
        targets[3] = gate_target if clyde_released else (clyde_x, clyde_y)
    if debug_mode:
        draw_vector_overlay([blinky, inky, pinky, clyde], targets, (center_x, center_y), direction)
    if hacker_mode:
        draw_hacker_overlay([blinky, inky, pinky, clyde], targets, (center_x, center_y), direction, level)

    turns_allowed = check_position(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        # Inky: se morto (olhos), sempre se move para retornar ao covil; se vivo e não liberado, fica parado
        if pellets_eaten >= INKY_RELEASE_PELLETS:
            inky_released = True
        if inky_dead:
            # quando morto (olhos), use o movimento mais livre para conseguir voltar ao covil
            inky_x, inky_y, inky_direction = inky.move_clyde()
        elif inky_released:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            # parado quando vivo e não liberado
            inky_x, inky_y, inky_direction = inky.x_pos, inky.y_pos, inky.direction

        # Clyde: se morto (olhos), sempre se move para retornar ao covil; se vivo e não liberado, fica parado
        if pellets_eaten >= CLYDE_RELEASE_PELLETS:
            clyde_released = True
        if clyde_dead:
            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
        elif clyde_released:
            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
        else:
            clyde_x, clyde_y, clyde_direction = clyde.x_pos, clyde.y_pos, clyde.direction
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    # add to if not powerup to check if eaten ghosts
    if not powerup:
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
                (player_circle.colliderect(inky.rect) and not inky.dead) or \
                (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
                (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
            else:
                game_over = True
                moving = False
                startup_counter = 0
                # resetar modos
                current_mode = 'scatter'
                mode_index = 0
                mode_timer_frames = 0
                blinky_elroy = False
                inky_released = False
                clyde_released = False
    # Nota: durante powerup, colisões com fantasmas devem ser sempre comestíveis (ou olhos inofensivos),
    # portanto não há penalidade de morte nesse estado.
    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_d:
                debug_mode = not debug_mode
            if event.key == pygame.K_s:
                hacker_mode = not hacker_mode
            if event.key == pygame.K_a:
                matrix_mode = not globals().get('matrix_mode', False)
            if event.key == pygame.K_SPACE and (game_over or game_won):
                powerup = False
                power_counter = 0
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False
                pellets_eaten = 0

    # Overlay da matriz do tabuleiro

    if matrix_mode:
        draw_matrix_overlay(level, screen, WIDTH, HEIGHT, _tile_sizes)


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False
    # revive flags are handled when eyes reach the box above

    pygame.display.flip()
pygame.quit()


# sound effects, restart and winning messages