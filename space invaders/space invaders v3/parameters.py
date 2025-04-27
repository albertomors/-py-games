import pygame
import math, numpy
from methods import *

pygame.font.init()

# <--- generics --->

SCREENW, SCREENH = 800,600
FPS = 120
PI = math.pi
RES_FOLDER = 'C:/Users/alber/Documents/pygame/arcade classics/space invaders/space invaders v3/res/'
FONT = pygame.font.SysFont('comicsans',12)

# <--- colors --->

WHITE = (255,255,255)
BLACK = (0,0,0)
DARKGRAY = (10,10,10)
LIGHTGRAY = (200,200,200)
GRAY = (128,128,128)
PAPER = (232,220,184)

RED = (255,0,0)
GREEN = (0,255,0)
DARKGREEN = (0,128,0)
YELLOW = (255,255,0)
LIGHTBLUE = (128,128,255)

# <--- background --->

BG = {
    'color' :           DARKGRAY,
    'speed' :           4,
    'stars_num' :       (5,50),
    'stars_size' :      (1,5),
}

# <--- bullets --->

BULLET = {
    'color' :       RED,
    'w' :           4,
    'h' :           8,
    'speed' :       -5,
    'lifecost' :    1,
}

BOMB = {
    'color' :       GRAY,
    'size' :        16,
    'speed' :       -3,
    'lifecost' :    5,
    'r_speed' :     180/FPS,
}

LASER = {
    'color' :        RED,
    'w' :            2,
    'h' :            SCREENH,
    'speed' :        -SCREENH,
    'lifecost' :     15/FPS, #damage/s
}

ROCKET = {
    'img' :         pygame.image.load(RES_FOLDER + 'rocket.png'),
    'w' :           6,
    'h' :           12,
    'speed' :       -3,
    'lifecost' :    10,
    'vision' :      200, #px
}

FLAME = {
    'size' :        (2,6),
    'speed' :       (-1,-2),
    'speed_dec' :   0.97,
    'lifecost' :    15/FPS,
    'lifetime' :    (1*FPS,1.5*FPS), #s
    'r_speed' :     BOMB['r_speed'],
}

# <--- guns --->

CANNON = {
    'firerate' :    2,
    'ammo' :        10,
}


LASERGUN = {
    'max_ammo' :        5*FPS,
    'charge_ratio' :    1/3,
    'firerate' :        0,
}


ROCKETLAUNCHER = {
    'firerate' :    2,
    'ammo' :        10,
}


FLAMETHROWER = {
    'firerate' :    0.01,
    'max_ammo' :    5*FPS,
    'ammo' :        0,
    'fire_angle' :  45/2,
}

# <--- enemies --->

ENEMY = {
    'img' :             pygame.image.load(RES_FOLDER+'sprites.png'),
    'size' :            64,
    'h_num' :           19,
    'v_num' :           11,
    'speed' :           (0.5,3),
    'spawn_time' :      (100,3000),
}

ASTEROID = {
    'img' :             pygame.image.load(RES_FOLDER+'asteroid.png'),
    'size' :            (50,300),
    'speed' :           (2,.5),
    'rot_speed' :       numpy.array((180,10))/FPS,
    'lives' :           (1,50),
    'spawn_time' :      (500,8000),
}

# <--- player --->

PLAYER = {
    'size' :            64,
    'imgs' :            [],
    'levels' :          5,
    'max_lives' :       (3,4,5,7,10),
    'max_speed' :       (4,4.3,4.7,5,5.5),
    'speed_eps' :       0.01,
    'acc' :             (0.08,0.1,0.12,0.15,0.18),
    'friction' :        0.95,
    'firerate' :        numpy.array((0.5,0.4,0.4,0.3,0.2)) * FPS,
    'firespots' :       [[[31,12]],[[31,12]],[[20,28],[44,28]],[[16,27],[48,27]],[[24,12],[40,12]]],
    'exp_to_lvlup' :    (15,30,60,120,math.inf),
    'gun_types' :       5,
    'gun_indexes' :     ('basic','cannon','rocketlauncher','lasergun','flamethrower'),
}
PLAYER['max_points'] = 200
for i in range(PLAYER['levels']):
    img = pygame.image.load(RES_FOLDER+'ss'+str(i+1)+'.png')
    PLAYER['imgs'].append(img)

# <--- items --->

SHIELD = {
    'off' :      30,
    'color' :    LIGHTBLUE,
    'alpha' :    32,
}
SHIELD['size'] = numpy.array((40,44,60,60,60)) + SHIELD['off']

# <--- powerups --->

PWUP = {
    'p_filename' :      RES_FOLDER,
    'size' :            32,
    'speed' :           2,
    'spawn_time' :      (10000,15000),
    'standard_time' :   10*FPS,
    'font' :            FONT,

    'exp_value' :       15,
    'triple_angle' :    45/2,
    'bomb_amt' :        10,
    'rocket_amt' :      10,
    'oil_amt' :         FLAMETHROWER['max_ammo']/3
}

# <--- level graphics --->

GAMEOVER = {
    'font1' : pygame.font.SysFont('comicsans', 60),
    'font2' : pygame.font.SysFont('comicsans', 20),
}

EXPBAR = {
    'x' :               10,
    'w' :               100,
    'h' :               10,
    'b_color' :         DARKGREEN,
    'f_color' :         GREEN,
}
EXPBAR['y'] = SCREENH-EXPBAR['h']-10

LEVELBAR = {
    'x' :           10,
    'y' :           EXPBAR['y']-5,
    'font' :        pygame.font.SysFont("comicsans",12)
}

LIFEBAR = {
    'size' :            20,
    'f_heart_img' :     pygame.image.load(RES_FOLDER+'heart_f.png'),
    'e_heart_img' :     pygame.image.load(RES_FOLDER+'heart_e.png'),
}
LIFEBAR['f_heart_img'] = pygame.transform.scale(LIFEBAR['f_heart_img'],(LIFEBAR['size'],LIFEBAR['size']))
LIFEBAR['e_heart_img'] = pygame.transform.scale(LIFEBAR['e_heart_img'],(LIFEBAR['size'],LIFEBAR['size']))
LIFEBAR['xs'] = SCREENW-10-(numpy.array(PLAYER['max_lives']))*LIFEBAR['size']
LIFEBAR['y'] = SCREENH-10-LIFEBAR['size']

POINTSBAR = {
    '_x' :          SCREENW-10,
    'y' :           10,
    'font' :        pygame.font.SysFont("comicsans",12),
}

GUN_BAR = {
    'p_filename' :          RES_FOLDER,
    'size' :                32,
    'u_size' :              48,
    'imgs' :                [],
    'space_between' :       10,
    'font' :                FONT,

    'ammo_bar_h' :          10,
    'laser_bar_c' :         RED,
    'oil_bar_c' :           YELLOW,
}
for i in range(PLAYER['gun_types']):
    img = pygame.image.load(RES_FOLDER+PLAYER['gun_indexes'][i]+'.png')
    GUN_BAR['imgs'].append(img)
GUN_BAR['h'] = GUN_BAR['u_size'] + 10 + GUN_BAR['ammo_bar_h'] + 5
GUN_BAR['w'] = (len(GUN_BAR['imgs'])-1)*GUN_BAR['size'] + 1*GUN_BAR['u_size'] + (len(GUN_BAR['imgs'])-1)*GUN_BAR['space_between']
GUN_BAR['y'] = SCREENH-10-GUN_BAR['h']
GUN_BAR['x'] = (SCREENW-GUN_BAR['w'])/2
GUN_BAR['ammo_bar_y'] = SCREENH-10-GUN_BAR['ammo_bar_h'] - 5
GUN_BAR['bx'] = GUN_BAR['x'] - 5
GUN_BAR['by'] = GUN_BAR['y'] + GUN_BAR['u_size'] - GUN_BAR['size'] + GUN_BAR['size']/2 + 5
GUN_BAR['bw'] = GUN_BAR['w'] + 2*5
GUN_BAR['bh'] = GUN_BAR['h'] - GUN_BAR['u_size'] + GUN_BAR['size'] - GUN_BAR['size']/2 - 5

LEVEL = {
    'intro_y' :         SCREENH+100,
    'gameloop_y' :      SCREENH-150,
    'intro_acc' :       0.016,
    'outro_acc' :       PLAYER['acc'][-1],
    'level_nums' :      5,
    'diffs' :           [],
    'points_to_pass' :  (20,40,70,120,200),
    
    'hit_screen_alpha' : 64,
    'hit_screen_time' :  1/3*FPS,
    'shake_time' :       1/2*FPS,
    'shake_amt' :        10, #px
}

for i in range(LEVEL['level_nums']-1):
    diff = clamped_remap((i+1),1,3,0,1)
    LEVEL['diffs'].append(diff)