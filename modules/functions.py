import pygame
from data import DATA

def solidXCollision(sprite):
    collidedPlatform = pygame.sprite.spritecollideany(sprite, DATA["solids"])
    if collidedPlatform != None:
        if sprite.rect.left < collidedPlatform.rect.left:
            sprite.rect.right = collidedPlatform.rect.left
        else:
            sprite.rect.x = collidedPlatform.rect.right
        sprite.vel[0] = 0
        return True
    return False

def solidYCollision(sprite):
    collidedPlatform = pygame.sprite.spritecollideany(sprite, DATA["solids"])
    if collidedPlatform != None:
        if sprite.rect.top < collidedPlatform.rect.top:
            sprite.rect.bottom = collidedPlatform.rect.top
            sprite.inAir = False
        else:
            sprite.rect.y = collidedPlatform.rect.bottom
        sprite.vel[1] = 0
        return True
    return False

def healthBar(sprite, width, height, x, y):
    healthRemaining = pygame.Surface((width*(sprite.health/sprite.maxHealth) if sprite.health > 0 else 0, height))
    healthTotal = pygame.Surface((width, height))

    pygame.Surface.fill(healthRemaining, (255, 0, 0))
    pygame.Surface.fill(healthTotal, (0, 0, 0))

    DATA["DISPLAY"].blit(healthTotal, (x, y))
    DATA["DISPLAY"].blit(healthRemaining, (x, y))

def unload_current_level():
    DATA["clouds"].empty()
    DATA["solids"].empty()
    DATA["enemies"].empty()
    DATA["coins"].empty()

# "Scroll" the game to follow the DATA["player"].
def scroll():
    SCROLL_AMOUNT = [-1*int((DATA["player"].rect.x-DATA["DISPLAY_SIZE"][0]/2+DATA["player"].rect.width/2)/4), -1*int((DATA["player"].rect.y-DATA["DISPLAY_SIZE"][1]/2+DATA["player"].rect.height/2)/6)]

    DATA["player"].rect = DATA["player"].rect.move(SCROLL_AMOUNT)
    
    DATA["player"].spawn[0] += SCROLL_AMOUNT[0]
    DATA["player"].spawn[1] += SCROLL_AMOUNT[1]

    for sprite in DATA["solids"]:
        sprite.rect = sprite.rect.move(SCROLL_AMOUNT)

    if len(DATA["bullets"]):
        for bullet in DATA["bullets"]:
            bullet.compPos = [bullet.compPos[0]+SCROLL_AMOUNT[0], bullet.compPos[1]+SCROLL_AMOUNT[1]]

    for cloud in DATA["clouds"]:
        cloud.rect = cloud.rect.move(SCROLL_AMOUNT[0]/cloud.scrollIntensity, 0)

    for enemy in DATA["enemies"]:
        enemy.rect = enemy.rect.move(SCROLL_AMOUNT)

    for coin in DATA["coins"]:
        coin.rect = coin.rect.move(SCROLL_AMOUNT)

# Player Hotbar
hotbarSlots = [pygame.Surface(DATA["inventorySlotSize"]) for i in range(3)]
for slot in hotbarSlots:
    pygame.Surface.fill(slot, (190, 190, 190))

hotbarContainer = pygame.Surface(DATA["hotbarSize"])
hotbarBorder = pygame.Surface((DATA["hotbarSize"][0]+4, DATA["hotbarSize"][1]+4))
hotbarContainer.set_alpha(225)
hotbarBorder.set_alpha(225)

pygame.Surface.fill(hotbarBorder, (0, 0, 0))
handBorder = pygame.Surface((DATA["inventorySlotSize"][0]+4, DATA["inventorySlotSize"][1]+4))

def hotbar():
    pygame.Surface.fill(hotbarContainer, (255, 255, 255))
    hotbarContainer.blit(handBorder, (DATA["player"].hand*(DATA["inventorySlotSize"][0]+5)+3, 3))
    for slot in enumerate(hotbarSlots):
        hotbarContainer.blit(slot[1], (slot[0]*(DATA["inventorySlotSize"][0]+5)+5, 5))
        if DATA["player"].hotbar[slot[0]]:
            slot[1].blit(DATA["player"].hotbar[slot[0]].image, (0, 0))
    hotbarBorder.blit(hotbarContainer, (2, 2))
    DATA["DISPLAY"].blit(hotbarBorder, (2, 2))

# Debug Menu
def debugMenu(keys):
    if DATA["debugCooldown"]:
        DATA["debugCooldown"]-=1
    elif keys[pygame.K_d] and keys[pygame.K_b] and keys[pygame.K_g]:
        DATA["debugMode"] = False if DATA["debugMode"] else False
        DATA["debugCooldown"] = 60

    if DATA["debugMode"]:
        DATA["DISPLAY"].blit(DATA["FONTS"]["default"].render("MOUSE POS: {}, {} PLAYER POS: {}, {}".format(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], DATA["player"].rect.x, DATA["player"].rect.y), True, (0, 0, 0)), (15, 15))

# Player Stats
statsContainer = pygame.Surface(DATA["statsSize"])
statsBorder = pygame.Surface((DATA["statsSize"][0]+4, DATA["statsSize"][1]+4))
statsBorder.set_alpha(225)
statsContainer.set_alpha(225)

pygame.Surface.fill(statsBorder, (0, 0, 0))
redHeart = pygame.image.load('./images/red_heart.png')
redHeart.set_colorkey((0, 255, 0))
blackHeart = pygame.image.load('./images/black_heart.png')
blackHeart.set_colorkey((0, 255, 0))
def stats():
    pygame.Surface.fill(statsContainer, (255, 255, 255))
    textLines = [
        DATA["FONTS"]["default"].render("Doofenheim's Stats", True, (0, 0, 0)),
        DATA["FONTS"]["default"].render("Money: ${}".format(DATA["player"].money), True, (0, 0, 0)),
        DATA["FONTS"]["default"].render("Health:", True, (0, 0, 0)),
        DATA["FONTS"]["default"].render("Ammo: {}".format(DATA["player"].hotbar[DATA["player"].hand].ammo), True, (0, 0, 0)) if DATA["player"].hotbar[DATA["player"].hand].ammo != -1 else DATA["FONTS"]['default'].render("", True, (0, 0, 0)),
        DATA["FONTS"]["default"].render("enemies: {}".format(len(DATA["enemies"])), True, (0, 0, 0))
    ]

    for line in enumerate(textLines):
        statsContainer.blit(line[1], (5, 5+line[0]*15))

    for i in range(0, 3):
        statsContainer.blit(redHeart if i < DATA["player"].lives else blackHeart, (12*i+137, 37))

    DATA["DISPLAY"].blit(statsBorder, (618, 3))
    statsBorder.blit(statsContainer, (2, 2))
    healthBar(DATA["player"], 75, 10, 680, 42)

# End Screen
DATA["endSize"] = [DATA["DISPLAY_SIZE"][0]-50, DATA["DISPLAY_SIZE"][1]-50]
endContainer = pygame.Surface(DATA["endSize"])
endBorder = pygame.Surface((DATA["endSize"][0]+4, DATA["endSize"][1]+4))
def endScreen(keys):
    pygame.Surface.fill(endContainer, (255, 255, 255))
    textLines = [
        DATA["FONTS"]["title"].render(F"GAME OVER", True, (0, 0, 0))
    ]

    for line in textLines:
        endContainer.blit(line, (int(DATA["endSize"][0]/2-line.get_size()[0]/2), 15))
    
    DATA["DISPLAY"].blit(endBorder, (23, 23))
    endBorder.blit(endContainer, (2, 2))

# Start Screen
DATA["startSize"] = [DATA["DISPLAY_SIZE"][0]-50, DATA["DISPLAY_SIZE"][1]-50]
startContainer = pygame.Surface(DATA["startSize"])
startBorder = pygame.Surface((DATA["startSize"][0]+4, DATA["startSize"][1]+4))
def startScreen(keys):
    pygame.Surface.fill(startContainer, (255, 255, 255))
    textLines = [
        DATA["FONTS"]["title"].render(F"Doofenheim's Pantless Adventure", True, (0, 0, 0)),
        DATA["FONTS"]["title"].render(F"", True, (0, 0, 0)),
        DATA["FONTS"]["default"].render(F"Press 'Space' to start!", True, (0, 0, 0)),
    ]

    for line in enumerate(textLines):
        startContainer.blit(line[1], (int(DATA["startSize"][0]/2-line[1].get_size()[0]/2), line[0]*22+10))
    
    DATA["DISPLAY"].blit(startBorder, (23, 23))
    startBorder.blit(startContainer, (2, 2))

def walk_anim(sprite, animImages):
    sprite.lastFrame = pygame.time.get_ticks() if not sprite.lastFrame else sprite.lastFrame

    if (pygame.time.get_ticks() - sprite.lastFrame) / 1000 > 0.25 and abs(sprite.vel[0]):
        sprite.lastFrame = pygame.time.get_ticks()
        sprite.animFrame = sprite.animFrame + 1 if sprite.animFrame + 1 < len(animImages) else 0
        sprite.image = animImages[sprite.animFrame]
        if sprite.facing == "L":
            sprite.image = pygame.transform.flip(sprite.image, True, False)
    elif not abs(sprite.vel[0]):
        sprite.image = sprite.idleImage