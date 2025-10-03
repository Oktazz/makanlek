# game_full.py
import pygame
from pygame.locals import *
from random import randint, choice
import os

pygame.init()
pygame.mixer.init()

# -------- CONFIG: Virtual resolution (game world) --------
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1280, 720  # design base (16:9)

# Window initial size (starts at virtual res; user can resize)
SCREEN_WIDTH, SCREEN_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Kucing Catch Game")

# Virtual surface - draw game here, then scale to screen
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# -------- Asset file paths (put your images/sounds here) --------
ASSET_PATH = "resource"
PLAYER_ASSETS = {
    "cat": os.path.join(ASSET_PATH, "images", "kucing.png"),
    "dog": os.path.join(ASSET_PATH, "images", "anjing.png"),
    "bunny": os.path.join(ASSET_PATH, "images" , "rabbit.png"),
}
GROUND_TILE = os.path.join(ASSET_PATH, "images" ,"ground.png")
SNACK_ASSET = os.path.join(ASSET_PATH, "images" ,"ikan.png")
OBSTACLE_ASSET = os.path.join(ASSET_PATH, "images" ,"bom.png")
BGM_FILE = os.path.join(ASSET_PATH, "sounds", "backsound.mp3")
SFX_STEP = os.path.join(ASSET_PATH, "sounds", "footstep.mp3")
SFX_EAT = os.path.join(ASSET_PATH, "sounds", "eat.wav")
SFX_HIT = os.path.join(ASSET_PATH, "sounds", "hit.mp3")
SFX_GAMEOVER = os.path.join(ASSET_PATH, "sounds", "game_over.wav")
HEART_ASSET = os.path.join(ASSET_PATH, "images", "love.png")

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
GROUND_HEIGHT = 100              # height of ground in virtual coords
PLAYER_W, PLAYER_H = 80, 80      # default player sprite size
SNACK_W, SNACK_H = 60, 60
OBST_W, OBST_H = 60, 60
MAX_LIVES = 9
STEP_SOUND_INTERVAL = 12         # frames between step sfx while walking

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

ground_tile_img = load_image(GROUND_TILE, (128, GROUND_HEIGHT), fallback_color=(100,50,20))
snack_img = load_image(SNACK_ASSET, (SNACK_W, SNACK_H), fallback_color=(0,200,0))
obst_img = load_image(OBSTACLE_ASSET, (OBST_W, OBST_H), fallback_color=(200,0,0))
heart_img = load_image(HEART_ASSET, (24, 24), fallback_color=(255,0,0))
sky_img = load_image(os.path.join(ASSET_PATH, "images", "sky.png"), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# sounds
bgm = BGM_FILE if os.path.exists(BGM_FILE) else None
sfx_step = load_sound(SFX_STEP)
sfx_eat = load_sound(SFX_EAT)
sfx_hit = load_sound(SFX_HIT)
sfx_gameover = load_sound(SFX_GAMEOVER)

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
score = 0
makanan_timer = 0
B_makanan_timer = 0

# lives
lives = MAX_LIVES

# Achievement variables
achievement_timer = 0
show_achievement = False
last_achievement_score = 0

# UI fonts
FONT = pygame.font.SysFont("arial", 28)
ACHIEVEMENT_FONT = pygame.font.SysFont("arial", 48, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 56, bold=True)

# menu state: "main", "character", "assets", "playing", "pause", "gameover"
state = "main"

# For menu selections
available_chars = list(player_images.keys())
selected_char_index = available_chars.index(selected_char_key)

# selected assets
selected_snack = snack_img
selected_obst = obst_img

# helper to reset gameplay
def reset_game():
    global makanans, B_makanans, score, makanan_timer, B_makanan_timer, lives, player_pos, achievement_timer, show_achievement, last_achievement_score
    makanans = []
    B_makanans = []
    score = 0
    makanan_timer = 0
    B_makanan_timer = 0
    lives = MAX_LIVES
    player_pos = [VIRTUAL_WIDTH//2, ground_rect.top - PLAYER_H]
    achievement_timer = 0
    show_achievement = False
    last_achievement_score = 0

# -------- UI helpers --------
def draw_text(surface, text, pos, font=FONT, color=(255,255,255)):
    img = font.render(text, True, color)
    surface.blit(img, pos)

def draw_button(surface, rect, text, font=FONT, bg=(50,50,50), fg=(255,255,255)):
    pygame.draw.rect(surface, bg, rect, border_radius=6)
    label = font.render(text, True, fg)
    lx = rect.x + (rect.width - label.get_width())//2
    ly = rect.y + (rect.height - label.get_height())//2
    surface.blit(label, (lx, ly))

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
                quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 520, 300, 60)
                if start_btn.collidepoint(vx, vy):
                    reset_game()
                    state = "playing"
                elif char_btn.collidepoint(vx, vy):
                    state = "character"
                elif asset_btn.collidepoint(vx, vy):
                    state = "assets"
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
                # select snack/obst from two sample boxes
                snack_box = pygame.Rect(220, 260, 120, 120)
                obst_box = pygame.Rect(400, 260, 120, 120)
                if snack_box.collidepoint(vx, vy):
                    # toggle between default and another if exists (simple)
                    # if you had more assets you'd present list; here we'll just keep default
                    selected_snack = snack_img
                if obst_box.collidepoint(vx, vy):
                    selected_obst = obst_img
                back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 520, 200, 50)
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
            
            elif state == "gameover":
                main_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 340, 300, 60)
                quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 420, 300, 60)
                if main_btn.collidepoint(vx, vy):
                    state = "main"
                elif quit_btn.collidepoint(vx, vy):
                    running = False

    # ---------- State updates ----------
    if state == "playing":

        virtual_surface.blit(sky_img, (0, 0))

        # draw ground tiles across width
        for x in range(0, VIRTUAL_WIDTH, ground_tile_img.get_width()):
            virtual_surface.blit(ground_tile_img, (x, VIRTUAL_HEIGHT - GROUND_HEIGHT))

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
                lives -= 1
                if sfx_hit:
                    sfx_hit.play()
                if lives <= 0:
                    if sfx_gameover:
                        sfx_gameover.play()
                    state = "gameover"

        # Controls - keyboard both A/D and arrows
        keys = pygame.key.get_pressed()
        is_walking = False
        moved = False
        if keys[K_a] or keys[K_LEFT]:
            player_pos[0] -= 8
            facing_right = False
            is_walking = True
            moved = True
        if keys[K_d] or keys[K_RIGHT]:
            player_pos[0] += 8
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
        for makanan in makanans:
            # draw snack image centered on rect
            virtual_surface.blit(selected_snack, (makanan["rect"].x, makanan["rect"].y))
        for obst in B_makanans:
            virtual_surface.blit(selected_obst, (obst["rect"].x, obst["rect"].y))

        # draw player
        virtual_surface.blit(player_image, (player_pos[0], player_pos[1]))

        # HUD: score and lives
        draw_text(virtual_surface, f"Score: {score}", (20, 20), FONT, (0,0,0))

        # Tombol Pause di pojok kiri atas
        pause_btn_rect = pygame.Rect(20, 60, 100, 40)
        draw_button(virtual_surface, pause_btn_rect, "Pause", FONT, bg=(80,80,120))


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
        virtual_surface.fill((30,30,50))  # dark BG for menus

        if state == "main":
            # title
            draw_text(virtual_surface, "Kucing Catch Game", (VIRTUAL_WIDTH//2 - 220, 120), TITLE_FONT, (255, 230, 180))
            # buttons
            start_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
            char_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
            asset_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
            quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 520, 300, 60)
            draw_button(virtual_surface, start_btn, "Start Game", FONT, bg=(40,160,40))
            draw_button(virtual_surface, char_btn, "Character Select", FONT, bg=(40,120,200))
            draw_button(virtual_surface, asset_btn, "Asset Select", FONT, bg=(200,120,40))
            draw_button(virtual_surface, quit_btn, "Quit", FONT, bg=(160,40,40))

        elif state == "character":
            draw_text(virtual_surface, "Choose Character", (VIRTUAL_WIDTH//2-170, 120), TITLE_FONT, (255,255,255))
            # thumbnails
            start_x = 180
            start_y = 220
            thumb_w = 140
            thumb_h = 140
            gap = 40
            for i, key in enumerate(available_chars):
                rx = start_x + i*(thumb_w + gap)
                r = pygame.Rect(rx, start_y, thumb_w, thumb_h)
                pygame.draw.rect(virtual_surface, (60,60,60), r, border_radius=8)
                # draw thumbnail scaled
                thumb_img = pygame.transform.smoothscale(player_images[key], (thumb_w-20, thumb_h-20))
                virtual_surface.blit(thumb_img, (rx+10, start_y+10))
                draw_text(virtual_surface, key.capitalize(), (rx+10, start_y+thumb_h+8), FONT, (220,220,220))
                # highlight selected
                if i == selected_char_index:
                    pygame.draw.rect(virtual_surface, (255,255,0), r, 4, border_radius=8)
            # back button
            back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 520, 200, 50)
            draw_button(virtual_surface, back_btn, "Back", FONT)

        elif state == "assets":
            draw_text(virtual_surface, "Asset Select", (VIRTUAL_WIDTH//2-120, 120), TITLE_FONT, (255,255,255))
            draw_text(virtual_surface, "Snack (click to choose):", (180, 230), FONT)
            draw_text(virtual_surface, "Obstacle (click to choose):", (380, 230), FONT)
            snack_box = pygame.Rect(220, 260, 120, 120)
            obst_box = pygame.Rect(400, 260, 120, 120)
            pygame.draw.rect(virtual_surface, (50,50,50), snack_box, border_radius=8)
            pygame.draw.rect(virtual_surface, (50,50,50), obst_box, border_radius=8)
            virtual_surface.blit(selected_snack, (snack_box.x + (snack_box.width - selected_snack.get_width())//2,
                                                  snack_box.y + (snack_box.height - selected_snack.get_height())//2))
            virtual_surface.blit(selected_obst, (obst_box.x + (obst_box.width - selected_obst.get_width())//2,
                                                 obst_box.y + (obst_box.height - selected_obst.get_height())//2))
            back_btn = pygame.Rect(VIRTUAL_WIDTH//2-100, 520, 200, 50)
            draw_button(virtual_surface, back_btn, "Back", FONT)

        elif state == "pause":
            draw_text(virtual_surface, "Paused", (VIRTUAL_WIDTH//2-70, 120), TITLE_FONT)
            resume_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 280, 300, 60)
            mainmenu_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 360, 300, 60)
            quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 440, 300, 60)
            draw_button(virtual_surface, resume_btn, "Resume", FONT, bg=(40,160,40))
            draw_button(virtual_surface, mainmenu_btn, "Main Menu", FONT, bg=(40,120,200))
            draw_button(virtual_surface, quit_btn, "Quit", FONT, bg=(160,40,40))

        elif state == "gameover":
            draw_text(virtual_surface, "Game Over", (VIRTUAL_WIDTH//2-140, 160), TITLE_FONT, (255,60,60))
            draw_text(virtual_surface, f"Score: {score}", (VIRTUAL_WIDTH//2-60, 260), FONT, (255,255,255))
            main_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 340, 300, 60)
            quit_btn = pygame.Rect(VIRTUAL_WIDTH//2-150, 420, 300, 60)
            draw_button(virtual_surface, main_btn, "Main Menu", FONT, bg=(40,120,200))
            draw_button(virtual_surface, quit_btn, "Quit", FONT, bg=(160,40,40))
            # mouse click handling for these buttons handled earlier by mapping state and clicks

    # -------- Final scaling to screen with letterbox (maintain aspect ratio) --------
    # calculate scale factor
    scale_w = SCREEN_WIDTH / VIRTUAL_WIDTH
    scale_h = SCREEN_HEIGHT / VIRTUAL_HEIGHT
    scale = min(scale_w, scale_h)
    new_w = int(VIRTUAL_WIDTH * scale)
    new_h = int(VIRTUAL_HEIGHT * scale)

    scaled_surface = pygame.transform.smoothscale(virtual_surface, (new_w, new_h))
    x_pos = (SCREEN_WIDTH - new_w) // 2
    y_pos = (SCREEN_HEIGHT - new_h) // 2

    screen.fill((0,0,0))
    screen.blit(scaled_surface, (x_pos, y_pos))
    pygame.display.flip()

pygame.quit()