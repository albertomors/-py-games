import pygame
import sys
from pygame.color import Color
import math
import random
import noise
import numpy as np
import copy

# =======================================================================
# PYGAME INITIALIZATION
# =======================================================================

pygame.init()
pygame.display.set_caption("Isometric!")
pygame.mouse.set_visible(True)
clock = pygame.time.Clock()
font = pygame.font.SysFont('bookantiqua', 18)
sfont = pygame.font.SysFont('bookantiqua', 12)

# =======================================================================
# CONFIG
# =======================================================================

# screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# map 
TILE_WIDTH = 32
TILE_HEIGHT = TILE_WIDTH//2
# MAP_SIZE = (SCREEN_HEIGHT // (TILE_HEIGHT // 2))
MAP_SIZE = 1000
# MAP_RADIUS = MAP_SIZE // 2
MAP_OFFSET_0 = [(SCREEN_WIDTH - TILE_WIDTH) // 2, (SCREEN_HEIGHT - TILE_HEIGHT * MAP_SIZE) // 2]
map_offset = MAP_OFFSET_0.copy()

# time
FPS = 30
time_mult = 1
DAY_LENGTH = 24 * 60 * 60 * 1000 # 24 hours
MS_IN_HOUR = 60 * 60 * 1000
INIT_TIME = 20 * MS_IN_HOUR
SEASON_LENGTH = 91 #days
TIME_MULT = 2

# map randomization
SEA_PROB = 0.4

# seeing
SEE_RADIUS2 = SCREEN_WIDTH * 4/3 // 2
SEE_RADIUS1 = SEE_RADIUS2/2
see_radius1 = SEE_RADIUS1
see_radius2 = SEE_RADIUS2
ELLIPSE_WIDTH = TILE_HEIGHT // 4

# ellipse mask
mask_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
mask_surf.fill((0,0,0,0))
mask_w = see_radius2 * 2
mask_h = int(mask_w * (TILE_HEIGHT / TILE_WIDTH))
pygame.draw.ellipse(mask_surf, Color('white'), ((SCREEN_WIDTH - mask_w) // 2, (SCREEN_HEIGHT - mask_h) // 2, mask_w, mask_h))

# sea
WAVE_SIZE = 3
WAVE_FREQ = 0.002
WAVE_COLOR_OFFSET = 50

# rain
RAIN_PROB = 0.1/FPS
RAIN_MAX = 1600
RAIN_GROWTH_RATE = 1
THUNDER_PROB = 0.4/FPS
rain_amt = 0
raining = False
rain_dir = 1

# sun
SUN_INIT_POS = 0 #east at 8AM
SUN_RADIUS = SCREEN_WIDTH*2

# colors
WOOD_COLOR = Color('saddlebrown')
BG_COLOR = Color('black')
HOUSE_COLOR = WOOD_COLOR
ROOF_COLOR = Color('peru')
GRASS_COLOR_LIGHT = Color('palegreen3')
GRASS_COLOR_DARK = Color('seagreen4')
GRID_COLOR = Color('gray10')
SEA_COLOR = Color('darkblue')
SEA_DEEP = Color('navy')
TOWER_COLOR = Color('silver')
BRIDGE_COLOR = WOOD_COLOR
SNOW_COLOR_LIGHT = Color('white')
SNOW_COLOR_DARK = Color('lightgray')
DIRT_COLOR_LIGHT = Color('sandybrown')
DIRT_COLOR_DARK = WOOD_COLOR
CHESS_LIGHT = GRASS_COLOR_LIGHT
CHESS_DARK = GRASS_COLOR_DARK
TREE_COLOR = Color('darkgreen')
BOAT_COLOR = Color('burlywood')
SAIL_COLOR = Color('white')
STONE_COLOR = Color('slategray')

CARBON_COLOR = Color('black')
IRON_COLOR = Color('dimgray')
COPPER_COLOR = Color('orange')
SILVER_COLOR = Color('silver')
GOLD_COLOR = Color('gold')
DIAMOND_COLOR = Color('lightblue')
MINERAL_COLORS = [CARBON_COLOR, IRON_COLOR, COPPER_COLOR, SILVER_COLOR, GOLD_COLOR, DIAMOND_COLOR]

# =======================================================================
# DRAWING
# =======================================================================

# cell tile
cell_points = [
    (0, TILE_HEIGHT // 2),              #left
    (TILE_WIDTH // 2, 0),               #top
    (TILE_WIDTH, TILE_HEIGHT // 2),     #right
    (TILE_WIDTH // 2, TILE_HEIGHT)      #bottom
]

# house tile
house_height = TILE_HEIGHT // 2
house_points = [
    (0, TILE_HEIGHT // 2),                            #left
    (0, TILE_HEIGHT // 2 - house_height),             #roofleft
    (TILE_WIDTH // 2, 0 - house_height),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 - house_height),    #roof right
    (TILE_WIDTH, TILE_HEIGHT // 2),                   #right
    (TILE_WIDTH // 2, TILE_HEIGHT)                    #bottom
]
cube_points = [
    (0, TILE_HEIGHT // 2),                            #left
    (0, TILE_HEIGHT // 2 - TILE_HEIGHT),             #roofleft
    (TILE_WIDTH // 2, 0 - TILE_HEIGHT),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 - TILE_HEIGHT),    #roof right
    (TILE_WIDTH, TILE_HEIGHT // 2),                   #right
    (TILE_WIDTH // 2, TILE_HEIGHT)                    #bottom
]
roof_points = [
    (0, TILE_HEIGHT // 2 - house_height),             #roofleft
    (TILE_WIDTH // 2, 0 - house_height),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 - house_height),    #roof right
    (TILE_WIDTH // 2, TILE_HEIGHT - house_height)     #roof bottom
]

# tower tile
tower_height = TILE_HEIGHT * 3.5
tower_points = [
    (0, TILE_HEIGHT // 2),                            #left
    (0, TILE_HEIGHT // 2 - tower_height),             #roofleft
    (TILE_WIDTH // 2, 0 - tower_height),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 - tower_height),    #roof right
    (TILE_WIDTH, TILE_HEIGHT // 2),                   #right
    (TILE_WIDTH // 2, TILE_HEIGHT)                    #bottom
]
tower_roof_points = [
    (0, TILE_HEIGHT // 2 - tower_height),             #roofleft
    (TILE_WIDTH // 2, 0 - tower_height),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 - tower_height),    #roof right
    (TILE_WIDTH // 2, TILE_HEIGHT - tower_height)     #roof bottom
]

TREE_HEIGHT = TILE_HEIGHT * 2/3
w = 2
h = w * TILE_HEIGHT // TILE_WIDTH
tree_points = [
    (0 + w, TILE_HEIGHT // 2 - TREE_HEIGHT),              #left
    (TILE_WIDTH // 2, -TILE_HEIGHT - TREE_HEIGHT + h),    #top
    (TILE_WIDTH - w, TILE_HEIGHT // 2 - TREE_HEIGHT),     #right
    (TILE_WIDTH // 2, TILE_HEIGHT - TREE_HEIGHT - h)      #bottom
]

# boat tile
boat_points = cell_points
sail_3rd_point = {
    'north' : (TILE_WIDTH*3/4, TILE_HEIGHT*1/4 - TREE_HEIGHT),
    'south' : (TILE_WIDTH*1/4, TILE_HEIGHT*3/4 - TREE_HEIGHT),
    'west' : (TILE_WIDTH*1/4, TILE_HEIGHT*1/4 - TREE_HEIGHT),
    'east' : (TILE_WIDTH*3/4, TILE_HEIGHT*3/4 - TREE_HEIGHT)
}
sail_points = [
    (TILE_WIDTH // 2, TILE_HEIGHT // 2 - TREE_HEIGHT),  #left
    (TILE_WIDTH // 2, -TILE_HEIGHT - TREE_HEIGHT),      #top
    sail_3rd_point['north'],                             #right
]

# stone
w = 4
h = 2
rock_points = [
    (0+w, TILE_HEIGHT // 2),                            #left
    (0+2*w, TILE_HEIGHT // 2 - house_height),             #roofleft
    (TILE_WIDTH // 2, 0 - house_height+2*h),              #roof top
    (TILE_WIDTH-2*w, TILE_HEIGHT // 2 - house_height),    #roof right
    (TILE_WIDTH-w, TILE_HEIGHT // 2),                   #right
    (TILE_WIDTH // 2, TILE_HEIGHT-h)                    #bottom
]

stack_points = [
    (0, TILE_HEIGHT // 2 + house_height*4),                            #left
    (0, TILE_HEIGHT // 2),             #roofleft
    (TILE_WIDTH // 2, 0),              #roof top
    (TILE_WIDTH, TILE_HEIGHT // 2 + house_height),    #roof right
    (TILE_WIDTH, TILE_HEIGHT // 2 + house_height*3),                   #right
    (TILE_WIDTH // 2, TILE_HEIGHT + house_height*3)                    #bottom
]

# =======================================================================
# MAP GENERATION
# =======================================================================

import numpy as np
import random, noise

def generate_archipelago(size=MAP_SIZE, 
                         num_archipelagos=3, 
                         sea_level=SEA_PROB,
                         scale=0.05,
                         detail_scale=0.1,
                         detail_blend=0.4,
                         seed=42):
    """
    Procedurally generates an archipelago map with biomes.
    Optimized with NumPy vectorization (only loops over centers).
    
    thanks ChatGPT
    """

    island_size = int(MAP_SIZE / num_archipelagos * 2/3 )
    island_size = min(island_size, size // 2)

    # Random seed
    # random.seed(seed)
    # np.random.seed(seed)

    # === 1. Coordinate grid ===
    y, x = np.mgrid[0:size, 0:size]

    # === 2. Base & detail heightmaps ===
    heightmap = np.vectorize(lambda i, j: noise.pnoise2(j * scale, i * scale, octaves=4))(y, x)
    detail_map = np.vectorize(lambda i, j: noise.pnoise2(j * detail_scale, i * detail_scale, octaves=6))(y, x)

    # Normalize maps
    heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())
    detail_map = (detail_map - detail_map.min()) / (detail_map.max() - detail_map.min())

    # === 3. Archipelago centers ===
    centers = [(random.randint(island_size, size - island_size),
                random.randint(island_size, size - island_size))
               for _ in range(num_archipelagos)]

    # === 4. Falloff map (Gaussian influence of closest center) ===
    dist_sq = np.full((size, size), np.inf)
    for cx, cy in centers:
        d = (x - cx) ** 2 + (y - cy) ** 2
        dist_sq = np.minimum(dist_sq, d)
    falloff_map = np.exp(-dist_sq / (2 * (island_size ** 2)))

    # === 5. Final terrain ===
    island_field = (heightmap * (1 - detail_blend) + detail_map * detail_blend) * falloff_map

    # === 6. Biomes (vectorized thresholds) ===
    biome_map = np.zeros_like(island_field, dtype=int)
    biome_map[(island_field >= sea_level) & (island_field < sea_level + 0.05)] = 1
    biome_map[(island_field >= sea_level + 0.05) & (island_field < 0.6)] = 2
    biome_map[island_field >= 0.6] = 3

    return biome_map, centers

def crop_borders(map):
    # find the outers convex set of sea
    borders = set()
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            if map[y][x] == 0:
                borders.add((x, y))

    while borders:
        x, y = borders.pop()
        if random.random() < SEA_PROB:
            map[y][x] = 0

            # look around
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy

                # check we dont go outside map and touch only ground
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and map[ny][nx] == 1:
                    borders.add((nx, ny))

    return map

def generate_one_island_map(radius):
    """Generates a map with a single island of given radius"""
    radius = min(radius, MAP_SIZE//2)

    # map_surf data: 1 = ground, 0 = sea
    map = [[1 if (x-MAP_SIZE//2)**2 + (y-MAP_SIZE//2)**2 <= (radius)**2 else 0 for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]
    
    return map

# =======================================================================
# MAP SPAWNING
# =======================================================================

def spawn_trees(howmany):
    for _ in range(howmany):
        if tree_positions:
            x, y = random.choice(tree_positions)
            # Check surrounding cells for empty ground to spawn new trees
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and uppermap[ny][nx] == 1:
                    if random.random() < 0.1:  # Small chance to spawn a new tree
                        uppermap[ny][nx] = 5

def spawn_minerals(width=MAP_SIZE, height=MAP_SIZE, cluster_count=MAP_SIZE, cluster_size=2):
    """
    Procedurally generate small clusters of minerals and metals on a 2D map.
    
    Parameters:
        width, height (int): size of map
        cluster_count (int): number of clusters to generate
        cluster_size (int): max radius of each cluster
    Returns:
        numpy array with resource distribution
    """
    
    # Possible resources with rarity weighting (more common -> higher weight)
    resources = {
        2 : 0.25,       # carbon
        3 : 0.20,       # iron
        4 : 0.15,       # copper
        5 : 0.10,       # silver
        6 : 0.05,       # gold
        7 : 0.02        # diamond
    }
    resource_names = list(resources.keys())
    weights = list(resources.values())

    # Initialize map
    game_map = np.full((height, width), 1, dtype=object)

    for _ in range(cluster_count):
        # Pick resource type weighted by rarity
        resource = random.choices(resource_names, weights)[0]

        # Pick random center point
        cx, cy = random.randint(0, width-1), random.randint(0, height-1)

        # Random cluster radius
        r = random.randint(2, cluster_size)

        # Fill cluster with resource using circular pattern
        for x in range(cx-r, cx+r+1):
            for y in range(cy-r, cy+r+1):
                if 0 <= x < width and 0 <= y < height:
                    if (x-cx)**2 + (y-cy)**2 <= r**2:
                        if random.random() < 0.6:  # not fully solid, some gaps
                            game_map[y, x] = resource

    return game_map

# =======================================================================
# SCREEN/CAMERA
# =======================================================================

def iso_to_screen(x, y):
    screen_x = (x - y) * TILE_WIDTH // 2 + map_offset[0]
    screen_y = (x + y) * TILE_HEIGHT // 2 + map_offset[1]
    return screen_x, screen_y

def screen_to_iso(mx, my):
    mx -= map_offset[0]
    my -= map_offset[1]
    x = (mx // (TILE_WIDTH // 2) + my // (TILE_HEIGHT // 2)) // 2
    y = (my // (TILE_HEIGHT // 2) - mx // (TILE_WIDTH // 2)) // 2
    return int(x), int(y)

def in_ellipse(x, y, r):
    """check if the cell coordinates is inside an isometric ellipse of horizontal radius r"""
    a = r
    b = a * (TILE_HEIGHT / TILE_WIDTH)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2

    # Isometric ellipse equation: ((x-cx)/a)^2 + ((y-cy)/b)^2 > 1
    return ((x -  cx) ** 2) / (a ** 2) + ((y - cy) ** 2) / (b ** 2)

def active_map():
    """returns a rectangular list of active cells to cover the whole screen taking the 4 corners"""
    active_cells = []
    
    tl = 0,0
    tr = SCREEN_WIDTH,0
    bl = 0,SCREEN_HEIGHT
    br = SCREEN_WIDTH,SCREEN_HEIGHT

    if world in ['down', 'going up']:
        cc = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        tl = cc[0] - see_radius2, cc[1] - see_radius2 * TILE_HEIGHT / TILE_WIDTH
        tr = cc[0] + see_radius2, cc[1] - see_radius2 * TILE_HEIGHT / TILE_WIDTH
        bl = cc[0] - see_radius2, cc[1] + see_radius2 * TILE_HEIGHT / TILE_WIDTH
        br = cc[0] + see_radius2, cc[1] + see_radius2 * TILE_HEIGHT / TILE_WIDTH

    minx = max(0, screen_to_iso(tl[0], tl[1])[0] - 1)
    miny = max(0, screen_to_iso(tr[0], tr[1])[1] - 1)
    maxx = min(MAP_SIZE-1, screen_to_iso(br[0], br[1])[0] + 1)
    maxy = min(MAP_SIZE-1, screen_to_iso(bl[0], bl[1])[1] + 1)

    # Create a grid of all points in the rectangular range
    for x in range(minx, maxx+1):
        for y in range(miny, maxy+1):
            active_cells.append((x, y))

    # In underground world, only include cells connected to player
    if world in ['down', 'going up']:
        # Create a set for fast lookups
        connected_cells = set()
        visited = set()
        queue = [player.pos]
        
        # BFS to find all connected cells
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
                
            visited.add((cx, cy))
            if (cx, cy) in active_cells and map[cy][cx] != 0:
                connected_cells.add((cx, cy))
                # Check adjacent cells (4-directional)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    queue.append((nx, ny))

        # Filter active cells to only include connected ones
        active_cells = [cell for cell in active_cells if cell in connected_cells]

    # Sort active cells by x+y to ensure correct drawing order (back to front)
    # active_cells.sort(key=lambda cell: cell[0] + cell[1])
    return active_cells

"""project nx,ny inside map"""
clamp = lambda nx, ny: (min(max(nx, 0), MAP_SIZE - 1), min(max(ny, 0), MAP_SIZE - 1))

# buggy
# def move_active_map_by_one(active_map, dx, dy):
#     """ if player moves by only one cell i know how much to move the camera"""
#     return [clamp(x + dx, y + dy) for x, y in active_map]

def recenter_camera():
    """recenter the camera on the player"""
    global map_offset

    px, py = iso_to_screen(player.pos[0], player.pos[1])
    diff_x, diff_y = SCREEN_WIDTH // 2 - px, SCREEN_HEIGHT // 2 - py

    map_offset[0] += diff_x
    map_offset[1] += diff_y

howtomovecamera={
                (0, 0) : (0, 0),
                (0, 1) : (-1,+1),     #down
                (1, 0) : (+1,+1),     #right
                (0,-1) : (+1,-1),    #up
                (-1,0) : (-1,-1)     #left
            }

def move_camera(dx, dy):
    """default method called"""
    global active_cells

    #recenter camera
    recenter_camera()
    active_cells = active_map()

# buggy
# def move_camera_by_one(dx, dy):
#     global map_offset, active_cells

#     #move camera
#     map_offset[0] -= TILE_WIDTH // 2 * howtomovecamera[(dx,dy)][0]
#     map_offset[1] -= TILE_HEIGHT // 2 * howtomovecamera[(dx,dy)][1]

#     active_cells = active_map()

# =======================================================================
# TIME HANDLING
# =======================================================================

def init_time():
    global current_time, last_time

    last_time = pygame.time.get_ticks()
    current_time = last_time + INIT_TIME

def update_time():
    global current_time, last_time
    global seconds, minutes, hour, day, season, hourstamp, daytime

    elapsed_time = (pygame.time.get_ticks() - last_time) * time_mult
    current_time += elapsed_time
    seconds = current_time // 1000
    minutes = seconds // 60
    hour = minutes // 60
    day = (hour // 24) % 364
    season = 'spring' if day+1 <= SEASON_LENGTH else 'summer' if day+1 <= SEASON_LENGTH*2 else 'fall' if day+1 <= SEASON_LENGTH*3 else 'winter'
    seconds = seconds % 60
    minutes = minutes % 60
    hour = hour % 24
    hourstamp = hour if hour <= 12 else hour - 12
    daytime = "night" if 0 <=hour < 6 else "morning" if hour < 12 else "afternoon" if hour < 18 else "evening" if hour <= 21 else "night"

    last_time = pygame.time.get_ticks()

# =======================================================================
# WEATHER
# =======================================================================

def update_weather():
    global raining, rain_amt, rain_dir

    # RAIN handling ---------------------------------------------------------------------------------
    if not raining and season != "winter":
        raining = random.random() < RAIN_PROB

    if raining:
        rain_amt = rain_amt + rain_dir * RAIN_GROWTH_RATE
        if rain_amt >= RAIN_MAX:
            rain_dir *= -1
            rain_amt = RAIN_MAX
        elif rain_amt <= 0:
            rain_dir *= -1
            raining = False
            rain_amt = 0
    
    # hail if its winter
    if season == "winter" and day%SEASON_LENGTH < 60: #snow only for 2 months
        raining = False
        rain_dir = 1
        rain_amt = 0

# =======================================================================
# MAP DRAWING
# =======================================================================

def draw_map_surf():
    global time_mult

    time = pygame.time.get_ticks()
    map_surf.fill(SEA_COLOR)

    for x, y in active_cells:
        sx, sy = iso_to_screen(x, y)

        if map[y][x] == 0: # Draw sea tiles with wave sine animation
            
            # Calculate direction towards the center
            dx, dy = x - MAP_SIZE // 2, y - MAP_SIZE // 2
            dist = math.hypot(dx, dy)
            wave_phase = time * WAVE_FREQ + dist
            wave_offset = int(WAVE_SIZE * math.sin(wave_phase)) + wavemap[y][x]
            wave_color = int(WAVE_COLOR_OFFSET / WAVE_SIZE * -1 * wave_offset)

            # Vary sea color for wave effect
            r = max(0, min(255, SEA_COLOR.r + wave_color))
            g = max(0, min(255, SEA_COLOR.g + wave_color))
            b = max(0, min(255, SEA_COLOR.b + wave_color))
            
            # Draw sea tile with wave offset
            # pygame.draw.polygon(map_surf, (r,g,b), [(sx + dx, sy + dy + wave_offset + house_height) for dx, dy in house_points])
            pygame.draw.polygon(map_surf, (r,g,b), [(sx+dx, sy+dy+wave_offset) for dx, dy in cell_points], 0)

        elif map[y][x] in (1,5,8): # Draw an empty tile
            is_even = (x + y) % 2 == 0
            val = (day%SEASON_LENGTH)/(SEASON_LENGTH-1)
            c1 = mix_color(GRASS_COLOR_LIGHT, DIRT_COLOR_LIGHT, val) if season == 'summer' else \
                 mix_color(SNOW_COLOR_LIGHT, DIRT_COLOR_LIGHT, 1-val) if season == 'fall' else \
                 mix_color(SNOW_COLOR_LIGHT, GRASS_COLOR_LIGHT, val) if season == 'winter' else \
                 GRASS_COLOR_LIGHT
            c2 = mix_color(GRASS_COLOR_DARK, DIRT_COLOR_DARK, val) if season == 'summer' else \
                 mix_color(SNOW_COLOR_DARK, DIRT_COLOR_DARK, 1-val) if season == 'fall' else \
                 mix_color(SNOW_COLOR_DARK, GRASS_COLOR_DARK, val) if season == 'winter' else \
                 GRASS_COLOR_DARK

            tile_color = c1 if is_even else c2
            # v = 80
            # darker_color = (max(0,tile_color.r - v), max(0,tile_color.g - v), max(0,tile_color.b - v))

            # pygame.draw.polygon(map_surf, darker_color, [(sx + dx, sy + dy + house_height) for dx, dy in house_points])
            pygame.draw.polygon(map_surf, tile_color, [(sx+dx, sy+dy) for dx, dy in cell_points], 0)

        elif map[y][x] == 4: # Draw a bridge
            pygame.draw.polygon(map_surf, BRIDGE_COLOR, [(sx + dx, sy + dy) for dx, dy in cell_points])

    map_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    #draw several concentric ellipses to simulate see radius
    weather_surf.fill((0,0,0,0))  # transparent background
    num_ellipses = math.ceil((see_radius2 - see_radius1) // ELLIPSE_WIDTH + 2)
    for i in range(num_ellipses):
        # Draw isometric ellipses (scaled circles) to match isometric perspective
        w = (see_radius1 + i * ELLIPSE_WIDTH) * 2
        h = int(w * (TILE_HEIGHT / TILE_WIDTH))
        lvl = int(255 * (i / num_ellipses))
        pygame.draw.ellipse(weather_surf, (0,0,0,lvl), ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h), ELLIPSE_WIDTH)

    if raining:
        for _ in range(rain_amt):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            c = random.randint(0, 100)
            pygame.draw.line(weather_surf, (0, c, 255), (x, y), (x, y + random.randint(5, 15)), 1)

        black_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        lvl = int(128 * (rain_amt/RAIN_MAX))
        black_surf.fill(Color('black'))
        black_surf.set_alpha(lvl)
        weather_surf.blit(black_surf, (0, 0))

        # weather_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_MULT) #clip rain

        # draw thunders as flashes
        if random.random() < THUNDER_PROB:
            white_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            white_surface.fill(Color('white'))
            weather_surf.blit(white_surface, (0, 0))
            print("thunder!")
    
    # hail if its winter
    if season == "winter" and day%SEASON_LENGTH < 60: #snow only for 2 months
        
        # Create a snow surface with alpha
        snow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for _ in range(200):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(snow_surface, (255, 255, 255), (x, y), random.randint(1, 3))
        
        # Add transparency to the snow surface before blitting
        snow_surface.set_alpha(235)
        weather_surf.blit(snow_surface, (0, 0))
    
    # SUN system ----------------------------------------------------------------
    sun_pos = (current_time % DAY_LENGTH - 8*MS_IN_HOUR) / DAY_LENGTH * (2 * math.pi) + SUN_INIT_POS
    sunx = SCREEN_WIDTH // 2 + SUN_RADIUS * math.cos(sun_pos)
    suny = SCREEN_HEIGHT // 2 + SUN_RADIUS * math.sin(-sun_pos) * TILE_HEIGHT / TILE_WIDTH

    if hh(8, 20):  # Daytime
        pygame.draw.circle(debug_surf, Color('yellow'), (int(sunx), int(suny)), 5)
    else:
        pygame.draw.circle(debug_surf, Color('black'), (int(sunx), int(suny)), 5)

    #8PM = 210°, 10PM = 240°
    #6AM = 0°, 8AM = 30°
    if hh(20, 22):
        lvl = int(128 * (current_time % DAY_LENGTH - 20*MS_IN_HOUR) / (2*MS_IN_HOUR))
    elif hh(22, 24) or hh(0,6):
        lvl = 128
    elif hh(6, 8):
        lvl = int(128 * (1 - (current_time % DAY_LENGTH - 6*MS_IN_HOUR) / (2*MS_IN_HOUR)))
    else:
        lvl = 0

    day_night_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    day_night_surf.fill(Color('black'))
    day_night_surf.set_alpha(lvl)

    lux_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    lux_surf.fill((255,255,255,255))
    
    # Draw sunlight rays from the sun to the left and right borders of houses and towers
    shadow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    shadow_surf.set_alpha(128)

    for x, y in active_cells:
        if map[y][x] in (2,3):  # Check for houses or towers
            sx, sy = iso_to_screen(x, y)

            if hh(8, 20):

                # Calculate left and right border points of the structure
                y1 = sy + cell_points[0][1]  # bottom point of the tile
                x1l, x1r = sx + cell_points[0][0], sx + cell_points[2][0]
                length = house_height if map[y][x] == 2 else tower_height
                r = abs(math.cos(sun_pos) * length * 2)  # Length of the shadow
                
                points = []
                for x1 in (x1l, x1r):
                    pygame.draw.line(debug_surf, Color('yellow'), (int(sunx), int(suny)), (x1, y1), 1)
                    if sunx != x1:
                        m = (suny - y1) / (sunx - x1) 
                        delta = r/math.sqrt(1 + m**2)
                        x2 = x1 - delta * math.copysign(1, sunx - x1)
                        y2 = y1 - m * delta * math.copysign(1, sunx - x1)
                        pygame.draw.line(debug_surf, Color('red'), (x1, y1), (x2, y2), 1)
                    else:
                        x2 = x1
                        y2 = y1 + r

                    points.append((x1, y1))
                    points.append((x2, y2))
                
                # correct the order flipping the third and fourth points
                points[2], points[3] = points[3], points[2]

                pygame.draw.polygon(shadow_surf, Color('black'), [(x,y) for x,y in points], 0)
            
            else:
                pygame.draw.ellipse(lux_surf, (255,255,255,128), (sx - TILE_WIDTH*2, sy - TILE_HEIGHT*2, TILE_WIDTH * 5, TILE_HEIGHT * 5))
                pygame.draw.ellipse(lux_surf, (255,255,255,64), (sx - TILE_WIDTH, sy - TILE_HEIGHT, TILE_WIDTH * 3, TILE_HEIGHT * 3))
                pygame.draw.ellipse(lux_surf, (255,255,255,0), (sx - TILE_WIDTH//2, sy - TILE_HEIGHT//2, TILE_WIDTH * 2, TILE_HEIGHT * 2))

                if map[y][x] == 2:
                    pass
                    # pygame.draw.polygon(lux_surf, (255,255,255,0), [(sx + dx, sy + dy) for dx, dy in house_points])
                    # pygame.draw.polygon(lux_surf, (255,255,255,0), [(sx + dx, sy + dy) for dx, dy in roof_points], 0)
                else:
                    pygame.draw.polygon(lux_surf, (255,255,255,0), [(sx + dx, sy + dy) for dx, dy in tower_points])
                    pygame.draw.polygon(lux_surf, (255,255,255,0), [(sx + dx, sy + dy) for dx, dy in tower_roof_points], 0)

    day_night_surf.blit(lux_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    weather_surf.blit(day_night_surf, (0, 0))
    map_surf.blit(shadow_surf, (0, 0))

    # draw houses on top of shadows
    for x, y in active_cells:
        sx, sy = iso_to_screen(x, y)

        if map[y][x] == 2: # Draw a house
            pygame.draw.polygon(map_surf, HOUSE_COLOR, [(sx + dx, sy + dy) for dx, dy in house_points])
            pygame.draw.polygon(map_surf, ROOF_COLOR, [(sx + dx, sy + dy) for dx, dy in roof_points], 0)
        
        elif map[y][x] == 3: # Draw a tower
            pygame.draw.polygon(map_surf, TOWER_COLOR, [(sx + dx, sy + dy) for dx, dy in tower_points])
            pygame.draw.polygon(map_surf, ROOF_COLOR, [(sx + dx, sy + dy) for dx, dy in tower_roof_points], 0)
        
        elif map[y][x] == 13: # Draw a ladder
            pygame.draw.polygon(map_surf, Color('black'), [(sx + dx, sy + dy) for dx, dy in cell_points])
            ccx = sx + TILE_WIDTH // 2
            ccy = sy + TILE_HEIGHT // 2
            pygame.draw.line(map_surf, WOOD_COLOR, (ccx-TILE_WIDTH//4, ccy-TILE_HEIGHT//2), (ccx-TILE_WIDTH//4, ccy + TILE_HEIGHT//4), 3)
            pygame.draw.line(map_surf, WOOD_COLOR, (ccx+TILE_WIDTH//4, ccy-TILE_HEIGHT//2), (ccx+TILE_WIDTH//4, ccy + TILE_HEIGHT//4), 3)        
            pygame.draw.line(map_surf, WOOD_COLOR, (ccx-TILE_WIDTH//4, ccy), (ccx+TILE_WIDTH//4, ccy), 2)

        elif map[y][x] == 5: # Draw a tree
            ctree = Color('white') if season == 'winter' else TREE_COLOR
            mult = 15
            r = max(0, min(255, ctree.r + mult * wavemap[y][x]))
            g = max(0, min(255, ctree.g + mult * wavemap[y][x]))
            b = max(0, min(255, ctree.b + mult * wavemap[y][x]))
            tile_color = c1 if is_even else c2
            pygame.draw.line(map_surf, WOOD_COLOR, (sx +TILE_WIDTH//2, sy + TILE_HEIGHT//2), (sx +TILE_WIDTH//2, sy + TILE_HEIGHT//2 - TREE_HEIGHT), 3)
            pygame.draw.polygon(map_surf, (r,g,b), [(sx + dx, sy + dy) for dx, dy in tree_points])

        elif map[y][x] == 7: # Draw a boat

            # Calculate direction towards the center
            dx, dy = x - MAP_SIZE // 2, y - MAP_SIZE // 2
            dist = math.hypot(dx, dy)
            wave_phase = time * WAVE_FREQ + dist
            wave_offset = int(WAVE_SIZE * math.sin(wave_phase)) + wavemap[y][x]

            dxdy_to_dir = {
                (1, 0): 'east',
                (-1, 0): 'west',
                (0, 1): 'south',
                (0, -1): 'north'
            }

            sail_dir = dxdy_to_dir[tuple(boats[(x, y)])]
            sail_points[2] = sail_3rd_point[sail_dir]

            pygame.draw.polygon(map_surf, BOAT_COLOR, [(sx+dx, sy+dy+wave_offset) for dx, dy in boat_points], 0)
            pygame.draw.polygon(map_surf, SAIL_COLOR, [(sx + dx, sy + dy + wave_offset) for dx, dy in sail_points])
            pygame.draw.line(map_surf, WOOD_COLOR, (sx +TILE_WIDTH//2, sy + TILE_HEIGHT//2+wave_offset), (sx +TILE_WIDTH//2, sy - TILE_HEIGHT - TREE_HEIGHT + wave_offset), 3)

        elif map[y][x] == 8:
            cstone = STONE_COLOR
            mult = 30
            r = max(0, min(255, cstone.r + mult * wavemap[y][x]))
            g = max(0, min(255, cstone.g + mult * wavemap[y][x]))
            b = max(0, min(255, cstone.b + mult * wavemap[y][x]))
            pygame.draw.polygon(map_surf, (r,g,b), [(sx + dx, sy + dy) for dx, dy in rock_points])

        if player.pos == (x, y):
            if map[y][x] in (2,3):
                # Draw smoke from the house
                smoke_x = sx + TILE_WIDTH // 2
                height = house_height if map[y][x] == 2 else tower_height
                smoke_y = sy - height - TILE_HEIGHT // 2

                # Create a random upward drift for the smoke
                for i in range(10):
                    g = random.randint(60,200)
                    smoke_color = (g, g, g, 128)  # Semi-transparent gray
                    offset_x = random.randint(-4, 4)
                    offset_y = -i * 4 + random.randint(-2, 2)
                    size = random.randint(1, 4)
                    pygame.draw.circle(map_surf, smoke_color, (smoke_x + offset_x, smoke_y + offset_y), size)
        
                time_mult = TIME_MULT if map[y][x] == 2 else TIME_MULT * 2

            elif map[y][x] == 7:
                # Calculate direction towards the center
                dx, dy = x - MAP_SIZE // 2, y - MAP_SIZE // 2
                dist = math.hypot(dx, dy)
                wave_phase = time * WAVE_FREQ + dist
                wave_offset = int(WAVE_SIZE * math.sin(wave_phase)) + wavemap[y][x]

                player.draw(map_surf, sx+TILE_WIDTH//2, sy+TILE_HEIGHT//2+wave_offset)
                time_mult = 1

            else:
                player.draw(map_surf, sx+TILE_WIDTH//2, sy+TILE_HEIGHT//2)
                time_mult = 1

    # SEE RADIUS handling --------------------------------------------------------------------------
    map_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit the masked surfaces to the screen
    # Clear the screen
    screen.fill(BG_COLOR)
    screen.blit(map_surf, (0, 0))
    screen.blit(weather_surf, (0, 0))

# =======================================================================
# UNDERWORLD
# =======================================================================

def draw_underworld():
    global time_mult

    map_surf.fill((20, 20, 20))
    lux_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    lux_surf.fill((255,255,255,255))

    #draw several concentric ellipses to simulate see radius
    weather_surf.fill((0,0,0,0))  # transparent background
    num_ellipses = math.ceil((see_radius2 - see_radius1) // ELLIPSE_WIDTH + 2)
    for i in range(num_ellipses):
        # Draw isometric ellipses (scaled circles) to match isometric perspective
        w = (see_radius1 + i * ELLIPSE_WIDTH) * 2
        h = int(w * (TILE_HEIGHT / TILE_WIDTH))
        lvl = int(255 * (i / num_ellipses))
        pygame.draw.ellipse(weather_surf, (0,0,0,lvl), ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h), ELLIPSE_WIDTH)

    for x, y in active_cells:
        sx, sy = iso_to_screen(x, y)

        if map[y][x] in (1,2,3,4,5,6,7,13) : # Draw an empty tile
            is_even = (x + y) % 2 == 0
            tile_color = DIRT_COLOR_LIGHT if is_even else DIRT_COLOR_DARK
            # v = 80
            # darker_color = (max(0,tile_color.r - v), max(0,tile_color.g - v), max(0,tile_color.b - v))
            # pygame.draw.polygon(map_surf, darker_color, [(sx + dx, sy + dy + house_height) for dx, dy in house_points])
            pygame.draw.polygon(map_surf, tile_color, [(sx+dx, sy+dy) for dx, dy in cell_points], 0)

        if map[y][x] == 13: # Draw a ladder
            ccx = sx + TILE_WIDTH // 2
            ccy = sy + TILE_HEIGHT // 2
            ladder_h = tower_height * 2/3
            pygame.draw.line(map_surf, Color('white'), (ccx-TILE_WIDTH//4, ccy+TILE_HEIGHT//2), (ccx-TILE_WIDTH//4, ccy - ladder_h), 3)
            pygame.draw.line(map_surf, Color('white'), (ccx+TILE_WIDTH//4, ccy+TILE_HEIGHT//2), (ccx+TILE_WIDTH//4, ccy - ladder_h), 3)

            for i in range(5):      
                pygame.draw.line(map_surf, Color('white'), (ccx-TILE_WIDTH//4, ccy-i*TILE_HEIGHT//2), (ccx+TILE_WIDTH//4, ccy-i*TILE_HEIGHT//2), 2)

            pygame.draw.polygon(lux_surf, (255,255,255,0), [(sx, 0), (sx, sy+TILE_HEIGHT//2), (sx+TILE_WIDTH//2, sy+TILE_HEIGHT), (sx+TILE_WIDTH, sy+TILE_HEIGHT//2), (sx+TILE_WIDTH, 0)], 0)
            weather_surf.blit(lux_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        elif map[y][x] == 99:
            time = pygame.time.get_ticks()
            # Create a color that changes over time using sine waves with different frequencies
            r = 128 + int(127 * math.sin(time * 0.0011))
            g = 128 + int(127 * math.sin(time * 0.002))
            b = 128 + int(127 * math.sin(time * 0.005))
            randcolor = (r, g, b)
            pygame.draw.polygon(map_surf, randcolor, [(sx+dx, sy+dy) for dx, dy in cube_points], 0)
            # Draw a question mark on the cube
            question_mark = sfont.render("?", True, Color('white'))
            question_rect = question_mark.get_rect(center=(sx + TILE_WIDTH // 2, sy))
            map_surf.blit(question_mark, question_rect)

        if map[y][x] in (2,3,4,5,6,7):
            #then draw mineral
            mineral_color = MINERAL_COLORS[map[y][x] - 2]
            pygame.draw.polygon(map_surf, mineral_color, [(sx + dx, sy + dy) for dx, dy in rock_points])

        if x == player.pos[0] and y == player.pos[1]:
            player.draw(map_surf, sx+TILE_WIDTH//2, sy+TILE_HEIGHT//2)

    map_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # SEE RADIUS handling --------------------------------------------------------------------------
    map_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Blit the masked surfaces to the screen
    # Clear the screen
    screen.fill(BG_COLOR)
    screen.blit(map_surf, (0, 0))
    screen.blit(weather_surf, (0, 0))

# =======================================================================
# GAMEBAR SCREEN
# =======================================================================

def draw_info_screen():
    info_surf.fill((0, 0, 0, 0))

    txt = f"weather: {'raining ' + str(int(rain_amt/RAIN_MAX*100)) + '%' if raining else 'snowing' if season == 'winter' and day%SEASON_LENGTH < 60 else 'sunny' if hh(8,20) else 'clear'}"
    rain_text = font.render(txt, True, Color('white'))
    rain_text_rect = rain_text.get_rect(topleft=(10, 10))
    info_surf.blit(rain_text, rain_text_rect)

    fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, Color('white'))
    fps_text_rect = fps_text.get_rect(topleft=(10, 30))
    info_surf.blit(fps_text, fps_text_rect)

    day_text = font.render(f"{daytime} {hourstamp:02d}:{minutes:02d} {'AM' if hour < 12 else 'PM'}   x{time_mult}>>", True, Color('white'))
    day_text_rect = day_text.get_rect(topleft=(10, 50))
    info_surf.blit(day_text, day_text_rect)

    season_text = font.render(f"day {day+1} - {season}", True, Color('white'))
    season_text_rect = season_text.get_rect(topleft=(10, 70))
    info_surf.blit(season_text, season_text_rect)
    
    spacing = 10
    txt = ['dig','put','house','tower','bridge','pickaxe','B-dig','boat','ladder']
    
    for i in range(ITEM_NUM):
        if i == current_item:
            y_pos = SCREEN_HEIGHT - TILE_HEIGHT - 10 - 10 -30
            text_surface = sfont.render(txt[i], True, Color('white'))
            text_rect = text_surface.get_rect(midbottom=((i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH//2, y_pos + 22 + TILE_HEIGHT//2))
            info_surf.blit(text_surface, text_rect)
        else:
            y_pos = SCREEN_HEIGHT - TILE_HEIGHT - 10 -30

        if i==0 or i==6:
            pygame.draw.polygon(info_surf, SEA_COLOR,  [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in cell_points], 0)
        elif i==1:
            pygame.draw.polygon(info_surf, CHESS_LIGHT,  [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in cell_points], 0)
        elif i==2:
            pygame.draw.polygon(info_surf, HOUSE_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in house_points])
            pygame.draw.polygon(info_surf, ROOF_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in roof_points], 0)
        elif i==3:
            pygame.draw.polygon(info_surf, TOWER_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in tower_points])
            pygame.draw.polygon(info_surf, ROOF_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in tower_roof_points], 0)
        elif i==4:
            pygame.draw.polygon(info_surf, BRIDGE_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in cell_points], 0)
        elif i==5:
            pygame.draw.polygon(info_surf, GRASS_COLOR_LIGHT, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in cell_points], 0)
            pygame.draw.line(info_surf, WOOD_COLOR, (((i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH//2), (y_pos + TILE_HEIGHT//2)), (((i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH//2), (y_pos + TILE_HEIGHT//2 - TREE_HEIGHT)), 3)
            pygame.draw.polygon(info_surf, TREE_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in tree_points])
        elif i==7:
            pygame.draw.polygon(info_surf, BOAT_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in boat_points], 0)
            pygame.draw.polygon(info_surf, SAIL_COLOR, [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in sail_points])
            pygame.draw.line(info_surf, WOOD_COLOR, (((i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH//2), (y_pos + TILE_HEIGHT//2)), (((i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH//2), (y_pos - TILE_HEIGHT - TREE_HEIGHT)), 3)
        elif i==8:
            pygame.draw.polygon(info_surf, Color('black'), [((i+1)*spacing + i*TILE_WIDTH + dx, y_pos + dy) for dx, dy in cell_points])
            ccx = (i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH // 2
            ccy = y_pos + TILE_HEIGHT // 2
            pygame.draw.line(info_surf, WOOD_COLOR, (ccx-TILE_WIDTH//4, ccy-TILE_HEIGHT//2), (ccx-TILE_WIDTH//4, ccy + TILE_HEIGHT//4), 3)
            pygame.draw.line(info_surf, WOOD_COLOR, (ccx+TILE_WIDTH//4, ccy-TILE_HEIGHT//2), (ccx+TILE_WIDTH//4, ccy + TILE_HEIGHT//4), 3)        
            pygame.draw.line(info_surf, WOOD_COLOR, (ccx-TILE_WIDTH//4, ccy), (ccx+TILE_WIDTH//4, ccy), 2)
        
        # Draw red crosses over unavailable items when in underworld
        if world == 'down' and i not in (1, 5, 8):
            ccx = (i+1)*spacing + i*TILE_WIDTH + TILE_WIDTH // 2
            ccy = y_pos + TILE_HEIGHT // 2

            # Draw a red X over the item
            pygame.draw.line(info_surf, Color('red'), 
                            (ccx - TILE_HEIGHT//2, ccy - TILE_HEIGHT//2),
                            (ccx + TILE_HEIGHT//2, ccy + TILE_HEIGHT//2), 2)
            pygame.draw.line(info_surf, Color('red'), 
                            (ccx - TILE_HEIGHT//2, ccy + TILE_HEIGHT//2),
                            (ccx + TILE_HEIGHT//2, ccy - TILE_HEIGHT//2), 2)

    info_surf.blit(minimap, (SCREEN_WIDTH - MINIMAP_SIZE - 10, SCREEN_HEIGHT - MINIMAP_SIZE - 10))

    mmc = (SCREEN_WIDTH - MINIMAP_SIZE - 10, SCREEN_HEIGHT - MINIMAP_SIZE - 10)
    if world in ['up', 'going down']:
        # Draw the camera view rectangle on the minimap
        scale = MINIMAP_SIZE/MAP_SIZE
        px,py = screen_to_iso(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        px,py = int(px * scale + mmc[0]), int(py * scale + mmc[1])
        pygame.draw.rect(info_surf, Color('yellow'), (px-1, py-1, 3, 3), 1)
    else:
        text_rect = font.render("?", True, Color('yellow')).get_rect(center=(mmc[0]+MINIMAP_SIZE//2, mmc[1]+MINIMAP_SIZE//2))
        info_surf.blit(font.render("?", True, Color('yellow')), text_rect)

    # Display inventory in the bottom right corner
    inventory_text = f" Terra: {inventory['dirt']} | Wood: {inventory['wood']} | Stone: {inventory['stone']} | C: {inventory['coal']} | Fe: {inventory['iron']} | Cu: {inventory['copper']} | Ag: {inventory['silver']} | Au: {inventory['gold']} | Diamond: {inventory['diamond']}"
    text_surface = sfont.render(inventory_text, True, Color('white'))
    text_rect = text_surface.get_rect(bottomleft=(10, SCREEN_HEIGHT - 10))
    info_surf.blit(text_surface, text_rect)

    # Calculate the space needed for inventory text

    # draw wind indicator
    COMPASS_RADIUS = 20
    
    cc = (SCREEN_WIDTH - COMPASS_RADIUS - 20, COMPASS_RADIUS + 20)
    ee = (int(cc[0] + math.cos(wind_dir) * COMPASS_RADIUS), int(cc[1] + math.sin(wind_dir) * COMPASS_RADIUS))
    
    if world in ['up', 'going down']:
        pygame.draw.line(info_surf, (128,128,128), (cc[0],cc[1]-COMPASS_RADIUS), (cc[0],cc[1]+COMPASS_RADIUS), 1)
        pygame.draw.line(info_surf, (128,128,128), (cc[0]-COMPASS_RADIUS,cc[1]), (cc[0]+COMPASS_RADIUS,cc[1]), 1)
        pygame.draw.line(info_surf, Color('red'), cc, ee, 1)
        pygame.draw.circle(info_surf, Color('white'), cc, 4, 1)
    else:
        text_rect = font.render("?", True, Color('yellow')).get_rect(center=(cc[0], cc[1]))
        info_surf.blit(font.render("?", True, Color('yellow')), text_rect)

    pygame.draw.circle(info_surf, Color('white'), cc, COMPASS_RADIUS, 2)
    

    ipo = math.sqrt(2)/2 * COMPASS_RADIUS
    txt = sfont.render('N', True, Color('white'))
    info_surf.blit(txt, txt.get_rect(bottomleft=(cc[0]+ipo,cc[1]-ipo)))
    txt = sfont.render('S', True, Color('white'))
    info_surf.blit(txt, txt.get_rect(topright=(cc[0]-ipo,cc[1]+ipo)))
    txt = sfont.render('E', True, Color('white'))
    info_surf.blit(txt, txt.get_rect(topleft=(cc[0]+ipo,cc[1]+ipo)))
    txt = sfont.render('W', True, Color('white'))
    info_surf.blit(txt, txt.get_rect(bottomright=(cc[0]-ipo,cc[1]-ipo)))

    NUM_TICKS = 10
    ticks = abs(int(wind_power / WIND_MAX_POWER * NUM_TICKS))
    tickw = COMPASS_RADIUS*2 // NUM_TICKS
    tickminh = 5
    tickmaxh = 15
    tickh_inc = (tickmaxh - tickminh) / NUM_TICKS

    ttx, tty = cc[0] - COMPASS_RADIUS, cc[1] + COMPASS_RADIUS + 20
    txt = font.render('wind', True, Color('white'))
    info_surf.blit(txt, txt.get_rect(midtop=(cc[0], tty + 10 + NUM_TICKS * tickh_inc)))

    for i in range(NUM_TICKS):
        pygame.draw.rect(info_surf, Color('white'), (ttx + i*tickw, tty+(NUM_TICKS-i) * tickh_inc, tickw-1, tickminh + i * tickh_inc), 1)
        if world in ['up', 'going down'] and i <= ticks:
            pygame.draw.rect(info_surf, mix_color(Color('green'),Color('red'),i/NUM_TICKS), (ttx + i*tickw, tty+(NUM_TICKS-i) * tickh_inc, tickw-1, tickminh + i * tickh_inc))
    
    screen.blit(info_surf, (0, 0))

def loading_screen():
    # Display "generating map..." text
    loading_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    loading_surf.fill((0, 0, 0, 128))  # Semi-transparent background
    loading_text = font.render("generating map...", True, Color('white'))
    text_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    loading_surf.blit(loading_text, text_rect)
    screen.blit(loading_surf, (0, 0))
    pygame.display.flip()

# =======================================================================
# DEBUG SCREEN
# =======================================================================

def draw_debug_surf():

    # SEE_RADIUS debug ellipses
    w = see_radius1 * 2
    h = int(w * (TILE_HEIGHT / TILE_WIDTH))
    pygame.draw.ellipse(debug_surf, Color('red'), ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h), 1)
    w = see_radius2 * 2
    h = int(w * (TILE_HEIGHT / TILE_WIDTH))
    pygame.draw.ellipse(debug_surf, Color('red'), ((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h), 1)

    screen.blit(debug_surf, (0, 0))

# =======================================================================
# OLD CAMERA HANDLING by mouse
# =======================================================================

def convex_map():
    
    # Calculate convex hull of ground tiles
    ground_points = []
    for x,y in active_cells:
        if map[y][x] in (1,4):  # ground tile or bridge
            sx, sy = iso_to_screen(x, y)
            # Add all 4 corners of the tile
            for dx, dy in cell_points:
                ground_points.append((sx + dx, sy + dy))

    # Graham scan to find convex hull
    def cross_product(O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    def convex_hull(points):
        points = sorted(set(points))
        if len(points) <= 1:
            return points
        
        # Build lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # Build upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        return lower[:-1] + upper[:-1]

    if ground_points:
        hull_points = convex_hull(ground_points)

        if hull_points:
            new_hull_points = []
            for i in range(len(hull_points) - 1):
                p1 = hull_points[i]
                p2 = hull_points[i + 1]
                new_hull_points.append(p1)
                # Calculate the distance between the points
                dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                # If the distance is greater than 3 cells, add intermediate points
                if dist > 3 * TILE_WIDTH:
                    num_intermediate = int(dist // (3 * TILE_WIDTH))
                    for j in range(1, num_intermediate + 1):
                        mx = p1[0] + (p2[0] - p1[0]) * j / (num_intermediate + 1)
                        my = p1[1] + (p2[1] - p1[1]) * j / (num_intermediate + 1)
                        new_hull_points.append((mx, my))
            new_hull_points.append(hull_points[-1])
            hull_points = new_hull_points
            
        return new_hull_points

# =======================================================================
# GAME INITIALIZATION
# =======================================================================

#create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
map_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
weather_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
debug_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
info_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

current_item = 1 # house
ITEM_NUM = 9 # 0 - sea, 1 - ground, 2 - house, 3 - tower, 4 - bridge, 5 - chop, 6 - seaBACK
             # 7 - boat, 8 - ladder

loading_screen()

height_map, centers = generate_archipelago(num_archipelagos=7)
random_center = random.choice(centers)
another_center = random.choice(centers)
while (another_center == random_center):
    another_center = random.choice(centers)

target = iso_to_screen(random_center[0], random_center[1])
drag = SCREEN_WIDTH // 2 - target[0], SCREEN_HEIGHT // 2 - target[1]
map_offset[0] += drag[0]
map_offset[1] += drag[1]

tree_positions = []
boats = {}
uppermap = crop_borders(height_map > 0).astype(int)
for y in range(MAP_SIZE):
    for x in range(MAP_SIZE):
        if height_map[y][x] == 3:
            uppermap[y][x] = 5
            tree_positions.append((x, y))
        elif height_map[y][x] == 1:
            if random.random() < 0.3:
                uppermap[y][x] = 8

# Create a small ground circle around the house
house_radius = 3
for dx in range(-house_radius, house_radius + 1):
    for dy in range(-house_radius, house_radius + 1):
        nx, ny = random_center[0] + dx, random_center[1] + dy
        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and (dx**2 + dy**2 <= house_radius**2):
            uppermap[ny][nx] = 1  # Set to ground

wavemap = np.random.randint(-3, 3, size=(MAP_SIZE, MAP_SIZE)).tolist()
undermap = copy.deepcopy(uppermap > 0).astype(int)
mineral_map = spawn_minerals()
undermap = mineral_map * undermap

for center in centers:
    if center != random_center:
        uppermap[center[1]][center[0]] = 13
        undermap[center[1]][center[0]] = 13
undermap[another_center[1]][another_center[0]] = 99
undermap[random_center[1]][random_center[0]] = 99

world = 'up'
map = uppermap
active_cells = active_map()

inventory = {
    "wood": 100,
    "dirt": 100,
    "stone": 100,
    "coal" : 0,
    "iron": 0,
    "copper": 0,
    "silver": 0,
    "gold": 0,
    "diamond": 0
}

# =======================================================================
# MINIMAP
# =======================================================================

MINIMAP_SIZE = 100
minimap = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE), pygame.SRCALPHA)
minimapcolors = [
    (0,0,0,0),          #sea
    GRASS_COLOR_DARK,   #land
    GRASS_COLOR_DARK,   #house
    GRASS_COLOR_DARK,   #tower
    BRIDGE_COLOR,       #bridge
    GRASS_COLOR_DARK,   #tree
    (0,0,0,0),          # - 6
    (0,0,0,0),          #boat
    STONE_COLOR,        #rock
    (0,0,0,0),          # - 9
    (0,0,0,0),          # - 10
    (0,0,0,0),          # - 11
    (0,0,0,0),          # - 12
    GRASS_COLOR_DARK,   #ladder
]
for x in range(MAP_SIZE):
    for y in range(MAP_SIZE):
        color = minimapcolors[map[y][x]]
        minimap.set_at((x * MINIMAP_SIZE // MAP_SIZE, y * MINIMAP_SIZE // MAP_SIZE), color)
minimap.set_alpha(128)
def update_minimap(x,y):
    minimap.set_at((x * MINIMAP_SIZE // MAP_SIZE, y * MINIMAP_SIZE // MAP_SIZE), minimapcolors[map[y][x]])
    minimap.set_alpha(128)

# =======================================================================
# UTILITIES
# =======================================================================

def mix_color(c1, c2, r):
    "return a gradual mix from c1 to c2 as r goes from 0 to 1"
    r = max(0, min(1, r))
    return Color(
        int(c1.r * (1 - r) + c2.r * r),
        int(c1.g * (1 - r) + c2.g * r),
        int(c1.b * (1 - r) + c2.b * r)
    )

def hh(h1,h2):
        if h1 > h2:
            return hh(h1,24) or hh(0,h2)
        else:
            return h1*MS_IN_HOUR <= current_time % DAY_LENGTH < h2*MS_IN_HOUR
        
# =======================================================================
# PLAYER CLASS
# =======================================================================

class Player:
    def __init__(self,x,y):
        self.pos = (x,y)
        self.dir = [0, 1]  # Initial direction facing down

        self.w = 4
        self.h = TILE_HEIGHT
        self.speed = PLAYER_SPEED #every second
        self.last_move_time = pygame.time.get_ticks()

        self.offset_y = 0

    def move(self, dx, dy):
        global world
        if world in ['going up', 'going down']:
            return
        
        # rotate before moving of 1 cell
        if self.dir[0] == dx and self.dir[1] == dy and pygame.time.get_ticks() - self.last_move_time > 1000 / self.speed:
            self.last_move_time = pygame.time.get_ticks()

            nx, ny = clamp(self.pos[0] + dx, self.pos[1] + dy)
            ddx, ddy = nx-self.pos[0], ny-self.pos[1] # actual movement, if 
            
            if world == 'down':

                #move on land and bridges, hop on boats, enter houses
                if map[ny][nx] in (1,13):
                    self.pos = (nx, ny)
                    move_camera(ddx,ddy)

                if map[ny][nx] == 13:
                    world = 'going up'
                    change_world(world)

            else:

                #move on land and bridges, hop on boats, enter houses
                if map[ny][nx] in (1,2,3,4,7,13):
                    self.pos = (nx, ny)
                    move_camera(ddx,ddy)
                    if map[ny][nx] == 7:
                        self.speed = BOAT_SPEED * abs(wind_power / WIND_MAX_POWER)
                    else:
                        self.speed = PLAYER_SPEED

                    if map[ny][nx] == 13:
                        world = 'going down'
                        change_world(world)

                #if i'm on a boat
                if map[self.pos[1]][self.pos[0]] == 7:
                    self.speed = BOAT_SPEED * abs(wind_power / WIND_MAX_POWER)
                    # navigating
                    if map[ny][nx] == 0 and not (ny == self.pos[1] and nx == self.pos[0]) and (dx, dy) == wind_dir_to_vector(wind_dir):
                        map[self.pos[1]][self.pos[0]] = 0       #leave sea behind
                        self.pos = (nx, ny)                     #move me
                        map[ny][nx] = 7                         #move boat
                        boats[(nx, ny)] = self.dir.copy()       #update boat direction
                        move_camera(ddx,ddy)
            
        self.dir = [dx, dy]
    
    """ +item = put item, -item = remove item : how inventory changes"""
    build_table = {
        +0:     {"dirt": +1},                                   # dig
        +1:     {"dirt": -1},                                   # put ground
        +2:     {"wood": -4, "stone": -4, "dirt": -4},          # build house
        +3:     {"wood": -4, "stone": -12, "dirt": -12},        # build tower
        +4:     {"wood": -2},                                   # build bridge
        -4:     {"wood": +2},                  # remove bridge
        -5:     {"wood": +1},                  # chop tree
        +7:     {"wood": -4},                  # build boat
        -7:     {"wood": +4},                  # remove boat
        -8:     {"stone": +1},                 # mine stone
        #
        # UNDERGROUND
        -10:     {"dirt": -1},                  # block passage with dirt
        -11:     {"dirt": +1},                  # dig corridor
        -12:     {"coal": +1},                  # mine coal
        -13:     {"iron": +1},                  # mine iron
        -14:     {"copper": +1},                  # mine copper
        -15:     {"silver": +1},                  # mine silver
        -16:     {"gold": +1},                  # mine gold
        -17:     {"diamond": +1},                  # mine diamond
        #
        +13:    {"wood": -12}, #build a ladder
    }
    """ removing tile num : what do i put?"""
    replacement_table = {
        -4: 0,      # if i remove brige, put sea
        -5: 1,      # if i remove tree, put ground
        -7: 0,      # if i remove boat, put sea
        -8: 1,      # if i remove stone, put ground
        -1: 1,      # if i dig, put cave tile
        -10: 0,      # if i put dirt, remove cave tile
        -11:  1,                  # dig corridor
        -12:  1,                  # mine carbon
        -13:  1,                  # mine iron
        -14:  1,                  # mine copper
        -15:  1,                  # mine silver
        -16:  1,                  # mine gold
        -17:  1,                  # mine diamond
    }

    def lookup_table(self, action, nx, ny):
        global active_cells
        req = self.build_table[action]
        for resource, amount in req.items():
            if inventory[resource] < -amount:
                print(f"Not enough {resource} to perform action")
                return
        
        # else perform action
        map[ny][nx] = action if action >= 0 else self.replacement_table[action]
        for resource, amount in req.items():
            inventory[resource] += amount
        
        #addictional actions
        if action == 7:
            boats[(nx, ny)] = self.dir.copy()
            print(f"Boat created at {nx}, {ny} facing {self.dir}")
        elif action == -7:
            boats.pop((nx, ny), None)
        elif action == 13:
            undermap[ny][nx] = 13
            uppermap[ny][nx] = 13

        active_cells = active_map()
        update_minimap(nx, ny) if world == 'up' else None

    time_value_table = {
        "coal" : 1,
        "iron": 2,
        "copper": 3,
        "silver": 4,
        "gold": 5,
        "diamond": 10
    }

    def interact(self):
        global TIME_MULT, achivmnts

        nx, ny = clamp(self.pos[0] + self.dir[0], self.pos[1] + self.dir[1])
        bx, by = clamp(self.pos[0] - self.dir[0], self.pos[1] - self.dir[1]) #opposite

        if world in ['going up', 'going down']:
            return
        
        elif world == 'down':
            #if sea (wall) put dirt (dig)
            if map[ny][nx] == 0 and current_item == 5:
                self.lookup_table(-11, nx, ny)
            #if cave tile, you can put dirt on it
            elif map[ny][nx] == 1 and current_item == 1:
                self.lookup_table(-10, nx, ny)
            elif map[ny][nx] in (2,3,4,5,6,7) and current_item == 5:
                self.lookup_table(-10-map[ny][nx], nx, ny)
            #ladder
            elif map[ny][nx] == 1 and current_item == 8:
                self.lookup_table(13, nx, ny)
            elif map[ny][nx] == 99:
                for res in inventory.keys():
                    if inventory[res] > 0 and res not in ['dirt','wood','stone']:
                        achivmnts[res] += inventory[res]
                        print(f"added {inventory[res]} {res}")
                        inventory[res] = 0
                mult = 1
                for res in inventory.keys():
                    if res not in ['dirt','wood','stone']:
                        mult *= self.time_value_table[res] if achivmnts[res] > 0 else 1
                print(f"mult went to {mult}")
                tot = 0
                for res in achivmnts.keys():
                    if achivmnts[res] > 0:
                        tot += self.time_value_table[res] * achivmnts[res]
                TIME_MULT = tot * mult
                print(f"TIME_MULT is now {TIME_MULT}")
            return

        #if sea, put ground or build a bridge or put boat
        if map[ny][nx] == 0 and current_item in (1,4,7):
            self.lookup_table(current_item, nx, ny)

        #if ground: dig, build house or tower
        elif map[ny][nx] == 1 and current_item in (0,2,3):
            self.lookup_table(current_item, nx, ny)

        #if bridge: dig
        elif map[ny][nx] == 4 and current_item == 0:
            self.lookup_table(-4, nx, ny)

        #if tree: chop
        elif map[ny][nx] in (5, 8) and current_item == 5:
            self.lookup_table(-map[ny][nx], nx, ny)
        
        elif map[ny][nx] == 7 and current_item == 0:
            self.lookup_table(-7, nx, ny)
        elif map[by][bx] == 7 and current_item == 6:
            self.lookup_table(-7, bx, by)
        #ladder
        elif map[ny][nx] == 1 and current_item == 8:
            self.lookup_table(13, nx, ny)

        if current_item == 6 and map[by][bx] in (1,4):
            if map[by][bx] == 4:
                self.lookup_table(-4, bx, by)
            else:
                self.lookup_table(0, bx, by)

    def draw(self, surf, x, y):
        pygame.draw.rect(surf, Color('black'), (x - self.w//2, y - self.h + self.offset_y, self.w, self.h))
        pygame.draw.rect(surf, Color('black'), (x - self.w//2 - 1, y - self.h - 1 + self.offset_y, self.w + 2, self.w + 2))
        # Rotate direction vector isometrically
        dirx = self.dir[0] * TILE_WIDTH // 2 - self.dir[1] * TILE_WIDTH // 2
        diry = self.dir[0] * TILE_HEIGHT // 2 + self.dir[1] * TILE_HEIGHT // 2
        pygame.draw.line(debug_surf, Color('red'), (x, y), (x + dirx, y + diry), 1)

BOAT_SPEED = 5
PLAYER_SPEED = 10 #tiles/sec
player = Player(random_center[0], random_center[1]) #to the left of the house
player.dir = [0, +1]  # Initial direction facing down

WIND_MAX_POWER = 10
wind_dir = random.uniform(0, 2*math.pi)
wind_power = random.uniform(0, WIND_MAX_POWER)

achivmnts = {
    "coal": 0,
    "iron": 0,
    "copper": 0,
    "silver": 0,
    "gold": 0,
    "diamond": 0
}

def update_wind():
    global wind_dir, wind_power

    # Apply Brownian motion to wind direction
    # Small random changes, scaled by time
    elapsed = (pygame.time.get_ticks() - last_time) * time_mult / 1000.0  # Convert to seconds
    angle_change = random.uniform(-0.3, 0.3) * elapsed
    wind_dir = (wind_dir + angle_change) % (2 * math.pi)

    # Apply Brownian motion to wind power
    # Power changes more slowly, constrained between 0 and max
    power_change = random.uniform(-1, 1) * elapsed
    wind_power = max(-WIND_MAX_POWER, min(WIND_MAX_POWER, wind_power + power_change))

def wind_dir_to_vector(direction):
    """discretize the vector to dx,dy -> (0,1)"""
    # Convert the continuous angle to discrete 90-degree (pi/2) intervals
    # This gives us 4 possible directions: N, E, S, W
    angle_90deg = round((direction + math.pi/4) / (math.pi / 2)) % 4
    direction_vectors = [
        (0, -1),  # North (0)
        (1, 0),   # East (1)
        (0, 1),   # South (2)
        (-1, 0)   # West (3)
    ]
    dx, dy = direction_vectors[angle_90deg]
    return (dx, dy)

def update_see_radius():
    global see_radius1, see_radius2, mask_surf, world, map, time_mult, active_cells

    if abs(SEE_RADIUS1 - see_radius1) >= 1 or abs(SEE_RADIUS2 - see_radius2) >= 1:
        k = 0.2
        see_radius1 += k * (SEE_RADIUS1 - see_radius1)
        see_radius2 += k * (SEE_RADIUS2 - see_radius2)

        # ellipse mask
        mask_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        mask_surf.fill((0,0,0,0))
        mask_w = see_radius2 * 2
        mask_h = int(mask_w * (TILE_HEIGHT / TILE_WIDTH))
        pygame.draw.ellipse(mask_surf, Color('white'), ((SCREEN_WIDTH - mask_w) // 2, (SCREEN_HEIGHT - mask_h) // 2, mask_w, mask_h))
    
    else:
        see_radius1 = SEE_RADIUS1
        see_radius2 = SEE_RADIUS2
        if world == 'going up':
            map = uppermap
            world = 'up'
            player.offset_y = 0
            active_cells = active_map()
        elif world == 'going down':
            map = undermap
            world = 'down'
            player.offset_y = 0
            time_mult = 1
            active_cells = active_map()

def change_world(world):
    global SEE_RADIUS1, SEE_RADIUS2
    
    # seeing
    SEE_RADIUS2 = (SCREEN_WIDTH * 4/3) // 2 if world in ['going up','up'] else (SCREEN_WIDTH * 3/5) // 2
    SEE_RADIUS1 = SEE_RADIUS2/2


# =======================================================================
# MAIN LOOP
# =======================================================================

def main():
    global map_offset, current_item, active_cells, last_time, time_mult, world

    mouse_last_click = None
    hull_points = None

    running = True
    spawned = False
    
    init_time()

    while running:

        moved_view = False

        # =======================================================================
        # event handling
        # =======================================================================


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    mouse_last_click = None
                    moved_view = True

            elif event.type == pygame.MOUSEWHEEL:
                # event.y is +1 for up, -1 for down
                current_item -= event.y
                current_item = current_item % ITEM_NUM

            if pygame.mouse.get_pressed()[2]:
                mx, my = pygame.mouse.get_pos()
                if mouse_last_click is not None:
                    diff = (mx - mouse_last_click[0], my - mouse_last_click[1])
                    map_offset[0] += diff[0]
                    map_offset[1] += diff[1]

                    pygame.draw.line(debug_surf, Color('yellow'), mouse_last_click, (mx, my), 1)
                    center_screen = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    pygame.draw.line(debug_surf, Color('red'), center_screen, (mx, my), 2)

                mouse_last_click = (mx, my)
                moved_view = True
            
            elif pygame.mouse.get_pressed()[0]:
                player.interact()

        keys = pygame.key.get_pressed()
        if keys:

            if keys[pygame.K_w]:          player.move(0, -1)
            elif keys[pygame.K_s]:        player.move(0, 1)
            elif keys[pygame.K_a]:        player.move(-1, 0)
            elif keys[pygame.K_d]:        player.move(1, 0)
            
            if keys[pygame.K_SPACE]:      move_camera(None,None)

        # =======================================================================
        # OLD CAMERA HANDLING by mouse
        # =======================================================================

        if hull_points:
            if len(hull_points) > 2:
                pygame.draw.polygon(debug_surf, Color('yellow'), hull_points, 1)

            for point in hull_points:
                if in_ellipse(point[0], point[1], see_radius1) < 1:
                    pygame.draw.circle(debug_surf, Color('red'), (point[0], point[1]), 3)
                    center_screen = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    pygame.draw.line(debug_surf, Color('blue'), center_screen, (point[0], point[1]), 1)

                    # find the line parameters
                    dx = point[0] - center_screen[0]
                    dy = point[1] - center_screen[1]
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        # normalize direction vector
                        dir_x = dx / length
                        dir_y = dy / length
                        
                        # project point to ellipse border
                        a = see_radius1
                        b = a * (TILE_HEIGHT / TILE_WIDTH)
                        
                        # parametric line: x = cx + t*dir_x, y = cy + t*dir_y
                        # ellipse equation: ((x-cx)/a)^2 + ((y-cy)/b)^2 = 1
                        # solve for t where line intersects ellipse
                        A = (dir_x/a)**2 + (dir_y/b)**2
                        t = 1 / math.sqrt(A)
                        
                        # calculate projected point on ellipse border
                        projected_x = center_screen[0] + t * dir_x
                        projected_y = center_screen[1] + t * dir_y
                        
                        pygame.draw.circle(debug_surf, Color('green'), (int(projected_x), int(projected_y)), 3)

                        # # Calculate how much we need to move the map to keep the projected point in view
                        # target_x = projected_x - point[0]
                        # target_y = projected_y - point[1]
                        # map_offset[0] += target_x * 0.1
                        # map_offset[1] += target_y * 0.1
                        # moved_view = True

        if moved_view: 
            active_cells = active_map()
            hull_points = convex_map()

        # =======================================================================
        # updating
        # =======================================================================

        update_wind()
        update_time()
        update_weather()
        update_see_radius()

        #spawn at midnight
        if hour == 0 and not spawned:
            spawn_trees(30)
            spawned = True
            print("Spawned trees.")
        elif hour != 0:
            spawned = False

        # =======================================================================
        # drawing
        # =======================================================================

        if world == 'up' or world == 'going down':
            draw_map_surf()
        else:
            draw_underworld()
        draw_info_screen()
        # draw_debug_surf()
        # debug_surf.fill((0, 0, 0, 0))
    
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()