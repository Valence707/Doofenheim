import pygame
from pygame.locals import *
from data import DATA
from modules.mouse import Mouse
from modules.functions import *
from modules.enemy import Enemy
from modules.player import Player
from modules.animations import *
from modules.tile import Tile

pygame.init()

clock = pygame.time.Clock()

DATA["WINDOW"] = pygame.display.set_mode(DATA["WIN_SIZE"])
DATA["DISPLAY"] = pygame.Surface(DATA["DISPLAY_SIZE"])
DATA["FONTS"] = {
    "default": pygame.font.SysFont(None, 22),
    "title": pygame.font.SysFont(None, 36)
}

DATA["playerWalkImages"] = [
    pygame.image.load("./images/player_idle.png").convert(),
    pygame.image.load("./images/player_walk_1.png").convert(),
    pygame.image.load("./images/player_walk_2.png").convert()
]

for image in enumerate(DATA["playerWalkImages"]):
    DATA["playerWalkImages"][image[0]].set_colorkey((0, 255, 0))

pygame.display.set_icon(pygame.image.load('./images/icon.png'))
pygame.display.set_caption("Doofenheim's Pantless Adventure")

for i in range(9):
    DATA["clouds"].add(Cloud())
    
backgroundImage = pygame.image.load("./images/background.png").convert()
backgroundImage = pygame.transform.scale(backgroundImage, (DATA["DISPLAY_SIZE"][0], 100))
backgroundImage.set_colorkey((0, 255, 0))

DATA["enemies"].add(Enemy([-2000, 1000]))
DATA["gameRun"] = True
DATA["player"] = Player()
DATA["userMouse"] = Mouse()

# Load level data from text file
def load_level(path):
    world = []
    with open(F"levels/{path}.txt", "r") as worldObj:
        data = worldObj.read()
    data = data.split("\n")
    for row in data:
        world.append(row.split(","))

    y = 0
    for row in world:
        x = 0
        for item in row:
            if item != '0':
                Tile(item, x, y)
            x+=1
        y+=1

def game():
    load_level("test_level")
    while DATA["gameRun"]:
        start = pygame.time.get_ticks()
        DATA["DISPLAY"].fill((150, 150, 255))

        # Manage game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                DATA["gameRun"] = False

            if event.type == pygame.MOUSEWHEEL:
                DATA["player"].change_hand(event)

        keys = pygame.key.get_pressed()

        # Update the game
        for cloud in DATA["clouds"]:
            cloud.animate()

        DATA["player"].update(keys)
        for enemy in DATA["enemies"]:
            enemy.update()

        for bullet in DATA["bullets"]:
            bullet.update()

        DATA["DISPLAY"].blit(backgroundImage, (0, 350))
        DATA["clouds"].draw(DATA["DISPLAY"])
        DATA["solids"].draw(DATA["DISPLAY"])
        for enemy in DATA["enemies"]:
            enemy.draw()
        DATA["bullets"].draw(DATA["DISPLAY"])
        DATA["coins"].draw(DATA["DISPLAY"])
        DATA["player"].draw()

        scroll()

        stats()
        hotbar()
        
        debugMenu(keys)

        DATA["userMouse"].update()

        if DATA["gameOver"]:
            DATA["gameRun"] = False
            end_screen()
            break

        DATA["WINDOW"].blit(pygame.transform.scale(DATA["DISPLAY"], DATA["WIN_SIZE"]), (0, 0))
        pygame.display.flip()
        # print(pygame.time.get_ticks()-start)
        clock.tick(DATA["FPS"])

DATA["inStartScreen"] = True

def start_screen():
    while DATA["inStartScreen"]:
        DATA["DISPLAY"].fill((175, 175, 255))
        keys = pygame.key.get_pressed()

        startScreen(keys)
        if keys[pygame.K_SPACE]:
            DATA["inStartScreen"] = False
            DATA["gameRun"] = True
            game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                DATA["inStartScreen"] = False

        DATA["WINDOW"].blit(pygame.transform.scale(DATA["DISPLAY"], DATA["WIN_SIZE"]), (0, 0))
        pygame.display.flip()
        clock.tick(30)

def end_screen():
    while DATA["gameOver"]:
        DATA["DISPLAY"].fill((175, 175, 255))
        keys = pygame.key.get_pressed()

        endScreen(keys)

        if keys[pygame.K_q]:
            DATA["gameOver"] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                DATA["gameOver"] = False 
 
        DATA["WINDOW"].blit(pygame.transform.scale(DATA["DISPLAY"], DATA["WIN_SIZE"]), (0, 0))
        pygame.display.flip()
        clock.tick(40)

start_screen()
pygame.quit()