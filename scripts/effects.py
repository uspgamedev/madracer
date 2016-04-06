#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from utils import Vector
from game import Game

#******************************** EFFECTS ************************************
class Explosion:
    def __init__(self, center, size, speed, type):
        self.base_speed = speed
        self.original_size = Vector(size,size)
        self.size = self.original_size * Game.scale_factor
        self.size.x = self.size.y * self.original_size.x / self.original_size.y
        self.pos = center - self.size*0.5
        self.destroyed = False
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
        
        if self.limitInRect(Game.track_pos, Game.track_area) or self.frame_index >= self.type.num_frames:
            self.destroyed = True

    def updateGraphics(self, oldfactor):
        relcenter = self.center() / (Game.original_track_area * oldfactor)
        self.size = self.original_size * Game.scale_factor
        self.size.x = self.size.y * self.original_size.x / self.original_size.y
        self.pos = (relcenter * (Game.track_area)) - self.size*0.5
            
    def draw(self, window):
        self.spr.position = self.pos.toSFML() #sprite position
        #self.spr.origin = (self.spr.texture.width/2, self.spr.texture.height/2) #sprite origin
        self.spr.ratio = (self.size.x/self.sw, self.size.y/self.sh) #scale factor
        #self.spr.rotation = math.degrees(angle) #rotation angle (in degrees?)
        window.draw(self.spr)

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
        s = self.base_speed * Game.speed_level + 5
        return Game.scale_factor.y * s
#end class Explosion
def CreateExplosion(pos, size, speed, type):
    Game.effects.append( Explosion(pos, size, speed, type) )

def CreateExplosionAt(ent, size, speed, type):
    CreateExplosion(ent.center(), size, speed, type)

def CreateVehicleExplosion(ent):
    CreateExplosionAt(ent, ent.original_size.len()*2, 1, Game.animations.vehicle_explosion)
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
