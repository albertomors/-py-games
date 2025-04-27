# <--- space invaders - the game.py --->
#
# Author: ZeroKroen (Alberto Morselli)
# Date: 22/03 -- 

import pygame, sys
import random, math, numpy
from parameters import *
from methods import *

dfont = pygame.font.SysFont('comicsans',10)

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
    
    def debug_render(self,surf):
        pygame.draw.rect(surf,RED,self.rect,1)

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
    
    def debug_render(self,surf):
        super().debug_render(surf)
        surf.blit(dfont.render(str(self.pos),True,WHITE),(self.pos+(0,0)))
        surf.blit(dfont.render(str(self.vel),True,WHITE),(self.pos+(0,10)))

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
    
    def debug_render(self,surf):
        pygame.draw.rect(surf,RED,(self.rect.left,self.pos.y,self.w,self.h/2),1)

class Sprite(MovableObj):
    def __init__(self,x,y,w,h,img,c,vel):
        super().__init__(x,y,w,h,img,c,vel)

        self.maxlives = self.lives = self.lifecost = self.value = 1
        self.exp = self.points = 0
        self.killer = None

        self.timers = {}

    def check_coll(self,obj):
        off_x = obj.rect.x - self.rect.x
        off_y = obj.rect.y - self.rect.y
        if self.mask.overlap(obj.mask,(off_x,off_y)):
            self.lives -= obj.lifecost
            obj.lives -= self.lifecost
        
        if self.lives <= 0:
            if isinstance(obj,Bullet):      self.killer = obj.owner
            else:                           self.killer = obj
        if obj.lives <= 0:
            if isinstance(self,Bullet):     obj.killer = self.owner
            else:                           obj.killer = self
    
    def check_coll_w(self,others):
        for o in others:
            if not (o == self or (isinstance(o,Bullet) and (o.owner == self or \
                                                           (isinstance(self,Bullet) and o.owner == self.owner)))):
                self.check_coll(o)
    
    def update(self,bullets):
        super().update()
        self.check_coll_w(bullets)

    def update_lifecost(self):
        self.lifecost = self.lives
    
    def add_timer(self,name):
        timer = Timer()
        self.timers[name] = timer
    
    def remove_timer(self,name):
        if self.timers[name]:
            del self.timers[name]
    
    def update_timers(self):
        for t in self.timers:
            self.timers[t].update()
    
    def debug_render(self, surf):
        super().debug_render(surf)
        surf.blit(dfont.render('lives: '+str(self.lives),True,WHITE),(self.pos+(0,20)))
        surf.blit(dfont.render('cost: '+str(self.lifecost),True,WHITE),(self.pos+(0,30)))

class Bullet(Sprite):
    def __init__(self,x,y,w,h,img,color,vel,owner):
        super().__init__(x,y,w,h,img,color,vel)
        self.owner = owner
    
    def oo_borders(self,xlim,ylim):
        out =   (self.rect.bottom <= 0) or \
                (self.rect.top >= ylim) or \
                (self.rect.right <= 0) or \
                (self.rect.left >= xlim)
        return out

    def update(self,bullets,enemies,asteroids):
        super().update(bullets)

    def update_lifecost(self):
        pass

class BasicBullet(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,BULLET['size'],BULLET['size'],BULLET['img'],None,(0,BULLET['speed']),owner)

class CannonBall(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,CANNONBALL['size'],CANNONBALL['size'],CANNONBALL['img'],None,(0,CANNONBALL['speed']),owner)
        self.lifecost = CANNONBALL['lifecost']

        #attributes for rotation
        self.rot_speed = CANNONBALL['r_speed']
        self.angle = 0
        self.r_surf = self.surf
    
    def rotate(self):
        self.angle = (self.angle+self.rot_speed)%360
        self.r_surf = pygame.transform.rotate(self.surf,self.angle)
        self.mask = pygame.mask.from_surface(self.r_surf)
        self.rect = self.r_surf.get_rect(center = (round(self.pos.x),round(self.pos.y)))
    
    def update(self,bullets,enemies,asteroids):
        self.rotate()
        super().update(bullets,enemies,asteroids)
    
    def render(self,surf):
        surf.blit(self.r_surf,self.rect)

class Laser(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,LASER['w'],LASER['h'],None,LASER['color'],(0,LASER['speed']),owner)
        self.lives = +math.inf

class Rocket(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,ROCKET['size'],ROCKET['size'],ROCKET['img'],None,(0,ROCKET['speed']),owner)
        self.lifecost = ROCKET['lifecost']

        #attributes for rotation
        self.angle = math.atan2(self.vel.y,self.vel.x)
        self.r_surf = self.surf
        self.radar = ROCKET['radar']
    
    def check_dir(self,enemies,asteroids):
        for list in [enemies,asteroids]:
            for e in list:
                
                dir = (self.pos - e.pos)
                if dir.length() <= self.radar + min(e.w,e.h)/2:
                    angle = math.degrees(math.atan2(dir.y,dir.x))
                    self.vel = pygame.math.Vector2(ROCKET['speed'],0).rotate(angle)
                    self.rotate()
                    return
    
    def rotate(self):
        self.angle = math.degrees(math.atan2(-self.vel.y,self.vel.x))
        self.r_surf = pygame.transform.rotate(self.surf,(self.angle-90))
        self.mask = pygame.mask.from_surface(self.r_surf)
        self.rect = self.r_surf.get_rect(center = (round(self.pos.x),round(self.pos.y)))

    def update(self,bullets,enemies,asteroids):
        self.check_dir(enemies,asteroids)
        super().update(bullets,enemies,asteroids)
    
    def render(self,surf):
        surf.blit(self.r_surf,self.rect)
    
    def debug_render(self,surf):
        super().debug_render(surf)
        pygame.draw.circle(surf,YELLOW,(self.pos),self.radar,1)

class Flame(Bullet):
    def __init__(self,x,y,owner):
        s = FLAME['size']
        size = clamped_gaussian(s*(1-2/3),s*(1+2/3),s)
        super().__init__(x,y,size,size,FLAME['img'],None,(0,FLAME['speed']),owner)
        self.w, self.h = size, size
        self.surf = pygame.Surface((self.w,self.h),pygame.SRCALPHA)
        r,g = clamped_gaussian(0,255,255), clamped_gaussian(0,255,64)
        self.surf.fill((r,g,0))
        #self.surf = self.surf.copy().convert_alpha()
        self.lifecost = FLAME['lifecost']
        
        self.add_timer('lifetime')
        a,b = FLAME['lifetime'][0], FLAME['lifetime'][1]
        self.lifetime = round(clamped_gaussian(a,b,(a+b)/2))
        self.timers['lifetime'].start(self.lifetime)
        self.friction = FLAME['speed_dec']
    
    def vanish(self):
        
        if self.timers['lifetime'].running:
            time_r = self.timers['lifetime'].time
            self.surf.set_alpha(remap(time_r,self.lifetime,0,255,0))
            self.vel.scale_to_length(remap(time_r,self.lifetime,0,abs(FLAME['speed']),0))
        else:
            self.lives = 0
    
    def update(self,bullets,enemies,asteroids):
        super().update(bullets,enemies,asteroids)
        self.update_timers()
        self.vanish()

class Asteroid(Sprite):
    def __init__(self,x,y,diff):

        #load params
        s1,s2 = ASTEROID['size'][0], ASTEROID['size'][1]
        v1,v2 = ASTEROID['speed'][0], ASTEROID['speed'][1]
        r1,r2 = ASTEROID['rot_speed'][0], ASTEROID['rot_speed'][1]
        l1,l2 = ASTEROID['lives'][0], ASTEROID['lives'][1]

        #generate randomic asteroid and remap speed, rot_speed and lives based on size
        size = round(clamped_gaussian(s1,s2,clamped_remap(diff,0,1,s1,s2)))
        vel = clamped_remap(size,s1,s2,v1,v2)
        rot_speed = clamped_remap(size,s1,s2,r1,r2)
        lives = round(clamped_remap(size,s1,s2,l1,l2))

        super().__init__(x,y,size,size,ASTEROID['img'],None,(0,vel))

        #attributes for rotation
        self.rot_speed = rot_speed
        self.angle = 0
        self.r_surf = self.surf

        self.lives = self.maxlives = lives
        self.lifecost = self.value = max(1,round(clamped_remap(size,s1,s2,1,PLAYER['max_lives'][-1])))
    
    def update_lifecost(self):
        self.lifecost = max(1,round(clamped_remap(self.lives,1,self.maxlives,1,PLAYER['max_lives'][-1])))
    
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
        img = pygame.transform.scale(ENEMY['img'].subsurface(crop_rect),(ENEMY['size'],ENEMY['size']))

        vel = 0, random.uniform(ENEMY['speed'][0],ENEMY['speed'][1])
        super().__init__(x,y,ENEMY['size'],ENEMY['size'],img,None,vel)
    
    def oo_borders(self,xlim,ylim):
        out =   (self.rect.top >= ylim) or \
                (self.rect.right <= 0) or \
                (self.rect.left >= xlim)
        
        return out

class Shield(Sprite):
    def __init__(self,owner):
        
        img = pygame.Surface((SHIELD['size'][owner.level-1],SHIELD['size'][owner.level-1]),pygame.SRCALPHA)
        pygame.draw.circle(img,SHIELD['color'],(round(SHIELD['size'][owner.level-1]/2),round(SHIELD['size'][owner.level-1]/2)),round(SHIELD['size'][owner.level-1]/2))
        img.convert_alpha()
        img.set_alpha(SHIELD['alpha'])

        super().__init__(owner.pos.x,owner.pos.y,SHIELD['size'][owner.level-1],SHIELD['size'][owner.level-1],img,None,(0,0))
        self.owner = owner
        self.maxlives = self.lives = self.lifecost = +math.inf
    
    def move(self):
        self.pos = self.owner.pos
        self.rect.center = round(self.pos.x), round(self.pos.y)
    
    def check_coll_w(self,others):
        for o in others:
            if not (o == self or (isinstance(o,Bullet) and o.owner == self.owner)):
                self.check_coll(o)
    
    def update(self,enemies,bullets,asteroids):
        self.move()
        self.check_coll_w(enemies)
        self.check_coll_w(bullets)
        self.check_coll_w(asteroids)

class Gun():
    def __init__(self,owner):
        self.owner = owner
        self.firerate_modifier = 1
        self.ammo = +math.inf
    
    def shoot(self,bullets,triple):
        for spot in self.owner.firespots:
            if triple:
                for angle in (0, PWUP['triple_angle'], -PWUP['triple_angle']):
                    self.shoot_single(bullets,angle,spot)
            else:
                self.shoot_single(bullets,0,spot)

        self.owner.timers['ready_to_shoot'].start(self.owner.firerate * self.firerate_modifier)
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo > 0:
            self.ammo -= 1

    def rotate_b(self,b,angle,bullets):
        b.vel.rotate_rad_ip(angle)
        rot_surf = pygame.transform.rotate(b.surf,360-math.degrees(angle))
        b.surf = rot_surf.copy()
        b.mask = pygame.mask.from_surface(b.surf)
        b.w, b.h = b.surf.get_size()
        b.rect = b.surf.get_rect(center = b.pos)
        bullets.append(b)

class BasicCannon(Gun):
    def __init__(self,owner):
        super().__init__(owner)
    
    def shoot_single(self,bullets,angle,spot):
        bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-BULLET['size']/2).rotate_rad(angle)
        b = BasicBullet(bpos.x,bpos.y,self.owner)
        super().rotate_b(b,angle,bullets)

class Cannon(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = CANNON['firerate']
        self.ammo = CANNON['ammo']
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-CANNONBALL['size']/2).rotate_rad(angle)
            b = CannonBall(bpos.x,bpos.y,self.owner)
            super().rotate_b(b,angle,bullets)

class LaserGun(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = LASERGUN['firerate']
        self.ammo = self.max_ammo = LASERGUN['max_ammo']
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,LASER['h']/2).rotate_rad(angle)
            b = Laser(bpos.x,bpos.y,self.owner)
            super().rotate_b(b,angle,bullets)
    
    def recharge(self):
        if self.ammo < LASERGUN['max_ammo']:   self.ammo += LASERGUN['charge_ratio']

class RocketLauncher(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = ROCKETLAUNCHER['firerate']
        self.ammo = ROCKETLAUNCHER['ammo']
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-ROCKET['size']/2).rotate_rad(angle)
            b = Rocket(bpos.x,bpos.y,self.owner)
            super().rotate_b(b,angle,bullets)

class FlameThrower(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = FLAMETHROWER['firerate']
        self.ammo = FLAMETHROWER['ammo']
        self.max_ammo = FLAMETHROWER['max_ammo']
        self.max_angle = FLAMETHROWER['fire_angle']
    
    def shoot_single(self,bullets,angle,spot): #TODO
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-FLAME['size']/2).rotate_rad(angle)
            b = Flame(bpos.x,bpos.y,self.owner)
            r_angle = clamped_gaussian(angle-self.max_angle,angle+self.max_angle,angle)
            super().rotate_b(b,r_angle,bullets)
    
    def rotate_b(self,b,angle,bullets):
        b.vel.rotate_rad_ip(angle)
        rot_surf = pygame.transform.rotate(b.surf,360-math.degrees(angle))
        b.surf = rot_surf.copy()
        b.mask = pygame.mask.from_surface(b.surf)
        b.w, b.h = b.surf.get_size()
        b.rect = b.surf.get_rect(center = b.pos)
        bullets.append(b)

class Player(Sprite):
    def __init__(self,x,y):

        #load images
        self.images = PLAYER['imgs']

        self.level = 1
        super().__init__(x,y,PLAYER['size'],PLAYER['size'],self.images[self.level-1],None,(0,0))
        self.load_stats()
        self.acc = pygame.math.Vector2(0,0)
        
        self.guns = {
            'basic' :           BasicCannon(self),
            'cannon' :          Cannon(self),
            'rocketlauncher' :  RocketLauncher(self),
            'lasergun' :        LaserGun(self),
            'flamethrower' :    FlameThrower(self),
        }

        self.gun_index = 0
        self.gun = self.guns['basic']
        
        self.shield = None
        self.add_timer('ready_to_shoot')
    
    def load_stats(self):
        self.maxlives = PLAYER['max_lives'][self.level-1]
        if self.level == 1:     self.lives = self.maxlives
        else:                   self.lives += PLAYER['max_lives'][self.level-1] - PLAYER['max_lives'][self.level-2]
        self.max_speed = PLAYER['max_speed'][self.level-1]
        self.acc_value = PLAYER['acc'][self.level-1]
        if not 'firerate' in self.timers:   self.firerate = PLAYER['firerate'][self.level-1]
        self.firespots = PLAYER['firespots'][self.level-1]
    
    def move(self,pressed_keys,mouse_pos,mouse_in_window):
          
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

        if 'mouse' in self.timers and mouse_in_window:
            self.pos = pygame.math.Vector2(mouse_pos)
            self.rect.center = round(self.pos.x), round(self.pos.y)
    
    def check_coll_w_pwups(self,pwups):
        for pw in pwups:
            off_x = pw.rect.x - self.rect.x
            off_y = pw.rect.y - self.rect.y
            if self.mask.overlap(pw.mask,(off_x,off_y)):
                pw.active(self)
                self.add_timer(pw.type)
                self.timers[pw.type].start(pw.time)
                pwups.remove(pw)
                del(pw)
    
    def check_ended_timers(self):
        for timer in self.timers.copy():
            if not self.timers[timer].running:
                #deactivate and remove it

                if timer == 'firerate':
                    self.firerate = PLAYER['firerate'][self.level-1]
                elif timer == 'shield':
                    self.shield = None

                if timer != 'ready_to_shoot':
                    self.remove_timer(timer)
    
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
    
    def change_gun(self):
        if self.gun_index < PLAYER['gun_types']-1:      self.gun_index += 1
        else:                                           self.gun_index = 0

        self.gun = self.guns[PLAYER['gun_indexes'][self.gun_index]]
    
    def fire_handler(self,pressed_keys,bullets):
        if pressed_keys[pygame.K_SPACE] and not self.timers['ready_to_shoot'].running:
            triple = 'triple' in self.timers
            self.gun.shoot(bullets,triple)

        self.guns['lasergun'].recharge()
            
    def check_exp(self):
        if self.exp >= PLAYER['exp_to_lvlup'][self.level-1]:
            self.exp -= PLAYER['exp_to_lvlup'][self.level-1]
            self.level_up()
        
    def render(self,surf):
        super().render(surf)
        if self.shield:     self.shield.render(surf)
    
    def update(self,pressed_keys,mouse_pos,mouse_in_window,enemies,bullets,asteroids,pwups,xlim,ylim):
        self.move(pressed_keys,mouse_pos,mouse_in_window)
        if self.shield:     self.shield.update(enemies,asteroids,bullets)
        self.fire_handler(pressed_keys,bullets)
        self.check_coll_w(enemies)
        self.check_coll_w(bullets)
        self.check_coll_w(asteroids)
        self.check_coll_w_borders(xlim,ylim)
        self.check_coll_w_pwups(pwups)
        self.update_lifecost()
        self.update_timers()
        self.check_ended_timers()
        self.check_exp()

class PowerUp(Sprite):
    def __init__(self,x,y,type='randomic'):
        if type == 'randomic':
            self.type = random.choice(['firerate','bomb_crate','fuel','rocketsbox','shield','mouse','triple','heart_full','exp'])
        else:
            self.type = type
        
        img = pygame.Surface((PWUP['size'],PWUP['size']),pygame.SRCALPHA)
        pygame.draw.rect(img,WHITE,(0,0,PWUP['size'],PWUP['size']),0,5)
            
        if self.type == 'firerate':
            tw,th = PWUP['font'].size('F')
            pygame.draw.rect(img,RED,(0,0,PWUP['size'],PWUP['size']),0,5)
            img.blit(PWUP['font'].render('F', True, BLACK),((PWUP['size']-tw)/2,(PWUP['size']-th)/2))
        elif self.type == 'exp':
            tw,th = PWUP['font'].size('++')
            pygame.draw.rect(img,DARKGREEN,(0,0,PWUP['size'],PWUP['size']),0,5)
            img.blit(PWUP['font'].render('++', WHITE, BLACK),((PWUP['size']-tw)/2,(PWUP['size']-th)/2))
        else:
            f_img = pygame.transform.scale(pygame.image.load(PWUP['filename_p'] + str(self.type) + '.png'),(PWUP['size'],PWUP['size']))
            img.blit(f_img,(0,0))
            pygame.draw.rect(img,WHITE,(0,0,PWUP['size'],PWUP['size']),2,5)

        super().__init__(x,y,PWUP['size'],PWUP['size'],img,None,(0,PWUP['speed']))

        self.time = PWUP['standard_time']

    def active(self,target):
        if self.type == 'firerate' and 'firerate' not in target.timers:
            target.firerate /= 3

        elif self.type == 'bomb_crate':
           target.guns['cannon'].ammo += PWUP['bomb_amt']
        elif self.type == 'fuel':
           target.guns['flamethrower'].ammo += PWUP['fuel_amt']
           target.guns['flamethrower'].ammo = min(target.guns['flamethrower'].ammo, target.guns['flamethrower'].max_ammo)
        elif self.type == 'rocketsbox':
           target.guns['rocketlauncher'].ammo += PWUP['rockets_amt']

        elif self.type == 'shield':
            target.shield = Shield(target)
        elif self.type == 'heart_full':
            if target.lives < target.maxlives:  target.lives += 1
        elif self.type == 'exp':
            target.exp += PWUP['exp_value']

        if self.type in ('firerate','shield','mouse','triple'):
            target.add_timer(self.type)
            target.timers[self.type].start(self.time)
    
    def update(self):
        self.move()
    
    def oo_borders(self,xlim,ylim):
        return self.rect.top >= ylim

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
    pwups = []
    player = Player(SCREENW/2,PLAYER['starting_y'])
    gameloop = True

    enemy_timer_rst = asteroid_timer_rst = pwup_timer_rst = pygame.time.get_ticks()
    diff = clamped_remap(player.points,0,PLAYER['max_points'],0,1)
    inv_diff = 1-diff

    t1, t2 = ENEMY['spawn_time'][0], ENEMY['spawn_time'][1]
    enemy_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)
    t1, t2 = ASTEROID['spawn_time'][0], ASTEROID['spawn_time'][1]
    asteroid_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)
    t1, t2 = PWUP['spawn_time'][0], PWUP['spawn_time'][1]
    pwup_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

    while gameloop:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                gameloop = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                player.change_gun()

        # <--- gameloop --->

        time = pygame.time.get_ticks()
        pressed_keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_window = pygame.mouse.get_focused()    

        if player.lives > 0:
            
            diff = clamped_remap(player.points,0,PLAYER['max_points'],0,1)
            inv_diff = 1-diff

            if time - enemy_timer_rst >= enemy_timer:
                enemy_timer_rst = time
                t1, t2 = ENEMY['spawn_time'][0], ENEMY['spawn_time'][1]
                enemy_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

                x, y = random.uniform(ENEMY['size']/2,SCREENW-ENEMY['size']/2), -ENEMY['size']
                enemies.append(Enemy(x,y))

            if time - asteroid_timer_rst >= asteroid_timer:
                asteroid_timer_rst = time
                t1, t2 = ASTEROID['spawn_time'][0], ASTEROID['spawn_time'][1]
                asteroid_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

                x, y = random.uniform(ASTEROID['size'][1]/2,SCREENW-ASTEROID['size'][1]/2), -ASTEROID['size'][1]
                asteroids.append(Asteroid(x,y,diff))
            
            if time - pwup_timer_rst >= pwup_timer:
                pwup_timer_rst = time
                t1, t2 = PWUP['spawn_time'][0], PWUP['spawn_time'][1]
                pwup_timer = clamped_gaussian(t1,t2,inv_diff*(t2-t1)+t1)

                x, y = random.uniform(PWUP['size']/2,SCREENW-PWUP['size']/2), -PWUP['size']
                pwups.append(PowerUp(x,y))

            update_all(pressed_keys,mouse_pos,mouse_in_window,player,bg,enemies,bullets,asteroids,pwups,SCREENW,SCREENH)
            kill_sprites_handler([enemies,asteroids,bullets,pwups],SCREENW,SCREENH)

            render_all(screen,player,[[bg],bullets,asteroids,enemies,pwups])

            #debug
            """ for a in asteroids:
                screen.blit(dfont.render('w:'+str(a.w)[:5],True,WHITE),(a.pos))
                screen.blit(dfont.render('vel:'+str(a.vel)[:5],True,WHITE),(a.pos)+(0,10))
                screen.blit(dfont.render('rot:'+str(a.rot_speed)[:5],True,WHITE),(a.pos)+(0,20))
                screen.blit(dfont.render('angle:'+str(a.angle)[:5],True,WHITE),(a.pos)+(0,30))
                screen.blit(dfont.render('l:'+str(a.lives),True,WHITE),(a.pos)+(0,40))
                screen.blit(dfont.render('val:'+str(a.lifecost),True,WHITE),(a.pos)+(0,50))
            
            screen.blit(dfont.render('enemy:'+str(enemy_timer)[:5]+'->'+str(enemy_timer-time+enemy_timer_rst)[:5],True,WHITE),(10,10))
            screen.blit(dfont.render('asteroid:'+str(asteroid_timer)[:5]+'->'+str(asteroid_timer-time+asteroid_timer_rst)[:5],True,WHITE),(10,20))
            screen.blit(dfont.render('pwup:'+str(pwup_timer)[:5]+'->'+str(pwup_timer-time+pwup_timer_rst)[:5],True,WHITE),(10,30))
            screen.blit(dfont.render('diff:'+str(diff)[:5],True,WHITE),(10,40))
            screen.blit(dfont.render('lives:'+str(player.lives),True,WHITE),(10,50))
            screen.blit(dfont.render('timers:'+str(player.timers.keys()),True,WHITE),(10,60))
            screen.blit(dfont.render(str(clock.get_fps())[:5]+' FPS',True,WHITE),(10,70))
            screen.blit(dfont.render('firerate: '+str(player.firerate),True,WHITE),(10,80))
            screen.blit(dfont.render('spots: '+str(player.firespots),True,WHITE),(10,90))
        
            for b in bullets:
                pygame.draw.circle(screen,WHITE,b.pos,10,1) """
        
        pygame.display.flip()
        clock.tick(FPS)