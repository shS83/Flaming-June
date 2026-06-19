import pygame
import pygame.gfxdraw
import random
import math

from pygame.transform import average_color

x_res = 1024
y_res = 768
timer = pygame.time.Clock()
pygame.init()
running = True
font = pygame.font.Font('VINERITC.TTF', 36)
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
fSizeX = 200
fSizeY = 150
fStartX = int(x_res/2-fSizeX/2)
#fStartY = int(y_res/2+fSizeY/2)
fStartY = y_res
y = 199
x = 1
flame = [[]]
alpha = [[]]
startTime = pygame.time.get_ticks()
blast = True

# Fire Color
def fire_color(v, alpha):
    v = max(0, min(255, int(v)))

    if v < 35:
        return (0, 0, 0, alpha)
    if v < 90:
        return (v * 2, 0, 0, alpha)
    if v < 150:
        return (255, (v - 90) * 3, 0, alpha)
    if v < 220:
        return (255, 180 + (v - 150), (v - 150) // 2, alpha)
    return (255, 245, 210, alpha)

# area init
scale = 3.5
fire_surf = pygame.Surface((fSizeX+100, fSizeY)).convert()
fire_big = pygame.Surface((fSizeX * scale+100, fSizeY * scale)).convert()
glow_big = pygame.Surface((fSizeX * scale * 2+100, fSizeY * scale * 2)).convert()

palette = [fire_surf.map_rgb(fire_color(i, i)) for i in range(256)]
flame = [flame[:] for flame in [[0] * (fSizeX+1)] * (fSizeY+1)]
alpha = [alpha[:] for alpha in [[0] * (fSizeX+1)] * (fSizeY+1)]

while running:
    
    ticks = pygame.time.get_ticks()

    for event in pygame.event.get():    
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False
    
    # INIT DISPLAY
    def rand():
        return [round(random.randint(0, 255)), round(random.randint(0, 255)), round(random.randint(0, 255)), round(random.randint(0, 255))]
    screen.fill((0, 0, 0))

    text = "Happy Flaming June!"

    def draw_rainbow_text(screen, font, text, pos, tick):
        x, y = pos

        for i, char in enumerate(text):
            r = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45))
            g = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45 + 2.1))
            b = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45 + 4.2))

            letter = font.render(char, True, (r, g, b))
            letter = pygame.transform.rotozoom(letter, 90, 0.95)
            screen.blit(letter, (x, y))
            letter = pygame.transform.rotozoom(letter, 0, 1)
            screen.blit(letter, (x, y))
            y -= letter.get_height()

    draw_rainbow_text(screen, pygame.font.Font("VINERITC.TTF", 36), text, (50, y_res // 2 + 200), pygame.time.get_ticks())

    # RANDOM SEED


    for r in range(fSizeX):
        flame[fSizeY][r] = random.randint(0, 255)

    # MAIN

    px = pygame.PixelArray(fire_surf)

    for y in range(fSizeY - 1, 0, -1):
        for x in range(1, fSizeX - 1):
            alpha[y][x] = random.randint(0, 255)
            cooling = random.randint(0, 8)
            drift = random.choice([-1, 0, 1])
            src_x = max(1, min(fSizeX - 2, x + drift))

            value = (
                            flame[y + 1][src_x - 1]
                            + flame[y + 1][src_x]
                            + flame[y + 1][src_x + 1]
                            + flame[y][x]
                    ) / 4 / 0.9685

            heat = max(0, int(value - cooling))
            flame[y][x] = heat
            try:
                px[x, y] = palette[heat]
            except IndexError:
                continue

    del px

    ydisplacement = fStartY
    if heat < 1:
        heat = 0

    pygame.gfxdraw.rectangle(fire_surf, (x, y, x+1, ydisplacement - y+1), fire_color(heat, alpha[y][x]))
    pygame.transform.scale(fire_surf, fire_big.get_size(), fire_big)

    screen.blit(
        fire_big,
        (fStartX, fStartY - fSizeY * scale),
    )
    pygame.transform.scale(fire_surf, glow_big.get_size(), glow_big)
    try:
        glow_big.set_alpha(alpha[random.randint(1, 255)][random.randint(1, 255)])
    except IndexError:
        glow_big.set_alpha(200)
    screen.blit(
        glow_big,
        (fStartX - fSizeX * scale * 3 // 2, fStartY - fSizeY * scale * 3),
        special_flags=pygame.BLEND_MULT,
    )


    ydisplacement -= 4

    pygame.display.flip()
    dt = timer.tick(159) / 1000