#!/usr/bin/env python

# IMPORTS
import pygame, sys, time, random, bres
from pygame.locals import *

# PREDEFINED COLOUR PALETTE 
black = (0, 0, 0)
grey = (200, 200, 200)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (55, 55, 255)
orange = (255, 140, 0)

# OBJECT SIZE GLOBALS
cWidth, cHeight = 0, 0 # City sizing ***set in main()***
bWidth, bHeight = 0, 0 # Missile battery sizing ***set in main()***
expRadius = 64 # Maximum explosion radius

# GAME GLOBALS
rX, rH = 0, 0 # Game resolution ***set in main()***
eventDelay = 16 # Number of milliseconds of delay before generating a USEREVENT
rateofAttack = 128 # Value for comparing against PRNG to decide when to launch a missile
attackNumber = 32 # Amount of attacks for the turn
maxAmmo = 32 # Amount of missiles the battery can hold
expRate = 4 # Speed in which explosions expand and contract ***must be even***

# OBJECTS + THEIR CONTAINERS
battery = None
cities = []
missiles = []
explosions = []

# CITY OBJECT
class city:
    def __init__(self, pos):
        # City constructor
        # Parametres: (pos) set position
        self._pos = pos
        self._top = [pos[0] + cWidth / 2, pos[1]] # Ref pos for other objects to use
        self.draw() # Draw on creation
    def draw(self):
        # Draws the city
        pygame.draw.rect(screen, grey, (self._pos[0], self._pos[1], cWidth, cHeight), 0)
    def update(self):
        # Polls for updates: NOT PRESENTLY NEEDED
        pass
    def check(self, e):
        # Checks if the city has been hit by given explosion 
        # Parametres: (e) explosion to test bounds of
        if (sqr(e._radius) > sqr(e._pos[0] - self._top[0]) + sqr(e._pos[1] - self._top[1])):
            cities.remove(self)

# MISSILE BATTERY OBJECT
class battery:
    def __init__(self, pos):
        # Missile battery constructor
        # Parametres: (pos) set position
        self._ammo = maxAmmo
        self._pos = pos
        self._aperture = [pos[0] + bWidth / 2, pos[1]] # Ref pos for other objects to use
        self.draw() #draw object on creation
    def draw(self):
        # Draws the missile battery
        pygame.draw.rect(screen, blue, (self._pos[0], self._pos[1], bWidth, bHeight), 0)
    def update(self):
        # Polls for updates: request ammo count draw update
        self.draw()
        # Render latest ammo value
        drawText(str(self._ammo), (self._pos[0] + (bWidth / 3), self._pos[1] + (bHeight / 3)), 'Monospace', white) 
    def fire(self, pos):
        # Fires if ammo value allows
        if (self._ammo > 0):
            self._ammo -= 1
            createMissile(self._aperture, pos)
    def check(self, e):
        # Checks if the missile battery has been hit by given explosion 
        # Parametres: (e) explosion to test bounds of
        if (sqr(e._radius) > sqr(e._pos[0] - self._aperture[0]) + sqr(e._pos[1] - self._aperture[1])):
            remove(self)

# MISSILE OBJECT
class missile:
    def __init__(self, start, end):
        # Missile constructor
        # Parametres: (start) start position, (end) end position
        self._startPos = start
        self._endPos = end
        self._pos = start
        self._line = bres.bres(start, end) # Use Bres' algorithm to initialise line calculating function
        self._completed = False
    def update(self):
        # Polls for updates: checks whether missile needs to draw or erase it's trail
        if (not self._completed):
            # Is missile has not reached destination, poll for line drawing
            if ((int(self._pos[0]) != int(self._endPos[0])) or (int(self._pos[1]) != int(self._endPos[1]))):
                # Draws line sequentially if missile is still in transit
                self._pos = self._line.getNext()
                pygame.draw.line(screen, white, self._pos, self._pos, 1)
            else:
                self._completed = True
        else:
            # Quickly erase line with a black one if missile has been detonated
            self._eraseLine = bres.bres(self._startPos, self._endPos)
            self._pos = self._startPos
            while (int(self._pos[0]) != int(self._endPos[0])) or (int(self._pos[1]) != int(self._endPos[1])):
                # Iterate while erasing line is not completed
                self._pos = self._eraseLine.getNext()
                pygame.draw.line(screen, black, self._pos, self._pos, 1)
            createExplosion(self._pos)
            missiles.remove(self)
    def check(self, e):
        # Checks if the missile has been hit by given explosion 
        # Parametres: (e) explosion to test bounds of
        if (sqr(e._radius) > sqr(e._pos[0] - self._pos[0]) + sqr(e._pos[1] - self._pos[1])):
            self._completed = True
            self._endPos = self._pos

# EXPLOSION ENTITY
class explosion:
    def __init__(self, pos):
        # Explosion constructor
        # Parametres: (pos) epicenter for explosion
        self._pos = pos
        self._radius = 0
        self._expandCompleted = False # Flags whether the initial render is completed
        self._explosionCompleted = False # Flags whether the entire explosion is completed
    def update(self):
        # Poll for updates: checks whether explosion needs to expand on contract
        global expRadius, expRate
        if self._expandCompleted:
            pygame.draw.circle(screen, black, [int(self._pos[0]), int(self._pos[1])], expRadius, 0) # Returns area to black when explosion decays
            if self._radius > 0:
                pygame.draw.circle(screen, red, [int(self._pos[0]), int(self._pos[1])], self._radius, 0) # Red outline
                pygame.draw.circle(screen, orange, [int(self._pos[0]), int(self._pos[1])], (self._radius / 5) * 4, 0) # Orange interior
                self._radius -= expRate
            else:
                self._explosionComplete = True
                explosions.remove(self)
        else:
            if self._radius < expRadius:
                pygame.draw.circle(screen, red, [int(self._pos[0]), int(self._pos[1])], self._radius, 0) 
                pygame.draw.circle(screen, orange, [int(self._pos[0]), int(self._pos[1])], (self._radius / 5) * 4, 0)
                self._radius += expRate
            else:
                self._expandCompleted = True

# UTILITY FUNCTIONS
def sqr(x):
    # Simple squaring (^2) function
    # Parametres: (x) no to square
    return x * x 

def drawText(txt, pos, font, col):
    # Attempts to draw text with given params 
    # Parametres: (txt) text contents, (pos) start pos, (font) text font, (col) text colour
    try: # Attempt to draw
        font = pygame.font.SysFont(font, 32)
        text = font.render(txt, False, col)
        screen.blit(text, pos)
    except: # Catch if desired font font is not present
        print "Cannot print text " + txt

# OBJECT CREATION FUNCTIONS
def createCities():
    # Creates 6 cities with relative to resolution positioning
    global cities
    cities += [city([((rX + cWidth) / 10) * 1, rH - cHeight])]
    cities += [city([((rX + cWidth) / 10) * 2, rH - cHeight])]
    cities += [city([((rX + cWidth) / 10) * 3, rH - cHeight])]
    cities += [city([((rX - cWidth) / 10) * 7, rH - cHeight])]
    cities += [city([((rX - cWidth) / 10) * 8, rH - cHeight])]
    cities += [city([((rX - cWidth) / 10) * 9, rH - cHeight])]

def createMissile(start, end):
    # Creates missile on que
    # Parametres: (start) start position, (end) end position
    global missiles
    missiles += [missile(start, end)]
    pygame.time.set_timer(USEREVENT + 1, eventDelay)

def createExplosion(pos):
    # Creates an explosion when called
    # Parametres: (pos) explosion's epicenter
    global explosions
    explosions += [explosion(pos)]
    pygame.time.set_timer(USEREVENT + 1, eventDelay)

# GAME LOOP FUNCTIONS
def update():
    # Update per frame method

    # Poll for updates from game objects
    if (cities != []):
        for c in cities:
            c.update()
    if (battery != None):
        battery.update()
    if missiles != []:
        for m in missiles:
            m.update()
    if (explosions != []):
        for e in explosions:
            e.update()

    # Redraw display
    pygame.display.flip()
    pygame.time.set_timer(USEREVENT + 1, eventDelay)

def waitForEvent():
    # Actual game loop method
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            battery.fire(pygame.mouse.get_pos())
        if event.type == USEREVENT + 1:
            update()
            #createAttack() # Attempt to create an attack each turn

# MAIN
def main():
    global screen, rX, rH, cWidth, cHeight, bWidth, bHeight, battery
    pygame.init()
    random.seed()

    # Access display information to set resolution
    rX, rH = pygame.display.Info().current_w, pygame.display.Info().current_h

    # Set city and missile battery size based on resolution for scaling
    cWidth = cHeight = rX * 0.025
    bWidth = bHeight = rX * 0.05

    # Create game screen object
    screen = pygame.display.set_mode([rX, rH], pygame.FULLSCREEN)

    # Create game objects
    createCities()
    battery = battery([((rX + bWidth) / 10) * 4.5, rH - bHeight])

    # Begin game loop
    update()
    waitForEvent()

main()