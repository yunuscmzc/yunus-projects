import pygame


class Button:
    def __init__(self, x, y, button_type):
        self._image = pygame.image.load(f"assets\\images\\buttons\\{button_type}.png").convert_alpha()
        self._image = pygame.transform.scale_by(self._image, 1)
        self._rect = self._image.get_rect()
        self._rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self._image, self._rect)
        return self.update()

    def update(self):
        mouse_tick = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_tick[0] and self._rect.collidepoint(mouse_pos):
            return True
        return False
