# <--- space invaders - the game.py --->
#
# Author: Alberto Morselli
# Date: 22/03 -- 07/04/2023
 
import sys
from renderer import *

class Level():
    def __init__(self,level_no):

        self.level_no = level_no
        self.diff = self.inv_diff = None

        self.running = False
        self.gamestate = None
        self.renderer = Renderer(self)

        self.timers = {}
    
    def add_timer(self,name):
        timer = Timer()
        self.timers[name] = timer
    
    def remove_timer(self,name):
        if self.timers[name]:
            del self.timers[name]
    
    def update_timers(self):
        for t in self.timers:
            self.timers[t].update()
        
    def start(self,saveobj,time):
        self.running = True
        if self.level_no == 1:
            self.gamestate = 'tutorial'
        else:
            self.gamestate = 'intro'
            self.renderer.timers['intro'].start(2*FPS)

        #create all
        self.bg = saveobj['bg'] if 'bg' in saveobj else Background()
        self.player = saveobj['player'] if 'player' in saveobj else Player(SCREENW/2,LEVEL['intro_y'])
        self.player.rect.center = self.player.pos = pygame.math.Vector2(SCREENW/2,LEVEL['intro_y'])

        self.enemies = []
        self.asteroids = []
        self.bullets = []
        self.pwups = []

        #reset timers
        self.enemy_timer_rst = self.asteroid_timer_rst = self.pwup_timer_rst = time
        self.enemy_timer = self.asteroid_timer = self.pwup_timer = 0
        
    def update_diff(self):
        self.diff = clamped_remap(self.player.points,0,PLAYER['max_points'],0,1)
        self.inv_diff = 1-self.diff

    def check_timers(self,time):

        if time - self.enemy_timer_rst >= self.enemy_timer:
            self.enemy_timer_rst = time
            t1, t2 = ENEMY['spawn_time'][0], ENEMY['spawn_time'][1]
            self.enemy_timer = clamped_gaussian(t1,t2,self.inv_diff*(t2-t1)+t1)

            x, y = random.uniform(ENEMY['size']/2,SCREENW-ENEMY['size']/2), -ENEMY['size']
            self.enemies.append(Enemy(x,y))

        if time - self.asteroid_timer_rst >= self.asteroid_timer:
            self.asteroid_timer_rst = time
            t1, t2 = ASTEROID['spawn_time'][0], ASTEROID['spawn_time'][1]
            self.asteroid_timer = clamped_gaussian(t1,t2,self.inv_diff*(t2-t1)+t1)

            x, y = random.uniform(ASTEROID['size'][1]/2,SCREENW-ASTEROID['size'][1]/2), -ASTEROID['size'][1]
            self.asteroids.append(Asteroid(x,y,self.diff))
        
        if time - self.pwup_timer_rst >= self.pwup_timer:
            self.pwup_timer_rst = time
            t1, t2 = PWUP['spawn_time'][0], PWUP['spawn_time'][1]
            self.pwup_timer = clamped_gaussian(t1,t2,self.inv_diff*(t2-t1)+t1)

            x, y = random.uniform(PWUP['size']/2,SCREENW-PWUP['size']/2), -PWUP['size']
            self.pwups.append(PowerUp(x,y))
    
    def check_gamestate(self,saveobj):
        if self.gamestate == 'intro':
            if self.player.pos.y <= LEVEL['gameloop_y']:
                self.gamestate = 'gameloop'

        elif self.gamestate == 'gameloop' and self.player.alive():
            if self.player.points >= LEVEL['points_to_pass'][self.level_no-1]:
                self.gamestate = 'outro'
                self.renderer.timers['outro'].start(FPS)
        
        elif self.gamestate == 'outro' and self.player.rect.bottom <= 0:
            if self.level_no < LEVEL['level_nums']:
                self.savestate(saveobj)
                self.renderer.timers['intro'].start(FPS)
                self.running = False
            else:
                self.gamestate = 'win'
                
    def savestate(self,saveobj):
        saveobj['player'] = self.player
        saveobj['bg'] = self.bg
        
    def gameloop(self,time,pressed_keys,mouse_pos,mouse_in_window,mouse_keys,saveobj):

        if self.gamestate == 'tutorial':
            self.bg.update()

        elif self.gamestate == 'intro':
            self.bg.update()
            self.player.intro()
            self.check_gamestate(saveobj)

        elif self.gamestate == 'gameloop':
            if self.player.lives > 0:
                self.update_diff()
                self.check_timers(time)
                self.update_all(pressed_keys,mouse_pos,mouse_in_window,mouse_keys)
                self.kill_dead_sprites()
                self.kill_oo_sprites(SCREENW,SCREENH)
                self.check_gamestate(saveobj)
        
        elif self.gamestate == 'outro':
            self.bg.update()
            self.player.outro()
            for b in self.bullets:   b.update(self.bullets,[self.enemies,self.asteroids])
            self.check_gamestate(saveobj)
        
        self.update_timers()

    def update_all(self,pressed_keys,mouse_pos,mouse_in_window,mouse_keys):
        
        lives_r_before = self.player.lives/self.player.maxlives

        self.bg.update()
        for e in self.enemies:   e.update(self.bullets)
        for a in self.asteroids: a.update(self.bullets)
        for b in self.bullets:   b.update(self.bullets,[self.enemies,self.asteroids])
        for p in self.pwups:     p.update()
        self.player.update(pressed_keys,mouse_pos,mouse_in_window,mouse_keys,self.enemies,self.asteroids,self.bullets,self.pwups,SCREENW,SCREENH)
        
        lives_r_after = self.player.lives/self.player.maxlives
        if lives_r_after < lives_r_before:
            self.renderer.hit_screen()
            self.renderer.screen_shake()

    def kill_dead_sprites(self):
        for list in [self.enemies,self.asteroids,self.bullets]:
            for sprite in list:
                if sprite.lives <= 0:
                    if isinstance(sprite.killer,Player):
                        sprite.killer.exp += sprite.value
                        sprite.killer.points += sprite.value
                    list.remove(sprite)
                    del(sprite)

    def kill_oo_sprites(self,xlim,ylim):
        for list in [self.enemies,self.asteroids,self.bullets,self.pwups]:
            for sprite in list:
                if sprite.oo_borders(xlim,ylim):
                    list.remove(sprite)
                    del(sprite)
                
    def render(self,surf):
        self.renderer.render(surf)
 
# <--- initialize everything --->

pygame.init()
screen = pygame.display.set_mode((SCREENW,SCREENH))
pygame.display.set_caption('Space Invaders!')
pygame.display.set_icon(pygame.image.load(RES_FOLDER+'ss1.png'))
clock = pygame.time.Clock()
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
time = pygame.time.get_ticks()

level_no = 0
saveobj = {}

while True:

    level_no += 1
    level = Level(level_no)
    level.start(saveobj,time)
    
    while level.running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                level.running = False
                pygame.quit()
                sys.exit()
            
            if level_no == 1 and level.gamestate == 'tutorial' and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                level.gamestate = 'intro'
                level.renderer.timers['intro'].start(2*FPS)
                
            if (not level.player.alive() or level.gamestate == 'win') and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                level_no = 0
                saveobj = {} #trash saved player
                level.running = False

            if level.player.alive() and level.gamestate == 'gameloop' and event.type == pygame.MOUSEWHEEL:
                level.player.change_gun(-event.y)

        time = pygame.time.get_ticks()
        pressed_keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_keys = pygame.mouse.get_pressed()
        mouse_in_window = pygame.mouse.get_focused()    

        level.gameloop(time,pressed_keys,mouse_pos,mouse_in_window,mouse_keys,saveobj)
        level.render(screen)

        pygame.display.flip()
        clock.tick(FPS)