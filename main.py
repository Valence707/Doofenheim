import pygame, data

pygame.init()
data.WINDOW = pygame.display.set_mode(data.WIN_SIZE)
data.DISPLAY = pygame.Surface(data.DISPLAY_SIZE)
pygame.display.set_icon(pygame.image.load('./images/icon.png'))
pygame.display.set_caption("Doofenheim's Madness")

from pygame.locals import *
from functions import *
from entities import *
from animations import *
from terrain import Tile

# Initialization

clock = pygame.time.Clock()

data.FONTS = {
    "default": pygame.font.SysFont(None, 22),
    "title": pygame.font.SysFont(None, 36)
}

data.enemyDeathSound = pygame.mixer.Sound("./sounds/enemy_die.ogg")
data.enemyHitSound = pygame.mixer.Sound("./sounds/hit.ogg")
data.backgroundMusic = pygame.mixer.Sound("./sounds/background_music_1.ogg")
data.backgroundMusic.play(100, 0, 500)

backgroundImage = pygame.image.load("./images/background.png").convert()
backgroundImage = pygame.transform.scale(backgroundImage, (data.DISPLAY_SIZE[0], 100))
backgroundImage.set_colorkey((0, 255, 0))

# Load level data. from text file
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
            if item != '`':
                Tile(item, x, y)
            x+=1
        y+=1

def load_chunk(index):
    print(index)

def main():
    chunkIndex = [0, 0]
    data.chunkPos = [0, 0]
    loadedChunks = {}
    run = True
    while run:
        start = pygame.time.get_ticks()
        data.DISPLAY.fill((160, 160, 255))
        data.FPS = 60 if data.gameState == "game" else 30
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            run = False

        if data.gameState == "start":
            startScreen(keys)
            if keys[pygame.K_SPACE]:
                data.gameState = "game"
                for i in range(9):
                    data.clouds.add(Cloud())
                load_level(data.currentLevel)
                for image in enumerate(data.player.images):
                    image[1].convert()
                    image[1].set_colorkey((0, 255, 0))

        elif data.gameState == "game":

            # Update the game
            for cloud in data.clouds:
                cloud.animate()

            data.DISPLAY.blit(backgroundImage, (0, 350))
            data.clouds.draw(data.DISPLAY)
            data.solids.draw(data.DISPLAY)
            data.items.draw(data.DISPLAY)

            data.enemies.update()
            data.bullets.update()
            data.enemies.draw(data.DISPLAY)
            data.bullets.draw(data.DISPLAY)

            data.coins.draw(data.DISPLAY)
            data.player.draw()
            data.player.update(keys)

            scroll()
            stats()
            hotbar()

            if data.chunkPos[0] < -200:
                
                chunkIndex[0] += 1
                data.chunkPos[0] += 200

                for i in range(4):
                    if F"{chunkIndex[0]-1},{chunkIndex[1]+i}" in list(loadedChunks.keys()):
                        del loadedChunks[F"{chunkIndex[0]-1},{chunkIndex[1]+i}"]
                    loadedChunks[F"{chunkIndex[0]+6},{chunkIndex[1]+i}"] = "TEST"
                load_chunk(chunkIndex)
                
            elif data.chunkPos[0] > 0:
                chunkIndex[0] -= 1
                data.chunkPos[0] -= 200

                for i in range(4):
                    if F"{chunkIndex[0]+6},{chunkIndex[1]+i}" in list(loadedChunks.keys()):
                        del loadedChunks[F"{chunkIndex[0]+6},{chunkIndex[1]+i}"]
                    loadedChunks[F"{chunkIndex[0]},{chunkIndex[1]+i}"] = "TEST"
                load_chunk(chunkIndex)

            if data.chunkPos[1] < -200:
                chunkIndex[1] += 1
                data.chunkPos[1] += 200

                for i in range(4):
                    if F"{chunkIndex[0]+i},{chunkIndex[1]-1}" in list(loadedChunks.keys()):
                        del loadedChunks[F"{chunkIndex[0]+i},{chunkIndex[1]-1}"]
                    loadedChunks[F"{chunkIndex[0]+i},{chunkIndex[1]+4}"] = "TEST"
                load_chunk(chunkIndex)

            elif data.chunkPos[1] > 0:
                chunkIndex[1] -= 1
                data.chunkPos[1] -= 200

                for i in range(4):
                    if F"{chunkIndex[0]+i},{chunkIndex[1]+4}" in list(loadedChunks.keys()):
                        del loadedChunks[F"{chunkIndex[0]+i},{chunkIndex[1]+4}"]
                    loadedChunks[F"{chunkIndex[0]+i},{chunkIndex[1]}"] = "TEST"
                load_chunk(chunkIndex)

            debugMenu(keys)

            # Go to next level or end game
            if data.player.lives == 0 or data.victory:
                data.gameState = "nextLevelScreen" if data.victory else "endScreen" if data.player.lives == 0 else "winScreen"
                if data.gameState != "endScreen":
                    data.player.totalTime = round((data.player.startTime - pygame.time.get_ticks()) / 1000, 2)
                    data.player.startTime = 0
                unload_current_level()
                data.playerStats = [data.player.money, data.player.enemiesKilled, data.player.startTime, pygame.time.get_ticks()]
                data.victory = False
                data.player.kill()
                del data.player

        elif data.gameState == "endScreen":

            endScreen(keys)

            if keys[pygame.K_q]:
                run = False

        elif data.gameState == "nextLevelScreen":
            nextLevelScreen()
            if keys[pygame.K_SPACE]:
                data.currentLevel = "level_2"
                data.gameState = "game"
                data.playerStats = []
                load_level(data.currentLevel)
                for image in enumerate(data.player.images):
                    image[1].convert()
                    image[1].set_colorkey((0, 255, 0))
                for i in range(9):
                    data.clouds.add(Cloud())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEWHEEL:
                data.player.change_hand(event)

        data.WINDOW.blit(pygame.transform.scale(data.DISPLAY, data.WIN_SIZE), (0, 0))
        pygame.display.flip()
        # print(pygame.time.get_ticks()-start)
        clock.tick(data.FPS)

main()
pygame.quit()