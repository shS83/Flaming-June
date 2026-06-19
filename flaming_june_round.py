import pygame, pygame.gfxdraw, random, math

x_res = 1024
y_res = 768
timer = pygame.time.Clock()
pygame.init()
running = True
screen = pygame.display.set_mode([x_res, y_res], pygame.SHOWN)
fSizeX = 200
fSizeY = 200
fStartX = int(x_res/2-fSizeX/2)
fStartY = int(y_res/2+fSizeY/2)
y = 199
x = 1
flame = [[]]
startTime = pygame.time.get_ticks()
text = "Very Gay June for you all!"
calfont = pygame.font.Font("VINERITC.TTF", 32)
displacementX = calfont.size("Wz")[0]
letterX = calfont.size("Wg")[0] * len(text)
letterY = calfont.size("Wg")[1] * 2
letters = pygame.Surface((letterX, letterY))
# area init
fire_surf = pygame.Surface((round(fSizeX*1.1), round(fSizeY*1.1)))
flame = [flame[:] for flame in [[0] * (fSizeX+1)] * (fSizeY+1)]
yDisplacement = 4

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

def draw_rainbow_text(letters, font, text, pos, tick):
    x, y = pos

    text = "Happy Flaming June!"

    for i, char in enumerate(text):
        r = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45))
        g = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45 + 2.1))
        b = int(127 + 127 * math.sin(tick * 0.004 + i * 0.45 + 4.2))

        letter = font.render(char, True, (r, g, b))
        letters.blit(letter, (x, y))
        x += letter.get_width()
    return letters

colored_letters = draw_rainbow_text(letters, calfont, text, (0, 0), 159/1000)

while running:
    
    ticks = pygame.time.get_ticks()

    for event in pygame.event.get():    
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False
    
    # INIT DISPLAY

    screen.fill((0, 0, 0))

    # screen.blit(calfont.render("flaming june", True, (255, 255, 255)), (x_res//2 - 75, 100))
    screen.blit(colored_letters, (x_res // 2, 100))
    dt = timer.tick(159) / 1000

    # RANDOM SEED


    for r in range(fSizeX):
       edge = abs(r - fSizeX / 2) / (fSizeX / 2)
       shape = max(0, 1 - edge ** 2)
       flame[fSizeY][r] = int(random.randint(120, 255) * shape)
       #flame[fSizeY][r] = random.randint(0, 255)

    # MAIN
    
    for y in range(fSizeY-1, 0, -1):
        for x in range(0, fSizeX-1):
   
            flame[y][x] = int(round(((flame[y+1][x-1] + flame[y][x] + flame[y+1][x+1]) / 3)) / 1.0009)
            cooling = random.randint(0, 8)
            drift = random.choice([-1, 0, 1])
            src_x = max(1, min(fSizeX - 2, x + drift))
            value = (
                             flame[y + 1][src_x - 1]
                             + flame[y + 1][src_x]
                             + flame[y + 1][src_x + 1]
                             + flame[y][x]
                     ) / 4 / 0.9755
            flame[y][x] = max(0, int(value - cooling))
            red = flame[y][x]

            #yDisplacement = fStartY-fSizeY

            pygame.gfxdraw.rectangle(screen, (x_res / 2 + x, y_res / 2 - y, x, y), fire_color(red))
            # big_fire = pygame.transform.scale(fire_surf, (fSizeX * 2, fSizeY * 2))
            # screen.blit(big_fire, (x_res // 2, y_res - fStartY - fSizeY))>
    pygame.display.flip()