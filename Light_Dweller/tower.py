import pygame
from constants import *
from texts import Text
from items import Coin


class Tower:
    def __init__(self, x, y):
        self._image = pygame.image.load("assets\\images\\tower.png")
        self._image = pygame.transform.scale_by(self._image, 0.2)
        self._rect = pygame.Rect(0, 0, TILE_SIZE * 2, TILE_SIZE * 1.8)
        self._rect.center = (x, y)

        # Image of Bow
        self._bow_image = pygame.image.load("assets\\images\\weapons\\bow.png").convert_alpha()
        self._bow_image = pygame.transform.scale_by(self._bow_image, 2)
        self._bow_rect = self._bow_image.get_rect()
        self._bow_rect.center = (SCREEN_WIDTH // 3 - 55, SCREEN_HEIGHT // 1.6)
        self._bow_upgrade = 1
        self._previous_bow_upgrade = self._bow_upgrade
        self._bow_upgrade_price = self._bow_upgrade * 50

        # Image of Arrow
        self._arrow_image = pygame.image.load("assets\\images\\weapons\\arrow.png")
        self._arrow_image = pygame.transform.scale_by(self._arrow_image, 2)
        self._arrow_rect = self._arrow_image.get_rect()
        self._arrow_rect.center = (SCREEN_WIDTH // 3 - 20, SCREEN_HEIGHT // 2.2)
        self._arrow_upgrade = 1
        self._previous_arrow_upgrade = self._arrow_upgrade
        self._arrow_upgrade_price = self._arrow_upgrade * 50

        # Information texts
        self._shop_text = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50, "MARKET", 30, BRIGHT_YELLOW)
        self._bow_text = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.6, "Upgrade Frequency", 15, WHITE)
        self._bow_price_text = Text(SCREEN_WIDTH // 1.4, SCREEN_HEIGHT // 1.6, f"{self._bow_upgrade_price}", 15, WHITE)
        self._arrow_text = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.2, "Upgrade Damage (+2)", 15, WHITE)
        self._arrow_price_text = Text(SCREEN_WIDTH // 1.4, SCREEN_HEIGHT // 2.2, f"{self._arrow_upgrade_price}", 15, WHITE)

        # Coin Icons
        self._icon_coin_bow = Coin(SCREEN_WIDTH // 1.47, SCREEN_HEIGHT // 1.6)
        self._icon_coin_arrow = Coin(SCREEN_WIDTH // 1.47, SCREEN_HEIGHT // 2.2)

        # Purchase Area
        self._bow_purchase_area = pygame.Rect(self._icon_coin_bow.getRect().x, self._icon_coin_bow.getRect().y - 10, 70, 40)
        self._arrow_purchase_area = pygame.Rect(self._icon_coin_arrow.getRect().x, self._icon_coin_arrow.getRect().y - 10, 70, 40)

        # Upgrade Sound
        self._upgrade_sound = pygame.mixer.Sound("assets/audio/sounds/upgrade_sound.mp3")
        self._upgrade_sound.set_volume(30)

    def update(self, screen_scroll):
        self._rect.x += screen_scroll[0]
        self._rect.y += screen_scroll[1]

    def draw(self, surface):
        surface.blit(self._image, (self._rect.x - 55, self._rect.y - 120))

    def is_in_shop_region(self, hero):
        return self._rect.colliderect(hero.rect)

    def display_shop(self, is_shopping, surface, hero):
        self._update_information()
        if is_shopping:
            pygame.draw.rect(surface, GREY, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            # Images
            surface.blit(self._bow_image, self._bow_rect)
            surface.blit(self._arrow_image, self._arrow_rect)
            # Texts
            self._shop_text.draw(surface)
            self._bow_text.draw(surface)
            self._bow_price_text.draw(surface)
            self._arrow_text.draw(surface)
            self._arrow_price_text.draw(surface)
            # Coin Icons
            self._icon_coin_bow.draw(surface)
            self._icon_coin_bow.update(hero, [0, 0], False)
            self._icon_coin_arrow.draw(surface)
            self._icon_coin_arrow.update(hero, [0, 0], False)
            # Purchase Area
            pygame.draw.rect(surface, BRIGHT_YELLOW, self._bow_purchase_area, 1)
            pygame.draw.rect(surface, BRIGHT_YELLOW, self._arrow_purchase_area, 1)

    def upgrade_item(self, hero):
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pressed[0] and self._bow_purchase_area.collidepoint(mouse_pos):
            if hero.getCoinAmount() >= self._bow_upgrade_price and self._bow_upgrade < 3:
                self._upgrade_sound.play()
                hero.setShootingFrequency(hero.getShootingFrequency() - FPS)
                hero.setCoinAmount(-self._bow_upgrade_price)
                self._bow_upgrade += 1
        if mouse_pressed[0] and self._arrow_purchase_area.collidepoint(mouse_pos):
            if hero.getCoinAmount() >= self._arrow_upgrade_price and self._arrow_upgrade < 3:
                self._upgrade_sound.play()
                hero.setExtraDamage(hero.getExtraDamage() + 2)
                hero.setCoinAmount(-self._arrow_upgrade_price)
                self._arrow_upgrade += 1

    def _update_information(self):
        if self._bow_upgrade != self._previous_bow_upgrade:
            self._previous_bow_upgrade = self._bow_upgrade
            if self._bow_upgrade == 3:
                self._bow_upgrade_price = float("inf")
            else:
                self._bow_upgrade_price = self._bow_upgrade * 50
            self._bow_price_text = Text(SCREEN_WIDTH // 1.4, SCREEN_HEIGHT // 1.6, f"{self._bow_upgrade_price}", 15, WHITE)

        if self._arrow_upgrade != self._previous_arrow_upgrade:
            self._previous_arrow_upgrade = self._arrow_upgrade
            if self._arrow_upgrade == 3:
                self._arrow_upgrade_price = float("inf")
            else:
                self._arrow_upgrade_price = self._arrow_upgrade * 50
            self._arrow_price_text = Text(SCREEN_WIDTH // 1.4, SCREEN_HEIGHT // 2.2, f"{self._arrow_upgrade_price}", 15, WHITE)

    def getBowUpgrade(self):
        return self._bow_upgrade

    def setBowUpgrade(self, number):
        self._bow_upgrade = number

    def getArrowUpgrade(self):
        return self._arrow_upgrade

    def setArrowUpgrade(self, number):
        self._arrow_upgrade = number
