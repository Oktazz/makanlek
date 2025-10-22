# game_full.py
import pygame
from pygame.locals import *
from random import randint, choice
import os

pygame.init()
pygame.mixer.init()

# -------- CONFIG: Virtual resolution (game world) -------
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1280, 720  # design base (16:9)

# Window initial size (starts at virtual res; user can resize)
SCREEN_WIDTH, SCREEN_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Snack Scramble")

# Virtual surface - draw game here, then scale to screen
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# -------- Asset file paths (put your images/sounds here) --------
ASSET_PATH = "resource"
PLAYER_ASSETS = {
    "cat": os.path.join(ASSET_PATH, "images", "kucing.png"),
    "dog": os.path.join(ASSET_PATH, "images", "anjing.png"),
    "bunny": os.path.join(ASSET_PATH, "images" , "rabbit.png"),
    "hamster": os.path.join(ASSET_PATH, "images" , "hamster.png"),
}
GROUND_TILE = os.path.join(ASSET_PATH, "images" ,"ground.png")
# tambahkan path untuk ground level 2 & 3
GROUND_TILE_2 = os.path.join(ASSET_PATH, "images", "ground2.png")
GROUND_TILE_3 = os.path.join(ASSET_PATH, "images", "ground3.png")
SNACK_ASSETS = {
    "fish": os.path.join(ASSET_PATH, "images", "ikan.png"),
    "cheese": os.path.join(ASSET_PATH, "images", "keju.png"),
    "carrot": os.path.join(ASSET_PATH, "images", "wortel.png"),
}
OBSTACLE_ASSETS = {
    "bomb": os.path.join(ASSET_PATH, "images", "bom.png"),
    "rock": os.path.join(ASSET_PATH, "images", "batu.png"),
    "dog": os.path.join(ASSET_PATH, "images", "tai.png"),
}
BGM_FILE = os.path.join(ASSET_PATH, "sounds", "backsound.mp3")
SFX_STEP = os.path.join(ASSET_PATH, "sounds", "footstep.mp3")
SFX_EAT = os.path.join(ASSET_PATH, "sounds", "eat.wav")
SFX_HIT = os.path.join(ASSET_PATH, "sounds", "hit.mp3")
SFX_GAMEOVER = os.path.join(ASSET_PATH, "sounds", "game_over.wav")
SFX_VICTORY = os.path.join(ASSET_PATH, "sounds", "victory.mp3")
HEART_ASSET = os.path.join(ASSET_PATH, "images", "love.png")
BGM_FILE_2 = os.path.join(ASSET_PATH, "sounds", "backsound_fast.mp3")
BGM_FILE_3 = os.path.join(ASSET_PATH, "sounds", "backsound_faster.mp3")
SKY_IMG_2 = os.path.join(ASSET_PATH, "images", "sky_2.png")
SKY_IMG_3 = os.path.join(ASSET_PATH, "images", "sky_3.png")
SFX_POWERUP = os.path.join(ASSET_PATH, "sounds", "power.wav")
SFX_LEVELUP = os.path.join(ASSET_PATH, "sounds" "levelup.wav")
FRONT_OVERLAY = os.path.join(ASSET_PATH, "images", "bgtampilan.png")  # tambahkan ini
VICTORY_BG = os.path.join(ASSET_PATH, "images", "bg.win.png")     # <- new: victory background
GAMEOVER_BG = os.path.join(ASSET_PATH, "images", "bg.lose.png")  # <- new: gameover background


# -------- Recommended asset sizes (in pixels, relative to VIRTUAL) --------
# - player: 80x80 (good default). For HD art you can use 160x160 and scale down.
# - ground tile: width 128, height same as ground_height (see below), recommended 128x100
# - snack: 60x60
# - obstacle: 60x60
# - menu thumbnails: 120x120
#
# The code will scale loaded images to these sizes automatically.

# -------- Game settings --------
FPS = 60
GROUND_HEIGHT = 120               # height of ground in virtual coords
PLAYER_W, PLAYER_H = 80, 80      # default player sprite size
SNACK_W, SNACK_H = 60, 60
OBST_W, OBST_H = 60, 60
MAX_LIVES = 9
STEP_SOUND_INTERVAL = 12         # frames between step sfx while walking

# Character skills
CHARACTER_STATS = {
    "cat":     {"speed": 10, "lives": MAX_LIVES,   "points_per_snack": 1, "shield_duration": 5, "description": "Moves faster"},
    "dog":     {"speed": 8,  "lives": MAX_LIVES + 2, "points_per_snack": 1, "shield_duration": 5, "description": "Starts with more lives"},
    "bunny":   {"speed": 8,  "lives": MAX_LIVES,   "points_per_snack": 2, "shield_duration": 5, "description": "Gets more points from snacks"},
    "hamster": {"speed": 7,  "lives": MAX_LIVES,   "points_per_snack": 1, "shield_duration": 8, "description": "Shields last longer"}
}

# -------- Utilities: safe image/sound loaders with fallback --------
def load_image(path, size=None, fallback_color=None):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except Exception:
            pass
    # fallback: colored surface
    surf = pygame.Surface(size if size else (32,32), pygame.SRCALPHA)
    color = fallback_color if fallback_color else (200,200,200)
    surf.fill(color)
    return surf

def load_sound(path):
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    # fallback: create silent Sound by generating 1-silence (can't easily create programmatically in pygame),
    # so return None and caller must check
    return None

# -------- Load default assets (with recommended sizes) --------
player_images = {}
for name, path in PLAYER_ASSETS.items():
    player_images[name] = load_image(path, (PLAYER_W, PLAYER_H), fallback_color=(180,180,180))

ground_tile_img = load_image(GROUND_TILE, (1080, GROUND_HEIGHT), fallback_color=(100,50,20))
# load additional ground variants
ground_tile_img_2 = load_image(GROUND_TILE_2, (1080, GROUND_HEIGHT), fallback_color=(110,60,30))
ground_tile_img_3 = load_image(GROUND_TILE_3, (1080, GROUND_HEIGHT), fallback_color=(80,40,20))

# current ground used for drawing (will change with score)
current_ground_img = ground_tile_img

snack_images = {}
for name, path in SNACK_ASSETS.items():
    snack_images[name] = load_image(path, (SNACK_W, SNACK_H), fallback_color=(0,200,0))

obstacle_images = {}
for name, path in OBSTACLE_ASSETS.items():
    obstacle_images[name] = load_image(path, (OBST_W, OBST_H), fallback_color=(200,0,0))

heart_img = load_image(HEART_ASSET, (30, 30), fallback_color=(255,0,0))
sky_img = load_image(os.path.join(ASSET_PATH, "images", "sky.png"), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# Level-specific assets
sky_img_2 = load_image(SKY_IMG_2, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
if not os.path.exists(SKY_IMG_2): # If file doesn't exist, create tinted version
    sky_img_2 = sky_img.copy()
    sky_img_2.fill((255, 200, 200), special_flags=pygame.BLEND_RGB_ADD)

sky_img_3 = load_image(SKY_IMG_3, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
if not os.path.exists(SKY_IMG_3): # If file doesn't exist, create tinted version
    sky_img_3 = sky_img.copy()
    sky_img_3.fill((255, 150, 150), special_flags=pygame.BLEND_RGB_ADD)

# muat overlay foreground (gunakan fallback debug jika file tidak ada)
if os.path.exists(FRONT_OVERLAY):
    try:
        front_overlay_img = pygame.image.load(FRONT_OVERLAY).convert_alpha()
        # only scale if sizes differ to avoid unnecessary smoothing/blur
        if front_overlay_img.get_size() != (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            front_overlay_img = pygame.transform.scale(front_overlay_img, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        # keep per-pixel alpha (do not call set_alpha unless you want uniform transparency)
        print("Overlay loaded:", FRONT_OVERLAY)
    except Exception as e:
        print("Error loading overlay:", e)
        front_overlay_img = None
else:
    print("Overlay file NOT found:", FRONT_OVERLAY)
    # buat overlay debug semi-transparan agar terlihat kalau memang di-blit
    front_overlay_img = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    front_overlay_img.fill((255, 0, 0, 120))  # merah semi-transparan debug

golden_food_img = load_image(os.path.join(ASSET_PATH, "images", "apple.png"), (SNACK_W, SNACK_H))
shield_img = load_image(os.path.join(ASSET_PATH, "images", "perisai.png"), (SNACK_W, SNACK_H))
youwin_img = load_image(os.path.join(ASSET_PATH, "images", "bg.win.png"), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# load victory background (falls back to solid/dark surface if not found)
victory_bg_img = load_image(VICTORY_BG, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT), fallback_color=(30, 30, 60))
# load gameover background (falls back to dark/red surface if not found)
gameover_bg_img = load_image(GAMEOVER_BG, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT), fallback_color=(40, 10, 10))

# sounds
bgm = BGM_FILE if os.path.exists(BGM_FILE) else None
sfx_step = load_sound(SFX_STEP)
if sfx_step:
    sfx_step.set_volume(0.15)
sfx_eat = load_sound(SFX_EAT)
sfx_hit = load_sound(SFX_HIT)
sfx_gameover = load_sound(SFX_GAMEOVER)
sfx_victory = load_sound(SFX_VICTORY)
sfx_powerup = load_sound(SFX_POWERUP)
sfx_levelup = load_sound(SFX_LEVELUP)

# play bgm loop when menu starts (we will manage play/pause)
if bgm:
    try:
        pygame.mixer.music.load(bgm)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

# -------- Game state variables --------
clock = pygame.time.Clock()
running = True
fullscreen = False

# Gameplay variables
ground_rect = pygame.Rect(0, VIRTUAL_HEIGHT - GROUND_HEIGHT, VIRTUAL_WIDTH, GROUND_HEIGHT)
game_level = 0
game_tempo = 1.0
current_sky_img = sky_img
player_speed = CHARACTER_STATS["cat"]["speed"] # Default to cat

# player default
selected_char_key = "cat"
player_idle_right = player_images[selected_char_key]
player_idle_left = pygame.transform.flip(player_idle_right, True, False)
# simple walk frame: slightly squashed for subtle movement
player_walk_right = pygame.transform.scale(player_idle_right, (PLAYER_W, int(PLAYER_H*0.9)))
player_walk_left = pygame.transform.flip(player_walk_right, True, False)

walk_frames_r = [player_idle_right, player_walk_right]
walk_frames_l = [player_idle_left, player_walk_left]
player_image = player_idle_right
facing_right = True
is_walking = False
player_pos = [VIRTUAL_WIDTH//2, ground_rect.top - PLAYER_H]

# step sound timer
step_timer = 0

# Spawned items
makanans = []
B_makanans = []
makanan_timer = 0
B_makanan_timer = 0
golden_foods = []
shields = []
invincible = False
invincible_timer = 0
golden_food_timer = 0
shields_timer = 0

# lives
lives = MAX_LIVES

# Achievement variables
achievement_timer = 0
show_achievement = False
last_achievement_score = 0

# --- UI Theme Colors ---
COLOR_BG = (252, 242, 244) # Light pink
# ubah tombol jadi kuning/keemasan
COLOR_ACCENT = (255, 223, 0)       # bright gold
COLOR_ACCENT_DARK = (212, 175, 55) # darker gold (border/highlight)
COLOR_TEXT = (94, 74, 74) # Dark brown
COLOR_TITLE = (229, 115, 115) # Title pink

# --- UI Fonts ---
try:
    # Try to use a cuter font if available
    TITLE_FONT_NAME = "comicsansms"
    pygame.font.SysFont(TITLE_FONT_NAME, 20) # test if font exists
except:
    TITLE_FONT_NAME = "arial"

FONT = pygame.font.SysFont("arial", 32)
ACHIEVEMENT_FONT = pygame.font.SysFont("arial", 48, bold=True)
TITLE_FONT = pygame.font.SysFont(TITLE_FONT_NAME, 80, bold=True)

# try load a local pixel font (put a .ttf in resource/fonts/pixel.ttf for best results)
PIXEL_FONT_PATH = os.path.join(ASSET_PATH, "fonts", "pixel.ttf")
if os.path.exists(PIXEL_FONT_PATH):
    try:
        PIXEL_FONT = pygame.font.Font(PIXEL_FONT_PATH, 14)  # size will be scaled integer later
        print("Loaded pixel font:", PIXEL_FONT_PATH)
    except Exception:
        PIXEL_FONT = None
else:
    PIXEL_FONT = None

# helper: render teks pixel-art (render kecil lalu scale integer, lalu tint)
def render_pixel_text(text, color=(229,115,115), outline_color=(153, 102, 51), outline_thickness=2, base_size=12, pixel_scale=4, bold=True):
    """
    Render pixel-style text by:
    - rendering at a small base_size without antialiasing,
    - integer-scale the surface (pygame.transform.scale) to keep hard edges,
    - tint the white pixels to color and build an outline by blitting offset masks.
    """
    # choose font: prefer loaded pixel font for sharpness
    if PIXEL_FONT:
        # create a font object at requested base_size (Font handles TTF sizes)
        font = pygame.font.Font(PIXEL_FONT_PATH, base_size)
    else:
        font = pygame.font.SysFont(TITLE_FONT_NAME, base_size, bold=bold)

    # render without antialias for crisper pixel blocks
    surf = font.render(text, False, (255,255,255)).convert_alpha()
    w, h = surf.get_size()
    if w == 0 or h == 0:
        return pygame.Surface((1,1), pygame.SRCALPHA)

    # ensure pixel_scale is integer >=1
    ps = max(1, int(pixel_scale))
    surf = pygame.transform.scale(surf, (w * ps, h * ps))  # nearest-neighbor integer scaling

    # tint main text (use full alpha)
    colored = surf.copy()
    colored.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)

    # outline: thickness scaled with pixel_scale so it's visible
    ot = max(1, int(outline_thickness * max(1, ps // 2)))

    out_w = surf.get_width() + ot * 2
    out_h = surf.get_height() + ot * 2
    outline_surf = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

    # create outline mask once and blit around offsets
    outline_mask = surf.copy()
    outline_mask.fill(outline_color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    for dx in range(-ot, ot + 1):
        for dy in range(-ot, ot + 1):
            if dx == 0 and dy == 0:
                continue
            outline_surf.blit(outline_mask, (dx + ot, dy + ot))

    # main text on top
    outline_surf.blit(colored, (ot, ot))
    return outline_surf

# NEW helper: render label pixel-art yang menyesuaikan skala agar muat di tombol
def render_pixel_label_fit(text, fg_color, outline_color, max_w, max_h, base_size=10, bold=False):
    """
    Render a pixel label that fits inside max_w x max_h by choosing an integer scale factor.
    Uses a small base_size so integer scale produces crisp blocks.
    """
    # use test font to get base glyph size
    if PIXEL_FONT:
        test_font = pygame.font.Font(PIXEL_FONT_PATH, base_size)
    else:
        test_font = pygame.font.SysFont(TITLE_FONT_NAME, base_size, bold=bold)
    test_s = test_font.render(text, False, (255,255,255)).convert_alpha()
    tw, th = test_s.get_size()
    if tw <= 0 or th <= 0:
        tw, th = 1, 1
    # compute integer scale factor that fits both dimensions
    scale = max(1, min(max_w // tw, max_h // th))
    # safety cap to avoid enormous scale
    scale = max(1, min(scale, 12))
    # produce final pixel text with integer scale
    return render_pixel_text(text, color=fg_color, outline_color=outline_color, outline_thickness=1, base_size=base_size, pixel_scale=scale, bold=bold)

# menu state: "main", "character", "assets", "playing", "pause", "gameover", "victory"
state = "main"

# For menu selections
available_chars = list(player_images.keys())
selected_char_index = available_chars.index(selected_char_key)

# selected assets
available_snacks = list(snack_images.keys())
available_obstacles = list(obstacle_images.keys())
selected_snack_key = available_snacks[0]
selected_obstacle_key = available_obstacles[0]

# NEW: Difficulty / Level menu
DIFFICULTIES = ["Easy", "Normal", "Medium", "Hard"]
DIFFICULTY_LIVES = {"Easy": 9, "Normal": 5, "Medium": 3, "Hard": 1}
selected_difficulty = "Normal"  # default

# helper to reset gameplay
def reset_game():
    global makanans, B_makanans, score, makanan_timer, B_makanan_timer, lives, player_pos, achievement_timer, show_achievement, last_achievement_score, game_level, game_tempo, current_sky_img, player_speed, invincible, invincible_timer, golden_foods, shields
    makanans = []
    B_makanans = []
    golden_foods = []
    shields = []
    score = 0
    makanan_timer = 0
    B_makanan_timer = 0
    
    # Apply character stats
    stats = CHARACTER_STATS[selected_char_key]
    # base lives from character (kept for fallback) then override with difficulty
    lives = stats["lives"]
    # override start lives according to chosen difficulty
    lives = DIFFICULTY_LIVES.get(selected_difficulty, lives)
    player_speed = stats["speed"]

    player_pos = [VIRTUAL_WIDTH//2, ground_rect.top - PLAYER_H]
    achievement_timer = 0
    show_achievement = False
    last_achievement_score = 0
    
    # Reset level and tempo
    game_level = 0
    game_tempo = 1.0
    current_sky_img = sky_img
    invincible = False
    invincible_timer = 0

    # Reset BGM to default
    if bgm:
        try:
            pygame.mixer.music.load(bgm)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

# -------- UI helpers --------
def draw_text(surface, text, pos, font=FONT, color=(255,255,255), outline_color=None, outline_width=1):
    x, y = pos
    # 1. render the outline
    if outline_color:
        outline_img = font.render(text, True, outline_color)
        # blit in 8 directions
        surface.blit(outline_img, (x-outline_width, y-outline_width))
        surface.blit(outline_img, (x,               y-outline_width))
        surface.blit(outline_img, (x+outline_width, y-outline_width))
        surface.blit(outline_img, (x-outline_width, y))
        surface.blit(outline_img, (x+outline_width, y))
        surface.blit(outline_img, (x-outline_width, y+outline_width))
        surface.blit(outline_img, (x,               y+outline_width))
        surface.blit(outline_img, (x+outline_width, y+outline_width))
    
    # 2. render the main text on top
    img = font.render(text, True, color)
    surface.blit(img, pos)

def draw_button(surface, rect, text, font=FONT, bg=None, fg=COLOR_TEXT):
    """
    Draw a rounded button and place a pixel-art label centered.
    - bg: background color tuple. If None, use GOLD accent.
    - fg: label color (default dark brown).
    """
    if bg is None:
        bg = COLOR_ACCENT

    # button background
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    # subtle 1px inner border for depth (avoid thick smooth lines)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surface, COLOR_ACCENT_DARK, inner, 1, border_radius=6)

    # render pixel label that fits inside rect
    label_surf = render_pixel_label_fit(text, fg_color=fg, outline_color=(94, 74, 74), max_w=rect.width-12, max_h=rect.height-8, base_size=10, bold=True)
    lx = rect.x + (rect.width - label_surf.get_width()) // 2
    ly = rect.y + (rect.height - label_surf.get_height()) // 2
    surface.blit(label_surf, (lx, ly))

# -------- Main loop --------
frame_count = 0
while running:
    dt = clock.tick(FPS)
    frame_count += 1
    current_time = pygame.time.get_ticks()

    # handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_F11:  # fullscreen toggle
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    SCREEN_WIDTH, SCREEN_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            # universal ESC behavior
            if event.key == K_ESCAPE:
                if state == "playing":
                    state = "pause"
                elif state == "pause":
                    state = "playing"
                elif state in ("main", "character", "assets", "gameover"):
                    # in menus ESC -> quit
                    running = False

        if event.type == VIDEORESIZE and not fullscreen:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.size
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # convert mouse to virtual coords (inverse of final scale)
            # compute scale used currently
            scale_w = SCREEN_WIDTH / VIRTUAL_WIDTH
            scale_h = SCREEN_HEIGHT / VIRTUAL_HEIGHT
            scale = min(scale_w, scale_h)
            new_w = int(VIRTUAL_WIDTH * scale)
            new_h = int(VIRTUAL_HEIGHT * scale)
            x_pos = (SCREEN_WIDTH - new_w) // 2
            y_pos = (SCREEN_HEIGHT - new_h) // 2
            if not (x_pos <= mx <= x_pos + new_w and y_pos <= my <= y_pos + new_h):
                # clicks outside the game area don't count
                continue
            # map to virtual coords
            vx = int((mx - x_pos) / scale)
            vy = int((my - y_pos) / scale)

            # handle clicks in menu screens
            if state == "playing":
                pause_btn_rect = pygame.Rect(20, 60, 100, 40)
                if pause_btn_rect.collidepoint(vx, vy):
                    state = "pause"
            if state == "main":
                # simple button layout positions (virtual coords)
                start_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
                char_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
                asset_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
                level_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 520, 300, 60)
                quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 600, 300, 60)
                if start_btn.collidepoint(vx, vy):
                    reset_game()
                    if bgm:
                        # unpause if it was paused (e.g. after gameover)
                        pygame.mixer.music.unpause()
                    state = "playing"
                elif char_btn.collidepoint(vx, vy):
                    state = "character"
                elif asset_btn.collidepoint(vx, vy):
                    state = "assets"
                elif level_btn.collidepoint(vx, vy):
                    state = "level"
                elif quit_btn.collidepoint(vx, vy):
                    running = False

            elif state == "character":
                # show thumbnails; allow clicking thumbnails to select char
                # thumbnails area start
                start_x = 180
                start_y = 220
                thumb_w = 140
                thumb_h = 140
                gap = 40
                for i, key in enumerate(available_chars):
                    rx = start_x + i*(thumb_w + gap)
                    r = pygame.Rect(rx, start_y, thumb_w, thumb_h)
                    if r.collidepoint(vx, vy):
                        selected_char_index = i
                        selected_char_key = available_chars[selected_char_index]
                        # load chosen images
                        player_idle_right = player_images[selected_char_key]
                        player_idle_left = pygame.transform.flip(player_idle_right, True, False)
                        player_walk_right = pygame.transform.scale(player_idle_right, (PLAYER_W, int(PLAYER_H*0.9)))
                        player_walk_left = pygame.transform.flip(player_walk_right, True, False)
                        walk_frames_r = [player_idle_right, player_walk_right]
                        walk_frames_l = [player_idle_left, player_walk_left]
                        player_image = player_idle_right
                # Back button region
                back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 520, 200, 50)
                if back_btn.collidepoint(vx, vy):
                    state = "main"

            elif state == "assets":
                # Asset selection logic
                thumb_w, thumb_h, gap = 120, 120, 25
                
                # Snack selection
                snack_start_x = (VIRTUAL_WIDTH - (len(available_snacks) * (thumb_w + gap) - gap)) // 2
                snack_y = 250
                for i, key in enumerate(available_snacks):
                    r = pygame.Rect(snack_start_x + i * (thumb_w + gap), snack_y, thumb_w, thumb_h)
                    if r.collidepoint(vx, vy):
                        selected_snack_key = key

                # Obstacle selection
                obst_start_x = (VIRTUAL_WIDTH - (len(available_obstacles) * (thumb_w + gap) - gap)) // 2
                obst_y = 450
                for i, key in enumerate(available_obstacles):
                    r = pygame.Rect(obst_start_x + i * (thumb_w + gap), obst_y, thumb_w, thumb_h)
                    if r.collidepoint(vx, vy):
                        selected_obstacle_key = key

                # Back button
                back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 620, 200, 50)
                if back_btn.collidepoint(vx, vy):
                    state = "main"

            elif state == "pause":
                # pause menu rects
                resume_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
                mainmenu_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
                quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
                if resume_btn.collidepoint(vx, vy):
                    state = "playing"
                elif mainmenu_btn.collidepoint(vx, vy):
                    state = "main"
                elif quit_btn.collidepoint(vx, vy):
                    running = False
            
            elif state == "level":
                # level option buttons (same layout as draw)
                opt_w, opt_h = 360, 70
                start_y = 200
                gap = 90
                clicked_any = False
                for i, d in enumerate(DIFFICULTIES):
                    r = pygame.Rect(VIRTUAL_WIDTH//2 - opt_w//2, start_y + i*gap, opt_w, opt_h)
                    if r.collidepoint(vx, vy):
                        # choose difficulty and go back to main menu
                        selected_difficulty = d
                        state = "main"
                        clicked_any = True
                        break
                if clicked_any:
                    # nothing else to handle
                    pass
                else:
                    back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, start_y + len(DIFFICULTIES)*gap + 10, 200, 50)
                    if back_btn.collidepoint(vx, vy):
                        state = "main"

            elif state == "gameover" or state == "victory":
                main_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, VIRTUAL_HEIGHT - 150, 300, 60)
                if main_btn.collidepoint(vx, vy):
                    state = "main"

    # ---------- State updates ----------
    if state == "playing":

        # Level progression check
        if score >= 150 and game_level < 3:
            state = "victory"
            if bgm:
                pygame.mixer.music.pause()
            if sfx_victory:
                sfx_victory.play()
            # Stop processing this frame as "playing"
            continue
        elif score >= 100 and game_level < 2:
            game_level = 2
            game_tempo = 1.5
            current_sky_img = sky_img_3
            # gunakan ground3 mulai score 100
            current_ground_img = ground_tile_img_3
            if sfx_levelup: sfx_levelup.play()
            if os.path.exists(BGM_FILE_3):
                try:
                    pygame.mixer.music.load(BGM_FILE_3)
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(-1)
                except Exception: pass
        elif score >= 50 and game_level < 1:
            game_level = 1
            game_tempo = 1.2
            current_sky_img = sky_img_2
            # gunakan ground2 mulai score 50
            current_ground_img = ground_tile_img_2
            if sfx_levelup: sfx_levelup.play()
            if os.path.exists(BGM_FILE_2):
                try:
                    pygame.mixer.music.load(BGM_FILE_2)
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(-1)
                except Exception: pass

        virtual_surface.blit(current_sky_img, (0, 0))

        # draw ground tiles across width
        # for x in range(0, VIRTUAL_WIDTH, ground_tile_img.get_width()):
        #    virtual_surface.blit(ground_tile_img, (x, VIRTUAL_HEIGHT - GROUND_HEIGHT))
        # gunakan current_ground_img (ground default / ground2 / ground3)
        for x in range(0, VIRTUAL_WIDTH, current_ground_img.get_width()):
            virtual_surface.blit(current_ground_img, (x, VIRTUAL_HEIGHT - GROUND_HEIGHT))

        # spawn logic
        jumlah_makanan = 1 + (score // 5) # Reduced
        if len(makanans) < jumlah_makanan:
            makanan_timer += 1
            if makanan_timer > 45: # Slightly slower spawn
                x = randint(50, VIRTUAL_WIDTH-50)
                rect = pygame.Rect(x, 0, SNACK_W, SNACK_H)
                makanans.append({"rect": rect, "speed": 6})
                makanan_timer = 0

        jumlah_B_makanan = 1 + (score // 7) # Reduced
        if len(B_makanans) < jumlah_B_makanan:
            B_makanan_timer += 1
            if B_makanan_timer > 60: # Slightly slower spawn
                x = randint(50, VIRTUAL_WIDTH-50)
                rect = pygame.Rect(x, 0, OBST_W, OBST_H)
                B_makanans.append({"rect": rect, "speed": randint(4, 8)})
                B_makanan_timer = 0

        jumlah_golden_food = 1
        if len(golden_foods) < jumlah_golden_food:
            golden_food_timer += 1
            if golden_food_timer > 600: # every 10 seconds
                x = randint(50, VIRTUAL_WIDTH-50)
                rect = pygame.Rect(x, 0, SNACK_W, SNACK_H)
                golden_foods.append({"rect": rect, "speed": 5})
                golden_food_timer = 0

        jumlah_shields = 1
        if len(shields) < jumlah_shields:
            shields_timer += 1
            if shields_timer > 900: # every 15 seconds
                x = randint(50, VIRTUAL_WIDTH-50)
                rect = pygame.Rect(x, 0, SNACK_W, SNACK_H)
                shields.append({"rect": rect, "speed": 5})
                shields_timer = 0

        # items move
        for makanan in makanans[:]:
            makanan["rect"].top += makanan["speed"]
            if makanan["rect"].top > VIRTUAL_HEIGHT:
                makanans.remove(makanan)
            # collision with player rect
            player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_W, PLAYER_H)
            if player_rect.colliderect(makanan["rect"]):
                score += 1
                if sfx_eat:
                    sfx_eat.play()
                makanans.remove(makanan)
                # Achievement check
                if score > 0 and score % 25 == 0 and score != last_achievement_score:
                    show_achievement = True
                    achievement_timer = current_time
                    last_achievement_score = score

        for obst in B_makanans[:]:
            obst["rect"].top += obst["speed"]
            if obst["rect"].top > VIRTUAL_HEIGHT:
                B_makanans.remove(obst)
            player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_W, PLAYER_H)
            if player_rect.colliderect(obst["rect"]):
                B_makanans.remove(obst)
                if not invincible:
                    lives -= 1
                    if sfx_hit:
                        sfx_hit.play()
                    if lives <= 0:
                        if bgm:
                            pygame.mixer.music.pause()
                        if sfx_gameover:
                            sfx_gameover.play()
                        state = "gameover"

        for food in golden_foods[:]:
            food["rect"].top += food["speed"]
            if food["rect"].top > VIRTUAL_HEIGHT:
                golden_foods.remove(food)
            player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_W, PLAYER_H)
            if player_rect.colliderect(food["rect"]):
                score += 10
                if sfx_eat:
                    sfx_eat.play()
                golden_foods.remove(food)
                #achiaveement check
                if score > 0 and score % 25 == 0 and score != last_achievement_score:
                    show_achievement = True
                    achievement_timer = current_time
                    last_achievement_score = score

        for sh in shields[:]:
            sh["rect"].top += sh["speed"]
            if sh["rect"].top > VIRTUAL_HEIGHT:
                shields.remove(sh)
            player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_W, PLAYER_H)
            if player_rect.colliderect(sh["rect"]):
                invincible = True
                invincible_timer = 5 * FPS  # 5 seconds of invincibility
                sfx_powerup.play()
                shields.remove(sh)

        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False

        # Controls - keyboard both A/D and arrows
        keys = pygame.key.get_pressed()
        is_walking = False
        moved = False
        if keys[K_a] or keys[K_LEFT]:
            player_pos[0] -= player_speed
            facing_right = False
            is_walking = True
            moved = True
        if keys[K_d] or keys[K_RIGHT]:
            player_pos[0] += player_speed
            facing_right = True
            is_walking = True
            moved = True

        # clamp player to world
        player_pos[0] = max(0, min(player_pos[0], VIRTUAL_WIDTH - PLAYER_W))
        player_pos[1] = ground_rect.top - PLAYER_H

        # animation frame logic
        if is_walking:
            step_timer += 1
            if step_timer >= STEP_SOUND_INTERVAL:
                step_timer = 0
                if sfx_step:
                    sfx_step.play()
            # alternate frames every 10 frames
            if frame_count % 10 == 0:
                # swap between idle and walk for simplicity
                if facing_right:
                    walk_frames_r = [player_idle_right, player_walk_right]
                    player_image = walk_frames_r[(frame_count//10) % len(walk_frames_r)]
                else:
                    walk_frames_l = [player_idle_left, player_walk_left]
                    player_image = walk_frames_l[(frame_count//10) % len(walk_frames_l)]
        else:
            # idle
            player_image = player_idle_right if facing_right else player_idle_left

        # draw items
        selected_snack_img = snack_images[selected_snack_key]
        selected_obst_img = obstacle_images[selected_obstacle_key]
        for makanan in makanans:
            # draw snack image centered on rect
            virtual_surface.blit(selected_snack_img, (makanan["rect"].x, makanan["rect"].y))
        for obst in B_makanans:
            virtual_surface.blit(selected_obst_img, (obst["rect"].x, obst["rect"].y))
        for food in golden_foods:
            virtual_surface.blit(golden_food_img, (food["rect"].x, food["rect"].y))
        for sh in shields:
            virtual_surface.blit(shield_img, (sh["rect"].x, sh["rect"].y))

        # draw player
        if not (invincible and (frame_count // 6) % 2 == 0):
            virtual_surface.blit(player_image, (player_pos[0], player_pos[1]))

        # HUD: score and lives
        draw_text(virtual_surface, f"Score: {score}", (20, 20), FONT, color=(255,255,255), outline_color=(0,0,0), outline_width=2)
        # Draw lives
        for i in range(lives):
            virtual_surface.blit(heart_img, (VIRTUAL_WIDTH - 40 - (i * 35), 15))

        # Tombol Pause di pojok kiri atas
        pause_btn_rect = pygame.Rect(20, 60, 100, 40)
        # draw clearer pause button using regular antialiased font for in-game HUD
        pygame.draw.rect(virtual_surface, (80,80,120), pause_btn_rect, border_radius=8)
        pygame.draw.rect(virtual_surface, COLOR_ACCENT_DARK, pause_btn_rect.inflate(-6, -6), 1, border_radius=6)
        pause_label = FONT.render("Pause", True, (255, 255, 255))
        lx = pause_btn_rect.x + (pause_btn_rect.width - pause_label.get_width()) // 2
        ly = pause_btn_rect.y + (pause_btn_rect.height - pause_label.get_height()) // 2
        virtual_surface.blit(pause_label, (lx, ly))


        # Achievement display
        if show_achievement:
            if current_time - achievement_timer < 3000: # Show for 3 seconds
                ach_text = f"Achievement! {last_achievement_score} Points!"
                text_img = ACHIEVEMENT_FONT.render(ach_text, True, (255, 215, 0))
                text_rect = text_img.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 4))
                # Simple background for text
                bg_rect = text_rect.inflate(20, 20)
                pygame.draw.rect(virtual_surface, (60, 60, 80), bg_rect, border_radius=10)
                virtual_surface.blit(text_img, text_rect)
            else:
                show_achievement = False

    else:
        # non-playing screens: draw backgrounds and UI
        virtual_surface.fill(COLOR_BG)  # light pink BG for menus

        if state == "main":
            # blit overlay dulu sebagai dekorasi latar agar judul/menu tetap tajam
            if front_overlay_img:
                virtual_surface.blit(front_overlay_img, (0, 0))

            # title (pixel-art)
            title_img = render_pixel_text("Snack Scramble", color=(229,115,115), base_size=26, pixel_scale=5, bold=True)
            title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 150))
            virtual_surface.blit(title_img, title_rect)
            # buttons (add Level button)
            start_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
            char_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
            asset_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
            level_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 520, 300, 60)
            quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 600, 300, 60)
            draw_button(virtual_surface, start_btn, "Start Game", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            draw_button(virtual_surface, char_btn, "Character Select", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            draw_button(virtual_surface, asset_btn, "Asset Select", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            # show current selected difficulty on the Level button
            level_label = f"Level: {selected_difficulty}"
            draw_button(virtual_surface, level_btn, level_label, FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            draw_button(virtual_surface, quit_btn, "Quit", FONT, bg=COLOR_ACCENT_DARK, fg=COLOR_TEXT)

        elif state == "character":
            title_img = render_pixel_text("Choose Character", color=(229,115,115), base_size=22, pixel_scale=4, bold=True)
            title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 150))
            virtual_surface.blit(title_img, title_rect)
            # thumbnails
            start_x = 180
            start_y = 220
            thumb_w = 140
            thumb_h = 140
            gap = 40
            for i, key in enumerate(available_chars):
                rx = start_x + i*(thumb_w + gap)
                r = pygame.Rect(rx, start_y, thumb_w, thumb_h)
                pygame.draw.rect(virtual_surface, (255,255,255), r, border_radius=8)
                # draw thumbnail scaled
                thumb_img = pygame.transform.smoothscale(player_images[key], (thumb_w-20, thumb_h-20))
                virtual_surface.blit(thumb_img, (rx+10, start_y+10))
                draw_text(virtual_surface, key.capitalize(), (rx+10, start_y+thumb_h+8), FONT, COLOR_TEXT)
                # highlight selected
                if i == selected_char_index:
                    pygame.draw.rect(virtual_surface, COLOR_ACCENT_DARK, r, 4, border_radius=8)
            # Back button
            back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 520, 200, 50)
            draw_button(virtual_surface, back_btn, "Back", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)

        elif state == "assets":
            title_img = render_pixel_text("Asset Select", color=(229,115,115), base_size=22, pixel_scale=4, bold=True)
            title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 120))
            virtual_surface.blit(title_img, title_rect)
            
            thumb_w, thumb_h, gap = 120, 120, 25

            # Draw Snack choices
            draw_text(virtual_surface, "Choose your Snack", (VIRTUAL_WIDTH//2 - 150, 180), FONT, COLOR_TEXT)
            snack_start_x = (VIRTUAL_WIDTH - (len(available_snacks) * (thumb_w + gap) - gap)) // 2
            snack_y = 250
            for i, key in enumerate(available_snacks):
                r = pygame.Rect(snack_start_x + i * (thumb_w + gap), snack_y, thumb_w, thumb_h)
                pygame.draw.rect(virtual_surface, (255,255,255), r, border_radius=8)
                thumb_img = pygame.transform.smoothscale(snack_images[key], (thumb_w-20, thumb_h-20))
                virtual_surface.blit(thumb_img, (r.x+10, r.y+10))
                if key == selected_snack_key:
                    pygame.draw.rect(virtual_surface, COLOR_ACCENT_DARK, r, 4, border_radius=8)

            # Draw Obstacle choices
            draw_text(virtual_surface, "Choose your Obstacle", (VIRTUAL_WIDTH//2 - 160, 380), FONT, COLOR_TEXT)
            obst_start_x = (VIRTUAL_WIDTH - (len(available_obstacles) * (thumb_w + gap) - gap)) // 2
            obst_y = 450
            for i, key in enumerate(available_obstacles):
                r = pygame.Rect(obst_start_x + i * (thumb_w + gap), obst_y, thumb_w, thumb_h)
                pygame.draw.rect(virtual_surface, (255,255,255), r, border_radius=8)
                thumb_img = pygame.transform.smoothscale(obstacle_images[key], (thumb_w-20, thumb_h-20))
                virtual_surface.blit(thumb_img, (r.x+10, r.y+10))
                if key == selected_obstacle_key:
                    pygame.draw.rect(virtual_surface, COLOR_ACCENT_DARK, r, 4, border_radius=8)

            # Back button
            back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 620, 200, 50)
            draw_button(virtual_surface, back_btn, "Back", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)

        elif state == "pause":
            # create a semi-transparent overlay
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            virtual_surface.blit(overlay, (0,0))

            title_img = render_pixel_text("Paused", color=(255,255,255), base_size=22, pixel_scale=4, bold=True)
            title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 160))
            virtual_surface.blit(title_img, title_rect)
            resume_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
            mainmenu_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
            quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
            draw_button(virtual_surface, resume_btn, "Resume", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            draw_button(virtual_surface, mainmenu_btn, "Main Menu", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)
            draw_button(virtual_surface, quit_btn, "Quit", FONT, bg=COLOR_ACCENT_DARK, fg=COLOR_TEXT)

        elif state == "level":
            # Level selection screen
            title_img = render_pixel_text("Select Level", color=(229,115,115), base_size=24, pixel_scale=5, bold=True)
            title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 120))
            virtual_surface.blit(title_img, title_rect)

            # Create buttons for each difficulty option
            opt_w, opt_h = 360, 70
            start_y = 200
            gap = 90
            option_rects = {}
            for i, d in enumerate(DIFFICULTIES):
                r = pygame.Rect(VIRTUAL_WIDTH//2 - opt_w//2, start_y + i*gap, opt_w, opt_h)
                option_rects[d] = r
                draw_button(virtual_surface, r, d, FONT, bg=COLOR_ACCENT if d != selected_difficulty else COLOR_ACCENT_DARK, fg=COLOR_TEXT)
                # mark chosen difficulty with a thin highlight border
                if d == selected_difficulty:
                    pygame.draw.rect(virtual_surface, (30,20,10), r, 4, border_radius=8)

            # Back button
            back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, start_y + len(DIFFICULTIES)*gap + 10, 200, 50)
            draw_button(virtual_surface, back_btn, "Back", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)

        elif state == "gameover":
            # If the gameover background image is fullscreen and already contains the "Game Over"
            # artwork, don't draw an extra title on top — just blit the background and the button.
            if gameover_bg_img and gameover_bg_img.get_size() == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
                virtual_surface.blit(gameover_bg_img, (0, 0))
            else:
                # draw fallback background (or smaller bg image) and add a clear "Game Over" title
                if gameover_bg_img:
                    # if bg exists but is not fullscreen, center/scale it as decorative layer
                    bg_rect = gameover_bg_img.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2))
                    virtual_surface.blit(gameover_bg_img, bg_rect)
                else:
                    virtual_surface.fill((40, 10, 10))

                # draw a clear "Game Over" title with panel for contrast
                title_img = render_pixel_text(
                    "Game Over",
                    color=COLOR_TITLE,
                    outline_color=(20,12,6),
                    outline_thickness=3,
                    base_size=20,
                    pixel_scale=5,
                    bold=True,
                )
                title_rect = title_img.get_rect(center=(VIRTUAL_WIDTH//2, 200))
                panel_w, panel_h = title_rect.width + 40, title_rect.height + 20
                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                panel.fill((0,0,0,170))  # semi-transparent dark panel behind title
                virtual_surface.blit(panel, (title_rect.x - 20, title_rect.y - 10))
                virtual_surface.blit(title_img, title_rect)

            main_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, VIRTUAL_HEIGHT - 150, 300, 60)
            draw_button(virtual_surface, main_btn, "Main Menu", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)

        elif state == "victory":
            # draw victory background (or fallback color) and optional overlay
            if victory_bg_img:
                virtual_surface.blit(victory_bg_img, (0, 0))
            else:
                virtual_surface.fill((30, 30, 60))
            # optional: draw youwin overlay if present (centered)
            if youwin_img:
                yw_rect = youwin_img.get_rect()
                # if youwin_img is fullscreen it will cover bg; otherwise center it
                if yw_rect.size == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
                    virtual_surface.blit(youwin_img, (0, 0))
                else:
                    yw_rect.center = (VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2 - 40)
                    virtual_surface.blit(youwin_img, yw_rect)

            main_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, VIRTUAL_HEIGHT - 150, 300, 60)
            draw_button(virtual_surface, main_btn, "Main Menu", FONT, bg=COLOR_ACCENT, fg=COLOR_TEXT)

    # -------- Final scaling to screen with letterbox (maintain aspect ratio) --------
    # calculate scale factor
    scale_w = SCREEN_WIDTH / VIRTUAL_WIDTH
    scale_h = SCREEN_HEIGHT / VIRTUAL_HEIGHT
    scale = min(scale_w, scale_h)
    new_w = int(VIRTUAL_WIDTH * scale)
    new_h = int(VIRTUAL_HEIGHT * scale)

    # use nearest-neighbor scaling to keep pixel-art crisp (avoid smoothscale blur)
    scaled_surface = pygame.transform.scale(virtual_surface, (new_w, new_h))
    x_pos = (SCREEN_WIDTH - new_w) // 2
    y_pos = (SCREEN_HEIGHT - new_h) // 2

    screen.fill(COLOR_BG)
    screen.blit(scaled_surface, (x_pos, y_pos))
    pygame.display.flip()

pygame.quit()