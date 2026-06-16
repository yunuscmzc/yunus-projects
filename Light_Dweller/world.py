import random
import pygame
import csv
import os
from constants import TILE_SIZE, LEVEL_END_DURATION
from character import Hero, Enemy, Boss
from tower import Tower


class World:
    def __init__(self, level):
        self._level = level
        self._map_tiles = list()
        self._obstacle_tiles = list()
        self._all_tile_images = list()
        self._enemy_respawn_locations = dict()
        self._hero = None
        self._tower = None
        self._level_complete = False
        self._game_complete = False
        self._duration = 0
        self._remaining_enemy = self._level * 60

        pygame.mixer.music.load(f"assets/audio/musics/{self._level}.mp3")
        pygame.mixer.music.set_volume(2)
        pygame.mixer.music.play(-1, 0.0, 5000)

        for tile in os.listdir("assets\\tiles"):
            image = pygame.image.load(f"assets\\tiles\\{tile}").convert_alpha()
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            self._all_tile_images.append(image)

    def process_level(self):
        world_data = list()
        with open(f"assets/levels/level{self._level}.csv", newline="") as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            for row in reader:
                temp_list = list()
                for tile in row:
                    temp_list.append(tile)
                world_data.append(temp_list)

        for y, row in enumerate(world_data):
            for x, tile in enumerate(row):
                if int(tile) >= 0:
                    if tile.startswith("1"):
                        image = self._all_tile_images[1]
                    else:
                        image = self._all_tile_images[0]
                    image_rect = image.get_rect()
                    image_rect.center = (x * TILE_SIZE, y * TILE_SIZE)
                    self._map_tiles.append([image, image_rect])
                    if tile == "1":
                        self._obstacle_tiles.append([image, image_rect])
                    if tile == "2":
                        self._hero = Hero(x * TILE_SIZE, y * TILE_SIZE, 100)
                    elif tile == "3":
                        self._enemy_respawn_locations["skeleton"] = [x * TILE_SIZE, y * TILE_SIZE]
                    elif tile == "4":
                        self._enemy_respawn_locations["muddy"] = [x * TILE_SIZE, y * TILE_SIZE]
                    elif tile == "5":
                        self._enemy_respawn_locations["tiny_zombie"] = [x * TILE_SIZE, y * TILE_SIZE]
                    elif tile == "6":
                        self._enemy_respawn_locations["goblin"] = [x * TILE_SIZE, y * TILE_SIZE]
                    elif tile == "8":
                        boss = Boss(x * TILE_SIZE, y * TILE_SIZE)
                        Enemy.enemy_list.add(boss)
                    elif tile == "9":
                        self._tower = Tower(x * TILE_SIZE, y * TILE_SIZE)

        return self._tower, self._hero

    def update(self, screen_scroll):
        for tile in self._map_tiles:
            tile[1].centerx += screen_scroll[0]
            tile[1].centery += screen_scroll[1]
        for location in self._enemy_respawn_locations.values():
            location[0] += screen_scroll[0]
            location[1] += screen_scroll[1]

    def draw(self, surface):
        for tile in self._map_tiles:
            surface.blit(tile[0], tile[1])

    def getEnemyRespawnLocation(self):
        return self._enemy_respawn_locations

    def getObstacleTiles(self):
        return self._obstacle_tiles

    def generate_monsters(self):
        if self._level < 3:
            if self._remaining_enemy > 0:
                enemy_creation_frequency = random.random()
                if enemy_creation_frequency < self._level * 0.013:
                    self._remaining_enemy -= 1
                    enemy_type = random.choice(Enemy.all_enemy_types())
                    x_loc = self.getEnemyRespawnLocation()[enemy_type.CHAR_NAME][0]
                    y_loc = self.getEnemyRespawnLocation()[enemy_type.CHAR_NAME][1]
                    enemy = enemy_type(x_loc, y_loc)
                    Enemy.enemy_list.add(enemy)

            elif len(Enemy.enemy_list) == 0:
                current_time = pygame.time.get_ticks()
                if self._duration == 0:
                    self._duration = current_time
                if current_time - self._duration > LEVEL_END_DURATION:
                    self._level_complete = True
                    self._duration = 0
        else:
            if len(Enemy.enemy_list) == 0:
                self._game_complete = True

    def getLevelComplete(self):
        return self._level_complete

    def getGame_complete(self):
        return self._game_complete
