import pygame, data

def solidXCollision(sprite):
    collidedPlatform = pygame.sprite.spritecollideany(sprite, data.solids)
    if collidedPlatform != None:
        if sprite.rect.left < collidedPlatform.rect.left:
            sprite.rect.right = collidedPlatform.rect.left
        else:
            sprite.rect.x = collidedPlatform.rect.right
        sprite.vel[0] = 0
        return True
    return False

def solidYCollision(sprite):
    collidedPlatform = pygame.sprite.spritecollideany(sprite, data.solids)
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

    data.DISPLAY.blit(healthTotal, (x, y))
    data.DISPLAY.blit(healthRemaining, (x, y))

def unload_current_level():
    for cloud in data.clouds:
        cloud.kill()
        del cloud

    for solid in data.solids:
        solid.kill()
        del solid

    for enemy in data.enemies:
        enemy.kill()
        del enemy
        
    for coin in data.coins:
        coin.kill()
        del coin
        
    for item in data.items:
        item.kill()
        del item
        
    for bullet in data.bullets:
        bullet.kill()
        del bullet

# "Scroll" the game to follow the data.player.
def scroll():
    SCROLL_AMOUNT = [-1*int((data.player.rect.center[0]-data.DISPLAY_SIZE[0]/2)), -1*int((data.player.rect.center[1]-data.DISPLAY_SIZE[1]/2))]

    data.player.rect = data.player.rect.move(SCROLL_AMOUNT)
    data.chunkPos[0] += SCROLL_AMOUNT[0]
    data.chunkPos[1] += SCROLL_AMOUNT[1]
    
    data.player.spawn[0] += SCROLL_AMOUNT[0]
    data.player.spawn[1] += SCROLL_AMOUNT[1]

    for solid in data.solids:
        solid.rect = solid.rect.move(SCROLL_AMOUNT)

    if len(data.bullets):
        for bullet in data.bullets:
            bullet.compPos = [bullet.compPos[0]+SCROLL_AMOUNT[0], bullet.compPos[1]+SCROLL_AMOUNT[1]]

    for cloud in data.clouds:
        cloud.rect = cloud.rect.move(SCROLL_AMOUNT[0]/cloud.scrollIntensity, SCROLL_AMOUNT[1])

    for enemy in data.enemies:
        enemy.rect = enemy.rect.move(SCROLL_AMOUNT)

    for coin in data.coins:
        coin.rect = coin.rect.move(SCROLL_AMOUNT)

    for item in data.items:
        item.rect = item.rect.move(SCROLL_AMOUNT)

# Player Hotbar
hotbarSlots = [pygame.Surface(data.inventorySlotSize) for i in range(3)]
for slot in hotbarSlots:
    pygame.Surface.fill(slot, (190, 190, 190))

hotbarContainer = pygame.Surface(data.hotbarSize)
hotbarBorder = pygame.Surface((data.hotbarSize[0]+4, data.hotbarSize[1]+4))
hotbarBorder.set_alpha(225)

pygame.Surface.fill(hotbarBorder, (0, 0, 0))
handBorder = pygame.Surface((data.inventorySlotSize[0]+4, data.inventorySlotSize[1]+4))

hotbarImages = [pygame.image.load("./images/pistol.png").convert(), pygame.image.load("./images/shotgun.png").convert(), pygame.image.load("./images/machine_gun.png").convert()]
for i in enumerate(hotbarImages):
    hotbarImages[i[0]] = pygame.transform.scale(i[1], data.inventorySlotSize)
    hotbarImages[i[0]].set_colorkey((0, 255, 0))

def hotbar():
    pygame.Surface.fill(hotbarContainer, (255, 255, 255))
    hotbarContainer.blit(handBorder, (data.player.hand*(data.inventorySlotSize[0]+5)+3, 3))

    for slot in enumerate(hotbarSlots):
        pygame.Surface.fill(slot[1], (150, 150, 150))
        slot[1].blit(hotbarImages[slot[0]], (0, -3))
        slot[1].blit(data.FONTS["default"].render(str(data.player.gunAmmo[slot[0]]), False, (0, 0, 0)), (14, 27))
        hotbarContainer.blit(slot[1], (slot[0]*(data.inventorySlotSize[0]+5)+5, 5))

    hotbarBorder.blit(hotbarContainer, (2, 2))
    data.DISPLAY.blit(hotbarBorder, (2, 2))

# Debug Menu
def debugMenu(keys):
    if data.debugCooldown:
        data.debugCooldown-=1
    elif keys[pygame.K_d] and keys[pygame.K_b] and keys[pygame.K_g]:
        data.debugMode = False if data.debugMode else True
        print("DEBUG ON" if data.debugMode else "DEBUG OFF")
        data.debugCooldown = 60

    if data.debugMode:
        if keys[pygame.K_h]:
            data.player.health = data.player.maxHealth
            data.player.lives = 3
            
        if keys[pygame.K_k]:
            data.player.health -= 1
        data.DISPLAY.blit(data.FONTS["default"].render("MOUSE POS: {}, {} PLAYER POS: {}, {}".format(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], data.player.rect.x, data.player.rect.y), True, (0, 0, 0)), (15, 15))

# Player Stats
statsContainer = pygame.Surface(data.statsSize)
statsBorder = pygame.Surface((data.statsSize[0]+4, data.statsSize[1]+4))
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
        data.FONTS["default"].render("Doofenheim's Stats", True, (0, 0, 0)),
        data.FONTS["default"].render("Money: ${}".format(data.player.money), True, (0, 0, 0)),
        data.FONTS["default"].render("Health:", True, (0, 0, 0)),
        data.FONTS["default"].render("enemies: {}".format(len(data.enemies)), True, (0, 0, 0))
    ]

    for line in enumerate(textLines):
        statsContainer.blit(line[1], (5, 5+line[0]*15))

    for i in range(0, 3):
        statsContainer.blit(redHeart if i < data.player.lives else blackHeart, (12*i+132, 32))

    data.DISPLAY.blit(statsBorder, (618, 3))
    statsBorder.blit(statsContainer, (2, 2))
    healthBar(data.player, 75, 10, 680, 42)

# End Screen
data.endSize = [data.DISPLAY_SIZE[0]-50, data.DISPLAY_SIZE[1]-50]
endContainer = pygame.Surface(data.endSize)
endBorder = pygame.Surface((data.endSize[0]+4, data.endSize[1]+4))
def endScreen(keys):
    pygame.Surface.fill(endContainer, (255, 255, 255))
    textLines = [
        data.FONTS["title"].render(F"GAME OVER", True, (0, 0, 0))
    ]

    for line in textLines:
        endContainer.blit(line, (int(data.endSize[0]/2-line.get_size()[0]/2), 15))
    
    data.DISPLAY.blit(endBorder, (23, 23))
    endBorder.blit(endContainer, (2, 2))

# Start Screen
data.startSize = [data.DISPLAY_SIZE[0]-50, data.DISPLAY_SIZE[1]-50]
startContainer = pygame.Surface(data.startSize)
startBorder = pygame.Surface((data.startSize[0]+4, data.startSize[1]+4))
def startScreen(keys):
    pygame.Surface.fill(startContainer, (255, 255, 255))
    textLines = [
        data.FONTS["title"].render("Doofenheim's Madness", True, (0, 0, 0)),
        data.FONTS["title"].render("", True, (0, 0, 0)),
        data.FONTS["default"].render("Press 'Space' to start!", True, (0, 0, 0)),
    ]

    for line in enumerate(textLines):
        startContainer.blit(line[1], (int(data.startSize[0]/2-line[1].get_size()[0]/2), line[0]*22+10))
    
    data.DISPLAY.blit(startBorder, (23, 23))
    startBorder.blit(startContainer, (2, 2))

nextLevelContainer = pygame.Surface(data.startSize)
nextLevelBorder = pygame.Surface((data.startSize[0]+4, data.startSize[1]+4))
def nextLevelScreen():
    pygame.Surface.fill(nextLevelContainer, (255, 255, 255))
    textLines = [
        data.FONTS["title"].render("Level Cleared!", True, (0, 0, 0)),
        data.FONTS["title"].render("", True, (0, 0, 0)),
        data.FONTS["title"].render("Money Collected: {}".format(data.playerStats[0]), True, (0, 0, 0)),
        data.FONTS["title"].render("Enemies Killed: {}".format(data.playerStats[1]), True, (0, 0, 0)),
        data.FONTS["title"].render("Time: {} seconds".format(round((data.playerStats[3] - data.playerStats[2]) / 1000), 2), True, (0, 0, 0)),
        data.FONTS["title"].render("", True, (0, 0, 0)),
        data.FONTS["default"].render("Press 'Space' to advance!", True, (0, 0, 0)),
    ]

    for line in enumerate(textLines):
        nextLevelContainer.blit(line[1], (int(data.startSize[0]/2-line[1].get_size()[0]/2), line[0]*22+10))
    
    data.DISPLAY.blit(nextLevelBorder, (23, 23))
    nextLevelBorder.blit(nextLevelContainer, (2, 2))
