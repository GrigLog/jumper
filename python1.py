import pygame
import math
from copy import deepcopy
from random import randrange as r, choice as c
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global pp
        super().__init__()
        self.image = pygame.transform.scale(load_image('player.png'), (50, 98))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.ftimer = 0
        self.protected = False
        self.view = 1
        self.hp = 3
        self.st = ''
        self.j = False
        self.todo = [[], []]
        pp = pygame.sprite.Group()
        pp.add(self)

    def draw(self):
        pp.draw(screen)

    def update(self):
        if pygame.sprite.spritecollideany(self, static):
            self.st = 's'
            self.j = True
        else:
            self.st = ''
            self.j = False
        if pygame.sprite.spritecollideany(self, danger):
            self.take_damage()
        self.draw()

    def do(self):
        if self.todo != [[], []]:
            for i in range(len(self.todo)):
                if self.todo[i]:
                    self.todo[i][0][1](*self.todo[i][0][0])
                    del self.todo[i][0]

    def move(self, x, y):
        if self.view == 1 and x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = 0
        if self.view == 0 and x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = 1
        self.rect.x += x
        self.rect.y += y
        if pygame.sprite.spritecollideany(self, static):
            self.rect.y = pygame.sprite.spritecollideany(self, static).rect.y - self.rect[3] + 1

    def jump(self):
        self.todo[0] = [[(0, -30 + i * 2), self.move] for i in range(10)]
        self.j = False

    def take_damage(self):
        if not self.protected:
            pygame.time.set_timer(protect, 500)
            self.chtex('player2.png')
            self.todo[1].append([['player.png'], self.chtex])
            self.hp -= 1
            self.protected = True
        self.ftimer = 0
        self.jump()

    def chtex(self, image):
        self.image = pygame.transform.scale(load_image(image), (50, 98))
        if self.view == 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def fall(self):
        if self.st == '':
            self.move(0, self.ftimer + 5)
            self.ftimer += 0.2
        else:
            self.ftimer = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static)
        self.image = pygame.transform.scale(load_image('bricks.png'), (102, 102))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(danger)
        self.image = pygame.transform.scale(load_image('spikes.png'), (102, 54))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)


pygame.init()
pygame.font.init()
running = True
size = w, h = 1000, 500
screen = pygame.display.set_mode(size)
ss, stairs, pp, danger = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
static = pygame.sprite.Group()
p = Player(0, 0)
Platform(200, 300)
for i in range(10):
    Spike(300 + 100 * i, 350)
    Platform(300 + 100 * i, 400)
fall = pygame.USEREVENT
doing = pygame.USEREVENT + 1
protect = pygame.USEREVENT + 2
pygame.time.set_timer(fall, 20)
pygame.time.set_timer(doing, 20)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                if p.j:
                    p.jump()
        if event.type == doing:
            p.do()
        if event.type == fall:
            p.fall()
        if event.type == protect:
            p.protected = False
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        p.move(-1, 0)
    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        p.move(1, 0)
    screen.fill((150, 150, 150))
    p.update()
    danger.draw(screen)
    static.draw(screen)
    pygame.display.flip()
