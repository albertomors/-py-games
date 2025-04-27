from classes import *
from datetime import date

class Renderer():

    def __init__(self,parent):
        self.parent = parent
        self.timers = {}
        
        self.add_timer('intro')
        self.add_timer('outro')
        self.add_timer('hit_screen')
        self.add_timer('screen_shake')

        self.x, self.y = 50,50
        self.surf = pygame.Surface((SCREENW,SCREENH),pygame.SRCALPHA)

    def add_timer(self,name):
        timer = Timer()
        self.timers[name] = timer
    
    def remove_timer(self,name):
        if self.timers[name]:
            del self.timers[name]
    
    def update_timers(self):
        for t in self.timers:
            self.timers[t].update()

    def render(self,surf):

        self.parent.bg.render(self.surf)

        for list in [self.parent.enemies,self.parent.asteroids,self.parent.bullets,self.parent.pwups]:
            for sprite in list:
                sprite.render(self.surf)

        self.parent.player.render(self.surf)
        
        self.levelbar(self.surf)
        self.expbar(self.surf)
        self.lifebar(self.surf)
        self.pointsbar(self.surf)
        self.levelnumber(self.surf)
        self.gunbar(self.surf)
        
        if not self.parent.player.alive():
            self.gameover_screen(self.surf)
        
        if self.parent.gamestate == 'tutorial':
            self.tutorial(self.surf)
        elif self.parent.gamestate == 'intro' and self.parent.level_no > 1:
            self.intro(self.surf)
        elif self.parent.gamestate == 'outro':
            self.outro(self.surf)
        elif self.parent.gamestate == 'win':
            self.win_screen(self.surf)
        
        if self.timers['hit_screen'].running:
            self.render_hit_screen(self.surf)
        
        self.update_timers()
        self.update_screen_shake()

        #blit on parent screen
        surf.fill(BLACK)
        surf.blit(self.surf,(self.x,self.y))
    
    def black_screen(self,surf,alpha):
        assert 0 <= alpha <= 255
        black_surf = pygame.Surface((SCREENW,SCREENH),pygame.SRCALPHA)
        black_surf.fill(BLACK)
        black_surf.set_alpha(alpha)
        surf.blit(black_surf,(0,0))
    
    def tutorial(self,surf):
        pygame.draw.rect(surf,PAPER,(SCREENW/3,SCREENH/3-35,SCREENW/3,SCREENH/3+15+35))
        tw = FONT.size(str(date.today().strftime("%B %d, %Y")))[0]
        surf.blit(FONT.render(str(date.today().strftime("%B %d, %Y")),True,BLACK),(SCREENW*2/3-10-tw,SCREENH/3-30))
        surf.blit(FONT.render('Welcome to Space Invaders!',True,BLACK),(SCREENW/3+10,SCREENH/3+10))
        surf.blit(FONT.render('Use WASD to move your spaceship,',True,BLACK),(SCREENW/3+10,SCREENH/3+50))
        surf.blit(FONT.render('left CLICK to shoot and',True,BLACK),(SCREENW/3+10,SCREENH/3+65))
        surf.blit(FONT.render('MOUSE WHEEL to change weapon.',True,BLACK),(SCREENW/3+10,SCREENH/3+80))

        surf.blit(FONT.render('You have 5 weapons available: machine gun,',True,BLACK),(SCREENW/3+10,SCREENH/3+120))
        surf.blit(FONT.render('cannon, rocket launcher, laser gun and',True,BLACK),(SCREENW/3+10,SCREENH/3+135))
        surf.blit(FONT.render('a flamethrower',True,BLACK),(SCREENW/3+10,SCREENH/3+150))

        tw = FONT.size('Good luck, space traveler!')[0]
        surf.blit(FONT.render('Good luck, space traveler!',True,BLACK),(SCREENW*2/3-10-tw,SCREENH/3+190))
        tw = FONT.size('Good luck, space traveler!')[0]
        surf.blit(FONT.render('(press any key to continue)',True,WHITE),((SCREENW-tw)/2,SCREENH/3+230))
        

    def intro(self,surf):
        alpha = round(clamped_remap(self.timers['intro'].time,self.timers['intro'].maxtime,0,255,0))
        self.black_screen(surf,alpha)
        txt1 = 'Level ' + str(self.parent.level_no)
        txt2 = 'PREPARE FOR BATTLE!'
        t1w, t1h = GAMEOVER['font1'].size(txt1)
        t2w, t2h = GAMEOVER['font2'].size(txt2)
        surf.blit(GAMEOVER['font1'].render(txt1, True, WHITE),((SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2))
        surf.blit(GAMEOVER['font2'].render(txt2, True, WHITE),((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))
    
    def outro(self,surf):
        alpha = round(clamped_remap(self.timers['outro'].time,self.timers['outro'].maxtime,0,0,255))
        self.black_screen(surf,alpha)

    def levelbar(self,surf):
        txt = 'ship level: '+str(self.parent.player.level)
        surf.blit(LEVELBAR['font'].render(txt,True,WHITE),(LEVELBAR['x'],LEVELBAR['y']-LEVELBAR['font'].size(txt)[1]))

    def expbar(self,surf):
        pygame.draw.rect(surf,EXPBAR['b_color'], (EXPBAR['x'], EXPBAR['y'], EXPBAR['w'], EXPBAR['h']))
        pygame.draw.rect(surf,EXPBAR['f_color'], (EXPBAR['x'], EXPBAR['y'], EXPBAR['w'] * self.parent.player.exp/PLAYER['exp_to_lvlup'][self.parent.player.level-1], EXPBAR['h']))

    def lifebar(self,surf):
        for i in range(self.parent.player.maxlives):
            if self.parent.player.lives > i:   surf.blit(LIFEBAR['f_heart_img'], (LIFEBAR['xs'][self.parent.player.level-1] + i*LIFEBAR['size'], LIFEBAR['y']))
            else:                  surf.blit(LIFEBAR['e_heart_img'], (LIFEBAR['xs'][self.parent.player.level-1] + i*LIFEBAR['size'], LIFEBAR['y']))

    def pointsbar(self,surf):
        txt = 'points: '+str(self.parent.player.points)
        txt_w = POINTSBAR['font'].size(txt)[0]
        surf.blit(POINTSBAR['font'].render(txt,True,WHITE),(POINTSBAR['_x']-txt_w,POINTSBAR['y']))
    
    def levelnumber(self,surf):
        txt = 'level: '+str(self.parent.level_no)
        surf.blit(FONT.render(txt,True,WHITE),(10,10))

    def gunbar(self,surf):

        i = 0
        x = 0
        
        b_surf = pygame.Surface((GUN_BAR['bw'],GUN_BAR['bh']),pygame.SRCALPHA)
        pygame.draw.rect(b_surf,LIGHTGRAY,(0,0,GUN_BAR['bw'],GUN_BAR['bh']))
        b_surf.set_alpha(32)
        surf.blit(b_surf,(GUN_BAR['bx'],GUN_BAR['by']))

        for name,gun in self.parent.player.guns.items():
            img = GUN_BAR['imgs'][i].copy()

            #if im using that
            if gun == self.parent.player.gun:
                img = pygame.transform.scale(img,(GUN_BAR['u_size'],GUN_BAR['u_size']))
                dx = GUN_BAR['u_size']
                dy = 0
            else:
                dx = GUN_BAR['size']
                dy = GUN_BAR['u_size'] - GUN_BAR['size']
                img.set_alpha(128)

            surf.blit(img,(GUN_BAR['x']+x,GUN_BAR['y']+dy))

            #show ammos
            if name == 'lasergun' or name == 'flamethrower':
                if name == 'lasergun':  color = GUN_BAR['laser_bar_c']
                else:                   color = GUN_BAR['oil_bar_c']

                bar_val = gun.ammo/gun.max_ammo
                pygame.draw.rect(surf,color, (GUN_BAR['x']+x, GUN_BAR['ammo_bar_y'], dx*bar_val, GUN_BAR['ammo_bar_h']))
                pygame.draw.rect(surf,WHITE, (GUN_BAR['x']+x, GUN_BAR['ammo_bar_y'], dx, GUN_BAR['ammo_bar_h']),1)

            else:
                txt_w, txt_h = GUN_BAR['font'].size(str(gun.ammo))
                txt = '∞' if gun.ammo == math.inf else str(gun.ammo)
                surf.blit(GUN_BAR['font'].render(txt,True,WHITE),(GUN_BAR['x']+x+(dx-txt_w)/2,GUN_BAR['ammo_bar_y']-txt_h/2+GUN_BAR['ammo_bar_h']/2))

            x += (dx + GUN_BAR['space_between'])
            i+=1

    def gameover_screen(self,surf):
        txt1 = 'Game Over!'
        txt2 = 'PRESS (R) TO PLAY AGAIN'
        t1w, t1h = GAMEOVER['font1'].size(txt1)
        t2w, t2h = GAMEOVER['font2'].size(txt2)
        surf.blit(GAMEOVER['font1'].render(txt1, True, WHITE),((SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2))
        surf.blit(GAMEOVER['font2'].render(txt2, True, WHITE),((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))
    
    def win_screen(self,surf):
        self.black_screen(surf,255)
        txt1 = 'Victory!'
        txt2 = 'PRESS (R) TO PLAY AGAIN'
        t1w, t1h = GAMEOVER['font1'].size(txt1)
        t2w, t2h = GAMEOVER['font2'].size(txt2)
        surf.blit(GAMEOVER['font1'].render(txt1, True, WHITE),((SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2))
        surf.blit(GAMEOVER['font2'].render(txt2, True, WHITE),((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))
    
    def render_hit_screen(self,surf):
        alpha = round(clamped_remap(self.timers['hit_screen'].time,self.timers['hit_screen'].maxtime,0,LEVEL['hit_screen_alpha'],0))
        red_surf = pygame.Surface((SCREENW,SCREENH),pygame.SRCALPHA)
        red_surf.fill(RED)
        red_surf.set_alpha(alpha)
        surf.blit(red_surf,(0,0))
    
    def update_screen_shake(self):
        if self.timers['screen_shake'].running:
            self.x = random.randint(-LEVEL['shake_amt'],+LEVEL['shake_amt'])
            self.y = random.randint(-LEVEL['shake_amt'],+LEVEL['shake_amt'])
        else:
            self.x, self.y = 0, 0
    
    def hit_screen(self):
        self.timers['hit_screen'].start(LEVEL['hit_screen_time'])
    
    def screen_shake(self):
        self.timers['screen_shake'].start(LEVEL['shake_time'])