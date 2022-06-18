import pygame, random, data
from entities import Enemy, Player

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
            data.player = Player()
            data.player.rect.x, data.player.rect.y = x*self.SIZE[0], y*self.SIZE[1]-data.player.rect.height-10
            data.player.spawn = [x*self.SIZE[0], y*self.SIZE[1]-data.player.rect.height-10]
        elif tileType == 'W':
            self.image = pygame.image.load("./images/win.png").convert()
        elif tileType == 'E':
            data.enemies.add(Enemy((x*20, y*20-50)))
            return
        elif tileType == "T":
            data.enemies.add(Enemy((x*20, y*20-50), health=500, fireRate=2))
            return
        else:
            print("INVALID TILE TYPE: ", type(tileType), tileType)
            pygame.quit()

        self.image.set_colorkey((0, 255, 0))
 
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x*self.SIZE[0], y*self.SIZE[1]
        if tileType == 'W':
            data.items.add(self)
        else:
            data.solids.add(self)

        # Randomly generate a coin above the surface
        if coinType:
            data.coins.add(Coin(self.rect.x, self.rect.y-25, coinType))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.image.load('./images/{}_coin.png'.format(type)).convert()
        self.value = 1 if type == "yellow" else 5 if type == "red" else 10 if type == "blue" else 50

        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y