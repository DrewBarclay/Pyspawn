#!/usr/bin/env python

#This is a simple version of Spawn Lite.
import sys, random, math, os

#Check for screensaver winrar.
if len(sys.argv) > 1:
    if sys.argv[1].upper() != "/S":
        sys.exit()
        
import pygame
from pygame.locals import *
import pygame.gfxdraw

#######################
#Configuration
#######################

size = x, y = (600, 600) #window size in (x, y)
background = (0, 0, 0, 3) #background color in (red, green, blue, alpha) alpha is also known as transparency. Set alpha to higher (all have a max of 255) and the spawn &quot;trails&quot; will fade faster.
spawnradius = 3 #radius of spawns i.e. how large the circles are
numberofspawns = 30
spawnminspeed = 40
spawnmaxspeed = 180  #The speed is randomly selected between these two. Can be any decimal or whole number.
spawnminweight = 1
spawnmaxweight = 10 #How much they are affected by little gravity points. Can be any decimal/whole number.
mousepowermin = 5
mousepowermax = 10 #The power the mouse exerts over the spawns while clicking.
enablecollision = 1 #Whether or not to allow spawns to colllide with each tower. 1 = true, 0 = false. Requires significant CPU.

#######################
#End Configuration
#######################

pygame.init()
pygame.display.set_caption("Spawn")

#Create our window.
screen = pygame.display.set_mode(size)

#Some variables.
clock = pygame.time.Clock()
timeelapsed = clock.tick()
timeelapsedsec = timeelapsed / 1000
blanker = pygame.Surface(size, pygame.SRCALPHA)

#Disable mouse
pygame.mouse.set_visible(0)

class gravitypoint:
    """This class represents a point on the screen where all spawns will be drawn to."""
    def __init__(self):
        self.x = random.randrange(0, x)
        self.y = random.randrange(0, y)
        self.power = random.random() * 5

class spawn:
    """This class controls every aspect of a &quot;spawn&quot;, and all of them at once."""

    spawns = []
    gravity = []

    def optimizeSpeed(self):
        self.cos = math.cos(self.angle)
        self.sin = math.sin(self.angle)
        self.xspeed = self.speed * self.cos
        self.yspeed = self.speed * self.sin
    
    def __init__(self):
        self.angle = random.randrange(0, 6)
        self.speed = random.randrange(spawnminspeed, spawnmaxspeed)
        self.optimizeSpeed()
        self.radius = spawnradius
        self.x = random.randrange(0, x)
        self.y = random.randrange(0, y)
        self.weight = random.random() * spawnmaxweight + spawnminweight
        self.color = pygame.Color(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255), 255)
        self.oldX = x
        self.oldY = y
        
    def moveAllSpawns():
        #This, obviously, moves every spawn.
        for s in spawn.spawns:
            cos = s.cos
            sin = s.sin
            for g in spawn.gravity:
                #Now we modify the spawns angle with every gravity point.
                angle = math.atan2(g.y - s.y, g.x - s.x)
                cos += math.cos(angle) * timeelapsedsec * g.power / s.weight
                sin += math.sin(angle) * timeelapsedsec * g.power / s.weight

            if cos != s.cos or sin != s.sin:
                s.angle = math.atan2(sin, cos)
                s.optimizeSpeed()

            s.oldX = s.x
            s.oldY = s.y
            
            s.x += s.xspeed * timeelapsedsec
            s.y += s.yspeed * timeelapsedsec

            #Check for wall collision
            if s.x > x or s.x < 0:
                s.angle = 3.28 - s.angle
                s.xspeed *= -1
                s.cos *= -1
            if s.y > y or s.y < 0:
                s.angle = 6.28 - s.angle
                s.yspeed *= -1
                s.sin *= -1

            if not enablecollision:
                continue
            
            #Check for other spawn collision.
            for ss in spawn.spawns:
                if s == ss:
                    continue
                if s.x + s.radius > ss.x and s.x - s.radius < ss.x and s.y + s.radius > ss.y and s.y - s.radius < ss.y:
                    #Collision. Compare weights to determine who is reversed.
                    lighter = s
                    if s.weight > ss.weight:
                        lighter = ss
                    lighter.angle += random.random() * 6.28
                    lighter.optimizeSpeed()
                        
    moveAllSpawns = staticmethod(moveAllSpawns)

    def drawSpawns():
        #Draws every spawn.
        for s in spawn.spawns:
            pygame.draw.line(screen, s.color, (int(s.x), int(s.y)), (int(s.oldX), int(s.oldY)), s.radius)
            #pygame.draw.circle(screen, s.color, (int(s.x), int(s.y)), s.radius)
            #pygame.gfxdraw.aacircle(screen, int(s.x), int(s.y), s.radius, s.color)
            #pygame.gfxdraw.aacircle(screen, int(s.x), int(s.y), s.radius - 1, s.color)
    drawSpawns = staticmethod(drawSpawns)
    
#We now create the number of spawns we want
for i in range(0, numberofspawns, 1):
    spawn.spawns.extend([spawn()])

global mg

while 1:
    #Infinite game loop begins. Check for quit events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYUP:
            if event.key == K_ESCAPE:
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mg = gravitypoint()
            mg.x, mg.y = pygame.mouse.get_pos()
            mg.power = random.randrange(mousepowermin, mousepowermax)
            spawn.gravity.extend([mg])
            pygame.mouse.set_visible(1)
        elif event.type == pygame.MOUSEBUTTONUP:
            del spawn.gravity
            spawn.gravity = []
            pygame.mouse.set_visible(0)
        elif event.type == pygame.MOUSEMOTION:
            check = pygame.mouse.get_pressed()
            if check[0]:
                mg.x, mg.y = pygame.mouse.get_pos()

    #Create our random movement.
    rnd = random.randrange(0, 101)
    if rnd > 99:
        check = pygame.mouse.get_pressed()
        if not check[0]: 
            #Cause a gravity event which causes them all to move towards the point.
            rnd = random.randrange(0, 4)
            if rnd:
                spawn.gravity.extend([gravitypoint()])
            else:
                del spawn.gravity
                spawn.gravity = []

    #Overwrite our background. This caues the "trail" of spawns (because we don't blit and background is somewhat transparent)
    blanker.fill(background)
    screen.blit(blanker, (0, 0))
    
    spawn.moveAllSpawns()
    spawn.drawSpawns()

    pygame.display.flip()

    #Limit of 200fps. Anything higher than 50 is stupid, due to the failings of the human eye, but it causes more beautiful stuff.
    timeelapsed = clock.tick(50)
    timeelapsedsec = timeelapsed / 1000
