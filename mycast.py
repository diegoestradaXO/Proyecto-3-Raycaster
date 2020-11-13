import os 
import pygame
from math import pi, cos, sin, atan2

screenSize = 200
halfSize = 100
zoom = 70
initialX = 20
initialY = 20
blockSize = 50
fov = pi/3
rot = 0
black = 0.1
spriteSize = 256
characterSize = 32
characterRes = 102

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 255)

wall1 = pygame.image.load('./sprites/wall1.png')
wall2 = pygame.image.load('./sprites/wall2.png')

textures = {
  "1": wall1,
  "2": wall2
}

hand = pygame.image.load('./sprites/hand.png')

enemies = [
  {
    "x": 100,
    "y": 200,
    "texture": pygame.image.load('./sprites/gem1.png')
  },
  {
    "x": 280,
    "y": 190,
    "texture": pygame.image.load('./sprites/gem2.png')
  },
  {
    "x": 225,
    "y": 340,
    "texture": pygame.image.load('./sprites/gem3.png')
  },
  {
    "x": 220,
    "y": 425,
    "texture": pygame.image.load('./sprites/gem4.png')
  },
  {
    "x": 320,
    "y": 420,
    "texture": pygame.image.load('./sprites/gem5.png')
  }
]

class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = blockSize
    self.player = {
      "x": self.blocksize + 20,
      "y": self.blocksize + 20,
      "a": 0,
      "fov": pi/3
    }
    self.map = []
    self.zbuffer = [-float('inf') for _ in range(0,200)]

    # self.clear()

  def clear(self):
    for x in range(self.width):
      for y in range(self.height):
        r = int((x/self.width)*255) if x/self.width < 1 else 1
        g = int((y/self.height)*255) if y/self.height < 1 else 1
        b = 0
        color = (r, g, b)
        self.point(x, y, color)

  def point(self, x, y, c = None):
    screen.set_at((x, y), c)


  def load_map(self, filename):
    with open(filename) as f:
      for line in f.readlines():
        self.map.append(list(line))

  def cast_ray(self, a):
    d = 0
    while True:
      x = self.player["x"] + d*cos(a)
      y = self.player["y"] + d*sin(a)

      i = int(int(x)/blockSize)
      j = int(int(y)/blockSize)

      if self.map[j][i] != ' ':
        hitx = x - i*blockSize
        hity = y - j*blockSize

        if 1 < hitx < 49:
          maxhit = hitx
        else:
          maxhit = hity

        tx = int(maxhit * spriteSize / blockSize)

        return d, self.map[j][i], tx

      d += 1

  def draw_stake(self, x, h, texture, tx):
    start = int(screenSize/2 - h/2)
    end = int(screenSize/2 + h/2)
    for y in range(start, end):
      ty = int(((y - start)*spriteSize)/(end - start))
      c = texture.get_at((tx, ty))
      self.point(x, y, c)

  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])   # why atan2? https://stackoverflow.com/a/12011762

    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
    sprite_size = (screenSize/sprite_d) * zoom

    sprite_x = (blockSize*(sprite_a - self.player["a"])/self.player["fov"] + blockSize/2 - sprite_size/2)
    sprite_y = screenSize/2 - sprite_size/2

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if 0 < x < screenSize and self.zbuffer[x] >= sprite_d:
          tx = int((x - sprite_x) * spriteSize/sprite_size)
          ty = int((y - sprite_y) * spriteSize/sprite_size)
          c = sprite["texture"].get_at((tx, ty))
          if c != (47, 3, 3, 255) and c != (28, 80, 71, 255) and c != (39, 70, 89, 255) and c != (177, 159, 111, 255) and c != (216, 221, 235, 255):
            self.point(x, y, c)
            self.zbuffer[x - screenSize] = sprite_d

  def draw_player(self, xi, yi, w = characterRes, h = characterRes):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * characterSize/w)
        ty = int((y - yi) * characterSize/h)
        c = hand.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)

  def render(self):
    for i in range(0, screenSize):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/screenSize
      d, c, tx = self.cast_ray(a)
      x = i
      h = screenSize/(d*cos(a-self.player["a"])) * zoom
      self.draw_stake(x, h, textures[c], tx)
      self.zbuffer[i] = d

    for enemy in enemies:
      self.point(enemy["x"], enemy["y"], (0, 0, 0))
      self.draw_sprite(enemy)

    self.draw_player(screenSize - characterRes - 50, screenSize - characterRes)

pygame.init()
screen = pygame.display.set_mode((200, 200), pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN|pygame.HWSURFACE)
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('./map.txt')

c = 0
while True:
  screen.fill((113, 113, 113))
  r.render()

  try:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            exit(0)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_a:
                r.player["a"] -= pi/10
                if r.player["a"] <= -11*pi/10:
                    r.player["a"] = 9*pi/10
                else:
                    pass
            
            elif e.key == pygame.K_d:
                r.player["a"] += pi/10
                if r.player["a"] >= 11*pi/10:
                    r.player["a"] = -9*pi/10
                else:
                    pass

            #Direccion
            elif e.key == pygame.K_RIGHT:
                r.player["y"] += 10*cos(r.player["a"])
                r.player["x"] += -1*10*sin(r.player["a"])
                if r.player["y"] <= 65 or r.player["y"] >= 630 or r.player["x"] <= 65 or r.player["x"] >= 1430:
                    r.player["y"] -= 10*cos(r.player["a"])
                    r.player["x"] -= -1*10*sin(r.player["a"])
                
            elif e.key == pygame.K_LEFT:
                r.player["y"] += -1*10*cos(r.player["a"])
                r.player["x"] += 1*10*sin(r.player["a"])
                if r.player["y"] <= 65 or r.player["y"] >= 630 or r.player["x"] <= 65 or r.player["x"] >= 1430:
                    r.player["y"] -= -1*10*cos(r.player["a"])
                    r.player["x"] -= 1*10*sin(r.player["a"])

            elif e.key == pygame.K_UP:
                r.player["x"] += 10*cos(r.player["a"])
                r.player["y"] += 10*sin(r.player["a"])
                if r.player["y"] <= 65 or r.player["y"] >= 630 or r.player["x"] <= 65 or r.player["x"] >= 1430:
                    r.player["x"] -= 10*cos(r.player["a"])
                    r.player["y"] -= 10*sin(r.player["a"])
            

            elif e.key == pygame.K_DOWN:
                r.player["x"] += -1*10*cos(r.player["a"])
                r.player["y"] += -1*10*sin(r.player["a"])
                if r.player["y"] <= 65 or r.player["y"] >= 630 or r.player["x"] <= 65 or r.player["x"] >= 1430:
                    r.player["x"] -= -1*10*cos(r.player["a"])
                    r.player["y"] -= -1*10*sin(r.player["a"])

            if e.key == pygame.K_f:
                if screen.get_flags() and pygame.FULLSCREEN:
                    pygame.display.set_mode((1000, 500))
                else:
                    pygame.display.set_mode((1000, 500),  pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN)
  except ZeroDivisionError:
        pass

  pygame.display.flip()
