import pygame
import random
import math
from data import DATA
from functions import *
from projectiles import Bullet

def detectPlatformFall(sprite):
    sprite.rect = sprite.rect.move(-23 if sprite.dir[0] == -1 else 23, 10)
    collidedPlatform = pygame.sprite.spritecollideany(sprite, DATA["solids"])
    sprite.rect = sprite.rect.move(23 if sprite.dir[0] == -1 else -23, -10)

    if not collidedPlatform:
        sprite.dir[0] *= -1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("./images/enemy.png")
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = pos
        self.vel = [0, 0]

        self.dir = [random.randrange(-1, 2, 2), 0]

        self.maxVel = random.randrange(1, 4)
        self.inAir = True
        self.acc = 1
        self.health = 30
        self.maxHealth = 30
        self.shotDelay = random.randrange(3, 7)
        self.lastShot = pygame.time.get_ticks()

    def update(self):
        if self.vel[1] <= 12:
            self.vel[1]+=DATA["GRAVITY"]

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            if solidXCollision(self):
                self.dir[0] *= -1

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        if (pygame.time.get_ticks() - self.lastShot) / 1000 >= self.shotDelay:
            self.lastShot = pygame.time.get_ticks()
            DATA["bullets"].add(Bullet(self.rect.center, DATA["player"].rect.center, 'enemy', 'pistol'))

        detectPlatformFall(self)
        newVel = [self.vel[0]+self.acc*self.dir[0], self.vel[1]+self.acc*self.dir[1]]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        bulletCollided = pygame.sprite.spritecollideany(self, DATA["playerBullets"])
        if bulletCollided:
            self.health -= bulletCollided.dmg
            bulletCollided.kill()

        if self.health <= 0:
            self.kill()
            DATA["player"].enemiesKilled += 1
            DATA["player"].hotbar[DATA["player"].hand].ammo += random.randrange(1, 7)

    def draw(self):
        healthBar(self, self.rect.width, 5, self.rect.x, self.rect.y-10)
        DATA["DISPLAY"].blit(self.image, (self.rect.x, self.rect.y))