import pygame
from data import DATA

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.winPos = [0, 0]
        self.pos = pygame.math.Vector2(0, 0)
        self.selected = None

    def update(self):
        self.winPos = pygame.mouse.get_pos()
        self.pos.x, self.pos.y = int(self.winPos[0]*(DATA["DISPLAY_SIZE"][0]/DATA["WIN_SIZE"][0])), int(self.winPos[1]*(DATA["DISPLAY_SIZE"][1]/DATA["WIN_SIZE"][1]))
        self.rect.x, self.rect.y = self.pos