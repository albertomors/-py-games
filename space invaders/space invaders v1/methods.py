import pygame, random
from parameters import *

# <--- methods --->

def remap(x,x1,x2,y1,y2):
    dx = x2-x1
    dy = y2-y1
    return y1 + (x-x1)*dy/dx



def clamped_gaussian(a,b,mu):
    assert a<=mu<=b
    #3*sigma = half side = (b-a)/2
    sigma = (b-a)/2/3
    y = random.gauss(mu,sigma)
    clamped = min(max(a,y),b)
    return clamped



def update_all(pressed_keys,player,bg,enemies,bullets,asteroids,SCREENW,SCREENH):
    bg.update()
    player.update(pressed_keys,enemies,asteroids,bullets,SCREENW,SCREENH)
    for b in bullets:   b.update(bullets)
    for e in enemies:   e.update(bullets)
    for a in asteroids: a.update(bullets)



def kill_dead_sprites(lists):
    for list in lists:
          for sprite in list:
               if sprite.lives <= 0:
                    sprite.killer.exp += sprite.value
                    sprite.killer.points += sprite.value
                    list.remove(sprite)
                    del(sprite)

def kill_oo_sprites(lists,xlim,ylim):
    for list in lists:
          for sprite in list:
               if sprite.oo_borders(xlim,ylim):
                    list.remove(sprite)
                    del(sprite)

def kill_sprites_handler(lists,xlim,ylim):
    kill_dead_sprites(lists)
    kill_oo_sprites(lists,xlim,ylim)



def render_all(surf,player,others):

    for list in others:
        for sprite in list:
            sprite.render(surf)
    player.render(surf)
    
    #levelbar
    font = pygame.font.SysFont("comicsans",LEVELBAR['fontsize'])
    txt = 'ship level: '+str(player.level)
    surf.blit(font.render(txt,True,WHITE),(LEVELBAR['x'],LEVELBAR['y']-font.size(txt)[1]))
    
    #expbar
    pygame.draw.rect(surf,EXPBAR['b_color'], (EXPBAR['x'], EXPBAR['y']-EXPBAR['h'], EXPBAR['w'], EXPBAR['h']))
    pygame.draw.rect(surf,EXPBAR['f_color'], (EXPBAR['x'], EXPBAR['y']-EXPBAR['h'], EXPBAR['w'] * player.exp/PLAYER['exp_to_lvlup'][player.level-1], EXPBAR['h']))

    #lifebar
    for i in range(player.maxlives):
        if player.lives > i:   surf.blit(LIFEBAR['f_heart_img'], (LIFEBAR['xs'][player.level-1] + i*LIFEBAR['w'], LIFEBAR['y']))
        else:                  surf.blit(LIFEBAR['e_heart_img'], (LIFEBAR['xs'][player.level-1] + i*LIFEBAR['w'], LIFEBAR['y']))
    
    #pointsbar
    font = pygame.font.SysFont("comicsans",POINTSBAR['fontsize'])
    txt = 'points: '+str(player.points)
    txt_w = font.size(txt)[0]
    surf.blit(font.render(txt,True,WHITE),(POINTSBAR['_x']-txt_w,POINTSBAR['y']))

    #gameover
    if player.lives <= 0:

        font1 = pygame.font.SysFont('comicsans', 60)
        font2 = pygame.font.SysFont('comicsans', 20)
        txt1 = 'Game Over!'
        txt2 = 'PREMI (R) PER GIOCARE DI NUOVO'
        t1w, t1h = font1.size(txt1)
        t2w, t2h = font2.size(txt2)
        surf.blit(font1.render(txt1, True, WHITE),((SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2))
        surf.blit(font2.render(txt2, True, WHITE),((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))
