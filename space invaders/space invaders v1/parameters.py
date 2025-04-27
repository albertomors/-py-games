import pygame
import math, numpy

# <--- game parameters --->

#generics
SCREENW, SCREENH = 800,600
FPS = 120
PI = math.pi
RES_FOLDER = 'C:/Users/alber/Documents/pygame/arcade classics/space invaders/space invaders v1/res/'
FONTSIZE = 14


#colors
WHITE = (255,255,255)
BLACK = (0,0,0)
DARKGRAY = (10,10,10)
RED = (255,0,0)
GREEN = (0,255,0)
DARKGREEN = (0,64,0)



BG = {
    'color' :           DARKGRAY,
    'scroll_speed' :    4,
    'stars_num' :       (5,50),
    'stars_size' :      (1,5),
}



BULLET = {
    'color' :   RED,
    'w' :       3,
    'h' :       10,
    'speed' :   -5,
}



ASTEROID = {
    'img' :             pygame.image.load(RES_FOLDER+'asteroid.png'),
    'size' :            (50,300),
    'speed' :           (2,.5),
    'rot_speed' :       numpy.array((180,10))/FPS,
    'lives' :           (1,60),
    'spawn_time' :      (500,8000),
}



ENEMY = {
    'crop_w' :          99,
    'crop_h' :          98,
    'img' :             pygame.image.load(RES_FOLDER+'sprites.png'),
    'h_num' :           19,
    'v_num' :           11,
    'w' :               50,
    'h' :               50,
    'speed' :           (0.5,3),
    'spawn_time' :      (100,3000),
}



PLAYER = {
    'img_path' :        RES_FOLDER+'ss',
    'w' :               (40,46,52,60,70),
    'h' :               (40,40,45,45,60),
    'levels' :          5,
    'maxlives' :        (3,4,5,7,10),
    'max_speed' :       (4,4.3,4.7,5,5.5),
    'speed_eps' :       0.01,
    'acc' :             (0.08,0.1,0.12,0.15,0.18),
    'friction' :        0.95,
    'firerate' :        numpy.array((0.5,0.25,0.25,0.15,0.15)) * FPS,
    'firespots' :       ([(20,2)],[(22,2)],[(12,18),(39,18)],[(12,13),(47,13)],[(12,19),(34,18),(57,19)]),
    'exp_to_lvlup' :    (15,30,60,120,math.inf),
}
PLAYER['max_points'] = sum(PLAYER['exp_to_lvlup'][:-1])+100



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
    'fontsize' :    FONTSIZE,
}

LIFEBAR = {
    'f_heart_img' :     pygame.image.load(RES_FOLDER+'heart_full.png'),
    'e_heart_img' :     pygame.image.load(RES_FOLDER+'heart_empty.png'),
    'xs' :              None,
    'y' :               None,
}
LIFEBAR['w'] = LIFEBAR['f_heart_img'].get_width()
LIFEBAR['h'] = LIFEBAR['f_heart_img'].get_width()
LIFEBAR['xs'] = SCREENW-10-(numpy.array(PLAYER['maxlives']))*LIFEBAR['w']
LIFEBAR['y'] = SCREENH-10-LIFEBAR['h']



POINTSBAR = {
    '_x' :          SCREENW-10,
    'y' :           10,
    'fontsize' :    FONTSIZE,
}