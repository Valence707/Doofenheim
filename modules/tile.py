import pygame, random
from data import DATA
from modules.coin import Coin
from modules.enemy import Enemy

class Tile(pygame.sprite.Sprite):
    """The world terrain objects"""
    def __init__(self, tileType, x, y):
        super().__init__()
        self.SIZE = [20, 20]
        coinType = None
        if tileType == '1':
            randCoin = random.randrange(1, 300)
            coinType = "yellow" if randCoin < 60 else "red" if randCoin >= 60 and randCoin < 90 else "blue" if randCoin >= 90 and randCoin < 99 else "black" if randCoin == 100 else None
            self.image = pygame.image.load('./images/dirt_top.png').convert()
        elif tileType == '2':
            self.image = pygame.image.load('./images/dirt_side.png').convert()
        elif tileType == '3':
            self.image = pygame.image.load('./images/stone.png').convert()
        elif tileType == 'S':
            self.image = pygame.image.load("./images/spawn.png").convert()
            DATA["player"].rect.x, DATA["player"].rect.y = x*self.SIZE[0], y*self.SIZE[1]-DATA["player"].rect.height-10
            DATA["player"].spawn = [x*self.SIZE[0], y*self.SIZE[1]-DATA["player"].rect.height-10]
        elif tileType == 'E':
            DATA["enemies"].add(Enemy((x*20, y*20-50)))
            return
        else:
            print("INVALID TILE TYPE: ", type(tileType), tileType)
            pygame.quit()

        self.image.set_colorkey((0, 255, 0))
            
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x*self.SIZE[0], y*self.SIZE[1]
        DATA["solids"].add(self)

        # Randomly generate a coin above the surface
        if coinType:
            DATA["coins"].add(Coin(self.rect.x, self.rect.y-25, coinType))