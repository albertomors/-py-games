import pygame
import sys
import random

# definitions ---------------------------------------------

SCREENW = 640
SCREENH = 480
SHAKE_AMT = 10
TILESIZE = 20
xlim = SCREENW // TILESIZE
ylim = SCREENH // TILESIZE
BODY_SIZE = TILESIZE - 4 # of the snake
BIGSIZE = round(TILESIZE * 1.5) # Big size for the hunter powerup
OFF = (TILESIZE - BODY_SIZE) // 2 # Offset between TILESIZE and BODYSIZE

RED = (255, 0, 0)
RATTLE_TAIL_COLOR = (255, 165, 0)  # Orange
warp_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color
wsize = TILESIZE // 4  # Initial size for warp rectangle
warping = False # if the snake/hunter is warping or not
wdir = 1 # warping animation direction

INITIAL_LINKS = 3
FPS = 10
VEN_PROB = 0.05/FPS # 10%
HUNTER_BIGDAMAGE_PROB = 0.1/FPS #10%
WALL_LIFE = 30*FPS # 30 seconds
WALL_POP_DELAY = 30 # ms
SNAKE_GROW_RATE = FPS * 1 # 1 block/sec
RATTLE_SNAKE_PROB = 0.1/FPS
TIMER_MAX = FPS * 10 # 10 seconds
HUNTER_DMG = WALL_LIFE * 1/4 #destroy it in 4 hits
WARP_PROB = 0.05/FPS

#---------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((SCREENW, SCREENH))
pygame.display.set_caption("What game? Snake! our snake")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# initial conditions --------------------------------------

N_links = INITIAL_LINKS
xs = [xlim // 2] * N_links
ys = [ylim // 2] * N_links
hx = 0
hy = 0

#----------------------------------------------------------

def change_season():
    global SEASON, SNEK_COLOR, BGCOLOR, HUNTER_COLOR, WALL_COLOR

    if SEASON == "winter":
        SNEK_COLOR = (230, 230, 230)  # White color for snake in winter
        BGCOLOR = (0, 191, 255)  # Deep sky blue background color for winter
        HUNTER_COLOR = (30, 30, 30)  # Dark gray color for hunter in winter
        WALL_COLOR = (173, 216, 230) # Light blue color for walls in winter
    elif SEASON == "spring":
        SNEK_COLOR = (0, 153, 0)  # Lawn green color for snake in spring
        BGCOLOR = (255, 228, 181)  # Moccasin background color for spring
        HUNTER_COLOR = (255, 20, 147)  # Deep pink color for hunter in spring
        WALL_COLOR = (25, 51, 0)  # Light yellow color for walls in spring
    elif SEASON == "autumn":
        SNEK_COLOR = (139, 69, 19)  # Saddle brown color for snake in autumn
        BGCOLOR = (255, 228 , 181)  # Moccasin background color for autumn
        HUNTER_COLOR = (255, 110, 0)  # Dark orange color for hunter in autumn
        WALL_COLOR = (153, 0 , 0)  # Dark red color for walls in autumn
    else: # summer
        SNEK_COLOR = (0, 0, 139)  # Dark blue color for snake in summer
        BGCOLOR = (255, 192, 203)  # Light pink background color for summer
        HUNTER_COLOR = (255, 255, 0)  # Yellow color for hunter in summer
        WALL_COLOR = (0, 0, 0)  # Black color for walls in summer

SEASONS = ["summer", "autumn", "winter", "spring", "win"]
SEASON = "summer"  # Set default season
change_season()

# items init ----------------------------------------------------------

venomous_timer = 0
venomous = False
counter = 0

bigdamage_timer = 0
dangerous = False
hsize = TILESIZE

rattle_tail = False
rattle_timer = 0

walls = []
wall_lifes = []

venomous_item = []
bigdamage_item = []
rattle_item = []
warp = []

screenx, screeny = 0, 0
rattle_direction = "ver"

# weather effects ---------------------------------------

rain_amt = 0
raining = False
rain_dir = 1
RAIN_MAX = 1600
SLIPPERY_PROB = 0.3
RAIN_PROB = 0.2/FPS

WHITE_PROB = 0.1/FPS
WHITE_DURATION = FPS*5
white_timer = 0
SNOW_MAX = 400
WHITE_MAX = 1000

#--------------------------------------------------------

def draw_game_objects():
    """Draw all game objects on the screen."""
    global rattle_direction, screenx, screeny, warp_color, wsize, wdir, rain_amt, raining, rain_dir, white_timer
    screen.fill(BGCOLOR)

    # Draw walls
    for i, wall in enumerate(walls):
        g = wall_lifes[i] / WALL_LIFE
        g = int(g * 255)
        wall_surface = pygame.Surface((BODY_SIZE, BODY_SIZE), pygame.SRCALPHA)
        wall_surface.fill(WALL_COLOR)
        wall_surface.set_alpha(g)  # Semi-transparent walls
        screen.blit(wall_surface, (wall[0] * TILESIZE + OFF, wall[1] * TILESIZE + OFF))

    # Draw items
    if venomous_item:
        pygame.draw.circle(screen, RED, (venomous_item[0] * TILESIZE + TILESIZE // 2, venomous_item[1] * TILESIZE + TILESIZE // 2), TILESIZE // 4)
    if bigdamage_item:
        pygame.draw.circle(screen, HUNTER_COLOR, (bigdamage_item[0] * TILESIZE + TILESIZE // 2, bigdamage_item[1] * TILESIZE + TILESIZE // 2), TILESIZE // 4)
    if rattle_item:
        pygame.draw.circle(screen, RATTLE_TAIL_COLOR, (rattle_item[0] * TILESIZE + TILESIZE // 2, rattle_item[1] * TILESIZE + TILESIZE // 2), TILESIZE // 4)

    #snake
    if warp and xs and xs[0] == warp[0] and ys and ys[0] == warp[1]:
        pass
    elif xs and ys:
        pygame.draw.rect(screen, SNEK_COLOR, (xs[0] * TILESIZE, ys[0] * TILESIZE, TILESIZE, TILESIZE))

    if xs and ys:
        for i in range(1, N_links-1):
            if (xs[i] == xs[i+1] and ys[i] == ys[i+1]) or (warp and xs[i] == warp[0] and ys[i] == warp[1]):
                pass
            else:
                pygame.draw.rect(screen, SNEK_COLOR, (xs[i] * TILESIZE + OFF, ys[i] * TILESIZE + OFF, BODY_SIZE, BODY_SIZE))
    
    if rattle_tail and xs and ys:
        randoff = round(random.choice([-1, 1]) * random.random() * TILESIZE // 5)
        i=0
        #find direction of the rattle tail
        if N_links >= 2:
            if xs[-1] == xs[-2] and ys[-1] == ys[-2]:
                pass
            elif xs[-1] == xs[-2]:
                rattle_direction = "ver"
            elif ys[-1] == ys[-2]:
                rattle_direction = "hor"
         
            if rattle_direction == "hor":
                pygame.draw.rect(screen, RATTLE_TAIL_COLOR, (xs[-1] * TILESIZE + OFF, ys[-1] * TILESIZE + OFF + (TILESIZE-4)//2 + randoff, BODY_SIZE, 4))
            else:
                pygame.draw.rect(screen, RATTLE_TAIL_COLOR, (xs[-1] * TILESIZE + OFF + (TILESIZE-4)//2 + randoff, ys[-1] * TILESIZE + OFF, 4, BODY_SIZE))
    elif xs and ys:
        pygame.draw.rect(screen, SNEK_COLOR, (xs[-1] * TILESIZE + OFF, ys[-1] * TILESIZE + OFF, BODY_SIZE, BODY_SIZE))

    # Draw hunter
    if warp and hx == warp[0] and hy == warp[1]:
        pass
    else:
        pygame.draw.rect(screen, HUNTER_COLOR, (hx * TILESIZE + (TILESIZE - hsize) // 2, hy * TILESIZE + (TILESIZE - hsize) // 2, hsize, hsize))

    if warp:
        wsize = wsize + wdir*2
        if wsize >= TILESIZE or wsize <= TILESIZE // 4:
            wdir *= -1  # Reverse direction when reaching size limits
        pygame.draw.rect(screen, warp_color, (warp[0] * TILESIZE + (TILESIZE-wsize) // 2, warp[1] * TILESIZE, wsize, TILESIZE))
        warp_color = [(c+random.randint(-30,30)) % 255 for c in warp_color]  # Random color for warp

    # Apply screen shake effect
    screen.blit(screen, (screenx, screeny))

    # hail if its winter
    if SEASON == "winter":
        
        # Create a snow surface with alpha
        snow_surface = pygame.Surface((SCREENW, SCREENH), pygame.SRCALPHA)
        for _ in range(SNOW_MAX):
            x = random.randint(0, SCREENW)
            y = random.randint(0, SCREENH)
            pygame.draw.circle(snow_surface, (255, 255, 255), (x, y), random.randint(1, 3))
        
        if white_timer <= 0:
            if random.random() < WHITE_PROB:
                white_timer = WHITE_DURATION
        
        if white_timer > 0:
            white_timer -= 1
            for _ in range(WHITE_MAX):
                x = random.randint(0, SCREENW)
                y = random.randint(0, SCREENH)
                pygame.draw.circle(snow_surface, (255, 255, 255), (x, y), random.randint(10, 30))
        
        # Add transparency to the snow surface before blitting
        snow_surface.set_alpha(235)
        screen.blit(snow_surface, (0, 0))
    
    # rain
    elif SEASON == "autumn":
        if not raining:
            raining = random.random() < RAIN_PROB
        
        if raining:
            rain_amt = rain_amt + rain_dir*10
            if rain_amt >= RAIN_MAX or rain_amt <= 0:
                rain_dir *= -1
            if rain_amt <= 0:
                raining = False

        if raining:
            for _ in range(rain_amt):
                x = random.randint(0, SCREENW)
                y = random.randint(0, SCREENH)
                c = random.randint(0,100)
                pygame.draw.line(screen, (0,c,255), (x, y), (x, y + random.randint(5, 15)), 1)
            
            black_surf = pygame.Surface((SCREENW, SCREENH))
            black_surf.fill((0, 0, 0))
            black_surf.set_alpha(int(rain_amt/1600 * 255))
            screen.blit(black_surf, (0, 0))

            # draw thunders as flashes
            if random.random() < 0.1:  # 1% chance for a thunder
                white_surface = pygame.Surface((SCREENW, SCREENH))
                white_surface.fill((255, 255, 255))  # White color for the flash
                white_surface.set_alpha(100)  # Semi-transparent white
                screen.blit(white_surface, (0, 0))

    pygame.display.flip()

# Main game loop ---------------------------------------------------

draw_game_objects()
season_text = font.render(f"{SEASON.capitalize()}", True, (0, 0, 0))
text_rect = season_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
screen.blit(season_text, text_rect)
pygame.display.flip()
pygame.time.delay(1000)  # Show the season text for 2 seconds

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #----------------------------------------------------------
    
    #generate a rand number to determine if the hunter is venomous
    if venomous_timer == 0:
        if venomous:
            venomous, SNEK_COLOR = False, SNEK_COLOR
            print("no more venomous")
        elif random.random() < VEN_PROB and not venomous_item:
            venomous_item = (random.randint(0, xlim), random.randint(0, ylim))
            while venomous_item in walls or venomous_item == (hx, hy) or venomous_item in [(x, y) for x, y in zip(xs, ys)]:
                venomous_item = (random.randint(0, xlim), random.randint(0, ylim))
    elif venomous_timer > 0:
        if venomous_timer < FPS * 3:
            g = venomous_timer / (FPS * 3)
            SNEK_COLOR = (int(g*255), 0, int((1-g)*139))
        else:
            SNEK_COLOR = (255, 0, 0)
        venomous_timer -= 1
    
    if bigdamage_timer == 0:
        if dangerous:
            dangerous, hsize = False, TILESIZE
            print("no more big damage")
        elif random.random() < HUNTER_BIGDAMAGE_PROB and not bigdamage_item:
            bigdamage_item = (random.randint(0, xlim), random.randint(0, ylim))
            while bigdamage_item in walls or bigdamage_item == (hx, hy) or bigdamage_item in [(x, y) for x, y in zip(xs, ys)]:
                bigdamage_item = (random.randint(0, xlim), random.randint(0, ylim))
    elif bigdamage_timer > 0:
        if bigdamage_timer < FPS * 3:
            hsize = int((bigdamage_timer / (FPS * 3)) * (BIGSIZE - TILESIZE) + TILESIZE)
        bigdamage_timer -= 1
    
    if rattle_timer == 0:
        if rattle_tail:
            rattle_tail = False
            print("no more rattle tail")
        elif random.random() < RATTLE_SNAKE_PROB and not rattle_item:
            rattle_item = (random.randint(0, xlim), random.randint(0, ylim))
            while rattle_item in walls or rattle_item == (hx, hy) or rattle_item in [(x, y) for x, y in zip(xs, ys)]:
                rattle_item = (random.randint(0, xlim), random.randint(0, ylim))
    elif rattle_timer > 0:
        rattle_timer -= 1

    if random.random() < WARP_PROB and not warp:
        warp = (random.randint(0, xlim), random.randint(0, ylim))
        while warp in walls or warp == (hx, hy) or warp in [(x, y) for x, y in zip(xs, ys)]:
            warp = (random.randint(0, xlim), random.randint(0, ylim))
    
    #--------------------------------------------------------

    check = True
    buttons = pygame.key.get_pressed()
    
    # Define direction vectors for each key
    directions = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0)
    }
    
    # Process movement for any pressed direction key
    for key, (dx, dy) in directions.items():
        if buttons[key]:
            # if not raining, otherwise slip randomly aside
            prob = rain_amt / RAIN_MAX * SLIPPERY_PROB
            if SEASON == "autumn" and raining and random.random() < prob:
                if random.choice([True, False]):
                    dx = random.choice([-1, 1])
                    dy = 0
                else:
                    dx = 0
                    dy = random.choice([-1, 1])
            new_x, new_y = xs[0] + dx, ys[0] + dy
        
            new_x = new_x % xlim
            new_y = new_y % ylim
            
            # Check collision with snake body or walls
            if any((new_x == xs[i] and new_y == ys[i]) for i in range(1, N_links)) or \
               any((new_x == w[0] and new_y == w[1]) for w in walls):
                check = False
            
            if check and not warping:
                # Update snake body positions
                for i in range(N_links - 1, 0, -1):
                    xs[i], ys[i] = xs[i-1], ys[i-1]
                xs[0], ys[0] = new_x, new_y
            break
    
    # Handle special action (create walls from snake body)
    if buttons[pygame.K_RSHIFT] and N_links > 2:
        for i in range(3, N_links):
            #add only 1 wall on the same cell
            if (xs[i], ys[i]) not in walls:
                walls.append((xs[i], ys[i]))
                wall_lifes.append(WALL_LIFE)
        N_links = 3
        xs = [xs[0], xs[1], xs[2]]
        ys = [ys[0], ys[1], ys[2]]

    #--------------------------------------------------------
    
    # Hunter movement with wall collision detection
    screenx, screeny = 0, 0
    checkhunter = True
    hunter_moves = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
    for key, (dx, dy) in hunter_moves.items():
        if buttons[getattr(pygame, f'K_{key}')]:
            prob = rain_amt / RAIN_MAX * SLIPPERY_PROB
            if SEASON == "autumn" and raining and random.random() < prob:
                if random.choice([True, False]):
                    dx = random.choice([-1, 1])
                    dy = 0
                else:
                    dx = 0
                    dy = random.choice([-1, 1])
            
            new_x = hx + dx
            new_y = hy + dy
            new_x = new_x % xlim
            new_y = new_y % ylim

            for i, w in enumerate(walls):
                if (new_x, new_y) == (w[0], w[1]):
                    checkhunter = False
                    wall_lifes[i] -= HUNTER_DMG
                    screenx, screeny = dx * SHAKE_AMT, dy * SHAKE_AMT
                    if dangerous:
                        connected_walls = []
                        explored = set([(w[0], w[1])])
                        to_explore = [((w[0], w[1]), 0)]  # (wall, distance)
                        
                        while to_explore:
                            (wx, wy), distance = to_explore.pop(0)
                            connected_walls.append(((wx, wy), distance))
                            
                            # Check all 4 adjacent positions
                            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                nx, ny = wx + dx, wy + dy
                                if (nx, ny) in walls and (nx, ny) not in explored:
                                    explored.add((nx, ny))
                                    to_explore.append(((nx, ny), distance + 1))
                        
                        # Sort walls by distance
                        connected_walls.sort(key=lambda x: x[1])
                        
                        # Remove all connected walls
                        for (wall_coords, _) in connected_walls:
                            if wall_coords in walls:
                                idx = walls.index(wall_coords)
                                walls.pop(idx)
                                wall_lifes.pop(idx)
                                pygame.time.delay(WALL_POP_DELAY)  # Delay for wall pop animation
                                # redrwaw the screen to show the wall being destroyed
                                # Draw the screen for the wall destruction animation
                                draw_game_objects()
                    break
            if checkhunter:
                hx += dx
                hy += dy
            break
    
    #--------------------------------------------------------
    
    # Wrap the snake head position
    for i in range(0,N_links):
        xs[i] = xs[i] % xlim
        ys[i] = ys[i] % ylim

    # Wrap hunter position
    hx = hx % xlim
    hy = hy % ylim
    
    #--------------------------------------------------------
    
    # Remove walls that have no life left
    walls = [w for w, life in zip(walls, wall_lifes) if life > 0]
    wall_lifes = [life - 1 for life in wall_lifes if life > 0]

    # check if snake eats the venomous item
    if venomous_item:
        if xs[0] == venomous_item[0] and ys[0] == venomous_item[1]:
            venomous = True
            venomous_timer = TIMER_MAX
            SNEK_COLOR = (255, 0, 0)
            venomous_item = []
            print("venomous!")

    # check if hunter eats the big damage item
    if bigdamage_item:
        if hx == bigdamage_item[0] and hy == bigdamage_item[1]:
            dangerous = True
            bigdamage_timer = TIMER_MAX
            hsize = BIGSIZE
            bigdamage_item = []
            print("big damage!")
    
    # check if snake eats the rattle item
    if rattle_item:
        if xs[0] == rattle_item[0] and ys[0] == rattle_item[1]:
            rattle_tail = True
            rattle_timer = TIMER_MAX
            rattle_item = []
            print("rattle tail!")

    # check if snake or hunter goes into warp
    if warp:
        changed = False

        if xs[0] == warp[0] and ys[0] == warp[1]:
            warping = True
            xs[0], ys[0] = warp[0], warp[1]

            for i in range(N_links - 1, 0, -1):
                xs[i], ys[i] = xs[i-1], ys[i-1]

            if xs[-1] == warp[0] and ys[-1] == warp[1]:
                print("snake warped!")
                warping = False
                changed = True

        if hx == warp[0] and hy == warp[1]:
            print("hunter warped!")
            changed = True
        
        if changed:
            warp = []
            walls = []
            wall_lifes = []
            venomous_item = []
            bigdamage_item = []
            rattle_item = []
            warping = False

            raining = False
            raining_amt = 0
            rain_dir = 1
            white_timer = 0

            #choose the next SEASON
            SEASON = SEASONS[(SEASONS.index(SEASON) + 1) % len(SEASONS)]

            if SEASON=="win":
                xs = []
                ys = []
                draw_game_objects()
                print("SNAKE WINS!")
                win_text = font.render("SNAKE WINS!", True, (0, 0, 0))
                text_rect = win_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
                screen.blit(win_text, text_rect)
                pygame.display.flip()
                pygame.time.delay(2000)  # Show the win text for 2 seconds
                running = False
                break

            change_season()
            draw_game_objects()
            season_text = font.render(f"{SEASON.capitalize()}", True, (0, 0, 0))
            text_rect = season_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
            screen.blit(season_text, text_rect)
            pygame.display.flip()
            pygame.time.delay(1000)

    #weather
    #if its winter make wind that moves laterally both player and snake
    if SEASON == "winter":
        wind = random.randint(-1,1)
        for i in range(N_links):
            xs[i] += wind
        hx += wind
        #move every item
        if venomous_item:
            venomous_item = (venomous_item[0] + wind, venomous_item[1])
        if bigdamage_item:
            bigdamage_item = (bigdamage_item[0] + wind, bigdamage_item[1])
        if rattle_item:
            rattle_item = (rattle_item[0] + wind, rattle_item[1])
        if warp:
            warp = (warp[0] + wind, warp[1])
        for i, wall in enumerate(walls):
            walls[i] = (wall[0] + wind, wall[1])

    #if its spring add climbing plants that grows from below as walls but avoid growing if they encounter snake or hunter
    elif SEASON == "spring":
        if random.random() < 0.4:  #90% chance to grow a wall
            #select the bottom border
            coords = [(x, ylim-1) for x in range(xlim)]
            #add to coord the cells above the existing walls
            for wall in walls:
                coords.append((wall[0], wall[1] - 1))
            #remove from coord all the cells already occupied by walls, snake or hunter
            coords = [c for c in coords if c not in walls and c not in [(x, y) for x, y in zip(xs, ys)] and c != (hx, hy)]
            if coords:
                new_wall = random.choice(coords)
                walls.append(new_wall)
                wall_lifes.append(WALL_LIFE)

    #--------------------------------------------------------

    draw_game_objects()

    # Check for collisions
    if (hx, hy) in list(zip(xs, ys)):
        if venomous:
            print("SNAKE WINS!")
            # print it on pygame screen
            win_text = font.render("SNAKE WINS!", True, (0, 0, 0))
            text_rect = win_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
            screen.blit(win_text, text_rect)
            pygame.display.flip()
            pygame.time.delay(2000)  # Show the win text for 2 seconds
        elif not venomous:
            if rattle_tail and hx == xs[-1] and hy == ys[-1] and N_links > 2:
                print("SNAKE WINS!")
                win_text = font.render("SNAKE WINS!", True, (0, 0, 0))
                text_rect = win_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
                screen.blit(win_text, text_rect)
                pygame.display.flip()
                pygame.time.delay(2000)  # Show the win text for 2 seconds
            else:
                print("HUNTER WINS!")
                # print it on pygame screen
                win_text = font.render("HUNTER WINS!", True, (0, 0, 0))
                text_rect = win_text.get_rect(center=(SCREENW // 2, SCREENH // 2))
                screen.blit(win_text, text_rect)
                pygame.display.flip()
                pygame.time.delay(2000)  # Show the win text for 2 seconds
        
        running = False

    # Control the frame rate
    clock.tick(FPS)

    # Update the counter and increase the snake length every second
    counter += 1
    if counter % (SNAKE_GROW_RATE) == 0:
        counter = 0
        N_links += 1
        xs.append(xs[-1])
        ys.append(ys[-1])    

pygame.quit()
sys.exit()