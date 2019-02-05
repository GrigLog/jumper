import pygame
import os
import sys
import ctypes
from threading import Timer
from random import randint, choice as ch
from math import sin, cos
import math

# path = os.environ['_MEIPASS']
path = os.getcwd()



'''w, h = ctypes.windll.user32.GetSystemMetrics(0),\
ctypes.windll.user32.GetSystemMetrics(1)'''
w, h = 1600, 900


def load_image(name, colorkey=None):
    fullname = os.path.join(os.path.join(path, 'images'), name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class LCursor(pygame.sprite.Sprite):
    def __init__(self):
        global cc
        super().__init__(cc)
        self.image = load_image('cursor.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rc = RCursor()

    def replace(self, b):
        self.rect.x = b.rect.x - 60
        self.rect.y = b.rect.y
        self.rc.replace(b)


class RCursor(pygame.sprite.Sprite):
    def __init__(self):
        global cc
        super().__init__(cc)
        self.image = load_image('cursor.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()

    def replace(self, b):
        self.rect.x = b.rect.x + b.rect.w + 10
        self.rect.y = b.rect.y


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text, func, params=None, requirment=True, font=None):
        super().__init__(buttons)
        self.text = text
        if font is None:
            self.font = font2
        if not requirment:
            self.col = (130, 130, 130)
            self.a = False
        else:
            self.col = (255, 255, 255)
            self.a = True
        w, h = self.font.render(self.text, False, self.col).get_size()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 5, y
        # pygame.draw.rect(self.image, (255, 255, 255), pygame.Rect(0, 0, w, h), 5)
        self.func = func
        self.params = params

    def update(self):
        screen.blit(self.font.render(self.text, False, self.col), (self.rect.x, self.rect.y))

    def activate(self):
        if self.params is None:
            self.func()
        elif type(self.params) == list:
            self.func(*self.params)
        else:
            self.func(self.params)


class Game_BackGround(pygame.sprite.Sprite):
    def __init__(self):
        global bg
        super().__init__(bg)
        self.image = pygame.transform.scale(load_image('columns.png'), (w, h))
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, main=True):
        super().__init__()
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
        global pp, p, d
        self.image = pygame.transform.scale(load_image('player.png'), (50, 80))
        self.rect = self.image.get_rect()
        self.view = 1
        self.vert = 0
        self.shifting = False
        self.hp = Health(4)
        self.protected = False
        p = self
        pp = pygame.sprite.Group()
        pp.add(self)
        d = Dagger()

    def update(self):
        self.mid = [self.rect.x + self.rect[2], self.rect.y + self.rect[3]]
        self.fall()
        self.do()
        if pygame.sprite.spritecollideany(self, danger):
            self.take_damage()
        obj = pygame.sprite.spritecollideany(self, enemies)
        if obj:
            if pygame.sprite.collide_mask(self, obj):
                self.take_damage()

    def do(self):
        if self.todo != [[], []]:
            for i in range(len(self.todo)):
                if self.todo[i]:
                    if type(self.todo[i][0][0]) in [list, tuple]:
                        self.todo[i][0][1](*self.todo[i][0][0])
                    else:
                        self.todo[i][0][1](self.todo[i][0][0])
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
            if self.st not in ['j', 'sh']:
                self.st = ''
            self.j = False

    def jump(self):
        self.todo[0] = [[(0, -18), self.move] for i in range(15)]
        self.j = False

    def shift(self):
        if self.sh:
            self.sh = False
            if self.vert != 1:
                self.todo[0] = [[(50 * self.view, 0), self.move] for i in range(4)]
            else:
                self.todo[0] = [[(0, -60), self.move] for i in range(4)]

    def take_damage(self, n=1):
        if not self.protected:
            self.st = ''
            pygame.time.set_timer(protect, 2000)
            self.chtex('player2.png')
            self.hp.remove(n)
            self.protected = True
        self.jump()
        self.sh = True

    def chtex(self, image, w=False, h=False):
        if not w:
            w, h = self.rect[2], self.rect[3]
        self.image = pygame.transform.scale(load_image(image), (w, h))
        if self.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.y += self.rect.h - h
        self.rect.w, self.rect.h = w, h


    def fall(self):
        if self.st != 's':
            if self.todo[0]:
                if self.todo[0][0][0][0] == 0:  # If shifting horisontally
                    self.move(0, 10)
            else:
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
        for i in range(c):
            self.n -= 1
            health.sprites()[-1].kill()
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
        self.rect.x, self.rect.y = int(x * 100), int(y * 100) + 50
        self.mask = pygame.mask.from_surface(self.image)


class Flash(pygame.sprite.Sprite):
    def __init__(self, x, y, rev):
        global flash
        super().__init__(flash)
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
        d.dirty = 0
        self.kill()


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
            pygame.time.set_timer(attacking, 200)
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
        self.mask = pygame.mask.from_surface(self.image)
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

    def fall(self):
        if self.st != 's':
            self.move(0, 10)


class Chaser(Enemy):
    def __init__(self, x, y, im='enemy1'):
        super().__init__(x, y, 50, 80, im)

    def update(self):
        super().update()
        if self.st != '':
            if ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[0] - p.mid[0]) ** 2) ** 0.5 <= 1000:
                if p.mid < self.mid:
                    h = Hand(self.rect.x - 50, self.rect.y - 100, 50, 280, danger)
                    if not h.a:
                        self.move(-4, 0)
                else:
                    h = Hand(self.rect.x + self.rect[2], self.rect.y - 100, 50, 280, danger)
                    if not h.a:
                        self.move(4, 0)

    def jump(self, fromplayer=True):
        self.todo[0] = [[(0, -20), self.move] for i in range(14)]
        if fromplayer:
            v = p.view * 6
            self.todo[1] = [[(v, 0), self.move] for i in range(14)]
            self.j = False


class Shooter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 70, 'enemy2')
        self.hp = 5
        self.t = Timer(1, self.attack)
        self.t.start()

    def update(self):
        super().update()
        self.v = ch([[1.4, 0], [-1.4, 0], [0, 1.4], [0, -1.4], [1, 1], [1, -1], [-1, 1], [-1, 1]])
        self.move(self.v[0], 0)
        self.move(0, self.v[1])

    def attack(self):
        d = ((self.mid[0] - p.mid[0])**2 + (self.mid[1] - p.mid[1])**2)**0.5
        sina = (p.mid[1] - self.mid[1]) / d
        cosa = (p.mid[0] - self.mid[0]) / d
        a = math.acos(cosa) * 57.3
        if sina < 0:
            a = -a
        Fireball(self.mid[0] / 100 - 0.35, self.mid[1] / 100 - 0.2, a)
        self.t = Timer(3, self.attack)
        self.t.start()

    def jump(self, fromplayer=True):
        pass

    def fall(self):
        pass

    def kill(self):
        self.t.cancel()
        super().kill()


class Fireball(Enemy):
    def __init__(self, x, y, a):
        super().__init__(x, y, 70, 42, 'fireball')
        self.sina, self.cosa = sin(a / 57.3), cos(a / 57.3)
        self.image = pygame.transform.rotate(self.image, -a)
        self.x, self.y = self.rect.x, self.rect.y

    def take_damage(self, n):
        pass

    def fall(self):
        pass

    def jump(self):
        pass

    def update(self):
        try:
            self.move(self.cosa * 6, 0)
            self.move(0, self.sina * 6)
        except Exception:
            pass
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def move(self, x, y):
        self.x += x
        self.y += y
        self.rect.x, self.rect.y = int(self.x), int(self.y)


class Jumper(Enemy):
    def __init__(self, x, y, im='enemy3'):
        super().__init__(x, y, 42, 78, im)
        self.t = Timer(3, self.customjump)
        self.t.start()

    def update(self):
        super().update()
        if self.st == '':
            self.move(5 * self.view, 0)

    def customjump(self):
        self.chtex(self.im + '.png', 42, 78)
        self.st = ''
        self.todo[0] = [[(0, -30 + i), self.move] for i in range(randint(16, 19))]
        if self.mid[0] - p.mid[0] > 0:
            self.view = -1
        else:
            self.view = 1
        self.t = Timer(2, self.customjump)
        self.t.start()

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

    def kill(self):
        self.t.cancel()
        super().kill()


class FShifter(Enemy):
    def __init__(self, x, y, im='fshifter'):
        super().__init__(x, y, 102, 36, im)
        self.image_copy = self.image.copy()
        self.a = False
        self.ready = False
        self.x, self.y = x * 100, y * 100
        self.t = Timer(3, self.setready)
        self.t.start()

    def setready(self):
        self.ready = True

    def take_damage(self, n, fromplayer=True):
        if not self.a:
            super().take_damage(n, fromplayer)

    def update(self):
        super().update()
        if self.ready and ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[1] - p.mid[1]) ** 2) ** 0.5 <= 400:
            self.ready = False
            self.attack()
        if not self.a:
            d = ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[1] - p.mid[1]) ** 2) ** 0.5
            sina = (p.mid[1] - self.mid[1]) / d
            cosa = (p.mid[0] - self.mid[0]) / d
            a = math.acos(cosa) * 57.3
            if sina < 0:
                a = -a
            self.image = pygame.transform.rotate(self.image_copy, -a)
            self.move(cos(a / 57.3) * 3, 0)  # rad needed
            self.move(0, sin(a / 57.3) * 3)
        else:
            self.move(cos(self.an) * 14, 0)
            self.move(0, sin(self.an) * 14)

    def attack(self):
        self.a = True
        d = ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[1] - p.mid[1]) ** 2) ** 0.5
        sina = (p.mid[1] - self.mid[1]) / d
        cosa = (p.mid[0] - self.mid[0]) / d
        self.an = math.acos(cosa)  # radians
        if sina < 0:
            self.an = -self.an
        self.image = pygame.transform.rotate(pygame.transform.scale(load_image(self.im + '-s.png'), (153, 48)), -self.an * 57.3)
        self.t.cancel()
        self.t = Timer(0.5, self.stop)
        self.t.start()

    def take_damage(self, n, fromplayer=True):
        if not self.a and fromplayer:
            self.jump()
            self.hp -= n
            self.chtex(self.im + '-d.png')
            self.timer = 20

    def jump(self, fromplayer=True):
        if fromplayer:
            d = ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[1] - p.mid[1]) ** 2) ** 0.5
            sina = - (p.mid[1] - self.mid[1]) / d
            cosa = - (p.mid[0] - self.mid[0]) / d
            self.todo[0] = [((cosa * 12, 0), self.move), ((0, sina * 12), self.move), ((cosa * 12, 0), self.move), ((0, sina * 12), self.move), ((cosa * 12, 0), self.move), ((0, sina * 12), self.move)]
            self.move(cosa * 4, 0)
            self.move(0, sina * 4)

    def chtex(self, image):
        super().chtex(image)
        self.image_copy = self.image

    def stop(self):
        self.a = False
        self.chtex(self.im + '.png')
        self.t = Timer(3, self.setready)
        self.t.start()

    def move(self, x, y):
        self.x += x
        self.y += y
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        '''super().move(int(self.x - self.rect.x), 0)
        super().move(0, int(self.y - self.rect.y))'''

    def fall(self):
        pass

    def kill(self):
        self.t.cancel()
        super().kill()


def ch_bg():
    global BG
    BG += 1
    BG = BG % 3
    settings[0] = 'BG:' + str(BG)


def setvalue(a, b):
    globals()[a] = b


def change_list(n):
    global btns, c, texts, sel
    if n == 0:
        btns = [Button(w // 2 - 150, h // 5 - 30, 'Select stage', change_list, 1),
                Button(w // 2 - 120, h // 5 * 2 - 30, 'Power-ups', change_list, 3, LVL > 4),
                Button(w // 2 - 100, h // 5 * 3 - 30, 'Settings', change_list, 2),
                Button(w // 2 - 110, h // 5 * 4 - 30, 'Quit game', setvalue, ['running', False])]
        def texts():
            pass

    elif n == 1:
        btns = [Button(w // 5, h // 2 - 30, '1', game_restart, 'data\level1.txt'),
                Button(w // 5 * 2, h // 2 - 30, '2', game_restart, 'data\level2.txt', LVL > 1),
                Button(w // 5 * 3, h // 2 - 30, '3', game_restart, 'data\level3.txt', LVL > 2)]
        def texts():
            pass

    elif n == 2:
        btns = [Button(w // 2 - 110, h // 2 - 30, 'Background', ch_bg),
                Button(w // 2 - 50, h - 200, 'Back', change_list, 0)]
        def texts():
            pass
    sel = 0
    c.replace(btns[0])


def game_over(mode='loose'):
    global running, menumode, c, cc, sel, btns, texts

    if mode == 'loose':
        if not menumode:
            btns = [Button((w - 500) // 2 + 50, (h - 200) // 2 + 100, 'YES!', game_restart, 'data/level'+str(lvl)+'.txt'),
                    Button((w - 500) // 2 + 250, (h - 200) // 2 + 100, 'EXIT', change_list, 0)]
            cc = pygame.sprite.Group()
            c = LCursor()
            sel = 0
            c.replace(btns[sel])
            menumode = True
            for e in glb:
                e.kill()
            for e in enemies:
                e.kill()
            def texts():
                screen.blit(font1.render('GAME OVER.', False, (255, 0, 0)), ((w - 500) // 2, (h - 200) // 2 - 200))
                screen.blit(font1.render('RESTART?', False, (255, 255, 255)), ((w - 500) // 2 + 10, (h - 200) // 2 - 100))

    elif mode == 'win':
        global LVL
        if not menumode:
            btns = [Button(w // 2, (h - 200) // 2 + 100, 'Ok', change_list, 0)]
            if lvl == LVL:
                LVL = lvl + 1
            cc = pygame.sprite.Group()
            c = LCursor()
            sel = 0
            c.replace(btns[sel])
            menumode = True
            for e in glb:
                e.kill()
            for e in enemies:
                e.kill()

            def texts():
                screen.blit(font1.render('CONGRATS!', False, (0, 200, 0)), (w // 2 - 180, (h - 200) // 2 - 200))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key in [pygame.K_DOWN, pygame.K_RIGHT]:
                sel = (sel + 1) % len(btns)
                while not btns[sel].a:
                    sel = (sel + 1) % len(btns)
                c.replace(btns[sel])
            if event.key in [pygame.K_UP, pygame.K_LEFT]:
                sel = (sel - 1) % len(btns)
                while not btns[sel].a:
                    sel = (sel - 1) % len(btns)
                c.replace(btns[sel])
            if event.key == 13:
                btns[sel].activate()
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    if BG == 1:
        screen.blit(pygame.transform.scale(load_image('ricardo.png'), (w, h)), pygame.Rect(0, 0, w, h))
    elif BG == 2:
        screen.blit(pygame.transform.scale(load_image('ricardo2.png'), (w, h)), pygame.Rect(0, 0, w, h))
    texts()
    cc.draw(screen)
    buttons.draw(screen)
    for e in btns:
        e.update()
    pygame.display.flip()


def game_restart(levelname):
    global glb, enemies, bg, waves, lvl
    lvl = int(levelname[10])
    menumode = False
    end = False
    stage = 0
    pp, danger, bg, health, buttons, flash, static, enemies = [pygame.sprite.Group() for i in range(8)]
    globals().update(locals())
    file = open(levelname, 'r')
    waves = []
    arr = []
    for l in file.read().split('\n'):
        if l == '':
            continue
        o, x, y = l.split()
        x, y = int(x), int(y)
        if o == 'p':
            arr.append((Platform, (x, y)))
        elif o == 's':
            arr.append((Spike, (x, y)))
        elif o == 'pl':
            arr.append((Player, (x, y)))
        elif o == 'c':
            arr.append((Chaser, (x, y)))
        elif o == 'j':
            arr.append((Jumper, (x, y)))
        elif o == 'sh':
            arr.append((Shooter, (x, y)))
        elif o == 'fs':
            arr.append((FShifter, (x, y)))
        elif o == 'fin':
            arr.append('fin')
        elif o == 'w':
            waves.append(arr)
            arr = []

    Game_BackGround()
    globals().update(locals())
    attacking = pygame.USEREVENT
    flasht = pygame.USEREVENT + 1
    protect = pygame.USEREVENT + 2
    smth = pygame.USEREVENT + 3
    pygame.time.set_timer(smth, 1000)
    globals().update(locals())

settings = open('data\settings.txt', 'r').read()[:-1].split('\n')
for l in settings:
    a, b = l.split(':')
    if b[0] != '"':
        b = float(b)
        if int(b) == b:
            b = int(b)
    else:
        b = b[1:-1]
    globals()[a] = b
pygame.init()
pygame.font.init()
font1 = pygame.font.Font('images/Samson.ttf', 100)
font2 = pygame.font.Font('images/Samson.ttf', 50)
size = w, h
screen = pygame.display.set_mode(size)
screen_rect = pygame.Rect(0, 0, w, h)
pygame.mouse.set_visible(False)
menumode = False
end = True
running = True
lvl = 'data/level1.txt'
buttons, glb, enemies = [pygame.sprite.Group() for i in range(3)]
clock = pygame.time.Clock()
game_over()
change_list(0)


def main():
    global running, stage, end
    if 'p' in globals():
        p.update()
        d.update()
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

        if (event.type == smth or stage == 0) and not enemies.sprites():
            for e in waves[stage]:
                if e != 'fin':
                    e[0](*e[1])
                else:
                    end = True
                    game_over('win')
            stage += 1

        """if event.type == smth:
            e = ch([Shooter])
            if e != Shooter:
                e(randint(0, 16), -1)
            else:
                e(randint(0, 15), randint(0, 3))"""

    if pygame.key.get_pressed()[pygame.K_LEFT]:
        p.move(-8, 0)
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        p.move(8, 0)
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        if p.st == 'j' and not(p.todo[0]):
            p.jcounter += 1
            if p.jcounter > 30:
                p.jcounter = 0
                p.st = ''
            p.move(0, -18)

    for e in enemies:
        e.update()
    bg.draw(screen)
    pp.draw(screen)
    glb.draw(screen)
    try:
        enemies.draw(screen)
    except Exception:
        pass
    flash.draw(screen)
    buttons.draw(screen)
    pygame.display.flip()


while running:
    if not end:
        main()
    else:
        game_over()
    clock.tick(60)
file = open(os.path.join(os.getcwd(), 'data\settings.txt'), 'w')
for e in settings:
    file.write(e.split(':')[0] + ':' + str(globals()[e.split(':')[0]]) + '\n')
file.close()
pygame.quit()
