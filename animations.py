import pygame, random, math, data

class Cloud(pygame.sprite.Sprite):
    """Moving clouds"""
    def __init__(self, pos=[0, 0]):
        super().__init__()
        self.image = pygame.image.load(F"./images/cloud_{random.randrange(1, 4)}.png").convert()
        self.image.set_colorkey((0, 255, 0))
        randomSizeFactor = random.randrange(1, 6)
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*randomSizeFactor, self.image.get_height()*randomSizeFactor))
        self.rect = self.image.get_rect()

        self.compPos = [pos[0] if pos[0] else int(random.randrange(0, data.DISPLAY_SIZE[0]-150)), pos[1] if pos[1] else int(random.randrange(0, data.DISPLAY_SIZE[1]-150))]
        self.rect.x, self.rect.y = self.compPos
        self.vel = [round(random.uniform(0.1, 0.5), 2), 0]
        self.scrollIntensity = 100/self.vel[0]

    def animate(self):
        self.compPos = [
            -1*self.rect.width if self.rect.left > data.DISPLAY_SIZE[0] and self.vel[0] > 0 else data.DISPLAY_SIZE[0] if self.rect.right < 0 and self.vel[0] < 0 else self.compPos[0]+self.vel[0],
            int(random.randrange(0, data.DISPLAY_SIZE[1]-150)) if self.rect.left > data.DISPLAY_SIZE[0] and self.vel[0] > 0 else int(random.randrange(0, data.DISPLAY_SIZE[1]-150)) if self.rect.right < 0 and self.vel[0] < 0 else self.compPos[1]+self.vel[1]
        ]
        
        self.compPos = [self.compPos[0]+self.vel[0], self.compPos[1]+self.vel[1]]
        self.rect.x, self.rect.y = math.floor(self.compPos[0]), math.floor(self.compPos[1])

