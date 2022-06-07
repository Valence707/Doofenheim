import pygame, random
from data import DATA
from modules.coin import Coin
from modules.enemy import Enemy

class Tile(pygame.sprite.Sprite):
    """The world terrain objects"""
    def __init__(self, tileType, x, y):
        super().__init__()
        self.SIZE = [20, 20]
        if tileType == '1':
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
        elif tileType == "#":
            self.image = pygame.Surface(self.SIZE)
            pygame.Surface.fill(self.image, (0, 0, 0))
            self.onScreen = 1
        else:
            print("INVALID TILE TYPE: ", type(tileType), tileType)
            pygame.quit()

        # Cause of ugly tiles. Need to resize all tile images to be 20x20px
        self.image = pygame.transform.scale(self.image, self.SIZE)
        self.image.set_colorkey((0, 255, 0))
            
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x*self.SIZE[0], y*self.SIZE[1]
        if tileType == '#':
            DATA["testTiles"].add(self)
        else:
            DATA["solids"].add(self)

        # Randomly generate a coin above the surface
        if tileType == '1' and not pygame.sprite.spritecollideany(Coin(self.rect.x, self.rect.y-25, 'yellow'), DATA["solids"]):
            randCoin = random.randrange(0, 300)
            if randCoin < 60:
                DATA["coins"].add(Coin(self.rect.x, self.rect.y-25, "yellow"))
            elif randCoin >= 60 and randCoin < 90:
                DATA["coins"].add(Coin(self.rect.x, self.rect.y-25, "red"))
            elif randCoin >= 90 and randCoin < 99: 
                DATA["coins"].add(Coin(self.rect.x, self.rect.y-25, "blue"))
            elif randCoin == 100:
                DATA["coins"].add(Coin(self.rect.x, self.rect.y-25, 'black'))

    def testTile(self):
        print(self.onScreen)