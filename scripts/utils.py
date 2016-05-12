#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math, code, traceback, sys
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

class GUIText(sf.Drawable):
    #perhaps implement this inheriting from sf.Text instead of encapsulating it?
    HOR_LEFT = 0
    HOR_RIGHT = 1
    HOR_CENTER = 2
    CENTER = 3
    HOR_LEFT_VER_CENTER = 4
    def __init__(self, txt, pos, align=HOR_LEFT, color=sf.Color.BLACK, size=20):
        sf.Drawable.__init__(self)
        self.txt = sf.Text(txt, game.Game.font, character_size=size)
        self.txt.color = color
        if type(pos) == type([]) or type(pos) == type(()):
            self.txt.position = pos
        else:
            self.txt.position = pos.toSFML()
        self.align = align
        self.updateOrigin()
        self._outline_color = None
        self._outline_thickness = 0
        
        self.outline_shader = None#sf.Shader.from_file(fragment="scripts/outline.frag")
        #self.outline_shader.set_currenttexturetype_parameter("texture")
        #self.outline_shader.set_2float_parameter("stepSize", 0.0, 0.0)
        
    @property
    def outline_color(self):
        return self._outline_color
        
    @outline_color.setter
    def outline_color(self, c):
        self._outline_color = c
        #self.outline_shader.set_color_parameter("outlineColor", c)
        
    @property
    def outline_thickness(self):
        return self._outline_thickness
        
    @outline_thickness.setter
    def outline_thickness(self, size):
        self._outline_thickness = size
        #stepSizeX = self._outline_thickness/self.txt.local_bounds.width if self.txt.local_bounds.width > 0 else 0
        #stepSizeY = self._outline_thickness/self.txt.local_bounds.height if self.txt.local_bounds.height > 0 else 0
        #self.outline_shader.set_2float_parameter("stepSize", stepSizeX, stepSizeY)
        
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
        elif self.align == GUIText.HOR_LEFT_VER_CENTER:
            self.txt.origin = (bounds.left, bounds.top + bounds.height/2)
        
    def text(self):
        return self.txt.string
    def set_text(self, s):
        try:
            self.txt.string = s
        except:
            self.txt.string = "<ERROR>"
            print "ERROR: Cant display string '%s'" % (s)
        self.updateOrigin()
        #stepSizeX = self._outline_thickness/self.txt.local_bounds.width if self.txt.local_bounds.width > 0 else 0
        #stepSizeY = self._outline_thickness/self.txt.local_bounds.height if self.txt.local_bounds.height > 0 else 0
        #self.outline_shader.set_2float_parameter("stepSize", stepSizeX, stepSizeY)
        
    def set_align(self, a):
        self.align = a
        self.updateOrigin()
        
    @property
    def position(self):
        return self.txt.position
    @position.setter
    def position(self, pos):
        self.txt.position = pos if type(pos) == type([]) or type(pos) == type(()) else pos.toSFML()
        self.updateOrigin()
        
    @property
    def bounds(self):
        return self.txt.global_bounds
        
    def char_pos(self, index):
        return self.txt.find_character_pos(index)
        
    def draw(self, target, states):
        color = self.txt.color
        pos = self.txt.position
        if self.outline_color != None:
            self.txt.color = self.outline_color
            for xoff, yoff in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                self.txt.position = (pos.x + xoff*self.outline_thickness, pos.y + yoff*self.outline_thickness)
                self.updateOrigin()
                target.draw(self.txt)
            self.txt.color = color
            self.txt.position = pos
            self.updateOrigin()
        target.draw(self.txt, sf.RenderStates(shader=self.outline_shader))

class PlayerHUD(sf.Drawable):
    RIGHT = 0
    LEFT = 1
    def __init__(self, player, pos, align=RIGHT):
        sf.Drawable.__init__(self)
        self.player = player
        if type(pos) == type(()) or type(pos) == type([]):
            pos = Vector(pos[0], pos[1])
        self._pos = pos
        self.align = align
        self.icons = []
        self.texts = []
        char_size = 18.0
        self.icons.append(sf.Sprite(game.Game.images.ammo))
        self.texts.append(sf.Text("", game.Game.font, character_size=char_size))
        self.icons.append(sf.Sprite(game.Game.images.bomb))
        self.texts.append(sf.Text("", game.Game.font, character_size=char_size))
        self.icons.append(sf.Sprite(game.Game.images.speed))
        self.texts.append(sf.Text("", game.Game.font, character_size=char_size))
        self.icons.append(sf.Sprite(game.Game.images.points))
        self.texts.append(sf.Text("", game.Game.font, character_size=char_size))
        yoff = 0
        for icon, text in zip(self.icons, self.texts):
            text.color = sf.Color.WHITE
            icon.ratio = (char_size*2/icon.texture.width, char_size*2/icon.texture.height)
            if self.align == PlayerHUD.LEFT:
                icon.position = (pos.x, pos.y + yoff)
                text.position = (icon.global_bounds.right + 3, icon.global_bounds.top + char_size/2)
            else:
                icon.position = (pos.x - icon.global_bounds.width, pos.y + yoff)
                text.origin = (text.global_bounds.left + text.global_bounds.width, text.global_bounds.top)
                text.position = (icon.global_bounds.left - 3, icon.global_bounds.top + char_size/2)
            yoff += icon.global_bounds.height + 5

        self.outline = sf.Shader.from_file(fragment="scripts/outline.frag")
        self.outline.set_currenttexturetype_parameter("texture")
        self.outline.set_2float_parameter("stepSize", 3.0/game.Game.images.speed.width, 3.0/game.Game.images.speed.height)
        self.outline.set_color_parameter("outlineColor", player.color)
        
    @property
    def position(self):
        return self._pos
    @position.setter
    def position(self, p):
        for icon, text in zip(self.icons, self.texts):
            icon.position = (p.x, p.y + icon.position.y - self._pos.y)
            text.position = (icon.global_bounds.right + 3, icon.global_bounds.top + char_size/2)
        self._pos = p
        
    def update(self, dt):
        mins, secs = game.Game.getTimeFromSpeedLevel(game.Game.speed_level)
        playerValues = ("%i/%i" % (self.player.shots_available, self.player.max_shots),
                        "%i" % self.player.bombs,
                        "%im%is" % (mins, secs),
                        "%i" % round(self.player.points))
        
        for icon, text, value in zip(self.icons, self.texts, playerValues):
            text.string = value
            #text.origin = (text.global_bounds.left + text.global_bounds.width, text.global_bounds.top)
            text.position = (icon.global_bounds.left - 3 - text.global_bounds.width, text.position.y)
        
    def draw(self, target, states):
        staout = sf.RenderStates(shader=self.outline)
        for icon, text in zip(self.icons, self.texts):
            target.draw(icon, staout)
            target.draw(text)
        
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

def getTextSize(s, char_size, is_bold=False):
    size = 0
    for i, c in enumerate(s):
        code = ord(c)
        size += game.Game.font.get_glyph(code, char_size, is_bold).advance
        if i > 0:
            size += game.Game.font.get_kerning(ord(s[i-1]), code, char_size)
    return size
    
def wrapText2(width, s, char_size, is_bold=False, lineBreakers=[' ', '\t']):
    size = 0
    wrapped = []
    line_start = 0
    last_whitespace_index = 0
    for i, c in enumerate(s):
        code = ord(c)
        if c in lineBreakers:
            last_whitespace_index = i
        size += Game.font.get_glyph(code, char_size, is_bold).advance
        if i > 0:
            size += Game.font.get_kerning(ord(s[i-1]), code, char_size)
        if size > width and last_whitespace_index > 0:
            wrapped.append( s )
            
    return wrapped

def wrapText(width, s, char_size, is_bold=False):
    parts = s.split(" ")
    wrapped = []
    size = 0
    line = []
    for sub_s in parts:
        w = getTextSize(sub_s+" ", char_size, is_bold)
        size += w
        if size > width:
            wrapped.append( " ".join(line) )
            size = w
            line = []
        line.append(sub_s)
    if len(line) > 0:
        wrapped.append( " ".join(line) )
    return wrapped    
 
################################################################
# Console
class Console(object,code.InteractiveConsole):
    def __init__(self, locals={}):
        code.InteractiveConsole.__init__(self, dict(globals().items() + locals.items()), "__console__")
        self.open = False
        self.initialized = False
        self.outputs = []
        self.output_index = 0
        self.log = []
        self.log_index = 0
        self.line = ""
        self._lineindex = 0
        self.stdout = sys.stdout
        
    @property
    def line_index(self):
        return self._lineindex
    @line_index.setter
    def line_index(self, i):
        self._lineindex = i
        if self._lineindex < 0:
            self._lineindex = 0
        if self._lineindex > len(self.line):
            self._lineindex = len(self.line)
        size = getTextSize(self.line[:self._lineindex], self.input.txt.character_size, game.Game.font)
        self.cursor.position = self.input.position.x + size - 2, self.input.position.y
       
    def initGraphics(self, rect):
        if self.initialized:    return
        self.initialized = True
        self.output_area = sf.RectangleShape(rect.size)
        self.output_area.position = rect.position
        self.output_area.fill_color = sf.Color(0,0,0,180)
        self.output_area.outline_thickness = 3
        self.output_area.outline_color = sf.Color.GREEN
        self.input_area = sf.RectangleShape((rect.width, 33))
        self.input_area.position = rect.left, self.output_area.global_bounds.bottom
        self.input_area.fill_color = sf.Color(0,0,0,180)
        self.input_area.outline_thickness = 3
        self.input_area.outline_color = sf.Color.BLUE
        self.input = GUIText("", (self.input_area.position.x+5, self.input_area.position.y+8), GUIText.HOR_LEFT, sf.Color.WHITE, 20)
        self.cursor = sf.RectangleShape((2, 20))
        self.cursor.fill_color = sf.Color.WHITE
        self.cursor.position = self.input.position
        self.scrollbar = sf.RectangleShape((5, self.output_area.size.y))
        self.scrollbar.fill_color = sf.Color.RED
        self.scrollbar.position = rect.right-self.scrollbar.size.x, rect.top
        self.output_char_size = 12  
        self.num_outputs = int( (self.output_area.local_bounds.height - 16) / self.output_char_size )
        
    def processInput(self, e):
        if type(e) == sf.TextEvent and self.open:
            # So ENTER(13)/BACKSPACE(8)/TAB(9) aparentemente podem vir aqui.
            if e.unicode == ord('\r') or e.unicode == ord('\n'): #ENTER \n ou \r
                if len(self.line) > 0:
                    self.log.insert(0, self.line)
                    try:
                        self.addOutput("$ "+self.line, sf.Color(180,180,255,255))
                        incomplete = self.push(self.line)
                    except:
                        traceback.print_exc(file=sys.stderr)
                    self.line = ""
                    self.line_index = 0
                    self.log_index = 0
            elif e.unicode == ord('\b'): #BACKSPACE   \b
                if len(self.line) > 0:
                    self.line = self.line[:self.line_index-1] + self.line[self.line_index:]
                    self.line_index -= 1
            else:
                try:
                    c = str(chr(e.unicode))
                    c = c.encode("ascii", "ignore")
                    self.line = self.line[:self.line_index] + c + self.line[self.line_index:]
                    self.line_index += 1
                except:
                    traceback.print_exc(file=sys.stderr)
        elif type(e) == sf.KeyEvent:
            if e.code == sf.Keyboard.TAB and e.control and e.released:
                self.open = not self.open
            elif self.open and e.released:
                if e.code == sf.Keyboard.LEFT:
                    self.line_index -= 1
                elif e.code == sf.Keyboard.RIGHT:
                    self.line_index += 1
                elif e.code == sf.Keyboard.UP:
                    self.log_index += 1
                    li = self.log_index - 1
                    if 0 <= li < len(self.log):
                        self.line = self.log[li]
                        self.line_index = len(self.line)
                    elif li >= len(self.log):
                        self.log_index = len(self.log)
                        if len(self.log) > 0:
                            self.line = self.log[self.log_index-1]
                            self.line_index = len(self.line)
                elif e.code == sf.Keyboard.DOWN:
                    self.log_index -= 1
                    li = self.log_index - 1
                    if 0 <= li < len(self.log):
                        self.line = self.log[li]
                        self.line_index = len(self.line)
                    elif li < 0:
                        self.log_index = 0
                        self.line = ""
                        self.line_index = 0
                elif e.code == sf.Keyboard.DELETE:
                    if len(self.line) > 0:
                        self.line = self.line[:self.line_index] + self.line[self.line_index+1:]
                elif e.code == sf.Keyboard.HOME:
                    self.line_index = 0
                elif e.code == sf.Keyboard.END:
                    self.line_index = len(self.line)
            elif self.open and e.code == sf.Keyboard.PAGE_UP:
                self.output_index -= 1
                if self.output_index < 0:
                    self.output_index = 0
            elif self.open and e.code == sf.Keyboard.PAGE_DOWN:
                self.output_index += 1
                if self.output_index > len(self.outputs) - self.num_outputs:
                    self.output_index -= 1
        elif type(e) == sf.MouseWheelEvent:
            self.output_index -= e.delta
            if self.output_index > len(self.outputs) - self.num_outputs:
                self.output_index = len(self.outputs) - self.num_outputs
            if self.output_index < 0:
                self.output_index = 0
                
    def push(self, line):
        ### OVERWRITING InteractiveConsole.push to print stuff to graphical console
        sys.stdout = self
        code.InteractiveConsole.push(self, line)
        sys.stdout = self.stdout
        
    def write(self, data):
        ### OVERWRITING InteractiveConsole.write to print to graphical console
        try:
            s = str(data)
            if data[-1] == "\n":
                s = str(data[:-1])
            s = str(s.encode("ascii", "ignore"))
            if len(s) <= 0: return
            self.addOutput(s, sf.Color.WHITE)
        except:
            traceback.print_exc(file=sys.stderr)
    
    def addOutput(self, out, color=sf.Color.WHITE):
        fullout = str(out.encode("ascii", "ignore"))
        for out in fullout.split("\n"):
            wraps = wrapText(self.output_area.local_bounds.width - 5, out, self.output_char_size)
            for s in wraps:
                txt = sf.Text()
                txt = sf.Text(s, game.Game.font, character_size=self.output_char_size)
                txt.color = color
                self.outputs.append(txt)
                if len(self.outputs) - self.output_index > self.num_outputs:
                    self.output_index += 1
            
    def drawOutputs(self, window):
        oY = self.output_area.global_bounds.top + 5
        for i in xrange(self.output_index, self.num_outputs+self.output_index):
            if i >= len(self.outputs):  break
            txt = self.outputs[i]
            if oY + txt.character_size > self.output_area.global_bounds.height:
                break
            txt.position = (self.output_area.global_bounds.left+3, oY)
            window.draw(txt)
            oY += txt.character_size
        
    def draw(self, window):
        if not self.open:   return
        window.draw(self.output_area)
        window.draw(self.input_area)
        self.drawOutputs(window)
        if len(self.outputs) > 0:
            self.scrollbar.position = self.scrollbar.position.x, self.output_area.position.y + self.output_area.size.y * self.output_index / len(self.outputs)
            bar_h = self.num_outputs * self.output_area.size.y / len(self.outputs)
            if bar_h > self.output_area.size.y:
                bar_h = self.output_area.size.y
            self.scrollbar.size = self.scrollbar.size.x, bar_h
        window.draw(self.scrollbar)
        self.input.set_text(self.line)
        window.draw(self.input)
        window.draw(self.cursor)
    
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