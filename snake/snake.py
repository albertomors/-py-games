# <--- snake.py --->
#
# Author: ZeroKroen (Alberto Morselli)
# Date: 1 -- 7/03/23



import pygame
import sys,random



# <--- game params --->

SCREENW,SCREENH = 800,600
TILESIZE = 20
FPS = 120

MAX_APPLE_VAL = 5
MAX_WALLS_NUM = 20

MIN_TP_TIME = 3_000
MAX_TP_TIME = 10_000
MIN_MOVE_TIME = 32
MAX_MOVE_TIME = 128
MAX_DIFF = 128

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)

SNAKE_H_GREEN = (0,64,0)
SNAKE_T_GREEN = (0,128,0)
APPLE_REDS = []
for c in range(MAX_APPLE_VAL):
    red = (255-c*200/MAX_APPLE_VAL,0,0) #darker red = more valuable
    APPLE_REDS.append(red)
GOLD = (218,165,32)


# <--- methods --->

def remap(x,x1,x2,y1,y2):
    dx = x2-x1
    dy = y2-y1
    y = x*dy/dx+x1
    return int(y)

def inv_remap(x,x1,x2,y1,y2):
    return y2-remap(x,x1,x2,y1,y2)

def collide(obj1,obj2):
    if obj1.x == obj2.x and obj1.y == obj2.y:
        return True
    else:
        return False

def check_gen_pos(obj,busy_tiles):
    if obj == None or obj.x == None or obj.y == None:
        return False
    for t in busy_tiles:
        if collide(obj,t):
            return False
    
    return True

def gen_walls(walls,busy_tiles,xlim,ylim):
    wall = None
    while not check_gen_pos(wall,busy_tiles):
        x,y = random.randint(0,xlim-1), random.randint(0,ylim-1)
        wall = Wall(x,y)

    walls.append(wall)

def gen_warp(warps,busy_tiles,xlim,ylim):
    warp = Warp(None, None, None, None)
    while not ( check_gen_pos(warp.tp1,busy_tiles) and check_gen_pos(warp.tp2,busy_tiles) and not collide(warp.tp1,warp.tp2) ):
        x1,y1 = random.randint(0,xlim-1), random.randint(0,ylim-1)
        x2,y2 = random.randint(0,xlim-1), random.randint(0,ylim-1)
        warp = Warp(x1,y1,x2,y2)

    warps.append(warp)

def update_busy_tiles(busy_tiles,snake,walls,warps,apples):
    busy_tiles.clear()
    busy_tiles.append(snake.head)
    for b in snake.body:    busy_tiles.append(b)
    for w in walls:         busy_tiles.append(w)
    for w in warps:
        busy_tiles.append(w.tp1)
        busy_tiles.append(w.tp2)
    for a in apples:        busy_tiles.append(a)

def check_apples(apples,busy_tiles,xlim,ylim):
    if apples == []:
        apple = None
        while not check_gen_pos(apple,busy_tiles):
            x,y = random.randint(0,xlim-1), random.randint(0,ylim-1)
            apple = Apple(x,y)
    
        apples.append(apple)

def render_all(surf,snake,walls,warps,apples):
    if snake.alive:
        surf.fill(WHITE)
        for l in [walls,warps,apples]:
            for obj in l:
                obj.render(surf)
        snake.render(surf)

        font = pygame.font.SysFont('comicsans', 20)
        points_str = str(snake.len)
        points_txt = font.render(points_str, False, BLACK)
        textw, texth = font.size(points_str)
        surf.blit(points_txt, (SCREENW-textw-20, 20))

    else:
        font1 = pygame.font.SysFont('comicsans', 60)
        font2 = pygame.font.SysFont('comicsans', 20)
        gameover_str1 = 'hai perso  !'
        gameover_str2 = 'PREMI (R) PER GIOCARE DI NUOVO'
        gameover_txt1 = font1.render(gameover_str1, False, BLACK)
        gameover_txt2 = font2.render(gameover_str2, False, BLACK)
        t1w, t1h = font1.size(gameover_str1)
        t2w, t2h = font2.size(gameover_str2)
        surf.blit(gameover_txt1, ((SCREENW-t1w)/2,(SCREENH-t1h-t2h)/2))
        surf.blit(gameover_txt2, ((SCREENW-t2w)/2,(SCREENH-t1h-t2h)/2+t1h))



# <--- objects --->

class Tile():
    def __init__(self,x,y,color):
        self.x = x
        self.y = y
        self.color = color

        self.surf = pygame.Surface((TILESIZE,TILESIZE))
        self.surf.fill(self.color)
        
    def render(self,surf):
        surf.blit(self.surf,(self.x*TILESIZE,self.y*TILESIZE))



class Apple(Tile):
    def __init__(self,x,y):

        if random.random() < .05: # 5% chance to golden apple
            self.val = 25
            super().__init__(x,y,GOLD)

        else:
            self.val = random.randint(1,MAX_APPLE_VAL)
            super().__init__(x,y,APPLE_REDS[self.val-1])



class Wall(Tile):
    def __init__(self,x,y):
        super().__init__(x,y,WHITE)
        pygame.draw.rect(self.surf,BLACK,(0,0,TILESIZE,TILESIZE),1) #black border



class Warp():
    def __init__(self,x1,y1,x2,y2):
        red,green = random.randint(0,255), random.randint(0,255)
        self.color = (red,green,255)
        self.tp1 = Tile(x1,y1,self.color)
        self.tp2 = Tile(x2,y2,self.color)
    
    def render(self,screen):
        self.tp1.render(screen)
        self.tp2.render(screen)



class Head(Tile):
    def __init__(self,x,y):
        super().__init__(x,y,SNAKE_H_GREEN)
        self.color = SNAKE_T_GREEN #to inizialize the body's shade
        self.dir = self.old_dir = random.choice(['u','d','l','r'])

    def move(self):
        if   self.dir == 'u':    self.y -= 1
        elif self.dir == 'd':    self.y += 1
        elif self.dir == 'l':    self.x -= 1
        elif self.dir == 'r':    self.x += 1

        self.old_dir = self.dir #updates after moving
    
    def update_dir(self,dir):
        #you can't go down if moving up etc...
        if  (dir == 'u' and self.old_dir != 'd') or \
            (dir == 'd' and self.old_dir != 'u') or \
            (dir == 'l' and self.old_dir != 'r') or \
            (dir == 'r' and self.old_dir != 'l'):       self.dir = dir

class Body(Tile):
    def __init__(self,prec):
        self.prec = prec
        green = min(prec.color[1]+1,255)
        self.color = (0,green,0)
        
        super().__init__(prec.x,prec.y,self.color)
    
    def move(self):
        self.x = self.prec.x
        self.y = self.prec.y

class Snake():
    def __init__(self,x,y):
        self.head = Head(x,y)
        self.body = []
        self.len = 1
        self.alive = True
    
    def grow(self,amount):
        while amount > 0:
            # if empty then, if not...
            prec = self.head if self.len == 1 else self.body[self.len-2] # [0] if len = 2(head + 1 body)
            b = Body(prec)
            self.body.append(b)
            self.len += 1
            amount -= 1
    
    def move(self):
        if self.len > 1:
            for b in self.body[::-1]:
                b.move()
        self.head.move()
    
    def render(self,surf):
        self.head.render(surf)
        for b in self.body:
            b.render(surf)

    def check_borders(self,xlim,ylim):
        if self.head.x > xlim-1:
            self.head.x = 0
        elif self.head.x < 0:
            self.head.x = xlim-1

        if self.head.y > ylim-1:
            self.head.y = 0
        elif self.head.y < 0:
            self.head.y = ylim-1

    def teleport(self,x,y):
        self.head.x = x
        self.head.y = y

    def check_collisions(self):
        if self.len > 2:
            for b in self.body:
                if collide(self.head,b):
                    self.alive = False
    
    def check_walls(self,walls):
        for wall in walls:
            if collide(self.head,wall):
                self.alive = False

    def check_warps(self,warps):
        for warp in warps:
            if collide(self.head,warp.tp1):
                self.teleport(warp.tp2.x,warp.tp2.y)
                warps.remove(warp)
            elif collide(self.head,warp.tp2):
                self.teleport(warp.tp1.x,warp.tp1.y)
                warps.remove(warp)
    
    def check_apples(self,apples):
       for apple in apples:
            if collide(self.head,apple):
                self.grow(apple.val)
                apples.remove(apple)

# <--- initialize everything --->

pygame.init()
screen = pygame.display.set_mode((SCREENW,SCREENH))
pygame.display.set_caption('Snake!')
clock = pygame.time.Clock()

#derived params
xs = SCREENW/TILESIZE
ys = SCREENH/TILESIZE

while True:

    WALLS_NUM = random.randint(1,MAX_WALLS_NUM)

    #initial conditions
    x,y = random.randint(0,xs-1), random.randint(0,ys-1)
    snake = Snake(x,y)
    apples = []
    walls = []
    warps = []
    busy_tiles = []

    for i in range(WALLS_NUM):
        gen_walls(walls,busy_tiles,xs,ys)

    tp_TIMER = random.randint(MIN_TP_TIME,MAX_TP_TIME) #first call
    move_TIMER = MAX_MOVE_TIME #first call
    tp_rst = move_rst = pygame.time.get_ticks() #curr_timers reset
    
    gameloop = True

    while gameloop:

        for event in pygame.event.get():

            # <--- check keyboard pressed and events --->

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    snake.head.update_dir('u')
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    snake.head.update_dir('d')
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    snake.head.update_dir('l')
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    snake.head.update_dir('r')
                    
                #gameover
                if event.key == pygame.K_r:
                    gameloop = False

        # <--- gameloop --->

        curr_time = pygame.time.get_ticks()

        if snake.alive:

            if curr_time - move_rst >= move_TIMER:
                move_rst = curr_time
                curr_upper = inv_remap(snake.len,1,MAX_DIFF,MIN_MOVE_TIME,MAX_MOVE_TIME)
                move_TIMER = max(MIN_MOVE_TIME,curr_upper)

                snake.check_warps(warps)
                snake.move()
                snake.check_collisions()
                snake.check_walls(walls)
                snake.check_borders(xs,ys)
                snake.check_apples(apples)

            if curr_time - tp_rst >= tp_TIMER:
                tp_rst = curr_time
                curr_upper = inv_remap(snake.len,1,MAX_DIFF,MIN_TP_TIME,MAX_TP_TIME)
                tp_TIMER = random.randint(MIN_TP_TIME,max(MIN_TP_TIME,curr_upper))
                gen_warp(warps,busy_tiles,xs,ys)
            
            check_apples(apples,busy_tiles,xs,ys)
            update_busy_tiles(busy_tiles,snake,walls,warps,apples)

        render_all(screen,snake,walls,warps,apples)

        pygame.display.flip()
        clock.tick(FPS)