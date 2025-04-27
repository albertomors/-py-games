from items import *

# <--- enemies --->

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

        img = pygame.transform.scale(ASTEROID['img'],(size,size))
        super().__init__(x,y,size,size,(0,vel),img,None)

        #attributes for rotation
        self.rotating = True
        self.img_angle_off = 0
        self.r_speed = rot_speed

        self.lives = self.maxlives = lives
        self.lifecost = self.value = max(1,round(clamped_remap(size,s1,s2,1,PLAYER['max_lives'][-1])))
    
    def update_lifecost(self):
        self.lifecost = max(1,round(clamped_remap(self.lives,1,self.maxlives,1,PLAYER['max_lives'][-1])))
    
    def check_coll(self,obj):
        off_x = obj.rect.x - self.rect.x
        off_y = obj.rect.y - self.rect.y
        if self.mask.overlap(obj.mask,(off_x,off_y)):

            #immune to fire
            if not isinstance(obj,Flame):
                self.lives -= obj.lifecost

            obj.lives -= self.lifecost
        
        if self.lives <= 0:
            if isinstance(obj,Bullet):      self.killer = obj.owner
            else:                           self.killer = obj
        if obj.lives <= 0:
            if isinstance(self,Bullet):     obj.killer = self.owner
            else:                           obj.killer = self
    
    def oo_borders(self,xlim,ylim):
        return self.rect.top >= ylim

class Enemy(Sprite):
    def __init__(self,x,y):
        
        #crop random image from enemies's 'sprites.png'
        x_crop = random.randint(0,ENEMY['h_num']-1) * ENEMY['size']
        y_crop = random.randint(0,ENEMY['v_num']-1) * ENEMY['size']
        img = pygame.Surface((ENEMY['size'],ENEMY['size']),pygame.SRCALPHA)
        img.blit(ENEMY['img'],(0,0),(x_crop,y_crop,ENEMY['size'],ENEMY['size']))

        v1,v2 = ENEMY['speed'][0], ENEMY['speed'][1]
        vel = clamped_gaussian(v1,v2,(v1+v2)/2)

        super().__init__(x,y,ENEMY['size'],ENEMY['size'],(0,vel),img,None)
    
    def oo_borders(self,xlim,ylim):
        out =   (self.rect.top >= ylim) or \
                (self.rect.right <= 0) or \
                (self.rect.left >= xlim)
        
        return out

# <-- player -->

class Player(Sprite):
    def __init__(self,x,y):
        self.images = PLAYER['imgs']
        super().__init__(x,y,PLAYER['size'],PLAYER['size'],(0,0),self.images[0],None)
        
        self.level = 1
        self.load_stats()
        self.acc = pygame.math.Vector2(0,0)
        self.exp = self.points = 0
        
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
    
    def end_all_timers(self):
        for timer in self.timers.copy():
            self.timers[timer].time = 0
            self.update_timers()
    
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
    
    def change_gun(self,dir):
        if 0 <= self.gun_index <= PLAYER['gun_types']-1:    self.gun_index += dir
        if self.gun_index == -1:                            self.gun_index = PLAYER['gun_types']-1
        elif self.gun_index == PLAYER['gun_types']:         self.gun_index = 0
        
        self.gun = self.guns[PLAYER['gun_indexes'][self.gun_index]]
    
    def fire_handler(self,mouse_keys,bullets):
        if mouse_keys[0] and not self.timers['ready_to_shoot'].running:
            triple = 'triple' in self.timers
            self.gun.shoot(bullets,triple,0)

        self.guns['lasergun'].recharge()
            
    def check_exp(self):
        if self.exp >= PLAYER['exp_to_lvlup'][self.level-1]:
            self.exp -= PLAYER['exp_to_lvlup'][self.level-1]
            self.level_up()
        
    def render(self,surf):
        super().render(surf)
        if self.shield:     self.shield.render(surf)
    
    def update(self,pressed_keys,mouse_pos,mouse_in_window,mouse_keys,enemies,asteroids,bullets,pwups,xlim,ylim):
        self.move(pressed_keys,mouse_pos,mouse_in_window)
        if self.shield:     self.shield.update(enemies,asteroids,bullets)
        self.fire_handler(mouse_keys,bullets)
        self.check_coll_w(enemies)
        self.check_coll_w(asteroids)
        self.check_coll_w(bullets)
        self.check_coll_w_borders(xlim,ylim)
        self.check_coll_w_pwups(pwups)
        self.update_lifecost()
        self.update_timers()
        self.check_ended_timers()
        self.check_exp()
    
    def intro(self):

        self.acc.x = self.vel.x = 0
        
        if self.pos.y >= LEVEL['gameloop_y']:
            self.acc.y = -LEVEL['intro_acc']
        else:
            self.acc.y = 0
            self.vel.y *= PLAYER['friction']
        
        # max speed handler
        self.vel += self.acc
        if self.vel.length() >= self.max_speed:   self.vel.clamp_magnitude_ip(self.max_speed)

        super().move()
    
    def outro(self):
        self.end_all_timers()
        self.check_ended_timers()

        self.acc.x = self.vel.x = 0

        if self.rect.bottom >= 0:
            self.acc.y = -LEVEL['outro_acc']
        else:
            self.acc.y = 0
            self.vel.y = 0
        
        # max speed handler
        self.vel += self.acc
        if self.vel.length() >= self.max_speed:   self.vel.clamp_magnitude_ip(self.max_speed)

        super().move()