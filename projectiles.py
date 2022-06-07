import pygame, random
from data import DATA

class Bullet(pygame.sprite.Sprite):
    def __init__(self, origin, dest, type, gun):
        super().__init__()
        self.image = pygame.image.load("./images/bullet.png").convert()
        self.rect = self.image.get_rect()
        self.maxVel = 15
        self.dmg = 10
        if type == 'DATA["player"]':
            self.dmg = 10
            DATA["playerBullets"].add(self)
        elif type == 'enemy':
            self.dmg = 5
            self.maxVel = 7
            DATA["enemyBullets"].add(self)

        self.compPos = origin
        self.rect.x, self.rect.y = origin
        delta = pygame.math.Vector2(dest[0]*(DATA["DISPLAY_SIZE"][0]/DATA["WIN_SIZE"][0]), dest[1]*(DATA["DISPLAY_SIZE"][1]/DATA["WIN_SIZE"][1])) - origin
        direction = delta.normalize()

        if gun == 'shotgun':
            direction.x, direction.y = direction[0]+(random.uniform(-0.15, 0.15)), direction[1]+(random.uniform(-0.15, 0.15))
        elif gun == 'pistol':
            direction = direction

        self.vel = direction*self.maxVel
        self.duration = 3
        self.initTime = pygame.time.get_ticks()

    def update(self):
        self.compPos = [round(self.compPos[0]+self.vel[0], 2), round(self.compPos[1]+self.vel[1], 2)]
        self.rect.x, self.rect.y = self.compPos
        if (pygame.time.get_ticks()-self.initTime) / 1000 > self.duration or pygame.sprite.spritecollideany(self, DATA["solids"]):
            self.kill()