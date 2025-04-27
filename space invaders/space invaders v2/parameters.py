import pygame
import math, numpy

pygame.font.init()

# <--- game parameters --->

#generics
SCREENW, SCREENH = 800,600
FPS = 120
PI = math.pi
RES_FOLDER = 'C:/Users/alber/Documents/pygame/arcade classics/space invaders/space invaders v2/res/'
FONTSIZE = 14

#colors
WHITE = (255,255,255)
BLACK = (0,0,0)
DARKGRAY = (10,10,10)
RED = (255,0,0)
GREEN = (0,255,0)
DARKGREEN = (0,128,0)
YELLOW = (255,255,0)
LIGHTBLUE = (128,128,255)

#background

BG = {
    'color' :           DARKGRAY,
    'scroll_speed' :    4,
    'stars_num' :       (5,50),
    'stars_size' :      (1,5),
}

#guns + bullets

BULLET = {
    'img' :         pygame.image.load(RES_FOLDER + 'bullet.png'),
    'size' :        10,
    'speed' :       -5,
    'lifecost' :    1,
}
BASICCANNON = {
    'img' :         pygame.image.load(RES_FOLDER + 'cannon.png'),
}

CANNONBALL = {
    'img' :         pygame.image.load(RES_FOLDER + 'cannonball.png'),
    'size' :        BULLET['size'],
    'speed' :       -3,
    'lifecost' :    5,
    'r_speed' :     180/FPS
}
CANNON = {
    'img' :         pygame.image.load(RES_FOLDER + 'cannon.png'),
    'firerate' :    2,
    'ammo' :        10,
}

LASER = {
    'color' :        RED,
    'w' :            1,
    'h' :            SCREENH,
    'speed' :        -SCREENH,
}
LASERGUN = {
    'img' :             pygame.image.load(RES_FOLDER + 'lasergun.png'),
    'max_ammo' :        10*FPS,
    'charge_ratio' :    1/3,
    'firerate' :        0,
}

ROCKET = {
    'img' :         pygame.image.load(RES_FOLDER + 'rocket.png'),
    'size' :        BULLET['size']*3,
    'speed' :       -3,
    'lifecost' :    10,
    'radar' :       200, #px
}
ROCKETLAUNCHER = {
    'img' :         pygame.image.load(RES_FOLDER + 'rocketlauncher.png'),
    'firerate' :    3,
    'ammo' :        5,
}

FLAME = {
    'img' :         pygame.image.load(RES_FOLDER + 'flame.png'),
    'size' :        BULLET['size']*2/3,
    'speed' :       -2,
    'speed_dec' :   0.97,
    'lifecost' :    1,
    'lifetime' :    (1*FPS,2*FPS), #s
}
FLAMETHROWER = {
    'img' :         pygame.image.load(RES_FOLDER + 'flamethrower.png'),
    'firerate' :    0.005,
    'max_ammo' :    5*FPS,
    'ammo' :        0,
    'fire_angle' :  PI/8,
}

#enemies

ASTEROID = {
    'img' :             pygame.image.load(RES_FOLDER+'asteroid.png'),
    'size' :            (50,200),
    'speed' :           (2,.5),
    'rot_speed' :       numpy.array((180,10))/FPS,
    'lives' :           (1,50),
    'spawn_time' :      (1000,8000),
}

ENEMY = {
    'img' :             pygame.image.load(RES_FOLDER+'sprites.png'),
    'crop_w' :          99,
    'crop_h' :          98,
    'h_num' :           19,
    'v_num' :           11,
    'size' :            50,
    'speed' :           (0.5,3),
    'spawn_time' :      (100,3000),
}

#player

PLAYER = {
    'size' :            60,
    'filename_p' :      RES_FOLDER+'ss',
    'imgs' :            [],
    'levels' :          4,
    'max_lives' :       (3,4,5,7),
    'max_speed' :       (4,4.3,4.7,5),
    'speed_eps' :       0.01,
    'acc' :             (0.08,0.1,0.12,0.15),
    'friction' :        0.95,
    'firerate' :        numpy.array((0.5,0.5,0.25,0.25)) * FPS,
    'firespots' :       ([[49,32]],[[20,45],[79,35]],[[49,13]],[[10,45],[89,45]]),
    'exp_to_lvlup' :    (15,30,60,120,math.inf),
    'gun_types' :       5,
    'gun_indexes' :     ('basic','cannon','rocketlauncher','lasergun','flamethrower'),
    'starting_y' :      SCREENH-100,
}
PLAYER['max_points'] = sum(PLAYER['exp_to_lvlup'][:-1])
for i in range(PLAYER['levels']):
    img = pygame.image.load(PLAYER['filename_p']+str(i+1)+'.png')
    PLAYER['imgs'].append(img)
for spots in PLAYER['firespots']:
    for spot in spots:
        spot[0] *= PLAYER['size']/100
        spot[1] *= PLAYER['size']/100

#items

SHIELD = {
    'off' :      30,
    'color' :    LIGHTBLUE,
    'alpha' :    64,
}
SHIELD['size'] = numpy.array((50,60,65,75,90)) + SHIELD['off']

#powerups
PWUP = {
    'filename_p' :      RES_FOLDER,
    'b_color' :         WHITE,
    'size' :            40,
    'speed' :           2,
    'spawn_time' :      (5000,10000),
    'standard_time' :   10*FPS,
    'font' :            pygame.font.SysFont('comicsans',12),

    'exp_value' :       30,
    'triple_angle' :    PI/8,
    'bomb_amt' :        20,
    'rockets_amt' :     10,
    'fuel_amt' :        FLAMETHROWER['max_ammo']/3
}

#level graphics

GAMEOVER = {
    'font1' : pygame.font.SysFont('comicsans', 60),
    'font2' : pygame.font.SysFont('comicsans', 20),
}

EXPBAR = {
    'x' :               10,
    'y' :               None,
    'w' :               100,
    'h' :               10,
    'b_color' :         DARKGREEN,
    'f_color' :         GREEN,
}
EXPBAR['y'] = SCREENH-EXPBAR['h']-10

LEVELBAR = {
    'x' :           10,
    'y' :           EXPBAR['y']-10,
    'font' :        pygame.font.SysFont("comicsans",12)
}

LIFEBAR = {
    'size' :            20,
    'f_heart_img' :     pygame.image.load(RES_FOLDER+'heart_full.png'),
    'e_heart_img' :     pygame.image.load(RES_FOLDER+'heart_empty.png'),
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
    'img_size' :            30,
    'u_img_size' :          40,
    'font' :                pygame.font.SysFont('comicsans',12),
    'imgs' :                [],
    'ammo_bar_h' :          10,
    'laser_bar_c' :         RED,
    'fuel_bar_c' :          YELLOW,
    'space_between' :       10
}
for i in range(PLAYER['gun_types']):
    img = pygame.image.load(RES_FOLDER+PLAYER['gun_indexes'][i]+'.png')
    res_img = pygame.transform.scale(img,(GUN_BAR['img_size'],GUN_BAR['img_size']))
    GUN_BAR['imgs'].append(res_img)
GUN_BAR['h'] = GUN_BAR['u_img_size'] + 10 + GUN_BAR['ammo_bar_h']
GUN_BAR['w'] = (len(GUN_BAR['imgs'])-1)*GUN_BAR['img_size'] + 1*GUN_BAR['u_img_size'] + (len(GUN_BAR['imgs'])-1)*GUN_BAR['space_between']
GUN_BAR['y'] = SCREENH-10-GUN_BAR['h']
GUN_BAR['x'] = (SCREENW-GUN_BAR['w'])/2
GUN_BAR['ammo_bar_y'] = SCREENH-10-GUN_BAR['ammo_bar_h']