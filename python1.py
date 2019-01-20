import pygame
import os
import ctypes
from random import randint, choice


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
        super().__init__()
        self.image = pygame.transform.scale(load_image('player.png'), (50, 80))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(x * 100) + 25, int(y * 100)
        self.view = 1
        self.mid = [self.rect.x + self.rect[2], self.rect.y + self.rect[3]]
        self.st = ''
        self.j = False
        self.sh = True
        self.jcounter = 0
        self.todo = [[], []]
        if main:
            self.player_init()

    def player_init(self):
        global pp
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
        pp.draw(screen)

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
            self.todo[0] = [[(50 * self.view, 0), self.move] for i in range(4)]

    def take_damage(self):
        if not self.protected:
            pygame.time.set_timer(protect, 1000)
            self.chtex('player2.png')
            self.hp.remove(1)
            self.protected = True
        self.sh = True
        self.jump()

    def chtex(self, image):
        self.image = pygame.transform.scale(load_image(image), (50, 80))
        if self.view == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def fall(self):
        if self.st != 's':
            self.move(0, 10)


class Hitpoint(pygame.sprite.Sprite):
    def __init__(self, n):
        super().__init__(health)
        self.image = pygame.transform.scale(load_image('hp.png'), (60, 51))
        self.rect = self.image.get_rect()
        self.rect.x = 70 * n


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
            pygame.time.delay(800)

    def add(self, c=1):
        self.n += c
        Hitpoint(self.n)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static)
        self.image = pygame.transform.scale(load_image('bricks.png'), (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(x * 100), int(y * 100)


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(danger)
        self.image = pygame.transform.scale(load_image('spikes.png'), (100, 54))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(x * 100), int(y * 100)
        self.mask = pygame.mask.from_surface(self.image)


class Flash(pygame.sprite.Sprite):
    def __init__(self, x, y, rev):
        global flasht
        super().__init__(flash)
        self.image = pygame.transform.scale(load_image('flash.png'), (192, 45))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 20, y - 16
        if rev:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect.x -= 20
        pygame.time.set_timer(flasht, 100)
        pygame.event.post(pygame.event.Event(flasht, {'cell': self}))
        coll = pygame.sprite.groupcollide(flash, enemies, False, False)
        if coll:
            for e in coll[self]:
                e.take_damage(5)

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

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y


class Hand(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, g):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        if pygame.sprite.spritecollideany(self, g):
            self.a = True
        else:
            self.a = False


class Enemy(Player):
    def __init__(self, x, y, im='enemy1'):
        super().__init__(x, y, False)
        self.im = im
        self.image = pygame.transform.scale(load_image(im + '.png'), (50, 80))
        self.hp = 10
        self.timer = 0
        self.mid = [self.rect.x + self.rect[2], self.rect.y + self.rect[3]]
        enemies.add(self)

    def take_damage(self, n, fromplayer=True):
        self.hp -= n
        self.chtex(self.im + '-d.png')
        self.timer = 20
        self.jump(fromplayer)

    def jump(self, fromplayer=True):
        self.todo[0] = [[(0, -20), self.move] for i in range(14)]
        if fromplayer:
            v = p.view * 2
            self.todo[1] = [[(v, 0), self.move] for i in range(14)]
            self.j = False

    def update(self):
        self.mid = [self.rect.x + self.rect[2], self.rect.y + self.rect[3]]
        self.fall()
        self.do()
        if self.timer:
            self.timer -= 1
            if self.timer == 0:
                self.chtex(self.im + '.png')
        if self.hp <= 0:
            self.todo[0].insert(1, [(), self.kill])
        if pygame.sprite.spritecollideany(self, danger):
            self.take_damage(3, False)
        if ((self.mid[0] - p.mid[0]) ** 2 + (self.mid[0] - p.mid[0]) ** 2) ** 0.5 <= 600:
            if p.mid < self.mid:
                h = Hand(self.rect.x - 50, self.rect.y - 100, 50, 280, danger)
                if not h.a:
                    self.move(-4, 0)
            else:
                h = Hand(self.rect.x + self.rect[2], self.rect.y - 100, 50, 280, danger)
                if not h.a:
                    self.move(4, 0)


end = False
pygame.init()
pygame.font.init()
font1 = pygame.font.Font('data/Samson.ttf', 100)
font2 = pygame.font.Font('data/Samson.ttf', 50)
running = True
size = w, h
screen = pygame.display.set_mode(size)
ss, stairs, pp, danger, bg, health, buttons, enemies, flash = [pygame.sprite.Group() for i in range(9)]
static = pygame.sprite.Group()
p = Player(0, 0)
d = Dagger()
Platform(2, 3)
Platform(0, 3)
for i in range(10):
    Spike(3 + 1 * i, 3.5)
    Platform(3 + 1 * i, 4)
for i in range(20):
    Platform(i * 1, 7)
Platform(13, 6)
Platform(14, 5)
Enemy(14, 4)
clock = pygame.time.Clock()
attacking = pygame.USEREVENT
flasht = pygame.USEREVENT + 1
protect = pygame.USEREVENT + 2
smth = pygame.USEREVENT + 3
pygame.time.set_timer(smth, 1000)


def main():
    global running, cell
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
                d.attack()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                p.st = ''
                p.jcounter = 0

        if event.type == protect:
            pygame.time.set_timer(protect, 0)
            p.chtex('player.png')
            p.protected = False

        if event.type == flasht:
            if 'cell' in event.__dict__:
                cell = event.cell
            else:
                cell.destroy()
                pygame.time.set_timer(flasht, 0)

        if event.type == attacking:
            d.a = True

        if event.type == smth:
            Enemy(choice([0, 1, 2, 13, 14]), 0)

    if pygame.key.get_pressed()[pygame.K_LEFT]:
        p.move(-8, 0)
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        p.move(8, 0)
    if pygame.key.get_pressed()[pygame.K_UP]:
        p.vert = 1
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        if p.st == 'j':
            p.jcounter += 1
            if p.jcounter > 24:
                p.jcounter = 0
                p.st = ''
            p.move(0, -20)

    screen.fill((150, 150, 150))
    p.update()
    d.update()
    for e in enemies:
        e.update()
    flash.draw(screen)
    enemies.draw(screen)
    health.draw(screen)
    danger.draw(screen)
    static.draw(screen)
    bg.draw(screen)
    buttons.draw(screen)


while running:
    if not end:
        main()
    else:
        game_over()
    pygame.display.flip()
    clock.tick(60)
