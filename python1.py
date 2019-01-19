import pygame
import os
import ctypes


sw, sh = ctypes.windll.user32.GetSystemMetrics(0),\
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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global pp
        super().__init__()
        self.image = pygame.transform.scale(load_image('player.png'), (50, 80))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.protected = False
        self.view = 1
        self.hp = 3
        self.st = ''
        self.j = False
        self.jcounter = 0
        self.todo = [[], []]
        pp = pygame.sprite.Group()
        pp.add(self)

    def draw(self):
        pp.draw(screen)

    def update(self):
        self.do()
        self.fall()
        if pygame.sprite.spritecollideany(self, static):
            self.st = 's'
            self.j = True
        else:
            if self.st != 'j':
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
        d.move(x, y)
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
            if self.view == 1:
                if self.rect.x + self.rect[2] - 5 <= obj.rect.x:
                    d.move(-x, 0)
                    self.rect.x -= x
                else:
                    self.rect.y = obj.rect.y - self.rect[3] + 1
            if self.view == -1:
                if self.rect.x + 5 >= obj.rect.x + obj.rect[3]:
                    d.move(-x, 0)
                    self.rect.x -= x
                else:
                    self.rect.y = obj.rect.y - self.rect[3] + 1

    def jump(self):
        self.todo[0] = [[(0, -30), self.move] for i in range(14)]
        self.j = False

    def shift(self):
        self.todo[0] = [[(100 * self.view, 0), self.move] for i in range(2)]

    def take_damage(self):
        if not self.protected:
            pygame.time.set_timer(protect, 1000)
            self.chtex('player2.png')
            self.todo[1].append([['player.png'], self.chtex])
            self.hp -= 1
            self.protected = True
        self.jump()

    def chtex(self, image):
        self.image = pygame.transform.scale(load_image(image), (50, 80))
        if self.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def fall(self):
        if self.st != 's':
            self.move(0, 10)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static)
        self.image = pygame.transform.scale(load_image('bricks.png'), (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(danger)
        self.image = pygame.transform.scale(load_image('spikes.png'), (102, 54))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)


class Flash(pygame.sprite.Sprite):
    def __init__(self, x, y):
        global flasht
        super().__init__(static)
        self.image = pygame.transform.scale(load_image('flash.png'), (128, 27))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + 30, y - 8
        pygame.time.set_timer(flasht, 200)
        pygame.event.post(pygame.event.Event(flasht, {'cell': self}))


class Dagger(pygame.sprite.DirtySprite):
    def __init__(self):
        global dd
        dd = pygame.sprite.Group()
        super().__init__(dd)
        self.image = pygame.transform.scale(load_image('dagger.png'), (128, 12))
        self.dirty = 0
        self.rect = self.image.get_rect()
        self.rect.x = p.rect.x + 18 + 18 * p.view
        self.rect.y = p.rect.y + 46

    def update(self):
        if p.view == 1:
            self.image = pygame.transform.scale(load_image('dagger.png'), (128, 12))
            self.rect.x = p.rect.x + 37
            self.rect.y = p.rect.y + 46
        elif p.view == -1:
            self.image = pygame.transform.scale(pygame.transform.flip(load_image('dagger.png'), True, False), (128, 12))
            self.rect.x = p.rect.x - 116
            self.rect.y = p.rect.y + 46
        if self.dirty:
            self.attack()
            dd.draw(screen)
            self.dirty = 0

    def attack(self):
        Flash(self.rect.x, self.rect.y)

    def chtex(self, image):
        self.image = pygame.transform.scale(load_image(image), (128, 12))
        if p.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y


pygame.init()
pygame.font.init()
running = True
size = w, h = 1200, 600
screen = pygame.display.set_mode(size)
ss, stairs, pp, danger = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
static = pygame.sprite.Group()
p = Player(0, 0)
d = Dagger()
Platform(200, 300)
Platform(0, 300)
for i in range(10):
    Spike(300 + 100 * i, 350)
    Platform(300 + 100 * i, 400)
clock = pygame.time.Clock()
flasht = pygame.USEREVENT + 1
protect = pygame.USEREVENT + 2


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                p.shift()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                if p.j and p.st == 's':
                    p.st = 'j'
                    p.j = False
            if pygame.key.get_pressed()[pygame.K_x]:
                d.dirty = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                p.st = ''
                p.jcounter = 0
        if event.type == protect:
            p.protected = False
        if event.type == flasht:
            if 'cell' in event.__dict__:
                cell = event.cell
            else:
                cell.kill()
                pygame.time.set_timer(flasht, 0)
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        p.move(-8, 0)
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        p.move(8, 0)
    if pygame.key.get_pressed()[pygame.K_UP]:
        p.view = 2
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        if p.st == 'j':
            p.jcounter += 1
            if p.jcounter > 24:
                p.jcounter = 0
                p.st = ''
            p.move(0, -23)
    screen.fill((150, 150, 150))
    p.update()
    d.update()
    danger.draw(screen)
    static.draw(screen)
    clock.tick(60)
    pygame.display.flip()
