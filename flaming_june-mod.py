import pygame, pygame.gfxdraw, random, math

x_res = 1024
y_res = 768
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
running = True
font = pygame.font.SysFont('msgothic', 18)
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
fSizeX = 200
fSizeY = 150
fStartX = int(x_res/2-fSizeX/2)
#fStartY = int(y_res/2+fSizeY/2)
fStartY = y_res
y = 199
x = 1
flame = [[]]
startTime = pygame.time.get_ticks()
blast = True

# Fire Color
def fire_color(v):
    v = max(0, min(255, int(v)))

    if v < 35:
        return (0, 0, 0)
    if v < 90:
        return (v * 2, 0, 0)
    if v < 150:
        return (255, (v - 90) * 3, 0)
    if v < 220:
        return (255, 180 + (v - 150), (v - 150) // 2)
    return (255, 245, 210)

# area init
scale = 4
fire_surf = pygame.Surface((fSizeX, fSizeY)).convert()
fire_big = pygame.Surface((fSizeX * scale, fSizeY * scale)).convert()
glow_big = pygame.Surface((fSizeX * scale * 2, fSizeY * scale * 2)).convert()

palette = [fire_surf.map_rgb(fire_color(i)) for i in range(256)]
flame = [flame[:] for flame in [[0] * (fSizeX+1)] * (fSizeY+1)]

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
            screen.blit(letter, (x, y))
            x += letter.get_width()

    draw_rainbow_text(screen, pygame.font.SysFont("msgothic", 36), text, (x_res // 2 - 150, 50), pygame.time.get_ticks())

    # RANDOM SEED


    for r in range(fSizeX):
        flame[fSizeY][r] = random.randint(0, 255)

    # MAIN

    px = pygame.PixelArray(fire_surf)

    for y in range(fSizeY - 1, 0, -1):
        for x in range(1, fSizeX - 1):
            cooling = random.randint(0, 8)
            drift = random.choice([-1, 0, 1])
            src_x = max(1, min(fSizeX - 2, x + drift))

            value = (
                            flame[y + 1][src_x - 1]
                            + flame[y + 1][src_x]
                            + flame[y + 1][src_x + 1]
                            + flame[y][x]
                    ) / 4 / 0.969

            heat = max(0, int(value - cooling))
            flame[y][x] = heat
            px[x, y] = palette[heat]

    del px

    ydisplacement = fStartY
    if heat < 1:
        heat = 0

    pygame.gfxdraw.pixel(fire_surf, x, ydisplacement + y, fire_color(heat))
    pygame.transform.scale(fire_surf, fire_big.get_size(), fire_big)

    screen.blit(
        fire_big,
        (fStartX, fStartY - fSizeY * scale),
    )
    pygame.transform.smoothscale(fire_surf, glow_big.get_size(), glow_big)
    glow_big.set_alpha(45)

    screen.blit(
        glow_big,
        (fStartX - fSizeX * scale // 2, fStartY - fSizeY * scale * 2),
        special_flags=pygame.BLEND_ADD,
    )


    ydisplacement -= 4

    pygame.display.flip()
    dt = timer.tick(159) / 1000