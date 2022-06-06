import pygame
from pygame.locals import *
from data import DATA
from mouse import Mouse
from functions import *
from enemy import Enemy
from player import Player
from animations import *
from tile import Tile

pygame.init()

clock = pygame.time.Clock()

# Sprite groups
DATA["solids"] = pygame.sprite.Group()
DATA["clouds"] = pygame.sprite.Group()
DATA["enemies"] = pygame.sprite.Group()
DATA["bullets"] = pygame.sprite.Group()
DATA["playerBullets"] = pygame.sprite.Group()
DATA["enemyBullets"] = pygame.sprite.Group()
DATA["coins"] = pygame.sprite.Group()
DATA["WINDOW"] = pygame.display.set_mode(DATA["WIN_SIZE"])
DATA["DISPLAY"] = pygame.Surface(DATA["DISPLAY_SIZE"])
DATA["FONTS"] = {
    "default": pygame.font.SysFont(None, 22),
    "title": pygame.font.SysFont(None, 36)
}

pygame.display.set_icon(pygame.image.load('./images/icon.png'))
pygame.display.set_caption("Doofenheim's Pantless Adventure")

for i in range(9):
    DATA["clouds"].add(Cloud())

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
            if item == 'E':
                DATA["enemies"].add(Enemy((x*20, y*20-50)))
            elif item != '0':
                DATA["solids"].add(Tile(item, x, y))
            x+=1
        y+=1
    print(DATA["enemies"])

def game():
    load_level("level_1")
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
        if not DATA["inMenu"]:
            for cloud in DATA["clouds"]:
                cloud.animate()

            DATA["player"].update(keys)
            for enemy in DATA["enemies"]:
                enemy.update()

            for bullet in DATA["bullets"]:
                bullet.update()

        # Draw everything to DATA["DISPLAY"]
        DATA["clouds"].draw(DATA["DISPLAY"])
        DATA["solids"].draw(DATA["DISPLAY"])
        for enemy in DATA["enemies"]:
            enemy.draw()
        DATA["bullets"].draw(DATA["DISPLAY"])
        DATA["coins"].draw(DATA["DISPLAY"])
        DATA["player"].draw()

        if not DATA["inMenu"]:
            scroll()

        
        if keys[pygame.K_ESCAPE] and not DATA["menuCooldown"]:
            DATA["inMenu"] = True if not DATA["inMenu"] else False
            DATA["menuCooldown"] = 20

        if DATA["menuCooldown"]:
            DATA["menuCooldown"] -= 1

        stats()
        hotbar()
        
        debugMenu(keys)
        if DATA["inMenu"]:
            player_inventory()
            equipables_menu()
            shop()

        DATA["userMouse"].update()

        if DATA["gameOver"]:
            DATA["gameRun"] = False
            end_screen()
            break

        DATA["WINDOW"].blit(pygame.transform.scale(DATA["DISPLAY"], DATA["WIN_SIZE"]), (0, 0))
        pygame.display.flip()
        print(pygame.time.get_ticks()-start)
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
        clock.tick(DATA["FPS"])

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
        clock.tick(DATA["FPS"])

start_screen()
pygame.quit()