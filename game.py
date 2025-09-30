import pygame
from pygame.locals import *
import math
from random import randint

pygame.init()
lebar_layar, tinggi_layar = 640, 480
screen = pygame.display.set_mode((lebar_layar, tinggi_layar))

# ukuran objek
lebar_pemain = 50
tinggi_pemain = 40

posisi = [100, 380]

score = 0

makanan_timer = 0
makanans = []
B_makanan = 0
B_makanans = []

def new_makanan():
    x = randint(50, lebar_layar-50)
    y = 0
    speed = randint(3, 7)
    rect = pygame.Rect(x, y, 20, 20)
    return {"rect": rect, "speed": speed}

running = True
while (running):
    pygame.time.delay(18) 

    screen.fill((255,192,203))

    if len(makanans) < 1:
        makanan_timer += 1
        if makanan_timer > 30:
            makanans.append(new_makanan())
            makanan_timer = 0

    for makanan in makanans[:]:
        makanan["rect"].top += makanan["speed"]
        if makanan["rect"].top > tinggi_layar:
            makanans.remove(makanan)
        if pygame.Rect(posisi[0], posisi[1], lebar_pemain, tinggi_pemain).colliderect(makanan["rect"]):
            score += 1
            makanans.remove(makanan)
            print("Score:", score)
        pygame.draw.rect(screen, (0,255,0), makanan["rect"])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        posisi[0] -= 5
    if keys[pygame.K_d]:
        posisi[0] += 5
            


    
    pygame.draw.rect(screen, (0,0,255), (posisi[0],posisi[1],lebar_pemain,tinggi_pemain))

    pygame.display.update()

pygame.quit()
