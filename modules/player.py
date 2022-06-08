import pygame, math
from data import DATA
from modules.functions import *
from modules.items import *

class Player(pygame.sprite.Sprite):
    """Sprite controlled by DATA["player"], used to interact with environment"""
    def __init__(self, pos=[round((DATA["DISPLAY_SIZE"][0]/2)-10, 2), round((DATA["DISPLAY_SIZE"][1]/2)-10)], size=[25, 50]):
        super().__init__()
        self.idleImage = DATA["playerWalkImages"][1]
        self.image = self.idleImage
        pygame.transform.flip(self.image, False, True)
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = self.compPos[0], self.compPos[1]
        self.spawn = [0, 0]

        self.vel = [0, 0]
        self.maxVel = 6
        self.jumpVel = -12
        self.inAir = True
        self.acc = 1

        self.facing = "R"
        self.animFlipped = False
        self.animFrame = 0
        self.lastFrame = 0

        self.money = 0
        self.health = 100
        self.lives = 3
        self.maxHealth = 100
        self.hand = 0
        self.hotbar = [
            Item('pistol', 3000,'pistol.png', pistol_shoot, 0.75), Item('shotgun', 3000, 'shotgun.png', shotgun_shoot, 1), Item('knife', 0, 'knife.png')
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
        self.movePlayer(keys)
        collectedCoin = pygame.sprite.spritecollideany(self, DATA["coins"])
        if collectedCoin:
            collectedCoin.kill()
            DATA["player"].money+=collectedCoin.value

        if keys[pygame.K_q]:
            DATA["gameRun"] = False

        if keys[pygame.K_k] and DATA["debugMode"]:
            self.health -= 10

        if pygame.mouse.get_pressed()[0]:
            if self.hotbar[self.hand]:
                self.hotbar[self.hand].use()
        else:
            self.hasShot = False

        if self.health <= 0:
            self.lives -= 1
            self.ammo = 30
            self.rect.x, self.rect.y = DATA["player"].spawn[0], DATA["player"].spawn[1]
            self.health = 100

        # End the game
        if self.lives == 0 or len(DATA["enemies"]) <= 0:
            DATA["gameOver"] = True
            unload_current_level()

    def movePlayer(self, keys):
        self.dir = [0, 0]

        # Manage player movement
        self.dir[0] = -1 if keys[pygame.K_a] or (self.vel[0] > 0 and not keys[pygame.K_d]) else 1 if keys[pygame.K_d] or self.vel[0] < 0 else self.dir[0]
        self.dir[1] = 1 if keys[pygame.K_s] else self.dir[1]
        newDirection = "L" if self.facing == "R" and keys[pygame.K_a] else "R" if self.facing == "L" and keys[pygame.K_d] else self.facing
        self.facing = newDirection if newDirection != self.facing else self.facing

        if keys[pygame.K_SPACE] and not self.inAir:
            self.vel[1]= self.jumpVel
            self.inAir = True

        if self.vel[1] < 16 :
            self.vel[1]+=DATA["GRAVITY"]

        newVel = [round(self.vel[0]+self.acc*self.dir[0], 2), round(self.vel[1]+self.acc*self.dir[1], 2)]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            solidXCollision(self)
            walk_anim(self, DATA["playerWalkImages"])

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        bulletCollided = pygame.sprite.spritecollideany(self, DATA["enemyBullets"])
        if bulletCollided:
            self.health -= bulletCollided.dmg
            bulletCollided.kill()

        if keys[pygame.K_1] or keys[pygame.K_2] or keys[pygame.K_3]:
            self.change_hand(keys=keys)

    def change_hand(self, event=None, keys=None, pos=0):
        newHand = self.hand-event.y if (event != None and event.type == pygame.MOUSEWHEEL and abs(event.y)) else 0 if keys[pygame.K_1] else 1 if keys[pygame.K_2] else 2 if keys[pygame.K_3] else pos
        self.hand = 2 if newHand < 0 else 0 if newHand > 2 else newHand
        
    def draw(self):
        DATA["DISPLAY"].blit(self.image, (self.rect.x, self.rect.y))