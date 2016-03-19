import sys
import pygame
from pygame.locals import *
from math import floor
import random


def init_window():
    pygame.init()
    pygame.display.set_mode((512, 512))
    pygame.display.set_caption('Packman')


def draw_background(scr, img=None):
    if img:
        scr.blit(img, (0, 0))
    else:
        bg = pygame.Surface(scr.get_size())
        bg.fill((0, 0, 0))
        scr.blit(bg, (0, 0))


class GameObject(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tile_size, map_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img)
        self.screen_rect = None
        self.x = 0
        self.y = 0
        self.tick = 0
        self.tile_size = tile_size
        self.map_size = map_size
        self.set_coord(x, y)

    def set_coord(self, x, y):
        self.x = x
        self.y = y
        self.screen_rect = Rect(floor(x) * self.tile_size, floor(y) * self.tile_size, self.tile_size, self.tile_size )

    def game_tick(self, _map):
        self.tick += 1

    def draw(self, scr):
        scr.blit(self.image, (self.screen_rect.x, self.screen_rect.y))


class Ghost(GameObject):
    def __init__(self, x, y, tile_size, map_size):
        GameObject.__init__(self, './resources/ghost.png', x, y, tile_size, map_size)
        self.direction = 0
        self.velocity = 4.0 / 10.0

    def game_tick(self, _map):
        super(Ghost, self).game_tick(_map)
        if self.tick % 20 == 0 or self.direction == 0:
            self.direction = random.randint(1, 4)

        if self.direction == 1 and not Map.is_wall(_map, int(self.x+1), int(self.y)):
            self.x += self.velocity
            if self.x >= self.map_size-1:
                self.x = self.map_size-1
                self.direction = random.choice((2, 3, 4))
        elif self.direction == 2 and not Map.is_wall(_map, int(self.x), int(self.y+1)):
            self.y += self.velocity
            if self.y >= self.map_size-1:
                self.y = self.map_size-1
                self.direction = random.choice((1, 3, 4))
        elif self.direction == 3 and not Map.is_wall(_map, int(self.x-1), int(self.y)):
            self.x -= self.velocity
            if self.x <= 0:
                self.x = 0
                self.direction = random.choice((1, 2, 4))
        elif self.direction == 4 and not Map.is_wall(_map, int(self.x), int(self.y-1)):
            self.y -= self.velocity
            if self.y <= 0:
                self.y = 0
                self.direction = random.choice((1, 2, 3))
        self.set_coord(self.x, self.y)



class Dot(GameObject):
    def __init__(self, x, y, tile_size, map_size, effect = 'zero'):
        GameObject.__init__(self, './resources/food.png', x, y, tile_size, map_size)
        self.effect = effect
        if effect == 'speed':
            self.image = pygame.image.load('./resources/speed_bonus.png')
        elif effect == 'eat':
            self.image = pygame.image.load('./resources/eat_bonus.png')


class Pacman(GameObject):
    def __init__(self, x, y, tile_size, map_size):
        GameObject.__init__(self, './resources/pacman_right.png', x, y, tile_size, map_size)
        self.direction = 0
        self.velocity = 4.0 / 10.0
        self.tick_speed = 0
        self.tick_eat = 0
        self.hungry = False


    def game_tick(self, _map):
        super(Pacman, self).game_tick(_map)

        if Map.is_dot(_map, int(self.x), int(self.y)):
            if _map.map[int(self.y)][int(self.x)].effect == 'speed':
                self.tick_speed = self.tick
                self.velocity = 8.0 / 10.0
            elif _map.map[int(self.y)][int(self.x)].effect == 'eat':
                self.tick_eat = self.tick
                self.hungry = True

            Map.remove_object(_map, int(self.x), int(self.y))
        if self.tick - self.tick_speed == 50:
            self.velocity = 4.0 / 10.0

        if self.tick - self.tick_eat == 50:
            self.hungry = False

        if self.direction == 1 and not Map.is_wall(_map, int(self.x+1), int(self.y)):
            self.image = pygame.image.load('./resources/pacman_right.png')
            self.x += self.velocity
            if self.x >= self.map_size-1:
                self.x = self.map_size-1
        elif self.direction == 2 and not Map.is_wall(_map, int(self.x), int(self.y+1)):
            self.image = pygame.image.load('./resources/pacman_down.png')
            self.y += self.velocity
            if self.y >= self.map_size-1:
                self.y = self.map_size-1
        elif self.direction == 3 and not Map.is_wall(_map, int(self.x-1), int(self.y)):
            self.image = pygame.image.load('./resources/pacman_left.png')
            self.x -= self.velocity
            if self.x <= 0:
                self.x = 0
        elif self.direction == 4 and not Map.is_wall(_map, int(self.x), int(self.y-1)):
            self.image = pygame.image.load('./resources/pacman_up.png')
            self.y -= self.velocity
            if self.y <= 0:
                self.y = 0


        self.set_coord(self.x, self.y)

class Wall(GameObject):
    def __init__(self, x, y, tile_size, map_size):
        GameObject.__init__(self, './resources/wall.png', x, y, tile_size, map_size)

class Map:
    def __init__(self, file):
        self.map = [[None for x in range(16)] for y in range(16)]
        f = open(file, 'r')
        txt_map = f.readlines()

        for (y, l) in enumerate(txt_map):
            for (x, c) in enumerate(l):
                if txt_map[y][x] == '#':
                    self.map[y][x] = Wall(x, y, tile_size, map_size)
                elif txt_map[y][x] == '.':
                    self.map[y][x] = Dot(x, y, tile_size, map_size)
                elif txt_map[y][x] == '^':
                    self.map[y][x] = Dot(x, y, tile_size, map_size, 'speed')
                elif txt_map[y][x] == '&':
                    self.map[y][x] = Dot(x, y, tile_size, map_size, 'eat')

    def draw_map(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if type(self.map[y][x]) == Wall or type(self.map[y][x]) == Dot:
                    self.map[y][x].draw(screen)

    def is_wall(self, x, y):
        if y < len(self.map) and x < len(self.map[y]):
            return type(self.map[y][x]) == Wall

    def is_dot(self, x, y):
        if y < len(self.map) and x < len(self.map[y]):
            return type(self.map[y][x]) == Dot

    def remove_object(self, x, y):
        self.map[y][x] = None


def process_events(events, packman):
    for event in events:
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
            sys.exit(0)
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                packman.direction = 3
            elif event.key == K_RIGHT:
                packman.direction = 1
            elif event.key == K_UP:
                packman.direction = 4
            elif event.key == K_DOWN:
                packman.direction = 2
            elif event.key == K_SPACE:
                packman.direction = 0


if __name__ == '__main__':
    init_window()
    tile_size = 32
    map_size = 16
    Ghosts = [Ghost(0, 0, tile_size, map_size), Ghost(10, 10, tile_size, map_size), Ghost(8, 8, tile_size, map_size), Ghost(9, 9, tile_size, map_size)]
    pacman = Pacman(5, 5, tile_size, map_size)
    background = pygame.image.load("./resources/background.png")
    screen = pygame.display.get_surface()
    map = Map('map.txt')

    while 1:
        process_events(pygame.event.get(), pacman)
        pygame.time.delay(100)
        pacman.game_tick(map)
        draw_background(screen, background)
        map.draw_map()
        for ghost in Ghosts:
            ghost.game_tick(map)
            if int(ghost.y) == int(pacman.y) and int(ghost.x) == int(pacman.x):
                if pacman.hungry:
                    Ghosts.remove(ghost)
                else:
                    sys.exit('You lost')
            ghost.draw(screen)
        pacman.draw(screen)

        pygame.display.update()

