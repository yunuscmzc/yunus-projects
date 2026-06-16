import pygame
from constants import *


class Text(pygame.sprite.Sprite):
    def __init__(self, x, y, text, size, color):
        super().__init__()
        font = pygame.font.Font("assets\\fonts\\AtariClassic.ttf", size)
        self.image = font.render(text, False, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, screen_scroll):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class DamageText(Text):
    def __init__(self, x, y, text, size, color=RED):
        super().__init__(x, y, text, size, color)
        self.cooldown = 0

    def update(self, screen_scroll):
        self.rect.y -= 1
        self.cooldown += 1
        if self.cooldown > FPS:
            self.kill()

        self.rect.centerx += screen_scroll[0]
        self.rect.centery += screen_scroll[1]
