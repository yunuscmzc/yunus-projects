import pygame
from constants import *


class Fade:
    def __init__(self, color):
        super().__init__()
        self._color = color
        self._fade_counter = 0

    def fade(self, surface):
        pass

    def setFadeCounter(self, number):
        self._fade_counter = number


class IntroFade(Fade):
    def __init__(self, color):
        super().__init__(color)

    def fade(self, surface):
        self._fade_counter += 4
        pygame.draw.rect(surface, self._color, (0 - self._fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        pygame.draw.rect(surface, self._color, (0, 0 - self._fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        pygame.draw.rect(surface, self._color, (SCREEN_WIDTH // 2 + self._fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        pygame.draw.rect(surface, self._color, (0, SCREEN_HEIGHT // 2 + self._fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        if self._fade_counter > SCREEN_WIDTH // 2:
            return True
        return False


class DeathFade(Fade):
    def __init__(self, color):
        super().__init__(color)

    def fade(self, surface):
        self._fade_counter += 5
        pygame.draw.rect(surface, self._color, (0, 0, SCREEN_WIDTH, self._fade_counter))
        if self._fade_counter > SCREEN_HEIGHT:
            return True
        return False


class LastFade(Fade):
    def __init__(self, color):
        super().__init__(color)

    def fade(self, surface):
        self._fade_counter += 4
        pygame.draw.rect(surface, self._color, (0, 0, SCREEN_WIDTH, self._fade_counter))
        if self._fade_counter > SCREEN_HEIGHT:
            return True
        return False
