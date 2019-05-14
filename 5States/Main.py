import pygame

from Settings import GlobalSettings

pygame.init()
screen = pygame.display.set_mode(GlobalSettings.SCREEN)
screen.fill(GlobalSettings.BACKGROUND)
pygame.display.set_caption(GlobalSettings.CAPTION)

while True:
    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
