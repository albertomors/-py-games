import pygame, random
from parameters import *

# <--- methods --->

def remap(x,x1,x2,y1,y2):
    dx = x2-x1
    dy = y2-y1
    return y1 + (x-x1)*dy/dx

def clamped_remap(x,x1,x2,y1,y2):
    try:
        ymin = min(y1,y2)
        ymax = max(y1,y2)
        y = remap(x,x1,x2,y1,y2)
        return min(max(y,ymin),ymax)
    except ZeroDivisionError:
        return y1

def clamped_gaussian(a,b,mu):
    assert a<=mu<=b
    #3*sigma = half side = (b-a)/2
    sigma = (b-a)/2/3
    y = random.gauss(mu,sigma)
    clamped = min(max(a,y),b)
    return clamped

# <-- update methods -->

def update_all(pressed_keys,mouse_pos,mouse_in_window,player,bg,enemies,bullets,asteroids,pwups,SCREENW,SCREENH):
    bg.update()
    player.update(pressed_keys,mouse_pos,mouse_in_window,enemies,bullets,asteroids,pwups,SCREENW,SCREENH)
    for b in bullets:   b.update(bullets,enemies,asteroids)
    for e in enemies:   e.update(bullets)
    for a in asteroids: a.update(bullets)
    for p in pwups:     p.update()

def kill_dead_sprites(lists):
    for list in lists:
          for sprite in list:
               if sprite.lives <= 0:
                    if sprite.killer:
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

# <--- graphics -->

def levelbar(surf,player):
    txt = 'ship level: '+str(player.level)
    surf.blit(LEVELBAR['font'].render(txt,True,WHITE),(LEVELBAR['x'],LEVELBAR['y']-LEVELBAR['font'].size(txt)[1]))

def expbar(surf,player):
    pygame.draw.rect(surf,EXPBAR['b_color'], (EXPBAR['x'], EXPBAR['y']-EXPBAR['h'], EXPBAR['w'], EXPBAR['h']))
    pygame.draw.rect(surf,EXPBAR['f_color'], (EXPBAR['x'], EXPBAR['y']-EXPBAR['h'], EXPBAR['w'] * player.exp/PLAYER['exp_to_lvlup'][player.level-1], EXPBAR['h']))

def lifebar(surf,player):
    for i in range(player.maxlives):
        if player.lives > i:   surf.blit(LIFEBAR['f_heart_img'], (LIFEBAR['xs'][player.level-1] + i*LIFEBAR['size'], LIFEBAR['y']))
        else:                  surf.blit(LIFEBAR['e_heart_img'], (LIFEBAR['xs'][player.level-1] + i*LIFEBAR['size'], LIFEBAR['y']))

def pointsbar(surf,player):
    txt = 'points: '+str(player.points)
    txt_w = POINTSBAR['font'].size(txt)[0]
    surf.blit(POINTSBAR['font'].render(txt,True,WHITE),(POINTSBAR['_x']-txt_w,POINTSBAR['y']))

def gunbar(surf,player):

    i = 0
    x = 0
    for name,gun in player.guns.items():
        img = pygame.Surface((GUN_BAR['img_size'],GUN_BAR['img_size']),pygame.SRCALPHA)
        pygame.draw.rect(img,WHITE,(0,0,GUN_BAR['img_size'],GUN_BAR['img_size']),0,3)
        img.blit(GUN_BAR['imgs'][i],(0,0))

        #if im using that
        if gun == player.gun:
            img = pygame.transform.scale(img,(GUN_BAR['u_img_size'],GUN_BAR['u_img_size']))
            dx = GUN_BAR['u_img_size']
            dy = 0
            alpha = 255
        else:
            dx = GUN_BAR['img_size']
            dy = GUN_BAR['u_img_size'] - GUN_BAR['img_size']
            alpha = 64

        img.set_alpha(alpha)
        surf.blit(img,(GUN_BAR['x']+x,GUN_BAR['y']+dy))

        #show ammos
        if name == 'lasergun' or name == 'flamethrower':
            if name == 'lasergun':  color = GUN_BAR['laser_bar_c']
            else:                   color = GUN_BAR['fuel_bar_c']

            bar_val = gun.ammo/gun.max_ammo
            pygame.draw.rect(surf,color, (GUN_BAR['x']+x, GUN_BAR['ammo_bar_y'], dx*bar_val, GUN_BAR['ammo_bar_h']))
            pygame.draw.rect(surf,WHITE, (GUN_BAR['x']+x, GUN_BAR['ammo_bar_y'], dx, GUN_BAR['ammo_bar_h']),1)

        else:
            txt_w = GUN_BAR['font'].size(str(gun.ammo))[0]
            txt = '∞' if gun.ammo == math.inf else str(gun.ammo)
            surf.blit(GUN_BAR['font'].render(txt,True,WHITE),(GUN_BAR['x']+x+(dx-txt_w)/2,GUN_BAR['ammo_bar_y']))

        x += (dx + GUN_BAR['space_between'])
        i+=1

def gameover_screen(surf):
    txt1 = 'Game Over!'
    txt2 = 'PREMI (R) PER GIOCARE DI NUOVO'
    t1w, t1h = GAMEOVER['font1'].size(txt1)
    t2w, t2h = GAMEOVER['font2'].size(txt2)
    surf.blit(GAMEOVER['font1'].render(txt1, True, WHITE),((SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2))
    surf.blit(GAMEOVER['font2'].render(txt2, True, WHITE),((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))

def render_all(surf,player,others):

    for list in others:
        for sprite in list:
            sprite.render(surf)
            #sprite.debug_render(surf)

    player.render(surf)
    #player.debug_render(surf)
    
    levelbar(surf,player)
    expbar(surf,player)
    lifebar(surf,player)
    pointsbar(surf,player)
    gunbar(surf,player)
    
    if player.lives <= 0:
        gameover_screen(surf)