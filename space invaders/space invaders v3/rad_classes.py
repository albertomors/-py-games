from parameters import *
from methods import *

# <-- timer -->

class Timer():
    def __init__(self):
        self.maxtime = self.time = 0
        self.running = False

    def start(self,time):
        self.maxtime = self.time = time
        self.running = True
    
    def update(self):
        if self.running:
            if self.time > 0:   self.time -= 1
            else:               self.running = False

# <-- bg -->

class Background():
    def __init__(self):
        self.y = -SCREENH
        self.surf = pygame.Surface((SCREENW, 2*SCREENH))
        self.surf_t = pygame.Surface((SCREENW,SCREENH))
        self.surf_b = self.surf_t.copy()
        self.color = BG['color']

        self.rect = self.surf.get_rect()

        self.generate_stars(self.surf_t)
        self.generate_stars(self.surf_b)
    
    def generate_stars(self,half_surf):
        half_surf.fill(self.color)
        w,h = half_surf.get_size()
        
        stars_num = random.randint(BG['stars_num'][0],BG['stars_num'][1])
        for _ in range(stars_num):
            size = random.randint(BG['stars_size'][0],BG['stars_size'][1])
            x,y = random.uniform(size/2,w-size/2), random.uniform(size/2,h-size/2)
            c = random.randint(max(self.color),255)

            #draw a monochromatic star
            pygame.draw.rect(half_surf,(c,c,c),(x,y,size,size))
    
    def update(self):
        self.y += BG['speed']

        if self.rect.top >= 0:
            self.change_color()
            # copy top on bottom, refill the top with new stars, and reset position
            self.surf_b = self.surf_t.copy()
            self.generate_stars(self.surf_t)
            self.y = 0
        
        self.rect.centery = self.y
    
    def change_color(self):
        i = random.randint(0,2)
        dc = random.randint(-2,+2)
        self.color += numpy.array((0==i,1==i,2==i))*dc
        self.color = numpy.clip(self.color,0,255)
    
    def render(self,surf):
        self.surf.blit(self.surf_t,(0,0))
        self.surf.blit(self.surf_b,(0,SCREENH))
        surf.blit(self.surf,self.rect)

# <-- sprite -->

class Sprite():
    def __init__(self,x,y,w,h,vel,img,c):
        self.pos = pygame.math.Vector2(x,y)
        self.vel = pygame.math.Vector2(vel)
        self.w, self.h = w,h

        if not img:
            self.surf = pygame.Surface((w,h),pygame.SRCALPHA)
            self.surf.fill(c)
        else:
            self.load_sprite(img)
        
        self.d_surf = self.surf.copy()
        self.rect = self.d_surf.get_rect(center = self.pos)

        self.maxlives = self.lives = self.lifecost = self.value = 1
        self.killer = None

        self.timers = {}

        #rotating attr
        self.rotating = False
        self.angle = 0 #degrees
        self.img_angle_off = 0
        self.r_speed = 0
    
    def load_sprite(self,img):
        self.surf = img
        self.d_surf = self.surf.copy()
        self.rect = self.d_surf.get_rect(center = self.pos)
        self.w, self.h = self.rect.size
        self.mask = pygame.mask.from_surface(self.d_surf)
    
    def move(self):
        self.pos += self.vel
        self.rect.center = self.pos
    
    def update_angle(self):
        self.angle = (self.angle+self.r_speed)%360
        #if r_speed set to 0 this doesn't change nothing

    def rotate(self):
        self.d_surf = pygame.transform.rotate(self.surf,360-(self.angle-self.img_angle_off))
        self.rect = self.d_surf.get_rect(center = self.pos)
        self.w,self.h = self.rect.size
        self.mask = pygame.mask.from_surface(self.d_surf)

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
        if self.rotating:
            self.update_angle()
            self.rotate()
        self.move()
        self.check_coll_w(bullets)

    def update_lifecost(self):
        self.lifecost = self.lives
    
    def alive(self):
        return self.lives > 0
    
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
        surf.blit(self.d_surf,self.rect)

# <-- bullet -->

class Bullet(Sprite):
    def __init__(self,x,y,w,h,vel,img,c,owner):
        super().__init__(x,y,w,h,vel,img,c)
        self.owner = owner

        #rotating attr - all pointing up
        self.img_angle_off = self.angle = 90
    
    def oo_borders(self,xlim,ylim):
        out =   (self.rect.bottom <= 0) or \
                (self.rect.top >= ylim) or \
                (self.rect.right <= 0) or \
                (self.rect.left >= xlim)
        return out

    def update(self,bullets,targets):
        super().update(bullets)

    def update_lifecost(self):
        pass