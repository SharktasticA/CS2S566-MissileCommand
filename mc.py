#!/usr/bin/env python

#imports--------------------------------------------------------------------------------------------------
import pygame, sys, time, random, bres
from pygame.locals import *

#colour palette-------------------------------------------------------------------------------------------
black = (0, 0, 0)
grey = (128, 128, 128)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
orange = (255, 140, 0)

#game globals---------------------------------------------------------------------------------------------
screenWidth, screenHeight = 0, 0 #game resolution
delay = 15  #number of milliseconds delay before generating a USEREVENT
rateOfAttack = 400 #value for pseudorandom number generator to use
attackNumber = 5 #amount of attacks for the turn

#city variables-------------------------------------------------------------------------------------------
cityWidth, cityHeight = 0, 0 #city sizing

#silo variables-------------------------------------------------------------------------------------------
maxAmmo = 24 #maximum ammo per silo
siloWidth, siloLength = 0, 0 #silo sizing

#explosion variables--------------------------------------------------------------------------------------
maxRadius = 64 #maximum radius of explosions

#object containers----------------------------------------------------------------------------------------
cities = []
silos = []
missiles = []
explosions = []

#city object----------------------------------------------------------------------------------------------
class city:
    def __init__(self, pos):
        #city constructor | parametres: (pos) set position
        self._pos = pos
        self._top = [pos[0] + cityWidth / 2, pos[1]] #target for missiles to hit
        self._exploding = False
        self.draw() #draw object on creation
    def draw(self):
        #drawer: draws the city as a grey rectangle
        pygame.draw.rect(screen, grey, (self._pos[0], self._pos[1], cityWidth, cityHeight), 0)
    def update(self):
        #updater: not presently needed
        pass
    def check(self, e):
        #checker: if city has been hit with an explosion, destroy the city | parametres: (e) currently-processing explosion
        if (not self._exploding) and sqr(e._radius) > sqr(e._pos[0] - self._top[0]) + sqr(e._pos[1] - self._top[1]):
            self._exploding = True
            createExplosion(self._top)
            removeCity(self)

#missile silo object--------------------------------------------------------------------------------------
class silo:
    def __init__(self, pos):
        #silo constructor | parametres: (pos) set position
        self._ammo = maxAmmo
        self._pos = pos
        self._aperture = [pos[0] + siloWidth / 2, pos[1]] #target for missiles and firing position
        self._exploding = False
        self.draw() #draw object on creation
    def draw(self):
        #drawer: draws the silo as a blue rectangle
        pygame.draw.rect(screen, blue, (self._pos[0], self._pos[1], siloWidth, siloLength), 0)
    def update(self):
        #updater: draws missile ammount of silo
        drawText(str(self._ammo + 1), (self._pos[0] + (siloWidth / 4), self._pos[1] + (siloLength / 6)), blue) #erase previous ammo draw
        drawText(str(self._ammo), (self._pos[0] + (siloWidth / 4), self._pos[1] + (siloLength / 6)), white) #draw new ammo 
    def fire(self, pos):
        if (not self._exploding) and self._ammo > 0:
            self._ammo -= 1
            createMissile(self._aperture, pos)
    def check(self, e):
        #checker: if silo has been hit with an explosion, destroy the silo | parametres: (e) currently-processing explosion
        if (not self._exploding) and sqr(e._radius) > sqr(e._pos[0] - self._aperture[0]) + sqr(e._pos[1] - self._aperture[1]):
            self._exploding = True
            createExplosion(self._aperture)
            removeSilo(self)

#missile object-------------------------------------------------------------------------------------------
class missile:
    def __init__(self, start, end):
        #missile constructor | parametres: (start) start position, (end) end position
        self._startPos = start
        self._endPos = end
        self._pos = start
        self._line = bres.bres(start, end) #uses Bres' algorithm to initialise line calculating function
        self._completed = False
    def update(self):
        #updater: checks whether missile needs to draw or erase it's trail
        if not self._line.finished() or self._completed == True:
            #draws line sequentially if missile is still in transit
            self._pos = self._line.getNext()
            pygame.draw.line(screen, white, self._pos, self._pos, 1)
        else:
            #quickly erase line if missile has been detonated
            self._completed = True
            self._eraseLine = bres.bres(self._startPos, self._endPos) #uses Bres' algorithm to initialise erasing line calculating function
            while not self._eraseLine.finished():
                #iterate while erasing line is not completed, draw a black line to hide the current section of the path
                self._pos = self._eraseLine.getNext()
                pygame.draw.line(screen, black, self._pos, self._pos, 1)
            createExplosion(self._pos)
            removeMissile(self)
    def hit(self, p):
        #destroys the missile
        self._completed = True
        self._endPos = p
    def check(self, e):
        #checker: if missile has been hit with an explosion, destroy the missile | parametres: (e) currently-processing explosion
        if (not self._completed) and sqr(e._radius) > sqr(e._pos[0] - self._pos[0]) + sqr(e._pos[1] - self._pos[1]):
            self._completed = True
            self._endPos = self._pos
            self.update()
            createExplosion(self._pos)
            removeMissile(self)

#explosion object-----------------------------------------------------------------------------------------
class explosion:
    def __init__(self, pos):
        #explosion constructor | parametres: (pos) epicenter for explosion
        self._pos = pos
        self._radius = 1
        self._expandCompleted = False #flags whether the initial render is completed
        self._explosionCompleted = False #flags whether the entire explosion is completed
    def update(self):
        #updater: checks whether explosion needs to expand on contract
        global maxRadius
        if self._expandCompleted:
            pygame.draw.circle(screen, black, [int(self._pos[0]), int(self._pos[1])], maxRadius, 0) #returns area to black when explosion decays
            if self._radius > 0:
                pygame.draw.circle(screen, red, [int(self._pos[0]), int(self._pos[1])], self._radius, 0) #red outline
                self._radius -= 1
            else:
                self._explosionComplete = True
                removeExplosion(self)
        else:
            if self._radius != maxRadius:
                pygame.draw.circle(screen, red, [int(self._pos[0]), int(self._pos[1])], self._radius, 0) 
                self._radius += 1
            else:
                self._expandCompleted = True

#global creation functions--------------------------------------------------------------------------------
def createCities():
    #creates cities by calculating their position relative to screen size
    global cities
    cities += [city([((screenWidth - cityWidth) / 6) * 2, screenHeight - cityHeight])]
    cities += [city([((screenWidth - cityWidth) / 6) * 4, screenHeight - cityHeight])]

def createSilos():
    #crates silos by calculating their position relative to screen size
    global silos
    silos += [silo([round(((screenWidth - cityWidth) / 6) - (siloWidth / 2)), screenHeight - (siloLength / 2)])]
    silos += [silo([round((((screenWidth - cityWidth) / 6) * 5) + siloWidth), screenHeight - (siloLength / 2)])]

def createMissile(start, end):
    #creates a missile when called | parametres: (start) start position, (end) end position
    global missiles
    missiles += [missile(start, end)]
    pygame.time.set_timer(USEREVENT + 1, delay)

def createExplosion(pos):
    #creates an explosion when called | parametres: (pos) explosion epicenter
    global explosions
    explosions += [explosion(pos)]
    pygame.time.set_timer(USEREVENT + 1, delay)

def createAttack():
    #creates a randomised attack
    global attackNumber
    if attackNumber > 0:
        if random.randint(1, rateOfAttack) == 1: #check if random number meets the criteria for creating a missile
            attackNumber -= 1
            c = cities[random.randint(0, len(cities) - 1)] #get the target city
            createMissile([random.randint (0, screenWidth - 1), 0], c._top)
        if random.randint(1, rateOfAttack) == 1: #check if random number meets the criteria for creating a missile
            attackNumber -= 1
            s = silos[random.randint(0, len(silos) - 1)] #get the target silo
            createMissile([random.randint (1, screenWidth), 0], s._aperture)

#global remove functions----------------------------------------------------------------------------------
def removeCity(c):
    if c in cities:
        cities.remove(c)

def removeSilo(s):
    if s in silos:
        silos.remove(s)

def removeMissile(m):
    if m in missiles:
        missiles.remove(m)

def removeExplosion(e):
    if e in explosions:
        explosions.remove(e)

#other functions------------------------------------------------------------------------------------------
def sqr(x):
    #simple squaring function (^2) | parametres: (x) number to square
    return x * x

def drawText(string, pos, colour):
    #draws some text | parametres: (string) message to print, (pos) starting position to print at, (colour) colour of text
    try: #attempts to draw
        font = pygame.font.SysFont('Monospace', 32)
        text = font.render(string, False, colour)
        screen.blit(text, pos)
    except: #safely catches the issue if the font needed happens to not be present
        print "Cannot print text " + string

def firing(btn, pos):
    #fires the desired silo | parametres: (btn) button reference, (pos) location of mouse pointer
    if silos != []:
        if btn == 1:
            silos[0].fire(pos)
        elif btn == 3:
            silos[1].fire(pos)

def checkCollisions(obj):
    #sequentially compares a provided object (explosions) | (obj) provided object
    if cities != []:
        for c in cities:
            if c in cities:
                c.check(obj)
    if silos != []:
        for s in silos:
            if s in silos:
                s.check(obj)
    if missiles != []:
        for m in missiles:
            if m in missiles:
                m.check(obj)

#per turn functions---------------------------------------------------------------------------------------
def updateAll():
    #general update per frame function
    if cities != []:
        for c in cities:
            c.update()
    if silos != []:
        for s in silos:
            s.update()
    if missiles != []:
        for m in missiles:
            m.update()
    if explosions != []:
        for e in explosions:
            e.update()
            checkCollisions(e)

    pygame.display.flip()
    pygame.time.set_timer(USEREVENT + 1, delay)

def wait_for_event():
    #general interactively handling function
    global screen, turnCount
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            firing(event.button, pygame.mouse.get_pos())
        if event.type == USEREVENT + 1:
            updateAll()
            createAttack() #attempt to create an attack each turn

#---------------------------------------------------------------------------------------------------------
def main():
    global screen, screenWidth, screenHeight, cityWidth, cityHeight, siloWidth, siloLength
    pygame.init()
    random.seed()

    displayInfo = pygame.display.Info() #allows access to the computer's display properties
    screenWidth, screenHeight = displayInfo.current_w, displayInfo.current_h

    cityWidth = displayInfo.current_w * 0.05 #scale city width
    cityHeight = displayInfo.current_h * 0.075 #scale city height

    siloWidth = displayInfo.current_w * 0.025 #scale silo width
    siloLength = displayInfo.current_h * 0.2 #scale silo height

    screen = pygame.display.set_mode([screenWidth, screenHeight], pygame.FULLSCREEN)
    createCities()
    createSilos()
    updateAll()
    wait_for_event()

main()