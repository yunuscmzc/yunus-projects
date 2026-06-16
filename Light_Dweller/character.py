import pygame
import os
import random
import math
from weapon import Bow, Arrow, FireBall
from constants import *
from items import Coin, Potion, Item


class Character(pygame.sprite.Sprite):
    CHAR_NAME = None

    def __init__(self, x, y, health, char_name):
        super().__init__()
        self._max_health = health
        self._health = health
        self._alive = True
        self._flip = False
        self._frame_index = 0
        self._speed = 4
        self._char_name = char_name
        self._animation_cooldown = FPS
        self._update_time = pygame.time.get_ticks()
        self._animation_dict = dict()
        animation_types = os.listdir(f"assets\\images\\characters\\{self._char_name}")
        for animation_type in animation_types:
            temp_list = list()
            animations = os.listdir(f"assets\\images\\characters\\{self._char_name}\\{animation_type}")
            for animation in animations:
                img = pygame.image.load(f"assets\\images\\characters\\{self._char_name}\\{animation_type}\\{animation}").convert_alpha()
                img = pygame.transform.scale_by(img, CHAR_SCALE)
                temp_list.append(img)
            self._animation_dict[animation_type] = temp_list
        self._action = "idle"
        self._previous_action = "idle"
        self.image = self._animation_dict[self._action][0]
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.rect.center = (x, y)

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self._flip, False)
        surface.blit(flipped_image, self.rect)
        self.draw_health(surface)

    def update(self):
        if self._health <= 0:
            self._health = 0
            self._alive = False

        animation_length = len(self._animation_dict[self._action])
        current_time = pygame.time.get_ticks()
        if self._action != self._previous_action:
            self._frame_index = 0
            self._update_time = current_time - self._animation_cooldown
            self._previous_action = self._action

        if self._frame_index >= animation_length:
            self._frame_index = 0

        if current_time - self._update_time > self._animation_cooldown:
            self.image = self._animation_dict[self._action][self._frame_index]
            self._update_time = current_time
            self._frame_index += 1

    def draw_health(self, surface):
        # Max health bar
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y, self.rect.width, 2))
        # Current health bar
        health_ratio = self._health / self._max_health
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y, self.rect.width * health_ratio, 2))

    def getHealth(self):
        return self._health

    def setHealth(self, number):
        self._health = number

    def getMaxHealth(self):
        return self._max_health

    def getAlive(self):
        return self._alive


class Hero(Character):
    CHAR_NAME = "elf"

    def __init__(self, x, y, health, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self.bow = Bow()
        self._shooting_cooldown = 0
        self._shooting_frequency = FPS * 4
        heart_images = os.listdir("assets\\images\\items\\hearts")
        self._heart_images_dict = dict()
        self._heart_health = 20
        self._coin_amount = 0
        self._extra_damage = 0
        for heart_image in heart_images:
            img = pygame.image.load(f"assets\\images\\items\\hearts\\{heart_image}")
            img = pygame.transform.scale_by(img, ITEM_SCALE)
            self._heart_images_dict[heart_image] = img

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self._flip, False)
        surface.blit(flipped_image, (self.rect.x, self.rect.y - 32))
        self.bow.draw(surface)

    def update(self):
        if self._health <= 0:
            self._health = 0
            self._alive = False
        else:
            self._alive = True

        animation_length = len(self._animation_dict[self._action])
        current_time = pygame.time.get_ticks()
        if self._action != self._previous_action:
            self._frame_index = 0
            self._update_time = current_time - self._animation_cooldown
            self._previous_action = self._action

        if self._frame_index >= animation_length:
            self._frame_index = 0

        if current_time - self._update_time > self._animation_cooldown:
            self.image = self._animation_dict[self._action][self._frame_index]
            self._update_time = current_time
            self._frame_index += 1
        self.bow.update(self)

    def shoot(self):
        mouse_ticks = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks()
        if mouse_ticks[0] and current_time - self._shooting_cooldown > self._shooting_frequency:
            self._shooting_cooldown = current_time
            arrow = Arrow(self.bow.rect.centerx, self.bow.rect.centery, self.bow.getAngle())
            self.bow.arrow_group.add(arrow)

    def move(self, obstacle_tiles):
        dx = 0
        dy = 0
        screen_scroll = [0, 0]
        moves = pygame.key.get_pressed()
        if moves[pygame.K_w]:
            dy = -self._speed
        elif moves[pygame.K_s]:
            dy = +self._speed
        if moves[pygame.K_a]:
            dx = -self._speed
            self._flip = True
        elif moves[pygame.K_d]:
            dx = +self._speed
            self._flip = False

        self.shoot()

        if dx != 0 or dy != 0:
            self._action = "run"
        else:
            self._action = "idle"

        self.rect.x += dx
        for obstacle in obstacle_tiles:
            if self.rect.colliderect(obstacle[1]):
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            if self.rect.colliderect(obstacle[1]):
                if dy < 0:
                    self.rect.top = obstacle[1].bottom
                if dy > 0:
                    self.rect.bottom = obstacle[1].top

        if self.rect.right >= SCREEN_WIDTH - INVINCIBLE_WALL:
            screen_scroll[0] = SCREEN_WIDTH - INVINCIBLE_WALL - self.rect.right
            self.rect.right = SCREEN_WIDTH - INVINCIBLE_WALL
        elif self.rect.left <= INVINCIBLE_WALL:
            screen_scroll[0] = INVINCIBLE_WALL - self.rect.left
            self.rect.left = INVINCIBLE_WALL

        if self.rect.top <= INVINCIBLE_WALL:
            screen_scroll[1] = INVINCIBLE_WALL - self.rect.top
            self.rect.top = INVINCIBLE_WALL
        elif self.rect.bottom >= SCREEN_HEIGHT - INVINCIBLE_WALL:
            screen_scroll[1] = SCREEN_HEIGHT - INVINCIBLE_WALL - self.rect.bottom
            self.rect.bottom = SCREEN_HEIGHT - INVINCIBLE_WALL

        return screen_scroll

    def draw_health(self, surface):
        for i in range(int(self._max_health / self._heart_health)):
            if (i + 1) * self._heart_health <= self._health:
                surface.blit(self._heart_images_dict["heart_full.png"], (10 + i * 40, BAR_HEIGHT - 35))
            elif int(self._heart_health / 2) <= self._health - i * self._heart_health:
                surface.blit(self._heart_images_dict["heart_half.png"], (10 + i * 40, BAR_HEIGHT - 35))
            else:
                surface.blit(self._heart_images_dict["heart_empty.png"], (10 + i * 40, BAR_HEIGHT - 35))

    def getCoinAmount(self):
        return self._coin_amount

    def setCoinAmount(self, number):
        self._coin_amount += number

    def getShootingFrequency(self):
        return self._shooting_frequency

    def setShootingFrequency(self, number):
        self._shooting_frequency = number

    def getExtraDamage(self):
        return self._extra_damage

    def setExtraDamage(self, number):
        self._extra_damage = number


class Enemy(Character):
    enemy_list = pygame.sprite.Group()

    def __init__(self, x, y, health, char_name):
        super().__init__(x, y, health, char_name)
        self._hit_time = 0
        self._speed = 2
        self._melee_damage = 3
        self._attack_range = TILE_SIZE / 2
        self._attack_cooldown = pygame.time.get_ticks()
        self._hit_sound = pygame.mixer.Sound("assets/audio/sounds/monster_bite.mp3")
        self._death_sound = pygame.mixer.Sound("assets/audio/sounds/monster_death.mp3")

    def ai(self, screen_scroll, hero):
        if not self._alive:
            if random.random() < 0.9:
                coin_drop_amount = random.randint(0, 3)
                for c in range(coin_drop_amount):
                    coin = Coin(self.rect.centerx + 10 * c, self.rect.centery + 10 * c)
                    Item.item_group.append(coin)
            else:
                potion = Potion(self.rect.centerx, self.rect.centery)
                Item.item_group.append(potion)
            self.kill()
            self._death_sound.play()

        self._move(hero)
        self._attack(hero)

        self.rect.centerx += screen_scroll[0]
        self.rect.centery += screen_scroll[1]

    def _move(self, hero):
        dx = 0
        dy = 0
        distance = math.sqrt((self.rect.centerx - hero.rect.centerx) ** 2 + (self.rect.centery - hero.rect.centery) ** 2)
        current_time = pygame.time.get_ticks()
        if distance >= self._attack_range and hero.getAlive() and current_time - self._hit_time > FPS * 2:
            if self.rect.centerx < hero.rect.centerx:
                dx = self._speed
                self._flip = False
            elif self.rect.centerx > hero.rect.centerx:
                dx = -self._speed
                self._flip = True
            if self.rect.centery < hero.rect.centery:
                dy = self._speed
            elif self.rect.centery > hero.rect.centery:
                dy = -self._speed
            self.rect.centerx += + dx
            self.rect.centery += + dy

        if dx != 0 or dy != 0:
            self._action = "run"
        else:
            self._action = "idle"

    def _attack(self, hero):
        distance = pow((self.rect.centerx - hero.rect.centerx) ** 2 + (self.rect.centery - hero.rect.centery) ** 2, 0.5)
        current_time = pygame.time.get_ticks()
        if distance < self._attack_range and current_time - self._attack_cooldown > FPS * 10 and hero.getAlive():
            damage = random.randint(-2, 2) + self._melee_damage
            self._hit_sound.play()
            hero.setHealth(hero.getHealth() - damage)
            self._attack_cooldown = current_time

    def setHitTime(self, new_time):
        self._hit_time = new_time

    @staticmethod
    def all_enemy_types():
        return [Muddy, Skeleton, Zombie, Goblin]


class Boss(Enemy):
    CHAR_NAME = "boss"

    def __init__(self, x, y, health=8000, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self.rect = pygame.Rect(0, 0, TILE_SIZE * 2, TILE_SIZE * 2)
        self._speed = 2.5
        self._melee_damage = 30
        self._bar_color = GREEN
        self._attack_range = TILE_SIZE
        self._attack_cooldown = pygame.time.get_ticks()
        self._hit_sound = pygame.mixer.Sound("assets/audio/sounds/boss_hit.mp3")
        self._death_sound = pygame.mixer.Sound("assets/audio/sounds/boss_death.mp3")
        self._death_sound.set_volume(10)
        self._fireball_group = pygame.sprite.Group()
        self._death_moment = 0
        self._fireball_cooldown = 0
        self._rage_cooldown = pygame.time.get_ticks()
        self._multiplier = 2
        self._imp_spawn_prob = 0.003
        self._rage = False

    def ai(self, screen_scroll, hero):
        current_time = pygame.time.get_ticks()
        if self._health <= 0:
            if self._death_moment == 0:
                self._death_sound.play()
                self._animation_cooldown = 6 * FPS
                self._death_moment = current_time
                if len(Enemy.enemy_list) > 1:
                    for enemy in Enemy.enemy_list:
                        if enemy != self:
                            enemy.kill()
            if current_time - self._death_moment > LEVEL_END_DURATION:
                self.kill()

        if current_time - self._rage_cooldown > FPS * 1000:
            self._rage = True
            if current_time - self._rage_cooldown > FPS * 1500:
                self._rage = False
                self._rage_cooldown = current_time

        self._attack(hero)
        self._move(hero)
        self._fireball_group.update(hero, screen_scroll)

        self.rect.centerx += screen_scroll[0]
        self.rect.centery += screen_scroll[1]

    def _attack(self, hero):
        current_time = pygame.time.get_ticks()
        distance = math.sqrt(pow(self.rect.centerx - hero.rect.centerx, 2) + pow(self.rect.centery - hero.rect.centery, 2))
        if distance < self._attack_range and hero.getAlive() and self._alive and current_time - self._attack_cooldown > FPS * 8:
            self._hit_sound.play()
            damage = random.randint(-5, 5) + self._melee_damage
            hero.setHealth(hero.getHealth() - damage)
            self._attack_cooldown = current_time

        if random.random() < self._imp_spawn_prob and self._alive and not self._rage:
            imp = Imp(self.rect.centerx, self.rect.centery)
            Enemy.enemy_list.add(imp)

        if current_time - self._fireball_cooldown > FPS * self._multiplier and self._alive and self._rage:
            fireball = FireBall(self.rect.centerx, self.rect.centery, hero)
            self._fireball_group.add(fireball)
            self._fireball_cooldown = current_time

    def _move(self, hero):
        dx = 0
        dy = 0
        distance = math.sqrt(pow(self.rect.centerx - hero.rect.centerx, 2) + pow(self.rect.centery - hero.rect.centery, 2))
        if distance >= self._attack_range and hero.getAlive() and self._alive and not self._rage:
            if self.rect.centerx < hero.rect.centerx:
                dx = self._speed
                self._flip = False
            elif self.rect.centerx > hero.rect.centerx:
                dx = -self._speed
                self._flip = True
            if self.rect.centery < hero.rect.centery:
                dy = self._speed
            elif self.rect.centery > hero.rect.centery:
                dy = -self._speed

        if dx != 0 or dy != 0:
            self._action = "run"
        else:
            self._action = "idle"

        self.rect.centerx += dx
        self.rect.centery += dy

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self._flip, False)
        surface.blit(flipped_image, self.rect)
        self._fireball_group.draw(surface)
        self.draw_health(surface)

    def draw_health(self, surface):
        health_ratio = self._health / self._max_health
        if (health_ratio < 0.6) and (health_ratio >= 0.2) and self._bar_color != YELLOW:
            self._bar_color = YELLOW
            self._multiplier = 1
            self._imp_spawn_prob = 0.005
        if health_ratio < 0.2 and self._bar_color != RED:
            self._bar_color = RED
            self._speed = 3.5
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH // 5, SCREEN_HEIGHT - 100, (SCREEN_WIDTH // 2 - SCREEN_WIDTH // 5) * 2, 40))
        pygame.draw.rect(surface, self._bar_color, (SCREEN_WIDTH // 5, SCREEN_HEIGHT - 100, ((SCREEN_WIDTH // 2 - SCREEN_WIDTH // 5) * 2) * health_ratio, 40))
        pygame.draw.rect(surface, GREY, (SCREEN_WIDTH // 5, SCREEN_HEIGHT - 100, (SCREEN_WIDTH // 2 - SCREEN_WIDTH // 5) * 2, 40), 2)


class Muddy(Enemy):
    CHAR_NAME = "muddy"

    def __init__(self, x, y, health=75, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self._melee_damage = 10
        self._speed = 1


class Imp(Enemy):
    CHAR_NAME = "imp"

    def __init__(self, x, y, health=50, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self._melee_damage = 4
        self._speed = 3.5


class Goblin(Enemy):
    CHAR_NAME = "goblin"

    def __init__(self, x, y, health=30, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self._melee_damage = 3
        self._speed = 3.5


class Zombie(Enemy):
    CHAR_NAME = "tiny_zombie"

    def __init__(self, x, y, health=40, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self._melee_damage = 5
        self._speed = 2.5


class Skeleton(Enemy):
    CHAR_NAME = "skeleton"

    def __init__(self, x, y, health=55, char_name=CHAR_NAME):
        super().__init__(x, y, health, char_name)
        self._melee_damage = 6
        self._speed = 2
