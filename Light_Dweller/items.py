import pygame
import os
from constants import *


class Item:
    item_group = list()

    def __init__(self, x, y, item_type):
        super().__init__()
        self._animations = os.listdir(f"assets\\images\\items\\{item_type}")
        self._image = pygame.image.load(f"assets\\images\\items\\{item_type}\\{self._animations[0]}").convert_alpha()
        self._image = pygame.transform.scale_by(self._image, ITEM_SCALE)
        self._rect = self._image.get_rect()
        self._rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self._image, self._rect)

    def update(self, hero, screen_scroll):
        pass

    def getRect(self):
        return self._rect


class Coin(Item):
    def __init__(self, x, y, item_type="coin"):
        super().__init__(x, y, item_type)
        self._coin_images = list()
        self._frame_index = 0
        self._update_time = pygame.time.get_ticks()
        self._creation = pygame.time.get_ticks()
        self._coin_sound = pygame.mixer.Sound("assets/audio/sounds/coin.wav")
        for animation in self._animations:
            img = pygame.image.load(f"assets\\images\\items\\coin\\{animation}").convert_alpha()
            img = pygame.transform.scale_by(img, ITEM_SCALE)
            self._coin_images.append(img)

    def update(self, hero, screen_scroll, collectable=True):
        current_time = pygame.time.get_ticks()
        if self._frame_index >= len(self._animations):
            self._frame_index = 0

        if current_time - self._update_time > FPS:
            self._image = self._coin_images[self._frame_index]
            self._frame_index += 1
            self._update_time = current_time

        if self._rect.colliderect(hero.rect) and collectable:
            self._coin_sound.play()
            hero.setCoinAmount(1)
            Item.item_group.remove(self)

        if collectable:
            self._rect.centerx += screen_scroll[0]
            self._rect.centery += screen_scroll[1]

        if pygame.time.get_ticks() - self._creation > FPS * 500:
            if self in Item.item_group:
                Item.item_group.remove(self)


class Potion(Item):
    def __init__(self, x, y, item_type="potion"):
        super().__init__(x, y, item_type)
        self._increment = 10
        self._heal_sound = pygame.mixer.Sound("assets/audio/sounds/heal.wav")
        self._creation = pygame.time.get_ticks()

    def update(self, hero, screen_scroll):
        if self._rect.colliderect(hero.rect):
            if hero.getHealth() < hero.getMaxHealth():
                hero.setHealth(min(hero.getMaxHealth(), hero.getHealth() + self._increment))
                self._heal_sound.play()
                Item.item_group.remove(self)

        self._rect.centerx += screen_scroll[0]
        self._rect.centery += screen_scroll[1]
