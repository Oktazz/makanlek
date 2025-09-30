import pygame
from pygame.locals import *
import math
from random import randint

pygame.init()
lebar_layar, tinggi_layar = 640, 480
screen = pygame.display.set_mode((lebar_layar, tinggi_layar))

# ukuran objek
lebar_pemain = 50
tinggi_pemain = 50

posisi = [100, 380]

player = pygame.image.load("resource/images/kucing.png")
player = pygame.transform.scale(player, (lebar_pemain, tinggi_pemain))

score = 0
level = 0

makanan_timer = 0
B_makanan_timer = 0
makanans = []
B_makanan = 0
B_makanans = []

def new_makanan():
    x = randint(50, lebar_layar-50)
    y = 0
    speed = 5
    rect = pygame.Rect(x, y, 20, 20)
    return {"rect": rect, "speed": speed}

def new_B_makanan():
    x = randint(50, lebar_layar-50)
    y = 0
    speed = randint(3, 6)
    rect = pygame.Rect(x, y, 20, 20)
    return {"rect": rect, "speed": speed}

running = True
while (running):
    pygame.time.delay(18) 

    screen.fill((255,192,203))

    jumlah_makanan = 1 + (score // 3)

    if len(makanans) < jumlah_makanan:
        makanan_timer += 1
        if makanan_timer > 30:
            makanans.append(new_makanan())
            makanan_timer = 0

    jumlah_B_makanan = 2 + (score // 5)

    if len(B_makanans) < jumlah_B_makanan:
        B_makanan_timer += 1
        if B_makanan_timer > 40:
            B_makanans.append(new_B_makanan())
            B_makanan_timer = 0

    for makanan in makanans[:]:
        makanan["rect"].top += makanan["speed"]
        if makanan["rect"].top > tinggi_layar:
            makanans.remove(makanan)
        if pygame.Rect(posisi[0], posisi[1], lebar_pemain, tinggi_pemain).colliderect(makanan["rect"]):
            score += 1
            makanans.remove(makanan)
            print("Score:", score)
        pygame.draw.rect(screen, (0,255,0), makanan["rect"])

    for B_makanan in B_makanans[:]:
        B_makanan["rect"].top += B_makanan["speed"]
        if B_makanan["rect"].top > tinggi_layar:
            B_makanans.remove(B_makanan)
        if pygame.Rect(posisi[0], posisi[1], lebar_pemain, tinggi_pemain).colliderect(B_makanan["rect"]):
            B_makanans.remove(B_makanan)
            pygame.quit()
        pygame.draw.rect(screen, (255,0,0), B_makanan["rect"])
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        posisi[0] -= 5
    if keys[pygame.K_d]:
        posisi[0] += 5
            


    
    screen.blit(player, (posisi[0], posisi[1]))

    pygame.display.update()

pygame.quit()
