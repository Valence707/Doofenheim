import pygame

WIN_SIZE = [1600, 900]
DISPLAY_SIZE = [800, 450]
FPS = 60
GRAVITY = 0.5
debugMode = False
debugCooldown = 0
inventorySlotSize = [40, 40]
hotbarSize = [140, 50]
statsSize = [175, 95]
solids = pygame.sprite.Group()
clouds = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
coins = pygame.sprite.Group()
items = pygame.sprite.Group()
victory = False
gameState = "start"
currentLevel = "level_1"