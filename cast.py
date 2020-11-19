import os 
import pygame
from math import pi, cos, sin, atan2

#Most used values
screenSize = 300
zoom = 70
initialX = 20
initialY = 20
blockSize = 50
fov = pi/3
a = 0
spriteSize = 256
characterSize = 32
characterRes = 102

#for fps display
CLOCK    = pygame.time.Clock()

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

wall1 = pygame.image.load('./sprites/wall1.png')
wall2 = pygame.image.load('./sprites/wall2.png')
wall3 = pygame.image.load('./sprites/wall3.png')
wall4 = pygame.image.load('./sprites/wall4.png')
wall5 = pygame.image.load('./sprites/wall5.png')

textures = {
  "1": wall1,
  "2": wall2,
  "3": wall3,
  "4": wall4,
  "5": wall5,
}

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

hand = pygame.image.load('./sprites/pickaxe.png')
hand1 = pygame.image.load('./sprites/hand.png')
hand2 = pygame.image.load('./sprites/sword.png')
  
class Raycaster(object):
  def __init__(self, screen):
    _, _, self.width, self.height = screen.get_rect()
    self.screen = screen
    self.blocksize = blockSize
    self.player = {
      "x": self.blocksize + initialX,
      "y": self.blocksize + initialY,
      "a": a,
      "fov": fov
    }
    self.map = []
    self.zbuffer = [-float('inf') for _ in range(0,screenSize)]


  def clear(self):
    self.screen.fill((47,111,135))


  def point(self, x, y, c = None):
    screen.set_at((x, y), c)

  #function for minimap rendering, uses the wall texture
  def draw_rectangle(self, x, y, texture):
    for cx in range(x, x + 10):
      for cy in range(y, y + 10):
        tx = int((cx - x)*600 / 50)
        ty = int((cy - y)*600 / 50)
        c = texture.get_at((tx, ty))
        self.point(cx, cy, c)

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

        tx = int(maxhit * spriteSize/blockSize)
        return d, self.map[j][i], tx

      #self.point(int(x), int(y), (255, 255, 255))

      d += 1


  def draw_stake(self, x, h, texture, tx):
    start = int(screenSize/2 - h/2)
    end = int(screenSize/2 + h/2)
    for y in range(start, end):
      ty = int((y - start) * spriteSize/(end - start))
      c = texture.get_at((tx,ty))
      self.point(x, y, c)


  def draw_sprite(self, sprite):
    sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])
    sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**(1/2)
    sprite_size = (screenSize/sprite_d) * zoom
    sprite_x = (screenSize*(sprite_a - self.player["a"])/self.player["fov"] + screenSize/2 - sprite_size/2)
    sprite_y = (screenSize/2 - sprite_size/2)

    sprite_x = int(sprite_x)
    sprite_y = int(sprite_y)
    sprite_size = int(sprite_size)

    
    for x in range(sprite_x, sprite_x + sprite_size):
      for y in range(sprite_y, sprite_y + sprite_size):
        if 0 < x < screenSize and self.zbuffer[x] >= sprite_d:
          tx = int((x - sprite_x) * spriteSize/sprite_size)
          ty = int((y - sprite_y) * spriteSize/sprite_size)
          c = sprite["texture"].get_at((tx, ty))

          if   c != (152, 0, 136, 255):
            self.point(x, y, c)
            self.zbuffer[x] = sprite_d

  def draw_player(self, xi, yi, w = characterRes, h = characterRes):
    for x in range(xi, xi + w):
      for y in range(yi, yi + h):
        tx = int((x - xi) * characterSize/w)
        ty = int((y - yi) * characterSize/h)
        c = hand.get_at((tx, ty))
        if c != (152, 0, 136, 255):
          self.point(x, y, c)


  def render(self):
    #Minimap rendering
    for x in range(0, 100, 10):
      for y in range(0, 100, 10):
        i = int(x / 10)
        j = int(y / 10)
        if self.map[j][i] != ' ':
          y = 200 + y
          z = 300 + x
          self.draw_rectangle(z, y, textures[self.map[j][i]])
    #player inside map
    self.point(int(self.player["x"] * 0.21) + 300, int(self.player["y"] * 0.21) + 200, WHITE)

    #game
    for i in range(0, screenSize):
      a =  self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/screenSize
      d, c, tx = self.cast_ray(a)
      x = i
      h = screenSize/(d*cos(a-self.player["a"])) * zoom
      self.draw_stake(x, h, textures[c], tx)

      self.zbuffer[i] = d

    #enemy rendering
    for enemy in enemies:
      self.point(enemy["x"], enemy["y"], (0, 0, 0))
      self.draw_sprite(enemy)

    #hand rendering
    self.draw_player(screenSize - characterRes - 50, screenSize - characterRes)

def show_fps(clock,screen):
    string = "FPS: " + str(int(clock.get_fps()))
    font = pygame.font.SysFont('Arial', 10, True)
    fps = font.render(string,0,(255,255,255))
    screen.blit(fps, (150,5))

def game(r):
  spriteControl = 0
  gameOver = True
  while gameOver:
    r.clear()
    d = 7
    try:

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                gameOver = False

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

                elif e.key == pygame.K_LEFT:
                    r.player["a"] -= pi/20
                elif e.key == pygame.K_RIGHT:
                    r.player["a"] += pi/20

                elif e.key == pygame.K_UP:
                    r.player["x"] += int(d * cos(r.player["a"]))
                    r.player["y"] += int(d * sin(r.player["a"]))
                elif e.key == pygame.K_DOWN:
                    r.player["x"] -= int(d * cos(r.player["a"]))
                    r.player["y"] -= int(d * sin(r.player["a"]))
                
                elif e.key == pygame.K_x:
                  hitSound.play()

                elif e.key == pygame.K_c:
                  spriteControl = (spriteControl+1) % 3
                  if spriteControl == 1:
                    hand = hand1
                  elif spriteControl == 2:
                    hand = hand2

                
                if e.key == pygame.K_f:
                    if screen.get_flags() and pygame.FULLSCREEN:
                        pygame.display.set_mode((screenSize, screenSize))
                    else:
                        pygame.display.set_mode((screenSize, screenSize),  pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN|pygame.HWSURFACE)

        if(200<r.player["x"]<300 and 375<r.player["y"]<500):
            portal.play()
            break
      
        r.render()    
        show_fps(CLOCK,screen)       
        pygame.display.flip()
        CLOCK.tick(60) 
        
    except ZeroDivisionError:
        pass

pygame.init()
pygame.mixer.init()

hitSound = pygame.mixer.Sound('./music/hit.mp3')
portal = pygame.mixer.Sound('./music/portal.mp3')
pygame.mixer.music.load("./music/sweden.mp3") 
pygame.mixer.music.play(-1,0.0)
pygame.mixer.music.set_volume(0.3)

#============ introduction ================
screen = pygame.display.set_mode((600,600))
intro = pygame.image.load("./sprites/intro.png").convert()
screen.blit(intro,(0,0))
pygame.display.flip()

introFlag = True
while (introFlag):
  for event in pygame.event.get():
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        introFlag = False
        pygame.display.quit()

#============= game =======================
screen = pygame.display.set_mode((screenSize, screenSize),pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HWACCEL)
screen.set_alpha(None)
r = Raycaster(screen)
r.load_map('./map.txt')
game(r)

#============ end ================
screen = pygame.display.set_mode((600,600))
end = pygame.image.load("./sprites/exit.png").convert()
screen.blit(end,(0,0))
pygame.display.flip()

endFlag = True
while (endFlag):
  for event in pygame.event.get():
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        endFlag = False
        pygame.display.quit()



