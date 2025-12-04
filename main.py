import pygame
from fighter import Fighter
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("i hate gingers")

clock = pygame.time.Clock()
fps = 60

bg_image = pygame.image.load("assets/images/backgrounds/FOREST.png").convert_alpha()


def draw_bg():
    scale_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scale_bg, (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, (255, 0, 0), (x, y,  300, 30))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, 300 * ratio, 30))


fighter_1 = Fighter(200, 310)
fighter_2 = Fighter(700, 310)

run = True
while run:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if fighter_1.jump_count < fighter_1.max_jumps:
                    fighter_1.vel_y = -30
                    fighter_1.jump_count += 1

    draw_bg()
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 680, 20)
    fighter_1.move(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
    fighter_1.draw(screen, fighter_2)

    fighter_2.draw(screen, fighter_1)  # fighter 2 does nothing yet

    pygame.display.update()

pygame.quit()
