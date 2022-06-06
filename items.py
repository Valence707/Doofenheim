import pygame
from functions import *
from projectiles import Bullet

class Item(pygame.sprite.Sprite):
    def __init__(self, name, ammo=0, image=None, action=None, cooldown=None, amount=1, autoUse=False):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.action = action
        self.name = name
        self.cooldown = cooldown
        self.ammo = ammo
        self.autoUse = autoUse
        self.lastUsed = pygame.time.get_ticks()
        self.hasBeenUsed = False
        self.image = pygame.image.load(F"./images/{image}")
        self.image = pygame.transform.scale(self.image, DATA["inventorySlotSize"])
        self.rect = self.image.get_rect()
        self.kill()

    def use(self):
        if round((pygame.time.get_ticks()-self.lastUsed)/1000, 2) >= self.cooldown:
            self.action(self)
            self.lastUsed = pygame.time.get_ticks()

def pistol_shoot(gun):
    if gun.ammo:
        DATA["bullets"].add(Bullet(DATA["player"].rect.center, pygame.mouse.get_pos(), 'DATA["player"]', 'pistol'))
        gun.hasBeenUsed = True
        gun.ammo -= 1
        pygame.mixer.Sound('./sounds/pistol_shoot.ogg').play()

def shotgun_shoot(gun):
    if gun.ammo:
        for i in range(5):
            DATA["bullets"].add(Bullet(DATA["player"].rect.center, pygame.mouse.get_pos(), 'DATA["player"]', 'shotgun'))
            gun.hasBeenUsed = True
        gun.ammo -= 1
        pygame.mixer.Sound('./sounds/shotgun_shoot.ogg').play()