#!/usr/bin/env python

# Bresenham's line algorithm implementation
# Used to calculate the lines that represent missile travels

class bres:
    def __init__(self, p0, p1):
        self.initial = True
        self.end = False
        self.p0 = p0
        self.p1 = p1
        self.x0 = p0[0]
        self.y0 = p0[1]
        self.x1 = p1[0]
        self.y1 = p1[1]
        self.dx = abs(self.x1-self.x0)
        self.dy = abs(self.y1-self.y0)
        if self.x0 < self.x1:
            self.sx = 1
        else:
            self.sx = -1
        if self.y0 < self.y1:
            self.sy = 1
        else:
            self.sy = -1
        self.err = self.dx-self.dy
    def getNext(self):
        if self.initial:
            self.initial = False
            return [self.x0, self.y0]
        if self.x0 == self.x1 and self.y0 == self.y1:
            self.end = True
            return [self.x1, self.y1]
        self.e2 = 2*self.err
        if self.e2 > -self.dy:
            self.err = self.err - self.dy
            self.x0 = self.x0 + self.sx
        if self.e2 < self.dx:
            self.err = self.err + self.dx
            self.y0 = self.y0 + self.sy
        return [self.x0, self.y0]