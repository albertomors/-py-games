# <--- pong.py --->
#
# Author: ZeroKroen (Alberto Morselli)
# Date: 8 -- 13/03/23


import pygame, sys
import math, random, numpy

from parameters import *
from methods import *



# <--- objects --->

class Obj():
    def __init__(self,x,y,w,h):
        self.pos = pygame.math.Vector2(x,y)
        self.w, self.h = w, h
        self.surf = pygame.Surface((w,h))
        self.rect = self.surf.get_rect(center = (x,y))

    def render(self,surf):
        surf.blit(self.surf,self.rect)



class Wall(Obj):
    def __init__(self,x):
        super().__init__(x,SCREENH/2,WALL_W,SCREENH)
        self.surf.fill(GRAY)
        self.destroy_TIMER = PWUP_WALL_TIME

    def update(self,walls):
        self.destroy_TIMER -= 1
        if self.destroy_TIMER <= 0: walls.remove(self)



class PowerUp(Obj):
    def __init__(self,x,y):
        super().__init__(x,y,PWUP_W,PWUP_H)
        self.type = random.choice(['mult','freeze','maxpad','minpad','wall','value','speed','ghost'])
        self.value = None

        #graphics
        self.surf.fill(PWUP_COLORS[self.type])
        pygame.draw.rect(self.surf,WHITE,self.rect,2)
            
        if self.type == 'mult':
            self.value = random.randint(PWUP_MIN_MULT,PWUP_MAX_MULT)
            font = pygame.font.SysFont('comicsans',14)
            txt = font.render('x' + str(self.value), True, BLACK)
            tw,th = font.size('x' + str(self.value))
            self.surf.blit(txt,((PWUP_W-tw)/2,(PWUP_H-th)/2))
        elif self.type == 'value':
            self.value = random.randint(PWUP_MIN_BALL_VALUE,PWUP_MAX_BALL_VALUE)
            font = pygame.font.SysFont('comicsans',14)
            txt = font.render('!', True, BLACK)
            tw,th = font.size('!')
            self.surf.blit(txt,((PWUP_W-tw)/2,(PWUP_H-th)/2))
        else:
            filename = 'C:/Users/alber/Documents/pygame/arcade classics/pong/res/' + str(self.type) + '.png'
            img = pygame.image.load(filename)
            self.surf.blit(img,(0,0))

    def active(self,active_ball,balls,walls):
        if self.type == 'mult':
            for i in range(self.value-1):
                b = Ball(active_ball.pos.x,active_ball.pos.y,active_ball.owner)
                balls.append(b)
        
        elif self.type == 'freeze':
            freeze_time = random.randint(PWUP_MIN_FREEZE_TIME,PWUP_MAX_FREEZE_TIME)
            active_ball.wait(freeze_time)
        
        elif self.type == 'maxpad':
            active_ball.owner.maximize()
        
        elif self.type == 'minpad':
            active_ball.owner.minimize()

        elif self.type == 'wall':
            if active_ball.owner == pad1:
                wall = Wall(WALL_W/2)
            else:
                wall = Wall(SCREENW-WALL_W/2)
            walls.append(wall)
        
        elif self.type == 'value':
            active_ball.value = self.value
            r,g,b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
            active_ball.surf = pygame.Surface((BALL_SIZE,BALL_SIZE))
            pygame.draw.circle(active_ball.surf,(r,g,b),(active_ball.w/2,active_ball.h/2),active_ball.radius)

        elif self.type == 'speed':
            active_ball.speed = PWUP_SPEED
            active_ball.vel.scale_to_length(active_ball.speed)
        
        elif self.type == 'ghost':
            active_ball.surf = pygame.Surface((BALL_SIZE,BALL_SIZE))
            pygame.draw.circle(active_ball.surf,(12,12,12),(active_ball.w/2,active_ball.h/2),active_ball.radius)



# <--- class Ball --->

class Ball(Obj):
    def __init__(self,x,y,owner):
        super().__init__(x,y,BALL_SIZE,BALL_SIZE)
        self.radius = BALL_SIZE/2
        pygame.draw.circle(self.surf,WHITE,(self.w/2,self.h/2),self.radius)

        #generate random starting angle
        angle = PI/2
        while abs(math.sin(angle)) >= .8: #make it not too vertical
            angle = random.uniform(0,2*PI)
        
        self.speed = BALL_SPEED
        self.vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * self.speed

        #timers
        self.wait_TIMER = 0
        self.waiting = False

        self.owner = owner
        self.value = 1

    def move(self):
        if not self.waiting:    self.pos += self.vel
        self.rect.center = round(self.pos.x),round(self.pos.y)
    
    def wait(self,time):
        self.wait_TIMER = time
        self.waiting = True
    
    def update_TIMERS(self):
        self.wait_TIMER -= 1

        if self.wait_TIMER <= 0:    self.waiting = False
    
    def check_coll_w_pwups(self,powerups,balls,walls):
        for pwup in powerups:
            if pygame.Rect.colliderect(self.rect,pwup.rect):
                pwup.active(self,balls,walls)
                powerups.remove(pwup)

    def check_coll_w_pads(self,pads):
        for p in pads:
            if pygame.Rect.colliderect(self.rect,p.rect):
                
                t = abs(self.rect.top - p.rect.bottom)
                b = abs(self.rect.bottom - p.rect.top)
                l = abs(self.rect.left - p.rect.right)
                r = abs(self.rect.right - p.rect.left)

                side = min(t,b,l,r) #search for minimum distance == collision

                if side == t or side == b:
                    if side == t:       self.rect.top = p.rect.bottom
                    elif side == b:     self.rect.bottom = p.rect.top
                    
                    self.vel.y *= -1   
                
                elif side == l or side == r:
                    if side == l:       self.rect.left = p.rect.right
                    elif side == r:     self.rect.right = p.rect.left

                    nv = self.pos - p.pos #bounce vector
                    self.vel.y = nv.normalize().y * math.sin(PAD_MAX_ANGLESPAN)/1 #reduce vertical span
                    # opposite old vel.x sign * vel.x amount remaining after vertical correction
                    self.vel.x = -1 * numpy.sign(self.vel.x) * math.sqrt(1 - self.vel.y**2)
                    self.vel.scale_to_length(self.speed)

                self.pos = pygame.math.Vector2(self.rect.center)
                self.owner = p

    def check_coll_w_walls(self,walls):
        for w in walls:
            if pygame.Rect.colliderect(self.rect,w.rect):

                t = abs(self.rect.top - w.rect.bottom)
                b = abs(self.rect.bottom - w.rect.top)
                l = abs(self.rect.left - w.rect.right)
                r = abs(self.rect.right - w.rect.left)

                side = min(t,b,l,r) #search for minimum distance == collision
        
                if side == t or side == b:
                    if side == t:       self.rect.top = w.rect.bottom
                    elif side == b:     self.rect.bottom = w.rect.top
                    
                    self.vel.y *= -1   
                
                elif side == l or side == r:
                    if side == l:       self.rect.left = w.rect.right
                    elif side == r:     self.rect.right = w.rect.left

                    self.vel.x *= -1   

                self.pos = pygame.math.Vector2(self.rect.center)

    def check_coll_w_borders(self,ylim):
        if self.pos.y - self.h/2 <= 0:
            self.pos.y = self.h/2
            self.vel.y *= -1
        elif self.pos.y + self.h/2 >= ylim:
            self.pos.y = ylim - self.h/2
            self.vel.y *= -1
        
        self.rect.centery = round(self.pos.y)

    def check_coll_w_balls(self,balls):
        for b in balls:
            if b != self:
                try:
                    nv = self.pos - b.pos
                    if nv.length() < self.radius + b.radius:
                        nv.scale_to_length(self.radius+b.radius-nv.length())
                        self.pos += nv
                        self.vel.reflect_ip(nv.normalize())

                        self.rect.center = round(self.pos.x), round(self.pos.y)
                except:
                    pass #wait for minimum distance
    
    def update(self,balls,pads,powerups,walls,ylim):
        self.update_TIMERS()
        self.move()
        self.check_coll_w_pwups(powerups,balls,walls)
        self.check_coll_w_balls(balls)
        self.check_coll_w_pads(pads)
        self.check_coll_w_walls(walls)
        self.check_coll_w_borders(ylim)



class Pad(Obj):
    def __init__(self,x,y,k_up,k_down):
        super().__init__(x,y,PAD_W,PAD_H)
        self.surf.fill(WHITE)
        self.vel = pygame.math.Vector2(0,0)
        self.acc = pygame.math.Vector2(0,0)

        self.k_up, self.k_down = k_up, k_down
        self.points = 0

        #timers
        self.lose_animation_TIMER = 0
        self.lost_point = False

        self.minmax_TIMER = 0
        self.stretched = False
    
    def reset_sprite(self):
        self.h = PAD_H
        self.surf = pygame.Surface((self.w,self.h))
        self.surf.fill(WHITE)
        self.rect = self.surf.get_rect(center = round(self.pos))
        
    def stretch(self,h):
        self.stretched = True
        self.minmax_TIMER = PWUP_MAXMIN_TIME

        self.h = h
        self.surf = pygame.Surface((self.w,self.h))
        self.surf.fill(WHITE)
        self.rect = self.surf.get_rect(center = round(self.pos))
    
    def minimize(self):
        self.stretch(PWUP_MINIMIZE_H)
    
    def maximize(self):
        self.stretch(PWUP_MAXIMIZE_H)
    
    def move(self,pressed_keys):
        if pressed_keys[self.k_up]:       self.acc.y = -PAD_ACC
        elif pressed_keys[self.k_down]:   self.acc.y = +PAD_ACC
        else:
            self.acc.y = 0
            self.vel *= PAD_FRICTION

        if self.vel.length() <= PAD_MAX_SPEED:      self.vel += self.acc
        else:                                       self.vel.clamp_magnitude_ip(PAD_MAX_SPEED)

        self.pos += self.vel
        self.rect.centery = round(self.pos.y)
    
    def check_coll_w_borders(self,ylim):
        if self.pos.y - self.h/2 <= 0:
            self.pos.y = self.h/2
        elif self.pos.y + self.h/2 >= ylim:
            self.pos.y = ylim - self.h/2
        
        self.rect.centery = round(self.pos.y)
    
    def lose_animation(self):
        self.lose_animation_TIMER = PAD_LOSING_ANIMATION_TIME
        self.lost_point = True
    
    def update_TIMERS(self):
        self.lose_animation_TIMER -= 1
        self.minmax_TIMER -= 1

        if self.lost_point:
            time_block = int(self.lose_animation_TIMER / PAD_LOSING_FLASH_TIME)
            color = WHITE if time_block % 2 == 0 else RED
            self.surf.fill(color)

        if self.lost_point and self.lose_animation_TIMER <= 0:
            self.reset_sprite()
            self.lost_point = False

        if self.stretched and self.minmax_TIMER <= 0:
            self.reset_sprite()
            self.stretched = False

    def update(self,pressed_keys,ylim):
        self.update_TIMERS()
        self.move(pressed_keys)
        self.check_coll_w_borders(ylim)
    
    def score(self,amt):
        self.points += amt



# <--- initialize everything --->

pygame.init()
screen = pygame.display.set_mode((SCREENW,SCREENH))
pygame.display.set_caption('Pong!')
clock = pygame.time.Clock()

while True:

    balls = []

    pads = []
    pad1 = Pad(PAD_W/2+20,SCREENH/2,pygame.K_w,pygame.K_s)
    pad2 = Pad(SCREENW-PAD_W/2-20,SCREENH/2,pygame.K_UP,pygame.K_DOWN)
    pads.append(pad1)
    pads.append(pad2)

    powerups = []
    walls = []
    
    pwup_TIMER = random.randint(PWUP_MIN_SPAWN_TIME, PWUP_MAX_SPAWN_TIME)
    last_hitter = random.choice([pad1,pad2])

    gameloop = True
    winner = None

    while gameloop:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                gameloop = False

        # <--- gameloop --->

        if not winner:

            pressed_keys = pygame.key.get_pressed()

            pwup_TIMER -= 1
            if pwup_TIMER <= 0:
                done = False
                while not done:
                    x,y = random.randint(PWUP_MIN_X,PWUP_MAX_X), random.randint(PWUP_MIN_Y,PWUP_MAX_Y)
                    pwup = PowerUp(x,y)
                    
                    colliding = False
                    for p in powerups:
                        if pygame.Rect.colliderect(pwup.rect,p.rect):
                            colliding = True
                    if not colliding:  done = True

                powerups.append(pwup)
                pwup_TIMER = random.randint(PWUP_MIN_SPAWN_TIME, PWUP_MAX_SPAWN_TIME)
            
            for pad in pads:
                pad.update(pressed_keys,SCREENH)
            
            for wall in walls:
                wall.update(walls)

            for ball in balls:
                ball.update(balls,pads,powerups,walls,SCREENH)

                if ball.rect.right <= 0:
                    pad2.score(ball.value)
                    balls.remove(ball)
                    pad1.lose_animation()
                    last_hitter = pad2

                elif ball.rect.left >= SCREENW:
                    pad1.score(ball.value)
                    balls.remove(ball)
                    pad2.lose_animation()
                    last_hitter = pad1
            
            if not balls:
                ball = Ball(SCREENW/2,SCREENH/2,last_hitter)
                ball.wait(NEWBALL_DELAY)
                balls.append(ball)
            
            if pad1.points >= POINTS_TO_WIN and pad2.points < POINTS_TO_WIN:
                winner = 'player 1'
            elif pad1.points < POINTS_TO_WIN and pad2.points >= POINTS_TO_WIN:
                winner = 'player 2'
            elif pad1.points >= POINTS_TO_WIN and pad2.points >= POINTS_TO_WIN:
                winner = 'player 1' if pad1.points > pad2.points else 'player 2'
            
            render_all(screen,balls,pads,powerups,walls)
        
        #wins
        else:
            
            font1 = pygame.font.SysFont('comicsans', 60)
            font2 = pygame.font.SysFont('comicsans', 20)
            gameover_str1 = winner + ' wins!'
            gameover_str2 = 'PREMI (R) PER GIOCARE DI NUOVO'
            gameover_txt1 = font1.render(gameover_str1, False, WHITE)
            gameover_txt2 = font2.render(gameover_str2, False, WHITE)
            t1w, t1h = font1.size(gameover_str1)
            t2w, t2h = font2.size(gameover_str2)
            x1, y1 = (SCREENW-t1w)/2, (SCREENH-t1h-t2h)/2
            x2, y2 = (SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h
            pygame.draw.rect(screen,BLACK,(x1,y1,t1w,y2-y1+t2h))
            screen.blit(gameover_txt1,(x1,y1))
            screen.blit(gameover_txt2,(x2,y2))

        pygame.display.flip()
        clock.tick(FPS)