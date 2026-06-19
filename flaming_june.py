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
fSizeY = 250
fStartX = int(x_res//2-fSizeX//2)
fStartY = int(y_res//2+fSizeY//2)
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
scale = 2
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

	screen.fill((0, 0, 0))

	screen.blit(font.render("flaming june", True, (255, 255, 255)), (x_res//2 - 75, 100))
	# RANDOM SEED


	for r in range(fSizeX):
		flame[fSizeY][r] = random.randint(1, 255)

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
					) / 4 / 0.968

			heat = max(0, int(value - cooling))
			flame[y][x] = heat
			px[x, y] = palette[heat]

	del px

	yDisplacement = fStartY
	pygame.gfxdraw.pixel(fire_surf, x, y - yDisplacement, fire_color(heat))
	#bigger = pygame.Surface((fSizeX * 2, fSizeY * 2))
	bigger = pygame.transform.scale_by(fire_surf, 2)

	screen.blit(bigger, (300, 200))
	yDisplacement -= 4

	pygame.display.flip()
	dt = timer.tick(159) / 1000
