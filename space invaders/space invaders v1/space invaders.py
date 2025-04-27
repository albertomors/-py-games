# <--- space invaders.py --->
#
# Author: ZeroKroen (Alberto Morselli)
# Date: 14 -- 20/3/23

import pygame, sys
import random, math, numpy
from parameters import *
from methods import *

# <--- objects --->

class Obj():
    def __init__(self,x,y,w,h,img,c):
        self.pos = pygame.math.Vector2(x,y)
        self.w, self.h = w, h

        #replace img with filled surf
        if not img:
            img = pygame.Surface((w,h),pygame.SRCALPHA)
            img.fill(c)

        self.load_sprite(img)
    
    def load_sprite(self,img):
        self.surf = pygame.transform.scale(img,(self.w,self.h))
        self.mask = pygame.mask.from_surface(self.surf)
        self.rect = self.surf.get_rect(center = (round(self.pos.x), round(self.pos.y)) )

    def render(self,surf):
        surf.blit(self.surf,self.rect)



class Timer():
    def __init__(self):
        self.time = 0
        self.running = False

    def start(self,time):
        self.time = time
        self.running = True
    
    def update(self):
        if self.running:
            if self.time > 0:   self.time -= 1
            else:               self.running = False



class MovableObj(Obj):
    def __init__(self,x,y,w,h,img,c,vel):
        super().__init__(x,y,w,h,img,c)
        self.vel = pygame.math.Vector2(vel)
    
    def move(self):
        self.pos += self.vel
        self.rect.center = round(self.pos.x), round(self.pos.y)
    
    def update(self):
        self.move()



class Background(MovableObj):
    def __init__(self):
        super().__init__(SCREENW/2,SCREENH,SCREENW,2*SCREENH,None,BG['color'],(0,BG['scroll_speed']))

        self.surf_t = pygame.Surface((self.w,self.h/2))
        self.surf_b = pygame.Surface((self.w,self.h/2))
        self.generate_stars(self.surf_t)
        self.generate_stars(self.surf_b)
    
    def generate_stars(self,half_surf):
        half_surf.fill(BG['color'])
        w,h = half_surf.get_size()
        
        stars_num = random.randint(BG['stars_num'][0],BG['stars_num'][1])
        for _ in range(stars_num):
            size = random.randint(BG['stars_size'][0],BG['stars_size'][1])
            x,y = random.uniform(size/2,w-size/2), random.uniform(size/2,h-size/2)
            c = random.randint(BG['color'][0],255)
            #draw a monochromatic star
            pygame.draw.rect(half_surf,(c,c,c),(x,y,size,size))
    
    def update(self):
        super().move()

        if self.rect.top >= 0:
            # copy top on bottom, refill the top with new stars, and reset position
            self.surf_b = self.surf_t.copy()
            self.generate_stars(self.surf_t)
            self.pos.y = 0
            self.rect.centery = round(self.pos.y)
    
    def render(self,surf):
        self.surf.blit(self.surf_t,(0,0))
        self.surf.blit(self.surf_b,(0,self.h/2))
        super().render(surf)



class Sprite(MovableObj):
    def __init__(self,x,y,w,h,img,c,vel):
        super().__init__(x,y,w,h,img,c,vel)

        self.maxlives = self.lives = 1
        self.value = 1
        self.exp = self.points = 0
        self.killer = None

        self.timers = {}

    def check_coll(self,obj):
        off_x = obj.rect.x - self.rect.x
        off_y = obj.rect.y - self.rect.y
        if self.mask.overlap(obj.mask,(off_x,off_y)):
            old_lives = self.lives
            self.lives -= obj.lives
            obj.lives -= old_lives
        
        if self.lives <= 0:
            if isinstance(obj,Bullet):      self.killer = obj.owner
            else:                           self.killer = obj
        if obj.lives <= 0:
            if isinstance(self,Bullet):     obj.killer = self.owner
            else:                           obj.killer = self
    
    def check_coll_w(self,others):
        for o in others:
            if not (o == self or (isinstance(o,Bullet) and o.owner == self)):
                self.check_coll(o)
    
    def update(self,bullets):
        super().update()
        self.check_coll_w(bullets)
    
    def add_timer(self,name):
        timer = Timer()
        self.timers[name] = timer
    
    def update_timers(self):
        for t in self.timers:
            self.timers[t].update()


class Bullet(Sprite):
    def __init__(self,x,y,owner):
        super().__init__(x,y,BULLET['w'],BULLET['h'],None,BULLET['color'],(0,BULLET['speed']))
        self.owner = owner
    
    def oo_borders(self,xlim,ylim):
        return self.rect.bottom <= 0



class Asteroid(Sprite):
    def __init__(self,x,y,diff):

        #load params
        s1,s2 = ASTEROID['size'][0], ASTEROID['size'][1]
        v1,v2 = ASTEROID['speed'][0], ASTEROID['speed'][1]
        r1,r2 = ASTEROID['rot_speed'][0], ASTEROID['rot_speed'][1]
        l1,l2 = ASTEROID['lives'][0], ASTEROID['lives'][1]

        #generate randomic asteroid and remap speed, rot_speed and lives based on size
        size = round(clamped_gaussian(s1,s2,remap(diff,0,1,s1,s2)))
        vel = remap(size,s1,s2,v1,v2)
        rot_speed = remap(size,s1,s2,r1,r2)
        lives = round(remap(size,s1,s2,l1,l2))

        super().__init__(x,y,size,size,ASTEROID['img'],None,(0,vel))

        #attributes for rotation
        self.rot_speed = rot_speed
        self.angle = 0
        self.r_surf = self.surf

        self.lives = self.maxlives = lives
        self.value = max(1,round(remap(size,s1,s2,1,PLAYER['maxlives'][-1])))
    
    def rotate(self):
        self.angle = (self.angle+self.rot_speed)%360
        self.r_surf = pygame.transform.rotate(self.surf,self.angle)
        self.mask = pygame.mask.from_surface(self.r_surf)
        self.rect = self.r_surf.get_rect(center = (round(self.pos.x),round(self.pos.y)))
    
    def update(self, bullets):
        self.rotate()
        super().update(bullets)
    
    def oo_borders(self,xlim,ylim):
        return self.rect.top >= ylim
    
    def render(self,surf):
        surf.blit(self.r_surf,self.rect)

class Enemy(Sprite):
    def __init__(self,x,y):
        
        #crop random image from enemies's 'sprites.png'
        x_crop = random.randint(0,ENEMY['h_num']-1) * ENEMY['crop_w']
        y_crop = random.randint(0,ENEMY['v_num']-1) * ENEMY['crop_h']
        crop_rect = pygame.Rect(x_crop,y_crop,ENEMY['crop_w'],ENEMY['crop_h'])
        img = pygame.transform.scale(ENEMY['img'].subsurface(crop_rect),(ENEMY['w'],ENEMY['h']))

        vel = 0, random.uniform(ENEMY['speed'][0],ENEMY['speed'][1])
        super().__init__(x,y,ENEMY['w'],ENEMY['h'],img,None,vel)
    
    def oo_borders(self,xlim,ylim):
        return self.rect.top >= ylim



class Player(Sprite):
    def __init__(self,x,y):

        #load images
        self.images = []
        for i in range(PLAYER['levels']):
            filename = PLAYER['img_path'] + str(i+1) + '.png'
            self.images.append(pygame.image.load(filename))

        self.level = 1
        super().__init__(x,y,PLAYER['w'][self.level-1],PLAYER['h'][self.level-1],self.images[self.level-1],None,(0,0))
        self.load_stats()
        self.acc = pygame.math.Vector2(0,0)
        
        self.add_timer('ready_to_shoot')
    
    def load_stats(self):
        self.w = PLAYER['w'][self.level-1]
        self.h = PLAYER['h'][self.level-1]
        self.maxlives = PLAYER['maxlives'][self.level-1]
        if self.level == 1:     self.lives = self.maxlives
        else:                   self.lives += PLAYER['maxlives'][self.level-1] - PLAYER['maxlives'][self.level-2]
        self.max_speed = PLAYER['max_speed'][self.level-1]
        self.acc_value = PLAYER['acc'][self.level-1]
        self.firerate = PLAYER['firerate'][self.level-1]
        self.firespots = PLAYER['firespots'][self.level-1]
    
    def move(self,pressed_keys):
        # acc handler on x-axis
        if pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:       self.acc.x = -self.acc_value
        elif pressed_keys[pygame.K_d] and not pressed_keys[pygame.K_a]:     self.acc.x = +self.acc_value
        else:
            self.acc.x = 0
            self.vel.x *= PLAYER['friction']
        
        # acc handler y-axis
        if pressed_keys[pygame.K_w] and not pressed_keys[pygame.K_s]:       self.acc.y = -self.acc_value
        elif pressed_keys[pygame.K_s] and not pressed_keys[pygame.K_w]:     self.acc.y = +self.acc_value
        else:
            self.acc.y = 0
            self.vel.y *= PLAYER['friction']
        
        # max speed handler
        self.vel += self.acc
        if self.vel.length() >= self.max_speed:   self.vel.clamp_magnitude_ip(self.max_speed)

        super().move()
    
    def check_coll_w_borders(self,xlim,ylim):
        #x-axis
        if self.pos.x - self.w/2 <= 0:
            self.pos.x = self.w/2
            self.vel.x = 0
        elif self.pos.x + self.w/2 >= xlim:
            self.pos.x = xlim - self.w/2
            self.vel.x = 0
        
        #y-axis
        if self.pos.y - self.h/2 <= 0:
            self.pos.y = self.h/2
            self.vel.y = 0
        elif self.pos.y + self.h/2 >= ylim:
            self.pos.y = ylim - self.h/2
            self.vel.y = 0
        
        #correct position
        self.rect.center = round(self.pos.x), round(self.pos.y)
    
    def level_up(self):
        if self.level < PLAYER['levels']:     self.level += 1
        self.load_stats()
        self.load_sprite(self.images[self.level-1])
    
    def fire_handler(self,pressed_keys,bullets):
         if pressed_keys[pygame.K_SPACE] and not self.timers['ready_to_shoot'].running:     self.shoot(bullets)
    
    def shoot(self,bullets):
        for spot in self.firespots:
            bullet = Bullet(self.pos.x - self.w/2 + spot[0], self.pos.y - self.h/2 + spot[1], self)
            bullets.append(bullet)

        self.timers['ready_to_shoot'].start(self.firerate)
    
    def check_exp(self):
        if self.exp >= PLAYER['exp_to_lvlup'][self.level-1]:
            self.level_up()
            self.exp = 0
    
    def update(self,pressed_keys,enemies,asteroids,bullets,xlim,ylim):
        self.move(pressed_keys)
        self.fire_handler(pressed_keys,bullets)
        self.check_coll_w(enemies)
        self.check_coll_w(bullets)
        self.check_coll_w(asteroids)
        self.check_coll_w_borders(xlim,ylim)
        self.update_timers()
        self.check_exp()

# <--- initialize everything --->

pygame.init()
screen = pygame.display.set_mode((SCREENW,SCREENH))
pygame.display.set_caption('Space Invaders!')
clock = pygame.time.Clock()

while True:

    bg = Background()
    enemies = []
    bullets = []
    asteroids = []
    player = Player(SCREENW/2,SCREENH-100)
    gameloop = True

    enemy_timer_rst = asteroid_timer_rst = pygame.time.get_ticks()
    diff = min(remap(player.points,0,PLAYER['max_points'],0,1),1)
    inv_diff = 1-diff

    t1, t2 = ENEMY['spawn_time'][0], ENEMY['spawn_time'][1]
    enemy_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)
    t1, t2 = ASTEROID['spawn_time'][0], ASTEROID['spawn_time'][1]
    asteroid_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

    while gameloop:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                gameloop = False

        # <--- gameloop --->

        time = pygame.time.get_ticks()
        pressed_keys = pygame.key.get_pressed()

        if player.lives > 0:
            
            diff = min(remap(player.points,0,PLAYER['max_points'],0,1),1)
            inv_diff = 1-diff

            if time - enemy_timer_rst >= enemy_timer:
                enemy_timer_rst = time
                t1, t2 = ENEMY['spawn_time'][0], ENEMY['spawn_time'][1]
                enemy_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

                x, y = random.uniform(ENEMY['w']/2,SCREENW-ENEMY['w']/2), -ENEMY['h']
                enemies.append(Enemy(x,y))

            if time - asteroid_timer_rst >= asteroid_timer:
                asteroid_timer_rst = time
                t1, t2 = ASTEROID['spawn_time'][0], ASTEROID['spawn_time'][1]
                asteroid_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

                x, y = random.uniform(ASTEROID['size'][1]/2,SCREENW-ASTEROID['size'][1]/2), -ASTEROID['size'][1]
                asteroids.append(Asteroid(x,y,diff))

            update_all(pressed_keys,player,bg,enemies,bullets,asteroids,SCREENW,SCREENH)
            kill_sprites_handler([enemies,asteroids,bullets],SCREENW,SCREENH)

            render_all(screen,player,[[bg],bullets,asteroids,enemies])

            #debug
            """ font = pygame.font.SysFont('comicsans',12)
            for a in asteroids:
                screen.blit(font.render('w:'+str(a.w)[:5],True,WHITE),(a.pos))
                screen.blit(font.render('vel:'+str(a.vel)[:5],True,WHITE),(a.pos)+(0,10))
                screen.blit(font.render('rot:'+str(a.rot_speed)[:5],True,WHITE),(a.pos)+(0,20))
                screen.blit(font.render('angle:'+str(a.angle)[:5],True,WHITE),(a.pos)+(0,30))
                screen.blit(font.render('l:'+str(a.lives),True,WHITE),(a.pos)+(0,40))
                screen.blit(font.render('val:'+str(a.value),True,WHITE),(a.pos)+(0,50))
            
            screen.blit(font.render('enemy:'+str(enemy_timer)[:5]+'->'+str(enemy_timer-time+enemy_timer_rst)[:5],True,WHITE),(10,10))
            screen.blit(font.render('asteroid:'+str(asteroid_timer)[:5]+'->'+str(asteroid_timer-time+asteroid_timer_rst)[:5],True,WHITE),(10,20))
            screen.blit(font.render('diff:'+str(diff)[:5],True,WHITE),(10,30))
            screen.blit(font.render('lives:'+str(player.lives),True,WHITE),(10,40)) """
        
        pygame.display.flip()
        clock.tick(FPS)