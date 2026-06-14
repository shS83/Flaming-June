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
fStartY = int(y_res/2+fSizeY/2)
y = 199
x = 1
flame = [[]]
startTime = pygame.time.get_ticks()
blast = True

# area init
fire_surf = pygame.Surface((1024, 768), pygame.SRCALPHA)
flame = [flame[:] for flame in [[0] * (fSizeX+1)] * (fSizeY+1)]

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

while running:
    
    ticks = pygame.time.get_ticks()

    for event in pygame.event.get():    
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False
    
    # INIT DISPLAY

    screen.fill((0, 0, 0))

    screen.blit(font.render("flaming june", True, (255, 255, 255)), (x_res//2 - 75, 100))
    # RANDOM SEED


    for r in range(fSizeX):
        edge = abs(r - fSizeX / 2) / (fSizeX / 2)
        shape = max(0, 1 - edge ** 2)
        flame[fSizeY][r] = int(random.randint(120, 255) * shape)
#        flame[fSizeY][r] = random.randint(0, 255)
    #    #flame[fSizeY-1][r] = random.randint(0, 255)
    #    #flame[fSizeY-2][r] = random.randint(0, 255)
    
    # MAIN
    
    for y in range(fSizeY-1, 0, -1):
        for x in range(0, fSizeX-1):
   
            # flame[y][x] = int(round(((flame[y+1][x-1] + flame[y][x] + flame[y+1][x+1]) / 3)) / 1.001)
            cooling = random.randint(0, 8)
            drift = random.choice([-1, 0, 1])
            src_x = max(1, min(fSizeX - 2, x + drift))
            value = (
                             flame[y + 1][src_x - 1]
                             + flame[y + 1][src_x]
                             + flame[y + 1][src_x + 1]
                             + flame[y][x]
                     ) / 4 / 0.98
            flame[y][x] = max(0, int(value - cooling))
            red = flame[y][x]

            ydisplacement = fStartY
            if red < 1:
                red = 0

            else:
                pygame.gfxdraw.pixel(screen, fStartX + x, ydisplacement - fSizeY + y, fire_color(red))
                #big_fire = pygame.transform.smoothscale(fire_surf, (fSizeX * 4, fSizeY * 4))
                #screen.blit(fire_surf, (x_res // 2, y_res // 2))
                #pygame.gfxdraw.pixel(screen, fStartX + x, ydisplacement-10 - fSizeY + y, (fCol, 0, 0))
                #pygame.gfxdraw.pixel(screen, fStartX + x, ydisplacement-20 - fSizeY + y, (fCol, 0, 0))
                ydisplacement -= 4
            #pygame.time.delay(1)

    #pygame.time.delay(1)
#    if y < 2:
#        y = fSizeY - 1
#        x = 1
#    if x > fSizeX - 1:
#        x = 1
    
#    x += 1

    pygame.display.flip()
    dt = timer.tick(159) / 1000