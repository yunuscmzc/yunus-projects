import pygame
import math
import random
from constants import *
from texts import DamageText

damage_text_group = pygame.sprite.Group()


class Bow:
    def __init__(self):
        self._angle = 0
        self._original_image = pygame.image.load("assets\\images\\weapons\\bow.png").convert_alpha()
        self._original_image = pygame.transform.scale_by(self._original_image, WEAPON_SCALE)
        self.image = pygame.transform.rotate(self._original_image, self._angle)
        self.rect = self.image.get_rect()
        self.arrow_group = pygame.sprite.Group()

    def update(self, player):
        self.rect.center = player.rect.center

        mouse_pos = pygame.mouse.get_pos()
        x_dist = mouse_pos[0] - player.rect.centerx
        y_dist = -(mouse_pos[1] - player.rect.centery)

        self._angle = math.degrees(math.atan2(y_dist, x_dist))

    def draw(self, surface):
        self.image = pygame.transform.rotate(self._original_image, self._angle)
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2)))

    def getAngle(self):
        return self._angle


class Arrow(pygame.sprite.Sprite):

    def __init__(self, x, y, angle):
        super().__init__()
        self._angle = angle
        self._speed = 11
        self._damage = 6
        self._original_image = pygame.image.load("assets\\images\\weapons\\arrow.png").convert_alpha()
        self._original_image = pygame.transform.scale_by(self._original_image, 1.3)
        self.image = pygame.transform.rotate(self._original_image, self._angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self._arrow_shot_sound = pygame.mixer.Sound("assets/audio/sounds/arrow_shot.mp3")
        self._arrow_shot_sound.play()
        self._arrow_hit_sound = pygame.mixer.Sound("assets/audio/sounds/arrow_hit.wav")
        self._dx = self._speed * math.cos(math.radians(self._angle))
        self._dy = self._speed * -math.sin(math.radians(self._angle))

    def update(self, enemy_list, hero):
        self.rect.x += self._dx
        self.rect.y += self._dy

        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for enemy in enemy_list:
            if self.rect.colliderect(enemy.rect) and enemy.getAlive():
                current_time = pygame.time.get_ticks()
                self._arrow_hit_sound.play()
                if random.random() < 0.90:
                    damage = self._damage + random.randint(-2, 2) + hero.getExtraDamage()
                    text = f"{damage}"
                elif random.random() < 0.95:
                    damage = (self._damage + random.randint(-2, 2) + hero.getExtraDamage()) * 5
                    text = f"CRIT {damage}"
                else:
                    damage = 0
                    text = "DODGE"
                enemy.setHealth(enemy.getHealth() - damage)
                enemy.setHitTime(current_time)
                damage_text = DamageText(enemy.rect.centerx, enemy.rect.y, text, 15)
                damage_text_group.add(damage_text)
                self.kill()
                break

    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width() / 2), self.rect.centery - int(self.image.get_height() / 2)))


class FireBall(pygame.sprite.Sprite):
    def __init__(self, x, y, hero):
        super().__init__()
        self.image = pygame.image.load("assets\\images\\weapons\\fireball.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self._speed = 6
        self._damage = 8
        x_dist = hero.rect.centerx - x
        y_dist = -(hero.rect.centery - y)
        self._angle = math.degrees(math.atan2(y_dist, x_dist))
        self._dx = self._speed * math.cos(math.radians(self._angle))
        self._dy = -(self._speed * math.sin(math.radians(self._angle)))

    def update(self, hero, screen_scroll):
        self.rect.x += self._dx + screen_scroll[0]
        self.rect.y += self._dy + screen_scroll[1]

        if self.rect.bottom < -SCREEN_HEIGHT or self.rect.top > 2 * SCREEN_HEIGHT or self.rect.right < -SCREEN_WIDTH or self.rect.left > 2 * SCREEN_WIDTH:
            self.kill()

        if self.rect.colliderect(hero.rect):
            damage = self._damage + random.randint(-2, 2)
            hero.setHealth(hero.getHealth() - damage)
            self.kill()

    def draw(self, surface):
        surface.blit(self.rect, self.image)
