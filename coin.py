import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        if type == 'yellow':
            self.image = pygame.image.load('./images/yellow_coin.png')
            self.value = 1
        elif type == 'red':
            self.image = pygame.image.load('./images/red_coin.png')
            self.value = 5
        elif type == 'blue':
            self.image = pygame.image.load('./images/blue_coin.png')
            self.value = 10
        elif type == 'black':
            self.image = pygame.image.load('./images/black_coin.png')
            self.value = 50

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y