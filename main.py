import math
import random
import pygame as pg
from pygame.locals import *

DATA = {
    "WIN_SIZE": [1600, 900],
    "DISPLAY_SIZE": [800, 450],
    "FPS": 60,
    "GRAVITY": 0.5,
    "GAME_OVER": False,
}

pg.init()

win = pg.display.set_mode(DATA["WIN_SIZE"])
pg.display.set_icon(pg.image.load('./images/icon.png'))
pg.display.set_caption("Doofenheim's Pantless Adventure")

clock = pg.time.Clock()

myFonts = {
    "default": pg.font.SysFont(None, 22),
    "title": pg.font.SysFont(None, 36)
}

class Mouse(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.winPos = [0, 0]
        self.pos = pg.math.Vector2(0, 0)
        self.selected = None

    def update(self):
        self.winPos = pg.mouse.get_pos()
        self.pos.x, self.pos.y = int(self.winPos[0]*(DATA["DISPLAY_SIZE"][0]/DATA["WIN_SIZE"][0])), int(self.winPos[1]*(DATA["DISPLAY_SIZE"][1]/DATA["WIN_SIZE"][1]))
        self.rect.x, self.rect.y = self.pos

class Tile(pg.sprite.Sprite):
    """The world terrain objects"""
    def __init__(self, tileType, x, y):
        super().__init__()
        self.SIZE = [20, 20]
        if tileType == '1':
            self.image = pg.image.load('./images/dirt_top.png')
        elif tileType == '2':
            self.image = pg.image.load('./images/dirt_side.png')
        elif tileType == '3':
            self.image = pg.image.load('./images/stone.png')
        elif tileType == 'S':
            self.image = pg.image.load("./images/spawn.png")
            player.rect.x, player.rect.y = x*self.SIZE[0], y*self.SIZE[1]-player.rect.height-10
            player.spawn = [x*self.SIZE[0], y*self.SIZE[1]-player.rect.height-10]
        else:
            print("INVALID TILE TYPE: ", type(tileType), tileType)
            pg.quit()

        # Cause of ugly tiles. Need to resize all tile images to be 20x20px
        self.image = pg.transform.scale(self.image, self.SIZE)
            
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x*self.SIZE[0], y*self.SIZE[1]

        # Randomly generate a coin above the surface
        if tileType == '1' and not pg.sprite.spritecollideany(Coin(self.rect.x, self.rect.y-25, 'yellow'), solids):
            randCoin = random.randrange(0, 300)
            if randCoin < 60:
                coins.add(Coin(self.rect.x, self.rect.y-25, "yellow"))
            elif randCoin >= 60 and randCoin < 90:
                coins.add(Coin(self.rect.x, self.rect.y-25, "red"))
            elif randCoin >= 90 and randCoin < 99: 
                coins.add(Coin(self.rect.x, self.rect.y-25, "blue"))
            elif randCoin == 100:
                coins.add(Coin(self.rect.x, self.rect.y-25, 'black'))

class Cloud(pg.sprite.Sprite):
    """Moving clouds"""
    def __init__(self, pos=[0, 0]):
        super().__init__()
        self.image = pg.image.load(F"./images/cloud_{random.randrange(1, 4)}.png")
        randomSizeFactor = random.randrange(1, 6)
        self.image = pg.transform.scale(self.image, (self.image.get_width()*randomSizeFactor, self.image.get_height()*randomSizeFactor))
        self.rect = self.image.get_rect()

        self.compPos = [pos[0] if pos[0] else int(random.randrange(0, DATA["DISPLAY_SIZE"][0]-150)), pos[1] if pos[1] else int(random.randrange(0, DATA["DISPLAY_SIZE"][1]-150))]
        self.rect.x, self.rect.y = self.compPos
        self.vel = [round(random.uniform(0.1, 0.5), 2), 0]
        self.scrollIntensity = 100/self.vel[0]

    def animate(self):
        self.compPos = [
            -1*self.rect.width if self.rect.left > DATA["DISPLAY_SIZE"][0] and self.vel[0] > 0 else DATA["DISPLAY_SIZE"][0] if self.rect.right < 0 and self.vel[0] < 0 else self.compPos[0]+self.vel[0],
            int(random.randrange(0, DATA["DISPLAY_SIZE"][1]-150)) if self.rect.left > DATA["DISPLAY_SIZE"][0] and self.vel[0] > 0 else int(random.randrange(0, DATA["DISPLAY_SIZE"][1]-150)) if self.rect.right < 0 and self.vel[0] < 0 else self.compPos[1]+self.vel[1]
        ]
        
        self.compPos = [self.compPos[0]+self.vel[0], self.compPos[1]+self.vel[1]]
        self.rect.x, self.rect.y = math.floor(self.compPos[0]), math.floor(self.compPos[1])

class Item(pg.sprite.Sprite):
    def __init__(self, name, ammo=0, image=None, action=None, cooldown=None, amount=1, autoUse=False):
        super().__init__()
        self.image = pg.Surface((30, 30))
        self.action = action
        self.name = name
        self.cooldown = cooldown
        self.ammo = ammo
        self.autoUse = autoUse
        self.lastUsed = pg.time.get_ticks()
        self.hasBeenUsed = False
        self.image = pg.image.load(F"./images/{image}")
        self.image = pg.transform.scale(self.image, inventorySlotSize)
        self.rect = self.image.get_rect()
        self.kill()

    def use(self):
        if round((pg.time.get_ticks()-self.lastUsed)/1000, 2) >= self.cooldown:
            self.action(self)
            self.lastUsed = pg.time.get_ticks()

class Bullet(pg.sprite.Sprite):
    def __init__(self, origin, dest, type, gun):
        super().__init__()
        self.image = pg.image.load("./images/bullet.png")
        self.rect = self.image.get_rect()
        self.maxVel = 15
        self.dmg = 10
        if type == 'player':
            self.dmg = 10
            playerBullets.add(self)
        elif type == 'enemy':
            self.dmg = 5
            self.maxVel = 7
            enemyBullets.add(self)

        self.compPos = origin
        self.rect.x, self.rect.y = origin
        delta = pg.math.Vector2(dest[0]*(DATA["DISPLAY_SIZE"][0]/DATA["WIN_SIZE"][0]), dest[1]*(DATA["DISPLAY_SIZE"][1]/DATA["WIN_SIZE"][1])) - origin
        direction = delta.normalize()

        if gun == 'shotgun':
            direction.x, direction.y = direction[0]+(random.uniform(-0.15, 0.15)), direction[1]+(random.uniform(-0.15, 0.15))
        elif gun == 'pistol':
            direction = direction

        self.vel = direction*self.maxVel
        self.duration = 3
        self.initTime = pg.time.get_ticks()

    def update(self):
        self.compPos = [round(self.compPos[0]+self.vel[0], 2), round(self.compPos[1]+self.vel[1], 2)]
        self.rect.x, self.rect.y = self.compPos
        if (pg.time.get_ticks()-self.initTime) / 1000 > self.duration or pg.sprite.spritecollideany(self, solids):
            self.kill()

        # Add collision detection

class Coin(pg.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        if type == 'yellow':
            self.image = pg.image.load('./images/yellow_coin.png')
            self.value = 1
        elif type == 'red':
            self.image = pg.image.load('./images/red_coin.png')
            self.value = 5
        elif type == 'blue':
            self.image = pg.image.load('./images/blue_coin.png')
            self.value = 10
        elif type == 'black':
            self.image = pg.image.load('./images/black_coin.png')
            self.value = 50

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Player(pg.sprite.Sprite):
    """Sprite controlled by player, used to interact with environment"""
    def __init__(self, pos=[round((DATA["DISPLAY_SIZE"][0]/2)-10, 2), round((DATA["DISPLAY_SIZE"][1]/2)-10)], size=[25, 50]):
        super().__init__()
        self.image = pg.image.load("./images/player.png")
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = self.compPos[0], self.compPos[1]
        self.spawn = [0, 0]

        self.vel = [0, 0]
        self.maxVel = 6
        self.jumpVel = -12
        self.inAir = True
        self.acc = 0.75
        self.dir = [0, 0]

        self.coinsCollected = 0
        self.enemiesKilled = 0
        self.ammo = 30
        self.health = 100
        self.lives = 3
        self.maxHealth = 100
        self.hand = 0
        self.hotbar = [
            Item('pistol', 30,'pistol.png', pistol_shoot, 0.25), Item('shotgun', 5, 'shotgun.png', shotgun_shoot, 1), Item('knife', 0, 'knife.png')
        ]
        self.inventory = [
            '', '', '',
            '', '', '',
        ]
        self.accessories = [
            '', '', ''
        ]
        self.vanity = [
            '', '', ''
        ]
        self.armor = [
            '', '', ''
        ]

    def update(self, keys):
        player.movePlayer(keys, solids)
        collectedCoin = pg.sprite.spritecollideany(self, coins)
        if collectedCoin:
            collectedCoin.kill()
            player.coinsCollected+=collectedCoin.value

        if keys[pg.K_q]:
            global gameRun
            gameRun = False

        if keys[pg.K_k] and debugMode:
            self.health -= 10

        if pg.mouse.get_pressed()[0]:
            if self.hotbar[self.hand]:
                self.hotbar[self.hand].use()
        else:
            self.hasShot = False

        if self.health <= 0:
            self.lives -= 1
            self.ammo = 30
            self.rect.x, self.rect.y = player.spawn[0], player.spawn[1]
            self.health = 100

        # End the game
        global gameOver
        if self.lives == 0 or len(enemies) <= 0:
            gameOver = True
            unload_current_level()

    def movePlayer(self, keys, solids):
        self.dir = [0, 0]

        # Manage player movement
        if keys[pg.K_a]:
            self.dir[0] = -1
        elif self.vel[0] < 0:
            self.dir[0] = 1

        if keys[pg.K_s]:
            self.dir[1] = 1

        if keys[pg.K_d]:
            self.dir[0] = 1
        elif self.vel[0] > 0:
            self.dir[0] = -1

        if keys[pg.K_SPACE]:
            if not self.inAir:
                self.vel[1]= self.jumpVel
                self.inAir = True

        if self.vel[1] < 12:
            self.vel[1]+=DATA["GRAVITY"]

        newVel = [round(self.vel[0]+self.acc*self.dir[0], 2), round(self.vel[1]+self.acc*self.dir[1], 2)]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            solidXCollision(self)

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        bulletCollided = pg.sprite.spritecollideany(self, enemyBullets)
        if bulletCollided:
            self.health -= bulletCollided.dmg
            bulletCollided.kill()

        if keys[pg.K_1] or keys[pg.K_2] or keys[pg.K_3]:
            self.change_hand(keys=keys)

    def change_hand(self, event=None, keys=None, pos=0):
        newHand = self.hand-event.y if (event != None and event.type == pg.MOUSEWHEEL and abs(event.y)) else 0 if keys[pg.K_1] else 1 if keys[pg.K_2] else 2 if keys[pg.K_3] else pos
        self.hand = 2 if newHand < 0 else 0 if newHand > 2 else newHand
        
    def draw(self):
        display.blit(self.image, (self.rect.x, self.rect.y))

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load("./images/enemy.png")
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = pos
        self.vel = [0, 0]

        self.dir = [random.randrange(-1, 2, 2), 0]

        self.maxVel = random.randrange(1, 4)
        self.inAir = True
        self.acc = 1
        self.health = 30
        self.maxHealth = 30
        self.shotDelay = random.randrange(3, 7)
        self.lastShot = pg.time.get_ticks()

    def update(self):
        if self.vel[1] <= 12:
            self.vel[1]+=DATA["GRAVITY"]

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            if solidXCollision(self):
                self.dir[0] *= -1

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        if (pg.time.get_ticks() - self.lastShot) / 1000 >= self.shotDelay:
            self.lastShot = pg.time.get_ticks()
            bullets.add(Bullet(self.rect.center, player.rect.center, 'enemy', 'pistol'))

        detectPlatformFall(self)
        newVel = [self.vel[0]+self.acc*self.dir[0], self.vel[1]+self.acc*self.dir[1]]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        bulletCollided = pg.sprite.spritecollideany(self, playerBullets)
        if bulletCollided:
            self.health -= bulletCollided.dmg
            bulletCollided.kill()

        if self.health <= 0:
            self.kill()
            player.enemiesKilled += 1
            player.hotbar[player.hand].ammo += random.randrange(1, 7)

    def draw(self):
        healthBar(self, self.rect.width, 5, self.rect.x, self.rect.y-10)
        display.blit(self.image, (self.rect.x, self.rect.y))

# Debug Menu
# Displays debug info
debugMode = False
debugCooldown = 0
def debugMenu(keys):
    global debugMode
    global debugCooldown

    if keys[pg.K_d] and keys[pg.K_b] and keys[pg.K_g]:
        if debugCooldown == 0:
            if debugMode:
                debugMode = False
            else:
                debugMode = True
            debugCooldown = 60

    if debugCooldown:
        debugCooldown-=1

    if debugMode:
        display.blit(myFonts["default"].render(F"MOUSE POS: {pg.mouse.get_pos()[0]}, {pg.mouse.get_pos()[1]}\nPLAYER POS: {player.rect.x}, {player.rect.y}", True, (0, 0, 0)), (15, 15))

inMenu = False
menuCooldown = 0

inventorySlotSize = [45, 45]
inventorySlots = [pg.Surface(inventorySlotSize) for i in range(6)]

for slot in inventorySlots:
    pg.Surface.fill(slot, (190, 190, 190))

# Player Inventory
inventorySize = [155, 105]
inventoryContainer = pg.Surface(inventorySize)
inventoryBorder = pg.Surface((inventorySize[0]+4, inventorySize[1]+4))
inventoryBorder.set_alpha(225)
inventoryContainer.set_alpha(225)

pg.Surface.fill(inventoryBorder, (0, 0, 0))

def player_inventory():
    pg.Surface.fill(inventoryContainer, (255, 255, 255))\

    for slot in enumerate(inventorySlots):
        inventoryContainer.blit(slot[1], ((slot[0]%3)*(inventorySlotSize[0]+5)+5, (slot[0]//3)*(inventorySlotSize[0]+5)+5))

    inventoryBorder.blit(inventoryContainer, (2, 2))
    display.blit(inventoryBorder, (2, 63))

# Player Hotbar
hotbarSize = [155, 55]
hotbarSlots = [pg.Surface(inventorySlotSize) for i in range(3)]
for slot in hotbarSlots:
    pg.Surface.fill(slot, (190, 190, 190))

hotbarContainer = pg.Surface(hotbarSize)
hotbarBorder = pg.Surface((hotbarSize[0]+4, hotbarSize[1]+4))
hotbarContainer.set_alpha(225)
hotbarBorder.set_alpha(225)

pg.Surface.fill(hotbarBorder, (0, 0, 0))
handBorder = pg.Surface((inventorySlotSize[0]+4, inventorySlotSize[1]+4))

def hotbar():
    pg.Surface.fill(hotbarContainer, (255, 255, 255))
    hotbarContainer.blit(handBorder, (player.hand*(inventorySlotSize[0]+5)+3, 3))
    for slot in enumerate(hotbarSlots):
        hotbarContainer.blit(slot[1], (slot[0]*(inventorySlotSize[0]+5)+5, 5))
        if player.hotbar[slot[0]]:
            slot[1].blit(player.hotbar[slot[0]].image, (0, 0))
    hotbarBorder.blit(hotbarContainer, (2, 2))
    display.blit(hotbarBorder, (2, 2))

# Player equipables
equipablesSize = [200, 300]
equipablesContainer = pg.Surface(equipablesSize)
equipablesBorder = pg.Surface((equipablesSize[0]+4, equipablesSize[1]+4))
equipablesContainer.set_alpha(225)
equipablesBorder.set_alpha(225)
pg.Surface.fill(equipablesBorder, (0, 0, 0))
def equipables_menu():
    pg.Surface.fill(equipablesContainer, (255, 255, 255))
    display.blit(equipablesBorder, (DATA["DISPLAY_SIZE"][0]-equipablesSize[0]-6, DATA["DISPLAY_SIZE"][1]-equipablesSize[1]-6))
    equipablesBorder.blit(equipablesContainer, (2, 2))

# Player shop
shopSize = [400, 200]
shopContainer = pg.Surface(shopSize)
shopBorder = pg.Surface((shopSize[0]+4, shopSize[1]+4))
shopBorder.set_alpha(225)
shopContainer.set_alpha(225)
def shop():
    pg.Surface.fill(shopContainer, (255, 255, 255))
    display.blit(shopBorder, (2, DATA["DISPLAY_SIZE"][1]-shopSize[1]-6))
    shopBorder.blit(shopContainer, (2, 2))

# Player Stats
statsSize = [175, 95]
statsContainer = pg.Surface(statsSize)
statsBorder = pg.Surface((statsSize[0]+4, statsSize[1]+4))
statsBorder.set_alpha(225)
statsContainer.set_alpha(225)

pg.Surface.fill(statsBorder, (0, 0, 0))
redHeart = pg.image.load('./images/red_heart.png')
blackHeart = pg.image.load('./images/black_heart.png')
def stats():
    pg.Surface.fill(statsContainer, (255, 255, 255))
    textLines = [
        myFonts["default"].render(F"Doofenheim's Stats", True, (0, 0, 0)),
        myFonts["default"].render(F"Money: ${player.coinsCollected}", True, (0, 0, 0)),
        myFonts["default"].render(F"Health:", True, (0, 0, 0)),
        myFonts["default"].render(F"Ammo: {player.hotbar[player.hand].ammo}", True, (0, 0, 0)) if player.hotbar[player.hand].ammo != -1 else myFonts['default'].render("", True, (0, 0, 0)),
        myFonts["default"].render(F"Enemies: {len(enemies)}", True, (0, 0, 0))
    ]

    for line in enumerate(textLines):
        statsContainer.blit(line[1], (5, 5+line[0]*15))

    for i in range(0, 3):
        statsContainer.blit(redHeart if i < player.lives else blackHeart, (12*i+137, 37))

    display.blit(statsBorder, (618, 3))
    statsBorder.blit(statsContainer, (2, 2))
    healthBar(player, 75, 10, 680, 42)

def solidXCollision(sprite):
    collidedPlatform = pg.sprite.spritecollideany(sprite, solids)
    if collidedPlatform != None:
        if sprite.rect.left < collidedPlatform.rect.left:
            sprite.rect.right = collidedPlatform.rect.left
        else:
            sprite.rect.x = collidedPlatform.rect.right
        sprite.vel[0] = 0
        return True
    return False

def solidYCollision(sprite):
    collidedPlatform = pg.sprite.spritecollideany(sprite, solids)
    if collidedPlatform != None:
        if sprite.rect.top < collidedPlatform.rect.top:
            sprite.rect.bottom = collidedPlatform.rect.top
            sprite.inAir = False
        else:
            sprite.rect.y = collidedPlatform.rect.bottom
        sprite.vel[1] = 0
        return True
    return False

def detectPlatformFall(sprite):
    sprite.rect = sprite.rect.move(-23 if sprite.dir[0] == -1 else 23, 10)
    collidedPlatform = pg.sprite.spritecollideany(sprite, solids)
    sprite.rect = sprite.rect.move(23 if sprite.dir[0] == -1 else -23, -10)

    if not collidedPlatform:
        sprite.dir[0] *= -1

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
            if item != '0' and item != 'E':
                solids.add(Tile(item, x, y))
            if item == 'E':
                enemies.add(Enemy((x*20, y*20-50)))
            x+=1
        y+=1

def unload_current_level():
    solids.empty()
    enemies.empty()
    coins.empty()

# "Scroll" the game to follow the player.
def scroll():
    SCROLL_AMOUNT = [-1*int((player.rect.x-DATA["DISPLAY_SIZE"][0]/2+player.rect.width/2)/4), -1*int((player.rect.y-DATA["DISPLAY_SIZE"][1]/2+player.rect.height/2)/6)]

    player.rect = player.rect.move(SCROLL_AMOUNT)
    
    player.spawn[0] += SCROLL_AMOUNT[0]
    player.spawn[1] += SCROLL_AMOUNT[1]

    for sprite in solids:
        sprite.rect = sprite.rect.move(SCROLL_AMOUNT)

    if len(bullets):
        for bullet in bullets:
            bullet.compPos = [bullet.compPos[0]+SCROLL_AMOUNT[0], bullet.compPos[1]+SCROLL_AMOUNT[1]]

    for cloud in clouds:
        cloud.rect = cloud.rect.move(SCROLL_AMOUNT[0]/cloud.scrollIntensity, 0)

    for enemy in enemies:
        enemy.rect = enemy.rect.move(SCROLL_AMOUNT)

    for coin in coins:
        coin.rect = coin.rect.move(SCROLL_AMOUNT)

def healthBar(sprite, width, height, x, y):
    healthRemaining = pg.Surface((width*(sprite.health/sprite.maxHealth) if sprite.health > 0 else 0, height))
    healthTotal = pg.Surface((width, height))

    pg.Surface.fill(healthRemaining, (255, 0, 0))
    pg.Surface.fill(healthTotal, (0, 0, 0))

    display.blit(healthTotal, (x, y))
    display.blit(healthRemaining, (x, y))

# End Screen
endSize = [DATA["DISPLAY_SIZE"][0]-50, DATA["DISPLAY_SIZE"][1]-50]
endContainer = pg.Surface(endSize)
endBorder = pg.Surface((endSize[0]+4, endSize[1]+4))
def endScreen(keys):
    pg.Surface.fill(endContainer, (255, 255, 255))
    textLines = [
        myFonts["title"].render(F"GAME OVER", True, (0, 0, 0))
    ]

    for line in textLines:
        endContainer.blit(line, (int(endSize[0]/2-line.get_size()[0]/2), 15))
    
    display.blit(endBorder, (23, 23))
    endBorder.blit(endContainer, (2, 2))

# Start Screen
startSize = [DATA["DISPLAY_SIZE"][0]-50, DATA["DISPLAY_SIZE"][1]-50]
startContainer = pg.Surface(startSize)
startBorder = pg.Surface((startSize[0]+4, startSize[1]+4))
def startScreen(keys):
    pg.Surface.fill(startContainer, (255, 255, 255))
    textLines = [
        myFonts["title"].render(F"Doofenheim's Pantless Adventure", True, (0, 0, 0)),
        myFonts["title"].render(F"", True, (0, 0, 0)),
        myFonts["default"].render(F"Press 'Space' to start!", True, (0, 0, 0)),
    ]

    for line in enumerate(textLines):
        startContainer.blit(line[1], (int(startSize[0]/2-line[1].get_size()[0]/2), line[0]*22+10))
    
    display.blit(startBorder, (23, 23))
    startBorder.blit(startContainer, (2, 2))

    if keys[pg.K_SPACE]:
        global inStartScreen
        inStartScreen = False
        global gameRun
        gameRun = True
        game()

# Sprite groups
solids = pg.sprite.Group()
clouds = pg.sprite.Group()
enemies = pg.sprite.Group()
bullets = pg.sprite.Group()
playerBullets = pg.sprite.Group()
enemyBullets = pg.sprite.Group()
coins = pg.sprite.Group()

display = pg.Surface(DATA["DISPLAY_SIZE"])

for i in range(10):
    clouds.add(Cloud())

enemies.add(Enemy([-2000, 1000]))

gameRun = True

def pistol_shoot(gun):
    if gun.ammo:
        bullets.add(Bullet(player.rect.center, pg.mouse.get_pos(), 'player', 'pistol'))
        gun.hasBeenUsed = True
        gun.ammo -= 1

def shotgun_shoot(gun):
    if gun.ammo:
        for i in range(5):
            bullets.add(Bullet(player.rect.center, pg.mouse.get_pos(), 'player', 'shotgun'))
            gun.hasBeenUsed = True
        gun.ammo -= 1

player = Player()
userMouse = Mouse()

def game():
    global gameRun
    global inMenu
    global menuCooldown
    load_level("level_1")
    while gameRun:
        display.fill((150, 150, 255))

        # Manage game events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                gameRun = False

            if event.type == pg.MOUSEWHEEL:
                player.change_hand(event)

        keys = pg.key.get_pressed()

        # Update the game
        if not inMenu:
            for cloud in clouds:
                cloud.animate()

            player.update(keys)
            for enemy in enemies:
                enemy.update()

            for bullet in bullets:
                bullet.update()

        # Draw everything to display
        clouds.draw(display)
        solids.draw(display)
        for enemy in enemies:
            enemy.draw()
        bullets.draw(display)
        coins.draw(display)
        player.draw()

        if not inMenu:
            scroll()

        
        if keys[pg.K_e] and not menuCooldown:
            inMenu = True if not inMenu else False
            menuCooldown = 20

        if menuCooldown:
            menuCooldown -= 1

        stats()
        hotbar()
        
        debugMenu(keys)
        if inMenu:
            player_inventory()
            equipables_menu()
            shop()

        userMouse.update()

        if gameOver:
            gameRun = False
            end_screen()
            break

        win.blit(pg.transform.scale(display, DATA["WIN_SIZE"]), (0, 0))
        pg.display.flip()
        clock.tick(DATA["FPS"])

inStartScreen = True

def start_screen():
    global inStartScreen
    while inStartScreen:
        display.fill((175, 175, 255))
        keys = pg.key.get_pressed()

        startScreen(keys)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                inStartScreen = False

        win.blit(pg.transform.scale(display, DATA["WIN_SIZE"]), (0, 0))
        pg.display.flip()
        clock.tick(DATA["FPS"])

gameOver = False
def end_screen():
    global gameOver
    while gameOver:
        display.fill((175, 175, 255))
        keys = pg.key.get_pressed()

        endScreen(keys)

        if keys[pg.K_q]:
            gameOver = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                gameOver = False

        win.blit(pg.transform.scale(display, DATA["WIN_SIZE"]), (0, 0))
        pg.display.flip()
        clock.tick(DATA["FPS"])

start_screen()
    
pg.quit()