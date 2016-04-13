#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from collections import namedtuple
from entities import *
from utils import Vector
from game import Game

#*********** PowerUp ******************
class PowerUp(BaseEntity):
    def __init__(self, x, y, action):
        BaseEntity.__init__(self, 'powerup', x, y, 30, 30, 'green', 5.0, 1, 0)
        self.dir = Vector(0, 1)
        self.show_life_bar = False
        self.was_picked_up = False
        self.onPickup = action
        #self.considers_game_speed = True

    def update(self, dt):
        if self.move(self.dir):
            self.hp = -1

    def collidedWith(self, ent):
        if ent.type != 'player':
            return
        self.was_picked_up = True
        self.hp = -1

    def onDeath(self):
        if self.was_picked_up:
            self.onPickup()
            self.point_value = 50
#end class PowerUp


def CheckAndDropPowerUp(pos, chanceToCreate):
    #print "checking for power dropping"
    pup = RandomizePowerUp(pos, chanceToCreate)
    if pup != None:
        Game.entities.append(pup)

def RandomizePowerUp(pos, chanceToCreate):
    #print "checking for power dropping"
    if random.random() <= chanceToCreate:
        itemIndex = random.random()
        cumulative = 0.0
        for pupdata in PowerUpTable:
            if itemIndex < pupdata.chance + cumulative:
                pup = PowerUp(pos.x, pos.y, pupdata.action)
                pup.spr = sf.Sprite(pupdata.image)
                return pup
            cumulative += pupdata.chance
    return None
        
#********************** POWER UP TABLE ******************
def hpupAction():
    Game.player.hp += 150
    if Game.player.hp > Game.player.max_hp:
        Game.player.hp = Game.player.max_hp
def bombupAction():
    Game.player.bombs += 1

PowerUpData = namedtuple("PowerUpData", "name chance image action")

PowerUpTable = [PowerUpData('hpup', 0.65, Game.images.hp_powerup, hpupAction), 
                PowerUpData('bombup', 0.35, Game.images.bomb_powerup, bombupAction)
]
        