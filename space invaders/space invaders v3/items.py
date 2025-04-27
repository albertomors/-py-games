from rad_classes import *

# <-- bullets -->

class BasicBullet(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,BULLET['w'],BULLET['h'],(0,BULLET['speed']),None,BULLET['color'],owner)

class Bomb(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,BOMB['size'],BOMB['size'],(0,BOMB['speed']),None,BOMB['color'],owner)
        self.lifecost = BOMB['lifecost']

        #attributes for rotation
        self.rotating = True
        self.r_speed = BOMB['r_speed']

class Laser(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,LASER['w'],LASER['h'],(0,LASER['speed']),None,LASER['color'],owner)
        
        self.lives = +math.inf
        self.lifecost = LASER['lifecost']

class Rocket(Bullet):
    def __init__(self,x,y,owner):
        super().__init__(x,y,ROCKET['w'],ROCKET['h'],(0,ROCKET['speed']),ROCKET['img'],None,owner)

        self.lifecost = ROCKET['lifecost']
        self.vision = ROCKET['vision']

        #attributes for rotation
        self.rotating = True
        self.r_speed = 0
    
    def find_target(self,targets):
        best_dir = pygame.math.Vector2(0,+math.inf)
        for list in targets:
            for t in list:
                dir = (self.pos - t.pos)
                if dir.length() <= self.vision + min(t.w,t.h)/2:
                    if dir.length() < best_dir.length():
                        best_dir = dir
        
        if best_dir.length() < + math.inf:
            #target found
            self.angle = math.degrees(math.atan2(best_dir.y,best_dir.x))
            self.vel = pygame.math.Vector2(ROCKET['speed'],0).rotate(self.angle)

    def update(self,bullets,targets):
        self.find_target(targets)
        super().update(bullets,targets)

class Flame(Bullet):
    def __init__(self,x,y,owner):
        
        #load params
        s1,s2 = FLAME['size'][0], FLAME['size'][1]
        v1,v2 = FLAME['speed'][0], FLAME['speed'][1]
        l1,l2 = FLAME['lifetime'][0], FLAME['lifetime'][1]

        #generate random attr
        size = clamped_gaussian(s1,s2,(s1+s2)/2)
        vel = clamped_gaussian(v1,v2,(v1+v2)/2)
        g = clamped_gaussian(0,255,80)
        color = (255,g,0)

        super().__init__(x,y,size,size,(0,vel),None,color,owner)
       
        self.lifecost = FLAME['lifecost']
        self.friction = FLAME['speed_dec']
        self.max_vel = abs(vel) #for vanish function
    
        self.rotating = True
        self.r_speed = BOMB['r_speed']
        
        self.add_timer('lifetime')
        self.lifetime = round(clamped_gaussian(l1,l2,(l1+l2)/2)) #for vanish function
        self.timers['lifetime'].start(self.lifetime)
        
    def vanish(self):
        if self.timers['lifetime'].running:
            
            time_r = self.timers['lifetime'].time
            alpha = clamped_remap(time_r,self.lifetime,0,255,100)
            speed = clamped_remap(time_r,self.lifetime,0,self.max_vel,0)

            self.surf.set_alpha(alpha)
            self.vel.scale_to_length(speed)
        else:
            self.lives = 0
    
    def update(self,bullets,targets):
        super().update(bullets,targets)
        self.update_timers()
        self.vanish()

# <-- guns -->

class Gun():
    def __init__(self,owner):
        self.owner = owner
        self.firerate_modifier = 1
        self.ammo = +math.inf
    
    def shoot(self,bullets,triple,dir):
        for spot in self.owner.firespots:
            if triple:
                for angle in (dir, dir+PWUP['triple_angle'], dir-PWUP['triple_angle']):
                    self.shoot_single(bullets,angle,spot)
            else:
                self.shoot_single(bullets,dir,spot)

        self.owner.timers['ready_to_shoot'].start(self.owner.firerate * self.firerate_modifier)

    def rotate_b(self,b,d_angle,bullets):
        b.vel.rotate_ip(d_angle)
        b.angle += d_angle
        b.rotate()
        bullets.append(b)

class BasicCannon(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.max_ammo = self.ammo = +math.inf
    
    def shoot_single(self,bullets,angle,spot):
        bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-BULLET['h']/2).rotate(angle)
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
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-BOMB['size']/2).rotate(angle)
            b = Bomb(bpos.x,bpos.y,self.owner)
            super().rotate_b(b,angle,bullets)

class LaserGun(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = LASERGUN['firerate']
        self.ammo = self.max_ammo = LASERGUN['max_ammo']
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-LASER['h']/2).rotate(angle)
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
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-ROCKET['h']/2).rotate(angle)
            b = Rocket(bpos.x,bpos.y,self.owner)
            super().rotate_b(b,angle,bullets)

class FlameThrower(Gun):
    def __init__(self,owner):
        super().__init__(owner)
        self.firerate_modifier = FLAMETHROWER['firerate']
        
        self.max_ammo = FLAMETHROWER['max_ammo']
        self.ammo = self.max_ammo
        self.max_angle = FLAMETHROWER['fire_angle']
    
    def shoot_single(self,bullets,angle,spot):
        if self.ammo >= 1:
            self.ammo -= 1
            bpos = self.owner.pos - (self.owner.w/2,self.owner.h/2) + spot + pygame.math.Vector2(0,-FLAME['size'][1]/2).rotate(angle)
            b = Flame(bpos.x,bpos.y,self.owner)
            rand_angle = clamped_gaussian(angle-self.max_angle,angle+self.max_angle,angle)
            super().rotate_b(b,rand_angle,bullets)

class Shield(Sprite):
    def __init__(self,owner):
        
        img = pygame.Surface((SHIELD['size'][owner.level-1],SHIELD['size'][owner.level-1]),pygame.SRCALPHA)
        pygame.draw.circle(img,SHIELD['color'],(round(SHIELD['size'][owner.level-1]/2),round(SHIELD['size'][owner.level-1]/2)),round(SHIELD['size'][owner.level-1]/2))
        img.convert_alpha()
        img.set_alpha(SHIELD['alpha'])

        super().__init__(owner.pos.x,owner.pos.y,SHIELD['size'][owner.level-1],SHIELD['size'][owner.level-1],(0,0),img,None)
        
        self.owner = owner
        self.maxlives = self.lives = self.lifecost = +math.inf
    
    def move(self):
        self.pos = self.owner.pos
        self.rect.center = self.pos
    
    def check_coll_w(self,others):
        for o in others:
            if not (isinstance(o,Bullet) and o.owner == self.owner):
                self.check_coll(o)
    
    def update(self,enemies,asteroids,bullets):
        self.move()
        self.check_coll_w(enemies)
        self.check_coll_w(asteroids)
        self.check_coll_w(bullets)

# <-- powerup -->

class PowerUp(Sprite):
    def __init__(self,x,y,type='randomic'):
        if type == 'randomic':
            self.type = random.choice(['firerate','bombs','oil','rockets','shield','mouse','triple','heart_f','exp'])
        else:
            self.type = type
        
        img = pygame.Surface((PWUP['size'],PWUP['size']),pygame.SRCALPHA)
            
        if self.type == 'firerate':
            tw,th = PWUP['font'].size('F')
            pygame.draw.rect(img,RED,(0,0,PWUP['size'],PWUP['size']),0,5)
            img.blit(PWUP['font'].render('F', True, BLACK),((PWUP['size']-tw)/2,(PWUP['size']-th)/2))
        elif self.type == 'exp':
            tw,th = PWUP['font'].size('+')
            pygame.draw.rect(img,DARKGREEN,(0,0,PWUP['size'],PWUP['size']),0,5)
            img.blit(PWUP['font'].render('+', WHITE, BLACK),((PWUP['size']-tw)/2,(PWUP['size']-th)/2))
        else:
            f_img = pygame.transform.scale(pygame.image.load(PWUP['p_filename'] + str(self.type) + '.png'),(PWUP['size'],PWUP['size']))
            img.blit(f_img,(0,0))

        super().__init__(x,y,PWUP['size'],PWUP['size'],(0,PWUP['speed']),img,None)
        self.time = PWUP['standard_time']

    def active(self,target):
        if self.type == 'firerate' and 'firerate' not in target.timers:
            target.firerate /= 3

        elif self.type == 'bombs':
           target.guns['cannon'].ammo += PWUP['bomb_amt']
        elif self.type == 'oil':
           target.guns['flamethrower'].ammo += PWUP['oil_amt']
           target.guns['flamethrower'].ammo = min(target.guns['flamethrower'].ammo, target.guns['flamethrower'].max_ammo)
        elif self.type == 'rockets':
           target.guns['rocketlauncher'].ammo += PWUP['rocket_amt']

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