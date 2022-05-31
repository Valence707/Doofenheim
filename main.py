import math
import random
import pygame as pg
from pygame.locals import *

WIN_SIZE = [1600, 900]
DISPLAY_SIZE = [800, 450]
FPS = 60
TILE_SIZE = [10, 10]
GRAVITY = 0.5
CLOUD_IMAGES = [
    pg.image.load('./images/cloud_1.png'),
    pg.image.load('./images/cloud_2.png'),
    pg.image.load('./images/cloud_3.png')
]

pg_icon = pg.image.load('./images/icon.png')
pg.display.set_icon(pg_icon)
pg.init()

background_music = pg.mixer.Sound('./sounds/background_music.ogg')
background_music.play()
pg.mixer.init()

clock = pg.time.Clock()
win = pg.display.set_mode(WIN_SIZE)
pg.display.set_caption("Doofenheim's Pantless Adventure")

myFonts = {
    "default": pg.font.SysFont(None, 22),
    "title": pg.font.SysFont(None, 36)
    }

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
        self.image.convert()
        self.image.set_colorkey((0, 255, 0))
            
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
        self.image = CLOUD_IMAGES[random.randrange(0, len(CLOUD_IMAGES))]
        randomSizeFactor = random.randrange(1, 6)
        self.image = pg.transform.scale(self.image, (self.image.get_width()*randomSizeFactor, self.image.get_height()*randomSizeFactor))
        self.image.convert()
        self.image.set_colorkey((0, 255, 0))

        self.compPos = [pos[0] if pos[0] else int(random.randrange(0, DISPLAY_SIZE[0]-150)), pos[1] if pos[1] else int(random.randrange(0, DISPLAY_SIZE[1]-150))]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.compPos[0], self.compPos[1]
        self.vel = [round(random.random()+0.3, 2), 0]
        self.scrollIntensity = 100/self.vel[0]

    def animate(self):
        if self.rect.left > DISPLAY_SIZE[0] and self.vel[0] > 0:
            self.compPos = [-1*self.rect.width, int(random.randrange(0, DISPLAY_SIZE[1]-150))]
        elif self.rect.right < 0 and self.vel[0] < 0:
            self.compPos = [DISPLAY_SIZE[0], int(random.randrange(0, DISPLAY_SIZE[1]-150))]
        
        self.compPos = [self.compPos[0]+self.vel[0], self.compPos[1]+self.vel[1]]
        self.rect.x, self.rect.y = math.floor(self.compPos[0]), math.floor(self.compPos[1])

class Bullet(pg.sprite.Sprite):
    def __init__(self, origin, dest, type):
        super().__init__()
        self.image = pg.image.load("./images/bullet.png")
        self.image.convert()
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.maxVel = 15
        self.dmg = 10

        self.rect.x, self.rect.y = origin
        delta = pg.math.Vector2(dest[0]*(DISPLAY_SIZE[0]/WIN_SIZE[0]), dest[1]*(DISPLAY_SIZE[1]/WIN_SIZE[1])) - origin
        direction = delta.normalize()
        self.vel = direction*self.maxVel

        self.sound = pg.mixer.Sound('./sounds/pew.ogg')
        self.sound.play()

        self.duration = 3
        self.initTime = pg.time.get_ticks()

        if type == 'player':
            playerBullets.add(self)
        elif type == 'enemy':
            enemyBullets.add(self)

    def update(self):
        self.rect = self.rect.move(self.vel)
        if (pg.time.get_ticks()-self.initTime) / 1000 > self.duration or pg.sprite.spritecollideany(self, solids):
            self.sound.stop()
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
        self.image.convert()
        self.image.set_colorkey((0, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

class Player(pg.sprite.Sprite):
    """Sprite controlled by player, used to interact with environment"""
    def __init__(self, pos=[round((DISPLAY_SIZE[0]/2)-10, 2), round((DISPLAY_SIZE[1]/2)-10)], size=[25, 50]):
        super().__init__()
        self.image = pg.image.load("./images/player.png").convert()
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = self.compPos[0], self.compPos[1]
        self.spawn = [0, 0]

        self.vel = [0, 0]
        self.maxVel = 6
        self.jumpVel = -12
        self.inAir = True
        self.acc = 1.5

        self.coinsCollected = 0
        self.enemiesKilled = 0
        self.ammo = 30
        self.health = 100
        self.lives = 3
        self.maxHealth = 100
        self.hurtSound = pg.mixer.Sound('./sounds/hurt.ogg')
        self.sounds = [pg.mixer.Sound('./sounds/bruh.ogg'), pg.mixer.Sound('./sounds/oof.ogg')]
        for sound in self.sounds:
            sound.stop()
        self.hurtSound.stop()

    def update(self, keys):
        player.movePlayer(keys, solids)
        collectedCoin = pg.sprite.spritecollideany(self, coins)
        if collectedCoin:
            collectedCoin.kill()
            player.coinsCollected+=collectedCoin.value

        if keys[pg.K_q]:
            global gameRun
            gameRun = False

        if keys[pg.K_k]:
            self.health = 0

        if self.health <= 0:
            self.lives -= 1
            self.ammo = 30
            self.rect.x, self.rect.y = player.spawn[0], player.spawn[1]
            self.health = 100

        global gameOver
        if self.lives == 0 or len(enemies) <= 0:
            gameOver = True
            background_music.stop()
            self.sounds[random.randrange(0, 2)].play()

    def movePlayer(self, keys, solids):

        # Manage player movement
        if keys[pg.K_a]:
            dir[0] = -1
        elif self.vel[0] < 0:
            dir[0] = 1

        if keys[pg.K_s]:
            dir[1] = 1

        if keys[pg.K_d]:
            dir[0] = 1
        elif self.vel[0] > 0:
            dir[0] = -1

        if keys[pg.K_SPACE]:
            if not self.inAir:
                self.vel[1]= self.jumpVel
                self.inAir = True

        if self.vel[1] < 12:
            self.vel[1]+=GRAVITY

        newVel = [round(self.vel[0]+self.acc*dir[0], 2), round(self.vel[1]+self.acc*dir[1], 2)]
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
            self.hurtSound.play()
            bulletCollided.kill()

    def shoot(self):
        if self.ammo:
            bullets.add(Bullet(player.rect.center, pg.mouse.get_pos(), 'player'))
            self.ammo -= 1

    def draw(self):
        display.blit(self.image, (self.rect.x, self.rect.y))

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load("./images/enemy.png").convert()
        self.image.set_colorkey((0, 255, 0))
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
        self.shotDelay = random.randrange(1, 4)
        self.lastShot = pg.time.get_ticks()

    def update(self):
        if self.vel[1] <= 12:
            self.vel[1]+=GRAVITY

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            if solidXCollision(self):
                self.dir[0] *= -1

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        if (pg.time.get_ticks() - self.lastShot) / 1000 >= self.shotDelay:
            self.lastShot = pg.time.get_ticks()
            bullets.add(Bullet(self.rect.center, player.rect.center, 'enemy'))

        healthBar(self, self.rect.width, 5, self.rect.x, self.rect.y-10)

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
            player.ammo += random.randrange(1, 7)

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
    with open(path+".txt", "r") as worldObj:
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

# "Scroll" the game to follow the player.
def scroll():
    SCROLL_AMOUNT = [-1*int((player.rect.x-DISPLAY_SIZE[0]/2+player.rect.width/2)/4), -1*int((player.rect.y-DISPLAY_SIZE[1]/2+player.rect.height/2)/6)]

    player.rect = player.rect.move(SCROLL_AMOUNT)
    
    player.spawn[0] += SCROLL_AMOUNT[0]
    player.spawn[1] += SCROLL_AMOUNT[1]

    for sprite in solids:
        sprite.rect = sprite.rect.move(SCROLL_AMOUNT)

    if len(bullets):
        for bullet in bullets:
            bullet.rect = bullet.rect.move(SCROLL_AMOUNT)

    for cloud in clouds:
        cloud.rect = cloud.rect.move(SCROLL_AMOUNT[0]/cloud.scrollIntensity, 0)

    for enemy in enemies:
        enemy.rect = enemy.rect.move(SCROLL_AMOUNT)

    for coin in coins:
        coin.rect = coin.rect.move(SCROLL_AMOUNT)

# Player Stats
statsSize = [175, 95]
statsContainer = pg.Surface(statsSize)
statsBorder = pg.Surface((statsSize[0]+4, statsSize[1]+4))
pg.Surface.fill(statsBorder, (0, 0, 0))
redHeart = pg.image.load('./images/red_heart.png').convert()
blackHeart = pg.image.load('./images/black_heart.png').convert()
redHeart.set_colorkey((0, 255, 0))
blackHeart.set_colorkey((0, 255, 0))
def stats():
    pg.Surface.fill(statsContainer, (255, 255, 255))
    textLines = [
        myFonts["default"].render(F"Doofenheim's Stats", True, (0, 0, 0)),
        myFonts["default"].render(F"Money: ${player.coinsCollected}", True, (0, 0, 0)),
        myFonts["default"].render(F"Health:", True, (0, 0, 0)),
        myFonts["default"].render(F"Ammo: {player.ammo}", True, (0, 0, 0)),
        myFonts["default"].render(F"Enemies: {len(enemies)}", True, (0, 0, 0))
    ]

    for line in enumerate(textLines):
        statsContainer.blit(line[1], (5, 5+line[0]*15))

    for i in range(0, 3):
        statsContainer.blit(redHeart if i < player.lives else blackHeart, (12*i+137, 37))

    display.blit(statsBorder, (618, 3))
    display.blit(statsContainer, (620, 5))
    healthBar(player, 75, 10, 680, 42)


# Player settings
settingsSize = [DISPLAY_SIZE[0]-100, DISPLAY_SIZE[1]-100]
settingsContainer = pg.Surface(settingsSize)
settingsBorder = pg.Surface((settingsSize[0]+4, settingsSize[1]+4))
settingsMode = False
settingsCooldown = 0
pg.Surface.fill(settingsBorder, (0, 0, 0))
def settingsMenu(keys):
    global settingsMode
    global settingsCooldown

    if keys[pg.K_ESCAPE] and not settingsCooldown:
        settingsMode = True if not settingsMode else False
        settingsCooldown = 20

    if settingsCooldown:
        settingsCooldown -= 1

    if settingsMode:
        pg.Surface.fill(settingsContainer, (255, 255, 255))
        textLines = [
            myFonts["default"].render(F"Test", True, (0, 0, 0))
        ]

        for line in enumerate(textLines):
            settingsContainer.blit(line[1], (5, 5+line[0]*15))

        display.blit(settingsBorder, (48, 48))
        display.blit(settingsContainer, (50, 50))

def healthBar(sprite, width, height, x, y):
    healthRemaining = pg.Surface((width*(sprite.health/sprite.maxHealth) if sprite.health > 0 else 0, height))
    healthTotal = pg.Surface((width, height))

    pg.Surface.fill(healthRemaining, (255, 0, 0))
    pg.Surface.fill(healthTotal, (0, 0, 0))

    display.blit(healthTotal, (x, y))
    display.blit(healthRemaining, (x, y))

endSize = [DISPLAY_SIZE[0]-50, DISPLAY_SIZE[1]-50]
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
    display.blit(endContainer, (25, 25))

player = Player()

# Sprite groups
solids = pg.sprite.Group()
clouds = pg.sprite.Group()
enemies = pg.sprite.Group()
bullets = pg.sprite.Group()
playerBullets = pg.sprite.Group()
enemyBullets = pg.sprite.Group()
coins = pg.sprite.Group()

run = True
display = pg.Surface(DISPLAY_SIZE)

for i in range(10):
    clouds.add(Cloud())

enemies.add(Enemy([200, 200]), Enemy([200, 200]), Enemy([200, 200]), Enemy([200, 200]), Enemy([200, 200]))

def start_screen():
    run = True
    while run:
        win.fill((255, 255, 255))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

gameRun = True
inStartscreen = False

def game():
    global gameRun
    load_level("world")
    while gameRun:
        display.fill((175, 175, 255))

        # Manage game events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                gameRun = False

            if event.type == pg.MOUSEBUTTONDOWN:
                player.shoot()

        keys = pg.key.get_pressed()

        # Draw background
        for cloud in clouds:
            cloud.animate()

        clouds.draw(display)
        solids.draw(display)

        player.update(keys)
        for enemy in enemies:
            enemy.update()

        for bullet in bullets:
            bullet.update()
        enemies.draw(display)
        bullets.draw(display)
        coins.draw(display)

        player.draw()

        scroll()

        stats()

        debugMenu(keys)
        settingsMenu(keys)

        if gameOver:
            gameRun = False
            end_screen()
            break

        win.blit(pg.transform.scale(display, WIN_SIZE), (0, 0))
        pg.display.flip()
        clock.tick(FPS)

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

        win.blit(pg.transform.scale(display, WIN_SIZE), (0, 0))
        pg.display.flip()
        clock.tick(FPS)

game()
    
pg.quit()