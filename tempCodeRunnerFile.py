import pygame
from pygame.locals import *
from random import randint

pygame.init()

# --- Virtual Resolution (game asli) ---
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1280, 720   # base resolution 16:9

# --- Window Setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT

# Resizable window with standard controls
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Kucing Catch Game")

# Virtual surface (game logic jalan di resolusi ini)
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

fullscreen = False # Flag to track fullscreen state

# --- Player ---
lebar_pemain = 80
tinggi_pemain = 80

# --- Ground / Tanah ---
ground_height = 80
ground_rect = pygame.Rect(0, VIRTUAL_HEIGHT - ground_height, VIRTUAL_WIDTH, ground_height)

# Set player position based on ground
posisi = [VIRTUAL_WIDTH // 2, ground_rect.top - tinggi_pemain]


# Load base sprite
player_idle_right = pygame.image.load("resource/images/kucing.png")
player_idle_right = pygame.transform.scale(player_idle_right, (lebar_pemain, tinggi_pemain))
player_idle_left = pygame.transform.flip(player_idle_right, True, False)

# Create a simple "walk" frame by squashing the image
player_walk_right = pygame.transform.scale(player_idle_right, (lebar_pemain, int(tinggi_pemain * 0.9)))
player_walk_left = pygame.transform.flip(player_walk_right, True, False)

# Animation variables
walk_animation_frames_r = [player_idle_right, player_walk_right]
walk_animation_frames_l = [player_idle_left, player_walk_left]
current_frame = 0
animation_speed = 10  # Change frame every 10 game ticks
animation_timer = 0

# Player state
player = player_idle_right
facing_right = True
is_walking = False


score = 0
makanan_timer = 0
B_makanan_timer = 0
makanans = []
B_makanans = []

def new_makanan():
    x = randint(50, VIRTUAL_WIDTH-50)
    y = 0
    speed = 6
    rect = pygame.Rect(x, y, 30, 30)
    return {"rect": rect, "speed": speed}

def new_B_makanan():
    x = randint(50, VIRTUAL_WIDTH-50)
    y = 0
    speed = randint(4, 8)
    rect = pygame.Rect(x, y, 30, 30)
    return {"rect": rect, "speed": speed}

# --- Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    virtual_surface.fill((255,192,203))

    # Gambar tanah (sementara warna coklat)
    pygame.draw.rect(virtual_surface, (139, 69, 19), ground_rect)

    # Spawn makanan hijau
    jumlah_makanan = 1 + (score // 3)
    if len(makanans) < jumlah_makanan:
        makanan_timer += 1
        if makanan_timer > 30:
            makanans.append(new_makanan())
            makanan_timer = 0

    # Spawn makanan merah
    jumlah_B_makanan = 2 + (score // 5)
    if len(B_makanans) < jumlah_B_makanan:
        B_makanan_timer += 1
        if B_makanan_timer > 40:
            B_makanans.append(new_B_makanan())
            B_makanan_timer = 0

    # Gerakan makanan hijau
    for makanan in makanans[:]:
        makanan["rect"].top += makanan["speed"]
        if makanan["rect"].top > VIRTUAL_HEIGHT:
            makanans.remove(makanan)
        if pygame.Rect(posisi[0], posisi[1], lebar_pemain, tinggi_pemain).colliderect(makanan["rect"]):
            score += 1
            makanans.remove(makanan)
            print("Score:", score)
        pygame.draw.rect(virtual_surface, (0,255,0), makanan["rect"])

    # Gerakan makanan merah
    for B_makanan in B_makanans[:]:
        B_makanan["rect"].top += B_makanan["speed"]
        if B_makanan["rect"].top > VIRTUAL_HEIGHT:
            B_makanans.remove(B_makanan)
        if pygame.Rect(posisi[0], posisi[1], lebar_pemain, tinggi_pemain).colliderect(B_makanan["rect"]):
            B_makanans.remove(B_makanan)
            running = False  # game over
        pygame.draw.rect(virtual_surface, (255,0,0), B_makanan["rect"])

    # --- Event ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # ESC untuk keluar
                running = False
            if event.key == K_F11: # F11 to toggle fullscreen
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    SCREEN_WIDTH, SCREEN_HEIGHT = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        if event.type == VIDEORESIZE:
            if not fullscreen:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    keys = pygame.key.get_pressed()
    is_walking = False
    if keys[pygame.K_a]:
        posisi[0] -= 8
        facing_right = False
        is_walking = True
    elif keys[pygame.K_d]:
        posisi[0] += 8
        facing_right = True
        is_walking = True

    # --- Animation ---
    if is_walking:
        animation_timer += 1
        if animation_timer >= animation_speed:
            animation_timer = 0
            current_frame = (current_frame + 1) % len(walk_animation_frames_r)
    else:
        current_frame = 0 # Reset to idle frame when not walking

    if facing_right:
        player = walk_animation_frames_r[current_frame]
    else:
        player = walk_animation_frames_l[current_frame]


    # Batas layar
    posisi[0] = max(0, min(posisi[0], VIRTUAL_WIDTH - lebar_pemain))

    # Gambar player
    virtual_surface.blit(player, (posisi[0], posisi[1]))

    # --- Scaling (letterbox fullscreen) ---
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