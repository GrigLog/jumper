import pygame
import os
import ctypes
from threading import Timer
from random import randint, choice as ch
from math import sin, cos
import math


w, h = ctypes.windll.user32.GetSystemMetrics(0),\
ctypes.windll.user32.GetSystemMetrics(1)


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


def game_over():
    global running
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    Button((w - 500) // 2 + 50, (h - 200) // 2 + 100, 100, 60, 'YES!')
    Button((w - 500) // 2 + 250, (h - 200) // 2 + 100, 100, 60, 'EXIT')
    screen.blit(font1.render('GAME OVER.', False, (255, 0, 0)), ((w - 500) // 2, (h - 200) // 2 - 200))
    screen.blit(font1.render('RESTART?', False, (255, 255, 255)), ((w - 500) // 2 + 10, (h - 200) // 2 - 100))
    buttons.draw(screen)


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text, font=None):
        super().__init__(buttons)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 5, y
        pygame.draw.rect(self.image, (255, 255, 255), pygame.Rect(0, 0, w, h), 5)
        if font is None:
            screen.blit(font2.render(text, False, (255, 255, 255)), (x, y))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, main=True):
        super().__init__(glb)
        if main:
            self.player_init()
        self.rect.x, self.rect.y = int(x * 100) + 25, int(y * 100)
        self.view = 1
        self.mid = [self.rect.x + self.rect[2] / 2, self.rect.y + self.rect[3] / 2]
        self.st = ''
        self.j = False
        self.sh = True
        self.jcounter = 0
        self.todo = [[], []]

    def player_init(self):
        global pp
        self.image = pygame.transform.scale(load_image('player.png'), (50, 80))
        self.rect = self.image.get_rect()
        self.vert = 0
        self.hp = Health(3)
        self.protected = False
        pp = pygame.sprite.Group()
        pp.add(self)

    def update(self):
        self.mid = [self.rect.x + self.rect[2], self.rect.y + self.rect[3]]
        self.fall()
        self.do()
        if pygame.sprite.spritecollideany(self, danger):
            self.take_damage()
        if pygame.sprite.spritecollideany(self, enemies):
            self.take_damage()

    def do(self):
        if self.todo != [[], []]:
            for i in range(len(self.todo)):
                if self.todo[i]:
                    self.todo[i][0][1](*self.todo[i][0][0])
                    del self.todo[i][0]

    def move(self, x, y):
        if self.view == 1 and x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = -1
        if self.view == -1 and x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = 1
        self.rect.x += x
        self.rect.y += y
        obj = pygame.sprite.spritecollideany(self, static)
        if obj:
            if x > 0:
                self.rect.x = obj.rect.x - self.rect[2] - 1
            elif x < 0:
                self.rect.x = obj.rect.x + obj.rect[2] + 1
            elif y > 0:
                self.st = 's'
                self.sh = True
                self.j = True
                self.rect.y = obj.rect.y - self.rect[3] - 1
            elif y < 0:
                self.rect.y = obj.rect.y + obj.rect[3] + 1
        else:
            if self.st != 'j':
                self.st = ''
            self.j = False

    def jump(self):
        self.todo[0] = [[(0, -20), self.move] for i in range(14)]
        self.j = False

    def shift(self):
        if self.sh:
            self.sh = False
            if self.vert != 1:
                self.todo[0] = [[(50 * self.view, 0), self.move] for i in range(4)]
            else:
                self.todo[0] = [[(0, -60), self.move] for i in range(4)]

    def take_damage(self):
        if not self.protected:
            pygame.time.set_timer(protect, 1000)
            self.chtex('player2.png')
            self.hp.remove(1)
            self.protected = True
            self.jump()
        self.sh = True

    def chtex(self, image, w=False, h=False):
        if type(image) == list:
            image = ''.join(image)
        if not w:
            w, h = self.rect[2], self.rect[3]
        self.image = pygame.transform.scale(load_image(image), (w, h))
        if self.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y += self.rect.h - h
        self.rect.w, self.rect.h = w, h


    def fall(self):
        if self.st != 's':
            self.move(0, 10)


class Hitpoint(pygame.sprite.Sprite):
    def __init__(self, n):
        super().__init__(health, glb)
        self.image = pygame.transform.scale(load_image('hp.png'), (60, 51))
        self.rect = self.image.get_rect()
        self.rect.y = 10
        self.rect.x = 70 * n + 10


class Health:
    def __init__(self, n):
        for i in range(n):
            Hitpoint(i)
        self.n = n

    def remove(self, c=1):
        global end
        self.n -= c
        health.remove(health.sprites()[-1])
        if self.n <= 0:
            end = True
            p.todo[1].append([(800), pygame.time.delay])

    def add(self, c=1):
        self.n += c
        Hitpoint(self.n)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static, glb)
        self.image = pygame.transform.scale(load_image('bricks.png'), (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(x * 100), int(y * 100)


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(danger, glb)
        self.image = pygame.transform.scale(load_image('spikes.png'), (100, 54))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(x * 100), int(y * 100)
        self.mask = pygame.mask.from_surface(self.image)


class Flash(pygame.sprite.Sprite):
    def __init__(self, x, y, rev):
        global flasht
        super().__init__(flash, glb)
        self.image = pygame.transform.scale(load_image('flash.png'), (192, 45))
        if p.vert == 1:
            self.image = pygame.transform.rotate(self.image, 90)
        elif p.vert == -1:
            self.image = pygame.transform.rotate(self.image, -90)
        if rev:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 20, y - 16

        if p.vert == 1:
            self.rect.y -= 30
        elif p.vert == -1:
            self.rect.y += 10
        if rev:
            if p.vert == 0:
                self.rect.x -= 20
            else:
                self.rect.x += 5

        self.rect[2], self.rect[3] = self.rect[2] + 10, self.rect[3] + 10
        Timer(0.1, self.destroy).start()
        coll = pygame.sprite.groupcollide(flash, enemies, False, False)
        if coll:
            for e in coll[self]:
                e.take_damage(4)
                if p.vert == -1:
                    p.jump()

    def destroy(self):
        self.kill()
        d.dirty = 0


class Dagger(pygame.sprite.Sprite):
    def __init__(self):
        global dd
        dd = pygame.sprite.Group()
        super().__init__(dd)
        self.image = pygame.transform.scale(load_image('dagger.png'), (128, 12))
        self.a = True
        self.damage = 3
        self.dirty = 0
        self.rect = self.image.get_rect()
        self.rect.x = p.rect.x + 18 + 18 * p.view
        self.rect.y = p.rect.y + 46

    def update(self):
        if p.vert:
            if p.vert == 1:
                self.image = pygame.transform.rotate(pygame.transform.scale(load_image('dagger.png'), (128, 12)), 90)
                self.rect.x = p.rect.x + 30
                self.rect.y = p.rect.y - 100
                if p.view == -1:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.rect.x -= 30
            elif p.vert == -1:
                self.image = pygame.transform.rotate(pygame.transform.scale(load_image('dagger.png'), (128, 12)), -90)
                self.rect.x = p.rect.x + 30
                self.rect.y = p.rect.y + 60
                if p.view == -1:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.rect.x -= 30
        else:
            if p.view == 1:
                self.image = pygame.transform.scale(load_image('dagger.png'), (128, 12))
                self.rect.x = p.rect.x + 37
                self.rect.y = p.rect.y + 46
            elif p.view == -1:
                self.image = pygame.transform.scale(pygame.transform.flip(load_image('dagger.png'), True, False), (128, 12))
                self.rect.x = p.rect.x - 116
                self.rect.y = p.rect.y + 46
        if self.dirty:
            dd.draw(screen)

    def attack(self):
        if self.a:
            self.draw()
            pygame.time.set_timer(attacking, 300)
            self.a = False
            if p.view == 1:
                Flash(self.rect.x, self.rect.y, False)
            else:
                Flash(self.rect.x, self.rect.y, True)

    def draw(self):
        self.dirty = 2

    def chtex(self, image):
        self.image = pygame.transform.scale(load_image(image), (128, 12))
        if p.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)


class Hand(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, g):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        if pygame.sprite.spritecollideany(self, g):
            self.a = True
        else:
            self.a = False


class Enemy(Player):
    def __init__(self, x, y, w, h, im):
        self.im = im
        self.image = pygame.transform.scale(load_image(self.im + '.png'), (w, h))
        self.rect = self.image.get_rect()
        super().__init__(x, y, False)
        self.hp = 10
        self.timer = 0
        self.mid = [self.rect.x + self.rect[2] / 2, self.rect.y + self.rect[3] / 2]
        enemies.add(self)

    def take_damage(self, n, fromplayer=True):
        self.hp -= n
        self.chtex(self.im + '-d.png')
        self.timer = 20
        if p.vert != -1:
            self.jump(fromplayer)

    def jump(self, fromplayer=True):
        self.todo[0] = [[(0, -20), self.move] for i in range(14)]
        if fromplayer:
            v = p.view * 2
            self.todo[1] = [[(v, 0), self.move] for i in range(14)]
            self.j = False

    def update(self):
        self.mid = [self.rect.x + self.rect[2] / 2, self.rect.y + self.rect[3] / 2]
        self.fall()
        self.do()
        if self.timer:
            self.timer -= 1
            if self.timer == 0:
                self.chtex(self.im + '.png')
        if self.hp <= 0:
            self.todo[0].insert(1, [(), self.kill])
        if pygame.sprite.spritecollideany(self, danger):
            self.take_damage(d.damage, False)


class Chaser(Enemy):
    def __init__(self, x, y, im='enemy1'):
        super().__init__(x, y, 50, 80, im)

    def update(self):
        super().update()
        if ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[0] - p.mid[0]) ** 2) ** 0.5 <= 1000:
            if p.mid < self.mid:
                h = Hand(self.rect.x - 50, self.rect.y - 100, 50, 280, danger)
                if not h.a:
                    self.move(-4, 0)
            else:
                h = Hand(self.rect.x + self.rect[2], self.rect.y - 100, 50, 280, danger)
                if not h.a:
                    self.move(4, 0)


class Shooter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 70, 'enemy2')
        self.t = Timer(2, self.attack)
        self.t.start()

    def update(self):
        super().update()
        self.v = ch([[1.4, 0], [-1.4, 0], [0, 1.4], [0, -1.4], [1, 1], [1, -1], [-1, 1], [-1, 1]])
        self.move(self.v[0], 0)
        self.move(0, self.v[1])

    def attack(self):
        d = ((self.mid[0] - p.mid[0])**2 + (self.mid[1] - p.mid[1])**2)**0.5
        Fireball(self.mid[0] / 100, self.mid[1] / 100, (p.mid[1] - self.mid[1]) / d, (p.mid[0] - self.mid[0]) / d)
        self.t = Timer(2, self.attack)
        self.t.start()

    def jump(self, fromplayer=True):
        pass

    def fall(self):
        pass

    def kill(self):
        super().kill()
        self.t.cancel()


class Fireball(Enemy):
    def __init__(self, x, y, sina, cosa):
        super().__init__(x, y, 70, 42, 'fireball')
        self.sina, self.cosa = sina, cosa
        a = math.acos(cosa) * 57.3
        if sina < 0:
            a = -a
        self.image = pygame.transform.rotate(self.image, -a)

    def take_damage(self, n):
        pass

    def fall(self):
        pass

    def jump(self):
        pass

    def update(self):
        self.move(self.cosa * 8, 0)
        self.move(0, self.sina * 8)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y


class Jumper(Enemy):
    def __init__(self, x, y, im='enemy3'):
        super().__init__(x, y, 42, 78, im)
        self.t = Timer(2, self.customjump)
        self.t.start()
        self.t2 = Timer(1.7, self.chtex, args=[self.im + '-s.png', 42, 48])
        self.t2.start()

    def update(self):
        super().update()
        if self.st == '':
            self.move(5 * self.view, 0)

    def customjump(self):
        self.chtex(self.im + '.png', 42, 78)
        self.st = ''
        self.todo[0] = [[(0, -35 + i), self.move] for i in range(randint(14, 17))]
        if self.mid[0] - p.mid[0] > 0:
            self.view = -1
        else:
            self.view = 1
        self.t = Timer(2, self.customjump)
        self.t.start()
        self.t2 = Timer(1.7, self.chtex, args=[self.im + '-s.png', 42, 58])
        self.t2.start()

    def move(self, x, y):
        if self.view == 1 and x < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = -1
        if self.view == -1 and x > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.view = 1
        self.rect.x += x
        self.rect.y += y
        obj = pygame.sprite.spritecollideany(self, static)
        if obj:
            if x > 0:
                self.rect.x = obj.rect.x - self.rect[2] - 1
            elif x < 0:
                self.rect.x = obj.rect.x + obj.rect[2] + 1
            elif y > 0:
                self.st = 's'
                self.rect.y = obj.rect.y - self.rect[3] - 1
            elif y < 0:
                self.st = ''
                self.rect.y = obj.rect.y + obj.rect[3] + 1
        else:
            if self.st != 'j':
                self.st = ''


end = False
pygame.init()
pygame.font.init()
font1 = pygame.font.Font('data/Samson.ttf', 100)
font2 = pygame.font.Font('data/Samson.ttf', 50)
running = True
size = w, h
screen = pygame.display.set_mode(size)
ss, stairs, pp, danger, bg, health, buttons, enemies, flash = [pygame.sprite.Group() for i in range(9)]
glb = pygame.sprite.LayeredUpdates()
static = pygame.sprite.Group()
p = Player(0, 0)
d = Dagger()
Platform(2, 3)
Platform(0, 3)
for i in range(10):
    Platform(3 + 1 * i, 3.5)
for i in range(20):
    Platform(i * 1, 7)
Platform(13, 6)
Platform(14, 5)
Jumper(14, 4)
clock = pygame.time.Clock()
attacking = pygame.USEREVENT
flasht = pygame.USEREVENT + 1
protect = pygame.USEREVENT + 2
smth = pygame.USEREVENT + 3
pygame.time.set_timer(smth, 1000)


def main():
    global running, cell
    p.update()
    if pygame.key.get_pressed()[pygame.K_UP]:
        p.vert = 1
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        p.vert = -1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                p.shift()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                if p.j and p.st == 's':
                    p.st = 'j'
                    p.j = False
            if pygame.key.get_pressed()[pygame.K_x]:
                d.attack()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                p.st = ''
                p.jcounter = 0
            if event.key in [pygame.K_UP, pygame.K_DOWN]:
                p.vert = 0

        if event.type == protect:
            pygame.time.set_timer(protect, 0)
            p.chtex('player.png')
            p.protected = False

        if event.type == attacking:
            d.a = True

    if pygame.key.get_pressed()[pygame.K_LEFT]:
        p.move(-8, 0)
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        p.move(8, 0)
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        if p.st == 'j':
            p.jcounter += 1
            if p.jcounter > 24:
                p.jcounter = 0
                p.st = ''
            p.move(0, -20)

    for e in enemies:
        e.update()
    screen.fill((150, 150, 150))
    glb.draw(screen)
    d.update()
    buttons.draw(screen)


while running:
    if not end:
        main()
    else:
        game_over()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()