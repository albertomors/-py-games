import pygame
from parameters import *



# <--- methods --->

def render_all(surf,balls,pads,powerups,walls):
    surf.fill(BLACK)
    for pad in pads:        pad.render(surf)
    for ball in balls:      ball.render(surf)
    for pw in powerups:     pw.render(surf)
    for w in walls:         w.render(surf)

    # text
    font = pygame.font.SysFont('comicsans',20)

    surf.blit(font.render('player 1',True,WHITE), (20,20))
    p1 = str(pads[0].points)
    txt1 = font.render(p1, True, WHITE)
    surf.blit(txt1, (20,45))

    surf.blit(font.render('player 2',True,WHITE), (SCREENW-font.size('player 2')[0]-20,20))
    p2 = str(pads[1].points)
    txt2 = font.render(p2, True, WHITE)
    surf.blit(txt2, (SCREENW-font.size(p2)[0]-20,45))