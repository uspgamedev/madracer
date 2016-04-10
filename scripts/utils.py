#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
#from game import Game
import game
from collections import namedtuple


#*********************************** UTILITIES *********************************
class Vector:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y)
    
    def squaredLen(self):
        return self.x**2 + self.y**2
    
    def len(self):
        return math.sqrt(self.squaredLen())
    
    def normalize (self):
        l = self.len()
        if l > 0:
            self.x = self.x / l
            self.y = self.y / l
        
    def copy(self):
        return Vector(self.x, self.y)
        
    def perpendicular(self):
        return Vector(self.y, -self.x)
    
    def angle(self):
        return math.atan2(self.y, self.x)
    def angleBetween(self, v):
        return v.angle() - self.angle()
    
    def __mul__(self, s):
        if type(s) == type(0) or type(s) == type(0.0):
            return Vector(self.x*s, self.y*s)
        elif type(s) == type(()) or type(s) == type([]):
            return Vector(self.x*s[0], self.y*s[1])
        else:
            return Vector(self.x * s.x, self.y * s.y)
    def __div__(self, s):
        if type(s) == type(0) or type(s) == type(0.0):
            return Vector(self.x/s, self.y/s)
        elif type(s) == type(()) or type(s) == type([]):
            return Vector(self.x/s[0], self.y/s[1])
        else:
            return Vector(self.x / s.x, self.y / s.y)
                  
    def toSFML(self):
        return sf.Vector2(self.x, self.y)
    def __str__(self):
        return "(%.4fx, %.4fy)" % (self.x, self.y)
    def __repr__(self):
        return self.__str__()
#end class Vector

class Turret:
    def __init__(self, ent, widthSizeFactor=0.6):
        self.ent = ent
        self.wsf = widthSizeFactor
        self.spr = sf.Sprite(game.Game.images.rigturret)
        
    def draw(self, window, dir):
        w = self.ent.size.x*self.wsf
        h = w * self.spr.texture.height / self.spr.texture.width
        xoffset = (self.ent.size.x - w)/2
        yoffset = self.ent.size.y/2 - h/2
        x = self.ent.pos.x + xoffset + w/2
        y = self.ent.pos.y + yoffset + h/2
        angle = 0.0
        if dir != None:
            angle = dir.angle() + math.pi/2
        self.spr.position = (x, y) #sprite position
        self.spr.origin = (self.spr.texture.width/2, self.spr.texture.height/2) #sprite origin
        self.spr.ratio = (w/self.spr.texture.width, h/self.spr.texture.height) #scale factor
        self.spr.rotation = math.degrees(angle) #rotation angle (in degrees?)
        window.draw(self.spr)

def isInArray(value, array):
    return value in array

class GUIText:
    #perhaps implement this inheriting from sf.Text instead of encapsulating it?
    HOR_LEFT = 0
    HOR_RIGHT = 1
    HOR_CENTER = 2
    CENTER = 3
    def __init__(self, txt, pos, align=HOR_LEFT, color=sf.Color.BLACK, size=20):
        self.txt = sf.Text(txt, game.Game.font, character_size=size)
        self.txt.color = color
        if type(pos) == type([]) or type(pos) == type(()):
            self.txt.position = pos
        else:
            self.txt.position = pos.toSFML()
        self.align = align
        self.updateOrigin()
        self.outline_color = None
        self.outline_thickness = 1
        
    def updateOrigin(self):
        bounds = self.txt.local_bounds
        if self.align == GUIText.HOR_LEFT:
            self.txt.origin = (bounds.left, bounds.top)
        elif self.align == GUIText.HOR_RIGHT:
            self.txt.origin = (bounds.left + bounds.width, bounds.top)
        elif self.align == GUIText.HOR_CENTER:
            self.txt.origin = (bounds.left + bounds.width/2, bounds.top)
        elif self.align == GUIText.CENTER:
            self.txt.origin = (bounds.left + bounds.width/2, bounds.top + bounds.height/2)
        
    def text(self):
        return self.txt.string
    def set_text(self, s):
        try:
            self.txt.string = s
        except:
            self.txt.string = "<ERROR>"
            print "ERROR: Cant display string '%s'" % (s)
        self.updateOrigin()
        
    def set_align(self, a):
        self.align = a
        self.updateOrigin()
        
    def position(self):
        return self.txt.position
    def set_position(self, pos):
        self.txt.position = pos if type(pos) == type([]) or type(pos) == type(()) else pos.toSFML()
        self.updateOrigin()
        
    def char_pos(self, index):
        return self.txt.find_character_pos(index)
        
    def draw(self, window):
        color = self.txt.color
        pos = self.txt.position
        if self.outline_color != None:
            self.txt.color = self.outline_color
            for xoff, yoff in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                self.txt.position = (pos.x + xoff*self.outline_thickness, pos.y + yoff*self.outline_thickness)
                self.updateOrigin()
                window.draw(self.txt)
            self.txt.color = color
            self.txt.position = pos
            self.updateOrigin()
        window.draw(self.txt)

def getEntClosestTo(point, validTargets = ['berserker', 'slinger', 'warrig', 'rigturret', 'dummy']):
    target = None
    min_dist = game.Game.track_area.squaredLen()
    for i in xrange(1, len(game.Game.entities)):
        ent = game.Game.entities[i]
        if ent.hp <= 0 or not ent.type in validTargets:
            continue
        dist = ent.center() - point
        if dist.squaredLen() < min_dist: #yay raizes desnecessarias!
            min_dist = dist.squaredLen()
            target = ent
    return target
        
def createPointMark(pos, radius, color):
    circle_res = 16 #in line segments
    mark = sf.VertexArray(sf.PrimitiveType.LINES, 2*(2+circle_res))
    circle_points = []
    angle_step = 2 * pi / circle_res
    angle = 0.0
    for i in xrange(circle_res):
        dir = sf.Vector2(cos(angle), sin(angle))
        p = dir*radius
        circle_points.append(p)
        circle_points.append(p)
        angle += angle_step
    circle_points.append(circle_points.pop(0))
    for i in xrange(circle_res*2):
        mark[i].position = circle_points[i]
        mark[i].color = color
        
    cross = [sf.Vector2(radius, 0), #left
             sf.Vector2(-radius, 0), #right
             sf.Vector2(0, radius), #top
             sf.Vector2(0, -radius)] #bottom
    for i in xrange(4):
        mark[circle_res*2 + i].position = cross[i]
        mark[circle_res*2 + i].color = color
    return mark
    
def getLineEquation(p1, p2):
    A = p2.y - p1.y
    B = p1.x - p2.x
    C = p2.x * p1.y - p1.x * p2.y
    def f(p):
        return A*p.x + B*p.y + C
    return f
    
RaycastEntry = namedtuple("RaycastEntry", "distance entity")
def raycastQuery(point, dir, validTargets = ['berserker', 'slinger', 'warrig', 'rigturret', 'dummy']):
    hits = []
    if dir.x == 0 and dir.y == 0:
        return hits
        
    endPoint = point + dir*game.Game.track_area.len()
    eq = getLineEquation(point, endPoint)
    def onWhichSide(p):
        v = eq(p)
        if v != 0:
            return v / abs(v)
        return 0
    
    for i in xrange(len(game.Game.entities)):
        ent = game.Game.entities[i]
        if ent.hp <= 0 or not ent.type in validTargets:
            continue
        dist = ent.center() - point
        if abs(dir.angleBetween(dist)) > math.pi/2:
            continue
        verts = ent.vertices()
        sides = [onWhichSide(p) for p in verts]
        #print "%s %i has sides: [%i,%i,%i,%i] (sum = %s) verts=%s" % (ent.type, ent.ID, sides[0], sides[1], sides[2], sides[3], sum(sides), verts)
        if abs(sum(sides)) < 4:
            hits.append( RaycastEntry(dist.len(), ent) )
            
    def comp(a,b):
        v = int(a.distance - b.distance)
        if v != 0:
            return v / abs(v)
        return 0
    hits.sort(comp)
            
    return hits
    
def coneQuery(point, dir, angle, validTargets = ['berserker', 'slinger', 'warrig', 'rigturret', 'dummy']):
    hits = []
    if dir.x == 0 and dir.y == 0:
        return hits
    
    for i in xrange(len(game.Game.entities)):
        ent = game.Game.entities[i]
        if ent.hp <= 0 or not ent.type in validTargets:
            continue
        dist = ent.center() - point
        if abs(dir.angleBetween(dist)) > angle:
            continue
        hits.append( RaycastEntry(dist.len(), ent) )
            
    def comp(a,b):
        v = int(a.distance - b.distance)
        if v != 0:
            return v / abs(v)
        return 0
    hits.sort(comp)
            
    return hits
    
################################################################
# Fix for SFML bug
def intersects(self, rectangle):
    # make sure the rectangle is a rectangle (to get its right/bottom border)
    l, t, w, h = rectangle
    rectangle = Rectangle((l, t), (w, h))

    # compute the intersection boundaries
    left = max(self.left, rectangle.left)
    top = max(self.top, rectangle.top)
    right = min(self.right, rectangle.right)
    bottom = min(self.bottom, rectangle.bottom)

    # if the intersection is valid (positive non zero area), then
    # there is an intersection
    if left < right and top < bottom:
        return Rectangle((left, top), (right-left, bottom-top))