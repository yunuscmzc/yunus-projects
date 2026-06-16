import pygame
from character import Enemy, Hero
from constants import *
from weapon import damage_text_group
from items import Coin, Item
from texts import Text
from world import World
from fade import IntroFade, DeathFade, LastFade
from button import Button


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self._surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Light Crawler")
        self._icon_coin = Coin(SCREEN_WIDTH - 35, BAR_HEIGHT / 2)
        self._icon_hero = Hero(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 1)
        self._screen_scroll = [0, 0]
        self._level = 1

    def run(self):

        # Texts
        death_text = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6, "YOU DIED!", 30, WHITE)
        congrats_text1 = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, "CONGRATS!", 30, BLACK)
        congrats_text2 = Text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "YOU'VE DEFEATED THE BOSS", 30, BLACK)

        # Fades
        intro_fade = IntroFade(BLACK)
        death_fade = DeathFade(BLACK)
        last_fade = LastFade(WHITE)

        # Buttons
        restart_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50, "restart")
        exit_button = Button(SCREEN_WIDTH // 2, (3 * SCREEN_HEIGHT) // 4 - 20, "exit")

        # Booleans
        is_on = True
        start_fade = True
        is_shopping = False

        # Initial creation of world
        clock = pygame.time.Clock()
        world = World(self._level)
        tower, hero = world.process_level()

        while is_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_on = False
                if event.type == pygame.KEYDOWN:
                    if tower.is_in_shop_region(hero):
                        if event.key == pygame.K_e:
                            is_shopping = True
                        elif event.key == pygame.K_q:
                            is_shopping = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if tower.is_in_shop_region(hero):
                        tower.upgrade_item(hero)

            if world.getLevelComplete():
                start_fade = True
                self._level += 1
                # Previous Level Conditions for Hero
                previous_coin_amount = hero.getCoinAmount()
                previous_shooting_frequency = hero.getShootingFrequency()
                previous_extra_damage = hero.getExtraDamage()

                # Previous Level Conditions for Tower
                previous_bow_upgrade = tower.getBowUpgrade()
                previous_arrow_upgrade = tower.getArrowUpgrade()

                tower, hero, world = self.reset_level()

                hero.setCoinAmount(previous_coin_amount)
                hero.setShootingFrequency(previous_shooting_frequency)
                hero.setExtraDamage(previous_extra_damage)
                tower.setBowUpgrade(previous_bow_upgrade)
                tower.setArrowUpgrade(previous_arrow_upgrade)

            # draw
            self._surface.fill(BG_COLOR)
            world.draw(self._surface)
            hero.draw(self._surface)
            tower.draw(self._surface)
            for item in Item.item_group:
                item.draw(self._surface)
            for enemy in Enemy.enemy_list:
                enemy.draw(self._surface)
            hero.bow.arrow_group.draw(self._surface)
            damage_text_group.draw(self._surface)
            self.draw_bar(hero)
            hero.draw_health(self._surface)
            if start_fade:
                if intro_fade.fade(self._surface):
                    start_fade = False
                    intro_fade.setFadeCounter(0)
            tower.display_shop(is_shopping, self._surface, hero)

            if not world.getGame_complete() and not is_shopping:
                if hero.getAlive():
                    world.generate_monsters()
                    # update
                    world.update(self._screen_scroll)
                    hero.update()
                    tower.update(self._screen_scroll)
                    for enemy in Enemy.enemy_list:
                        enemy.update()
                        enemy.ai(self._screen_scroll, hero)
                    hero.bow.arrow_group.update(Enemy.enemy_list, hero)
                    damage_text_group.update(self._screen_scroll)
                    for item in Item.item_group:
                        item.update(hero, self._screen_scroll)
                    # move player
                    self._screen_scroll = hero.move(world.getObstacleTiles())
                else:
                    self._level = 1
                    if death_fade.fade(self._surface):
                        self._icon_hero.draw(self._surface)
                        self._icon_hero.update()
                        death_text.draw(self._surface)
                        if restart_button.draw(self._surface):
                            death_fade.setFadeCounter(0)
                            start_fade = True
                            tower, hero, world = self.reset_level()
                        if exit_button.draw(self._surface):
                            is_on = False

            elif world.getGame_complete():
                if last_fade.fade(self._surface):
                    congrats_text1.draw(self._surface)
                    congrats_text2.draw(self._surface)
                    if exit_button.draw(self._surface):
                        is_on = False

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

    def reset_level(self):
        Item.item_group.clear()
        Enemy.enemy_list.empty()
        world = World(self._level)
        tower, hero = world.process_level()
        return tower, hero, world

    def draw_bar(self, hero):
        pygame.draw.line(self._surface, WHITE, (0, BAR_HEIGHT), (SCREEN_WIDTH, BAR_HEIGHT))
        pygame.draw.rect(self._surface, GREY, (0, 0, SCREEN_WIDTH, BAR_HEIGHT))
        self._icon_coin.draw(self._surface)
        self._icon_coin.update(hero, self._screen_scroll, False)
        coin_score = Text(self._icon_coin.getRect().x - 30, BAR_HEIGHT / 2, f"{hero.getCoinAmount()}X", 15, WHITE)
        coin_score.draw(self._surface)
        level_text = Text(SCREEN_WIDTH / 2, BAR_HEIGHT / 2, f"WAVE: {self._level}", 15, WHITE)
        level_text.draw(self._surface)
