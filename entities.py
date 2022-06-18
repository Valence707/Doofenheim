import pygame, random, math, data
from functions import *

class Player(pygame.sprite.Sprite):
    """Sprite controlled by data.player, used to interact with environment"""
    def __init__(self, pos=[round((data.DISPLAY_SIZE[0]/2)-10, 2), round((data.DISPLAY_SIZE[1]/2)-10)], size=[25, 50]):
        super().__init__()
        self.images = [
            pygame.image.load("./images/player_idle.png"),
            pygame.image.load("./images/player_walk_1.png"),
            pygame.image.load("./images/player_walk_2.png")
        ]
        self.image = self.images[0]
        pygame.transform.flip(self.image, False, True)
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = self.compPos[0], self.compPos[1]
        self.spawn = [0, 0]
        self.startTime = pygame.time.get_ticks()

        self.vel = [0, 0]
        self.maxVel = 6
        self.jumpVel = -12
        self.inAir = False
        self.acc = 1

        self.facing = 1
        self.animFlipped = False
        self.frame = 0
        self.lastFrame = 0

        self.enemiesKilled = 0
        self.money = 0
        self.health = 100
        self.lives = 3
        self.maxHealth = 100
        self.hand = 0
        self.hotbar = ['pistol', 'shotgun', 'machine_gun']
        self.hasShotPistol = False
        self.hasShotShotgun = False
        self.gunAmmo = ["inf", 30, 250]
        self.lastFiredPistol = 0
        self.lastFiredShotgun = 0
        self.lastFiredMachineGun = 0
        self.hurtSound = pygame.mixer.Sound('./sounds/hurt.ogg')
        self.gunSounds = [pygame.mixer.Sound('./sounds/pistol_shoot.ogg'), pygame.mixer.Sound('./sounds/shotgun_shoot.ogg'), pygame.mixer.Sound('./sounds/machine_gun.ogg')]

    def update(self, keys):
        self.movePlayer(keys)
        collectedCoin = pygame.sprite.spritecollideany(self, data.coins)
        if collectedCoin:
            collectedCoin.kill()
            pygame.mixer.Sound('./sounds/coin.ogg').play()
            data.player.money+=collectedCoin.value

        # Use items in hotbar
        if pygame.mouse.get_pressed()[0]:
            if self.hotbar[self.hand] == 'pistol' and not self.hasShotPistol and (pygame.time.get_ticks() - self.lastFiredPistol) / 1000 > 0.25:
                self.hasShotPistol = True
                self.lastFiredPistol = pygame.time.get_ticks()
                data.bullets.add(Bullet(data.player.rect.center, (pygame.mouse.get_pos()[0]*(data.DISPLAY_SIZE[0]/data.WIN_SIZE[0]), pygame.mouse.get_pos()[1]*(data.DISPLAY_SIZE[1]/data.WIN_SIZE[1])), 'player', 'pistol'))
                self.gunSounds[0].play()
            elif self.hotbar[self.hand] == 'shotgun' and self.gunAmmo[1] and (pygame.time.get_ticks() - self.lastFiredShotgun) / 1000 > 1 and not self.hasShotShotgun:
                self.hasShotShotgun = True
                self.lastFiredShotgun = pygame.time.get_ticks()
                for i in range(5):
                    data.bullets.add(Bullet(data.player.rect.center, (pygame.mouse.get_pos()[0]*(data.DISPLAY_SIZE[0]/data.WIN_SIZE[0]), pygame.mouse.get_pos()[1]*(data.DISPLAY_SIZE[1]/data.WIN_SIZE[1])), 'player', 'shotgun'))
                
                self.gunAmmo[1] -= 1
                self.gunSounds[1].play()
            elif self.hotbar[self.hand] == 'machine_gun' and self.gunAmmo[2] and (pygame.time.get_ticks() - self.lastFiredMachineGun) / 1000 > 0.1:
                self.lastFiredMachineGun = pygame.time.get_ticks()
                data.bullets.add(Bullet(data.player.rect.center, (pygame.mouse.get_pos()[0]*(data.DISPLAY_SIZE[0]/data.WIN_SIZE[0]), pygame.mouse.get_pos()[1]*(data.DISPLAY_SIZE[1]/data.WIN_SIZE[1])), 'player', 'machine_gun'))
                self.gunAmmo[2] -= 1
                self.gunSounds[2].play()

        else:
            self.hasShotPistol = False
            self.hasShotShotgun = False

        if self.health <= 0:
            self.lives -= 1
            self.rect.x, self.rect.y = data.player.spawn[0], data.player.spawn[1]
            self.health = 100

        if pygame.sprite.spritecollideany(self, data.items):
            data.victory = True

    def movePlayer(self, keys):
        self.dir = [0, 0]

        # Manage player movement & animation
        self.dir = -1 if keys[pygame.K_a] or (self.vel[0] > 0 and not keys[pygame.K_d]) else 1 if keys[pygame.K_d] or self.vel[0] < 0 else self.dir[0], 1 if keys[pygame.K_s] else self.dir[1]

        self.facing = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else self.facing

        if keys[pygame.K_SPACE] and not self.inAir:
            self.vel[1] = self.jumpVel
            self.inAir = True

        if self.vel[1] < 12 :
            self.vel[1]+=data.GRAVITY

        newVel = [round(self.vel[0]+self.acc*self.dir[0], 2), round(self.vel[1]+self.acc*self.dir[1], 2)]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            solidXCollision(self)
            self.lastFrame = pygame.time.get_ticks() if not self.lastFrame else self.lastFrame

            if (pygame.time.get_ticks() - self.lastFrame) / 1000 > 0.2:
                self.lastFrame = pygame.time.get_ticks()
                self.frame = self.frame+1 if self.frame+1 < 4 else 0
                self.image = self.images[0] if self.frame == 0 or self.frame == 2 else self.images[1] if self.frame == 1 else self.images[2] if self.frame == 3 else self.image

                if self.facing < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey((0, 255, 0))

        else:
            self.image = self.images[0]

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        if keys[pygame.K_1] or keys[pygame.K_2] or keys[pygame.K_3]:
            self.change_hand(keys=keys)

    def change_hand(self, event=None, keys=None, pos=0):
        newHand = self.hand-event.y if (event != None and event.type == pygame.MOUSEWHEEL and abs(event.y)) else 0 if keys[pygame.K_1] else 1 if keys[pygame.K_2] else 2 if keys[pygame.K_3] else pos
        self.hand = 2 if newHand < 0 else 0 if newHand > 2 else newHand
        
    def draw(self):
        data.DISPLAY.blit(self.image, (self.rect.x, self.rect.y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, health=30, fireRate=None):
        super().__init__()
        self.image = pygame.image.load("./images/enemy.png").convert()
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.compPos = pos
        self.rect.x, self.rect.y = pos
        self.vel = [0, 0]

        self.dir = [random.randrange(-1, 2, 2), 0]

        self.maxVel = random.randrange(1, 4)
        self.inAir = True
        self.acc = 1
        self.health = health
        self.maxHealth = health
        self.shotDelay = fireRate if fireRate else random.randrange(3, 7)
        self.lastShot = pygame.time.get_ticks()

    def update(self):
        if self.vel[1] <= 12:
            self.vel[1]+=data.GRAVITY

        if abs(self.vel[0]):
            self.rect.x = math.floor(self.vel[0]+self.rect.x)
            if solidXCollision(self):
                self.dir[0] *= -1

        if abs(self.vel[1]):
            self.rect.y = math.floor(self.vel[1]+self.rect.y)
            solidYCollision(self)

        if (pygame.time.get_ticks() - self.lastShot) / 1000 >= self.shotDelay:
            self.lastShot = pygame.time.get_ticks()
            data.bullets.add(Bullet(self.rect.center, data.player.rect.center, 'enemy', 'pistol'))

        self.rect = self.rect.move(-23 if self.dir[0] == -1 else 23, 10)
        collidedPlatform = pygame.sprite.spritecollideany(self, data.solids)
        self.rect = self.rect.move(23 if self.dir[0] == -1 else -23, -10)

        if not collidedPlatform:
            self.dir[0] *= -1
        
        newVel = [self.vel[0]+self.acc*self.dir[0], self.vel[1]+self.acc*self.dir[1]]
        self.vel = [newVel[0] if abs(newVel[0]) <= self.maxVel else self.vel[0], newVel[1] if abs(newVel[1]) <= self.maxVel else self.vel[1]]

        if self.health <= 0:
            data.enemyDeathSound.play()
            if data.player.hotbar[data.player.hand] == 'shotgun':
                data.player.gunAmmo[1] += 2
            else:
                data.player.gunAmmo[2] += 8

            data.player.enemiesKilled += 1
            self.kill()
            del self
            return

        healthBar(self, self.rect.width, 5, self.rect.x, self.rect.y-10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, origin, dest, firedFrom, gun):
        super().__init__()
        self.image = pygame.image.load("./images/bullet.png").convert()
        self.image.set_colorkey((0, 255, 0))
        self.rect = self.image.get_rect()
        self.maxVel = 15 if firedFrom == "player" else 7
        self.dmg = 10
        self.gun = gun
        self.firedFrom = firedFrom

        self.compPos = origin
        self.rect.x, self.rect.y = origin
        delta = pygame.math.Vector2(dest[0], dest[1]) - origin
        try:
            direction = delta.normalize()
        except:
            print("BULLET NORMALIZATION ERROR")

        if gun == 'shotgun':
            direction.x, direction.y = direction[0]+(random.uniform(-0.15, 0.15)), direction[1]+(random.uniform(-0.15, 0.15))
            self.dmg = 7
        elif gun == 'machine_gun':
            direction.x, direction.y = direction[0]+(random.uniform(-0.07, 0.07)), direction[1]+(random.uniform(-0.07, 0.07))
            self.dmg = 5

        if firedFrom == 'enemy':
            direction.x, direction.y = direction[0]+(random.uniform(-0.1, 0.1)), direction[1]+(random.uniform(-0.1, 0.1))

        self.vel = direction*self.maxVel
        self.duration = 3
        self.initTime = pygame.time.get_ticks()

    def update(self):
        self.compPos = [round(self.compPos[0]+self.vel[0], 2), round(self.compPos[1]+self.vel[1], 2)]
        self.rect.x, self.rect.y = self.compPos

        # Detect collisions with entities
        collidedSolid = pygame.sprite.spritecollideany(self, data.solids)
        if (pygame.time.get_ticks()-self.initTime) / 1000 > self.duration or collidedSolid:
            self.kill()
            del self
            return

        collidedEnemy = pygame.sprite.spritecollideany(self, data.enemies) if self.firedFrom != "enemy" else None
        if collidedEnemy:
            data.enemyHitSound.play()
            collidedEnemy.health -= self.dmg
            self.kill()
            del self
            return

        collidedPlayer = self.rect.colliderect(data.player.rect) if self.firedFrom != "player" else None
        if collidedPlayer:
            data.player.health -= self.dmg
            data.player.hurtSound.play()
            self.kill()
            del self
            return