#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from utils import Vector, GUIText
from game import Game

#******************************** EFFECTS ************************************
### EXPLOSIONS?!?
class Explosion(sf.Drawable):
    def __init__(self, center, size, speed, type):
        sf.Drawable.__init__(self)
        self.base_speed = speed
        self.size = Vector(size,size)
        self.pos = center - self.size*0.5
        self.destroyed = False
        self.priority = 1
        self.dir = Vector(0, 1)

        self.type = type
        self.frame_index = 0
        self.elapsed = 0.0
        if type.sw > 0:
            self.sw = type.sw
        else:
            self.sw = type.tex.width / self.type.cols
        if type.sh > 0:
            self.sh = type.sh
        else:
            self.sh = type.tex.height / self.type.rows
        self.spr = sf.Sprite(type.tex)
        self.spr.texture_rectangle = sf.Rectangle((0, 0), (self.sw, self.sh)) #pos, size
            
    def update(self, dt):
        self.pos = self.pos + self.dir*self.speed()
        
        if self.elapsed > 1.0 / self.type.fps:
            self.elapsed = 0.0
            self.frame_index += 1
            sx = (self.frame_index % self.type.cols) * self.sw
            sy = math.floor(self.frame_index / self.type.cols) * self.sh
            self.spr.texture_rectangle = sf.Rectangle((sx, sy), (self.sw, self.sh)) #pos, size
            #self.spr.texture_rectangle = sf.Rectangle((int(sx), int(sy)), (1024/8, 384/3)) #pos, siz
        self.elapsed += dt
        
        if self.frame_index >= self.type.num_frames:# or self.limitInRect(Game.track_pos, Game.track_area):
            self.destroyed = True

    def draw(self, target, states):
        self.spr.position = self.pos.toSFML() #sprite position
        self.spr.ratio = (self.size.x/self.sw, self.size.y/self.sh) #scale factor
        target.draw(self.spr, states)

    def limitInRect(self, pos, size):
        center = self.center()
        moved = False
        if center.x < pos.x:
            self.pos.x = pos.x - self.size.x/2
            moved = True
        elif center.x > pos.x + size.x:
            self.pos.x = pos.x + size.x - self.size.x/2
            moved = True
        if center.y < pos.y:
            self.pos.y = pos.y - self.size.y/2
            moved = True
        elif center.y > pos.y + size.y:
            self.pos.y = pos.y + size.y - self.size.y/2
            moved = True
        return moved

    def center(self):
        return self.pos + self.size*0.5

    def speed(self):
        s = self.base_speed * Game.states[-1].speed_level + 5
        return s
#end class Explosion
def CreateExplosion(pos, size, speed, type):
    Game.states[-1].effects.append( Explosion(pos, size, speed, type) )

def CreateExplosionAt(ent, size, speed, type):
    CreateExplosion(ent.center(), size, speed, type)

def CreateVehicleExplosion(ent):
    CreateExplosionAt(ent, ent.size.len()*2, 1, Game.animations.vehicle_explosion)
    Game.sounds.playVehicleExplosion(ent.center())

def CreateVehicleCollision(ent1, ent2):
    #var pos = ent1.center().add(ent2.center().sub(ent1.center()).scale(0.5));
    pos = ent1.center() + (ent2.center()-ent1.center())*0.5
    size = (ent1.size.len()+ent2.size.len())/2
    CreateExplosion(pos, size, 1, Game.animations.vehicle_collision)
    Game.sounds.playCollision(pos)

def CreateVehicleDustCloud(ent):
    #pos = ent.pos + ent.size*(-0.5,1)
    #size = ent.size.x*2
    #pos = pos - Vector(0, size*0.5)
    pos = ent.pos + ent.size*(0.5,1)
    size = ent.size.x*2
    if not hasattr(ent, 'dusttimer') or ent.dusttimer > 0.1:
        CreateExplosion(pos, size, 1, Game.animations.dust_cloud)
        ent.dusttimer = 0.0
    else:
        ent.dusttimer += Game.delta_time

        
#********************* ACTIONS **************************
# TimedAction is a effect that executes a single action once after a set period of time.
# Actions have a draw method, to draw something if needed while they are running.
# Actions have a __call__ method, executed when they are processed.
class TimedAction(sf.Drawable):
    def __init__(self, lifetime, action):
        sf.Drawable.__init__(self)
        self.destroyed = action == None
        self.priority = 10
        self.action = action
        self.lifetime = lifetime
        self.elapsed = 0
            
    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.lifetime and not self.destroyed:
            self.destroyed = True
            self.action()
        self.action.update(dt, self.elapsed / self.lifetime)
            
    def draw(self, target, states):
        self.action.draw(target, states)
            
### ACTIONS
class NewEntityAction:
    color_scheme = {
        'berserker': (False, sf.Color.YELLOW),  #amarelo
        'slinger': (False, sf.Color(255, 150, 0, 255)),     #laranja
        'warrig': (True, sf.Color.RED),   #vermelho piscante
        'rock': (True, sf.Color(160,82,45, 255)),   #vermelho ou ? piscante
        'quicksand': (False, sf.Color.BLUE), #azul
        'powerup': (True, sf.Color.GREEN),  #verde piscante
    }

    def __init__(self, ent):
        self.new_ent = ent
        textSize = 20
        apX = ent.pos.x + ent.size.x/2
        apY = 6 if ent.pos.y < Game.track_area.y/2 else Game.track_area.y - textSize - 3
        self.blinking, self.color = NewEntityAction.color_scheme[ent.type]
        self.alert = GUIText("!", (apX, apY), GUIText.HOR_CENTER, sf.Color.BLACK, textSize)
        self.alert.txt.style = sf.Text.BOLD
        self.alert.outline_color = self.color
        self.tri = sf.CircleShape(15, 3)
        self.tri.origin = (self.tri.local_bounds.left + self.tri.local_bounds.width/2,
                           self.tri.local_bounds.top + self.tri.local_bounds.height/2)
        self.tri.position = self.alert.txt.global_bounds.center #(apX, apY)
        if ent.pos.y < Game.track_area.y/2:
            self.tri.rotation = 180
            self.tri.position = self.tri.position.x, self.tri.position.y + 2
        self.fills = [sf.Color(int(self.color.r*0.2),int(self.color.g*0.2),int(self.color.b*0.2),150),
                      self.color,
                      sf.Color.WHITE
                      ]
        self.tri.outline_thickness = 2
        self.tri.outline_color = self.color
        self.blink_state = 0
        self.blink_elapsed = 0
        self.blink_durations = [.3, .3, .2]
        self.tri.fill_color = self.fills[self.blink_state]
        
    def __call__(self):
        #print "Generating entity %s %s at %s" % (type, self.new_ent.ID, self.new_ent.pos)
        Game.entities.append(self.new_ent)
        if self.new_ent.type == 'warrig': #special case...
            Game.entities[-1].createTurrets()
            
    def update(self, dt, time_lived):
        #time_lived is relative: is goes from 0 (just started) to 1 (lifetime ended)
        c = min(time_lived, 1.0)
        self.alert.txt.color = sf.Color(255*c, 255*c, 255*c, 255)
        if self.blinking:
            self.blink_elapsed += dt
            if self.blink_elapsed >= self.blink_durations[self.blink_state]:
                self.blink_state = (self.blink_state + 1) % len(self.fills)
                self.tri.fill_color = self.fills[self.blink_state]
            
    def draw(self, window, states):
        window.draw(self.tri, states)
        window.draw(self.alert, states)
