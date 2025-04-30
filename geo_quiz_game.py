import pygame
import sys

# Инициализация
pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini IO Game")

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)

player_pos = [WIDTH // 2, HEIGHT // 2]
player_radius = 20
speed = 5

clock = pygame.time.Clock()

# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += speed
    if keys[pygame.K_UP]:
        player_pos[1] -= speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += speed

    WIN.fill(WHITE)
    pygame.draw.circle(WIN, BLUE, player_pos, player_radius)
    pygame.display.update()
    clock.tick(60)
