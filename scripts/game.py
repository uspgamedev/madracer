﻿#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
import pickle
from collections import namedtuple

HighscoreEntry = namedtuple("HighscoreEntry", "name points level")
AnimationData = namedtuple("AnimationData", "tex rows cols num_frames fps sw sh")
class EntityGenerator:
    def __init__(self, name, interval, entities, number):
        self.name = name
        self.interval = interval
        self.entities = entities
        self.number = number
        self.time_to_create = 0.0

class TextureManager:
    def __init__(self):
        self.explosion1 = sf.Texture.from_file("images/explosion1.png")
        self.explosion2 = sf.Texture.from_file("images/explosion2.png")
        self.explosion3 = sf.Texture.from_file("images/explosion3.png")
        self.explosion4 = sf.Texture.from_file("images/explosion4.png")
        self.explosion5 = sf.Texture.from_file("images/explosion5.png")
        self.explosion6 = sf.Texture.from_file("images/explosion6.png")
        self.bomb_explosion = sf.Texture.from_file("images/bomb_explosion.png")
        self.vehicle_explosion = sf.Texture.from_file("images/vehicle_explosion.png")
        self.vehicle_collision = sf.Texture.from_file("images/vehicle_collision.png")
        self.dust_cloud = sf.Texture.from_file("images/dust_cloud.png")
        self.rock0 = sf.Texture.from_file("images/rock0.png")
        self.rock1 = sf.Texture.from_file("images/rock1.png")
        self.quicksand = sf.Texture.from_file("images/quicksand.png")
        self.bomb = sf.Texture.from_file("images/bomb.png")
        self.bomb_powerup = sf.Texture.from_file("images/bomb_powerup.png")
        self.hp_powerup = sf.Texture.from_file("images/hp_powerup.png")
        self.projectile = sf.Texture.from_file("images/projectile.png")
        self.player = sf.Texture.from_file("images/player.png")
        self.berserker = sf.Texture.from_file("images/berserker.png")
        self.slinger = sf.Texture.from_file("images/slinger.png")
        self.warrig = sf.Texture.from_file("images/warrig.png")
        self.rigturret = sf.Texture.from_file("images/rigturret.png")
        self.track = sf.Texture.from_file("images/track.png")
        self.track.repeated = True
    def __getitem__(self, k):
        return self.__dict__[k]

class AnimationManager:
    def __init__(self, images):
        self.explosion1 = AnimationData(images.explosion1, 9, 10, 90, 110, 100, 100)
        self.explosion2 = AnimationData(images.explosion2, 10, 10, 100, 120, 100, 100)
        self.explosion3 = AnimationData(images.explosion3, 6, 10, 60, 70, 100, 100)
        self.explosion4 = AnimationData(images.explosion4, 6, 10, 60, 70, 100, 100)
        self.explosion5 = AnimationData(images.explosion5, 6, 10, 60, 70, 100, 100)
        self.explosion6 = AnimationData(images.explosion6, 3, 10, 30, 40, 100, 100)
        self.bomb_explosion = AnimationData(images.bomb_explosion, 3, 8, 24, 24, None,None)
        self.vehicle_explosion = AnimationData(images.vehicle_explosion, 4, 4, 16, 15, None,None)
        self.vehicle_collision = AnimationData(images.vehicle_collision, 1, 13, 13, 16, None,None)
        self.dust_cloud = AnimationData(images.dust_cloud, 1, 13, 13, 16, None,None)
    def __getitem__(self, k):
        return self.__dict__[k]

class SoundManager:
    def __init__(self):
        self.collision1 = sf.SoundBuffer.from_file("sounds/collision1.wav")
        self.collision2 = sf.SoundBuffer.from_file("sounds/collision2.wav")
        self.collision3 = sf.SoundBuffer.from_file("sounds/collision3.wav")
        self.collision4 = sf.SoundBuffer.from_file("sounds/collision4.wav")
        self.explosion = sf.SoundBuffer.from_file("sounds/explosion.wav")
        self.bomb_explosion = sf.SoundBuffer.from_file("sounds/bomb_explosion.ogg")
        self.fire = sf.SoundBuffer.from_file("sounds/fire.wav")
        self.hit1 = sf.SoundBuffer.from_file("sounds/hit1.wav")
        self.hit2 = sf.SoundBuffer.from_file("sounds/hit2.wav")
        self.hit3 = sf.SoundBuffer.from_file("sounds/hit3.wav")
        self.hit4 = sf.SoundBuffer.from_file("sounds/hit4.wav")
        self.hit5 = sf.SoundBuffer.from_file("sounds/hit5.wav")
        self.vehicle_explosion = sf.SoundBuffer.from_file("sounds/vehicle_explosion.ogg")
        #no need to pre-load music file, its played differently by streaming
        self.sounds = []
    def playSound(self, sound, pos=None):
        s = sf.Sound(sound)
        if pos != None:
            sp = (pos - Game.track_pos) - (Game.player.pos - Game.track_pos)
            sp = (sp / Game.track_area)*100
            s.position = (sp.x, sp.y, 0)
            s.attenuation = 0.5
            s.min_distance = 10 #max dist where sound is heard full-volume, beyond this it attenuates
        s.play()
        self.sounds.append(s)
        return s
    def playCollision(self, pos=None):
        sound = self.__dict__["collision%i" % (1+int(random.random()*4))]
        return self.playSound(sound, pos)
    def playHit(self, pos=None):
        hit_sounds = [self.explosion, self.hit1, self.hit2, self.hit3, self.hit4]
        sound = random.choice(hit_sounds)
        return self.playSound(sound, pos)
    def playBombExplosion(self, pos=None):
        return self.playSound(self.bomb_explosion, pos)
    def playFire(self, pos=None):
        return self.playSound(self.fire, pos)
    def playVehicleExplosion(self, pos=None):
        return self.playSound(self.vehicle_explosion, pos)
    def update(self):
        toremove = []
        for s in self.sounds:
            if s.status == sf.Sound.STOPPED:
                toremove.append(s)
        for s in toremove:
            self.sounds.remove(s)

################################################################
class Game:
    fps = 30.0
    
    try:
        with open("./highscores", 'rb') as fh:
            highscores = pickle.load(fh)
    except:
        highscores = [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)]
    
    images = TextureManager()
    animations = AnimationManager(images)
    sounds = SoundManager()

    def __init__(self):
        pass
    def build(self):
        self.input_index = 0
        self.track_pos = Vector(100, 0)
        self.track_area = Vector(800, 700)
        def powerupFactory(x,y):
            return RandomizePowerUp(Vector(x,y), 1.0)
        self.entityFactory = {
            'berserker': Berserker,
            'slinger': Slinger,
            'warrig': WarRig,
            'rock': Rock,
            'quicksand': QuickSand,
            'powerup': powerupFactory,
            }
        self.generators = [
            EntityGenerator('obstacles', [10.0, 50.0], [('quicksand',0.6), ('rock',0.4)], lambda: round(Game.speed_level)),
            EntityGenerator('obstaclesSimple', [1.0, 5.0], [('rock',1.0)], lambda: 1),
            EntityGenerator('powerups', [10.0, 50.0], [('powerup',1.0)], lambda: round(Game.speed_level)),
            EntityGenerator('berserkers', [1.0, 5.0], [('berserker',1.0)], lambda: round(Game.speed_level)),
            EntityGenerator('slingers', [2.0, 8.0], [('slinger',1.0)], lambda: round(Game.speed_level)),
            EntityGenerator('enemiesSimple', [2.0, 12.0], [('berserker',0.6), ('slinger',0.4)], lambda: 2*math.floor(Game.speed_level)),
            EntityGenerator('allenemies', [10.0, 30.0], [('berserker',0.4), ('slinger',0.4), ('warrig',0.2)], lambda: 2*math.floor(Game.speed_level)),
            EntityGenerator('rigs', [60.0, 60.0], [('warrig',1.0)], lambda: round(Game.speed_level) - 1)
        ]
        self.console = Console({'game': self})
        
    def initialize(self, window, font, cheatsEnabled, stretchView, superhot):
        self.window = window
        self.font = font
        self.entities = []
        self.effects = []
        self.console.initGraphics()
        self.input = input.available_inputs[self.input_index]()
        if not self.input.valid():
            self.changeInput(False)
        self.superhot = superhot
        
        self.entCount = 0
        self.cont = True
        self.speed_level = 1.0
        self.points = 0.0
        self.track = sf.Sprite(self.images.track)
        self.track.position = self.track_pos.x, -2100
        self.delta_time = 1.0/self.fps
        self.actual_fps = self.fps
        self.music = sf.Music.from_file('sounds/music.ogg')
        self.music.play()
        self.music.loop = True
        self.music.volume = 80
        sf.Listener.set_direction((0,1,0))
        
        self.paused = False
        self.cheats_enabled = cheatsEnabled
        self.cheated = False
        self.generate_entities = True
        
        self.stretchView = stretchView
        self.updateGraphics()
        self.player_name = []
        self.player = Player(400, 400)
        self.entities.append(self.player)
        
        for gen in self.generators:
            gen.time_to_create = (gen.interval[1] - gen.interval[0])*random.random() + gen.interval[0]
        
        self.clock = sf.Clock()
        self.clock.restart()
        
    def initGraphics(self):
        self.track.position = (self.track_pos).toSFML()
        
        barWidth = self.track_pos.x
        width, height = self.window.view.size
        
        def createBar(x, w, color):
            bar = sf.RectangleShape((w, height))
            bar.fill_color = color
            bar.position = x, 0
            return bar
        self.side_bars = [
            createBar(0, barWidth, sf.Color.BLACK),
            createBar(self.track_pos.x+self.track_area.x, barWidth, sf.Color.BLACK),
            createBar(self.track_pos.x-3, 3, sf.graphics.Color(112,112,112,255)),
            createBar(self.track_pos.x+self.track_area.x, 3, sf.graphics.Color(112,112,112,255)),
            createBar(self.track_pos.x-6, 3, sf.graphics.Color(112,0,0,255)),
            createBar(self.track_pos.x+self.track_area.x+3, 3, sf.graphics.Color(112,0,0,255))]
        
        hsCor = sf.graphics.Color(160,160,0,255)
        
        #text point values: esquerda, right-align, branco
        #self.pointsTxt = GUIText("-", (100-6, 45), GUIText.HOR_RIGHT, sf.Color.WHITE, 18)
        #text player values: direita, right-align, branco
        self.plaDataTxts = []
        for i in xrange(4):
            self.plaDataTxts.append(GUIText("-", (width, 25 + 40*(i)), GUIText.HOR_RIGHT, sf.Color.WHITE, 18))
        
        self.fixedHudText = []
        #text commands: direita, left_align, amarelado *
        #text player keys: direita, right-align, branco *
        ckY = self.plaDataTxts[-1].txt.position.y + 2*18 #pos a little below the last text
        self.fixedHudText.append(GUIText(self.input.name, (width-barWidth+6,ckY), GUIText.HOR_LEFT, sf.Color.RED, 18))
        ckY += 18
        for cmd, key in self.input.command_list():
            self.fixedHudText.append(GUIText(cmd, (width-barWidth+6, ckY), GUIText.HOR_LEFT, hsCor, 18))
            ckY += 18
            self.fixedHudText.append(GUIText(key, (width, ckY), GUIText.HOR_RIGHT, sf.Color.WHITE, 18))
            ckY += 24
        
        #text highscore: esquerda, left-align, branco *
        self.fixedHudText.append(GUIText("Highscores:", (0,20), GUIText.HOR_LEFT, sf.Color.RED, 18))
        #text HSE points: esquerda, right-align, branco *
        hsY = 50
        for i, hse in enumerate(Game.highscores):
            #text HSE names: esquerda, left-align, amarelado *
            hsName = str(i+1)+': '+hse.name
            self.fixedHudText.append(GUIText(hsName, (0, hsY), GUIText.HOR_LEFT, hsCor, 18))
            hsY += 18
            self.fixedHudText.append(GUIText("%i"%(hse.points), (barWidth-6, hsY), GUIText.HOR_RIGHT, sf.Color.WHITE, 18))
            hsY += 18
            mins = hse.level-1
            secs = mins*60 - int(mins)*60
            mins = int(mins)
            self.fixedHudText.append(GUIText("%im%is"%(mins,secs), (barWidth-6, hsY), GUIText.HOR_RIGHT, sf.Color.WHITE, 18))
            hsY += 24
            
        #text player data: direita, left_align, branco *
        self.fixedHudText.append(GUIText("Shots:\n\nBombs:\n\nSpeed:\n\nPoints", (width-barWidth+6,5), GUIText.HOR_LEFT, hsCor, 18))
        #text points: esquerda, left-align, branco *
        #self.fixedHudText.append(GUIText("Points:", (0,25), GUIText.HOR_LEFT, hsCor, 18))

        self.pausedTxt = GUIText("PAUSED", (width/2, height/2), GUIText.CENTER, sf.Color.BLACK, 40)
        self.pausedTxt.txt.style = sf.Text.BOLD
        self.pausedTxt.outline_color = sf.Color.RED
        self.pausedTxt.outline_thickness = 1
        
        self.gameOverTxt = GUIText("GAME OVER", (width/2, height/2), GUIText.CENTER, sf.Color.BLACK, 40)
        self.gameOverTxt.txt.style = sf.Text.BOLD
        self.gameOverTxt.outline_color = sf.Color.RED
        self.gameOverTxt.outline_thickness = 1
        
        restxt = "Type in highscore name (max 8 chars):\n\n\nPress ENTER to start a new game."
        self.restartTxt = GUIText(restxt, (width/2, height/2 + 40), GUIText.HOR_CENTER, sf.Color.BLACK, 20)
        self.restartTxt.txt.style = sf.Text.BOLD
        self.restartTxt.outline_color = sf.Color.RED
        self.restartTxt.outline_thickness = 1
        
        self.plaNameTxt = GUIText("-", (width/2, height/2 + 70), GUIText.HOR_CENTER, sf.Color.BLACK, 30)
        self.plaNameTxt.txt.style = sf.Text.BOLD
        self.plaNameTxt.outline_color = sf.Color.RED
        self.plaNameTxt.outline_thickness = 1
        
    def updateGraphics(self):
        #to be executed when window changes size (ex.: change fullscreen status
        self.window.view = sf.View((0,0,1000,700))
        orisize = Vector(1000,700)
        if not self.stretchView:
            if self.window.width/orisize.x > self.window.height/orisize.y:
                # eixo Y eh o base
                ww = self.window.height * orisize.x / orisize.y
                ww = ww / self.window.width
                self.window.view.viewport = ((1.0 - ww)/2, 0.0, ww, 1.0)
            else:
                # eixo X eh o base
                hh = self.window.width * orisize.y / orisize.x
                hh = hh / self.window.height
                self.window.view.viewport = (0.0, (1.0 - hh)/2, 1.0, hh)

        self.initGraphics()
        
    def getIDfor(self, ent):
        self.entCount += 1
        return self.entCount
    
    ####### DRAW
    def draw(self):
        tpy = self.track.position.y
        if tpy > 0:
            topHalfY = tpy - self.track.texture.height
            self.track.position = self.track_pos.x, topHalfY
            self.window.draw(self.track)
            self.track.position = self.track_pos.x, tpy
        self.window.draw(self.track)
        
        for bar in self.side_bars:
            self.window.draw(bar)
        
        #text player values: direita, right-align, branco
        playerValues = ("%i/%i" % (self.player.shots_available, self.player.max_shots),
                        "%i" % self.player.bombs,
                        "%.2f%%" % (self.speed_level*100),
                        "%i" % round(self.points))
        for txt, s in zip(self.plaDataTxts, playerValues):
            txt.set_text( s )
            txt.draw(self.window)
        
        #draw fixed HUD text elements
        for txt in self.fixedHudText:
            txt.draw(self.window)
        
        #draw elements
        for ent in self.entities:
            ent.draw(self.window)
        
        #draw effects
        for eff in self.effects:
            eff.draw(self.window)
        
        if self.input.target_dir() != None:
            self.input.drawPlayerTarget(self.window)
                
        if self.player.hp <= 0:
            self.gameOverTxt.draw(self.window)
            if self.cheated:
                self.restartTxt.set_text("Press ENTER to start a new game.\nCheating disables highscores.")
            elif self.getHSindex() >= 0:
                self.plaNameTxt.set_text("".join(self.player_name))
                self.plaNameTxt.draw(self.window)
            else:
                self.restartTxt.set_text("Press ENTER to start a new game.")
            self.restartTxt.draw(self.window)
        else:
            if self.paused:
                self.pausedTxt.draw(self.window)
                
        self.console.draw(self.window)
        
    ####### UPDATE
    def update(self):
        ### debugging feature to run SUPER!HOT! (frame-per-frame)
        if not self.cont and self.superhot: 
            return
        self.cont = False

        elapsed = self.clock.restart()
        self.actual_fps = 1.0/elapsed.seconds
        
        dt = elapsed.seconds #1.0 / self.fps
        self.delta_time = dt
        
        self.sounds.update()
        self.input.update(dt)
        
        if self.player.hp > 0 and not self.paused and not self.console.open:
            # update game stats
            self.points += dt #+1 point per second
            self.speed_level += dt/60.0 #speed_level will increase by 1 each 60 secs
            
            # generate new entities
            if self.generate_entities:
                possibleBottomEntTypes = ['berserker', 'slinger']
                for gen in self.generators:
                    gen.time_to_create -= dt
                    if gen.time_to_create <= 0:
                        n = int(gen.number())
                        #print 'Executing generator '+gen.name+', n='+str(n)
                        for _ in xrange(n):
                            entIndex = random.random();
                            cumulative = 0.0
                            for type, chance in gen.entities:
                                if entIndex < chance + cumulative:
                                    X = random.random()*self.track_area.x
                                    newEnt = Game.entityFactory[type](X+self.track_pos.x, 0)                                        
                                    Y = -newEnt.size.y*0.85
                                    if random.random() < 0.25 and isInArray(type, possibleBottomEntTypes):
                                        Y = Game.track_area.y - newEnt.size.y*0.55
                                    newEnt.pos.x = newEnt.pos.x - newEnt.size.x * 0.5
                                    newEnt.pos.y = Y - Game.track_pos.y
                                    alert = TimedAction(3.0, NewEntityAction(newEnt))
                                    self.effects.append(alert)
                                    break
                                cumulative += chance
                        gen.time_to_create = (gen.interval[1] - gen.interval[0])*random.random() + gen.interval[0]
                        #print "Finished generator. New TTC = "+str(gen.time_to_create)
                        break
        
            # check for collision & handle them
            for i in xrange(len(self.entities)):
                for j in xrange(i+1, len(self.entities)):
                    ent1 = self.entities[i]
                    ent2 = self.entities[j]
                    if ent1.checkCollision(ent2):
                        ent1.collidedWith(ent2)

            # update each entity
            for ent in list(self.entities): #to operate on a copy of entity list so that it can be altered in self loop
                ent.update(dt)
                ent.stuck = False
                if ent.hp <= 0:
                    ent.onDeath()
                    self.points += ent.point_value
                    self.entities.remove(ent)
            
            # sort effect by priority
            def effect_comp(a,b):
                v = int(b.priority - a.priority) #greater values first
                if v != 0:
                    return v / abs(v)
                return 0
            self.effects.sort(effect_comp)
            # update each effect
            for eff in list(self.effects):
                eff.update(dt)
                if eff.destroyed:
                    self.effects.remove(eff)
            
            self.track.position = self.track_pos.x, self.track.position.y + (self.speed_level + 5)
            if self.track.position.y > 700:
                self.track.position = (self.track_pos.x, -2100)

    ####### INPUT
    def processTextInput(self, e):
        self.console.processInput(e)
        if not self.console.open:
            if self.player.hp <= 0:
                if not e.unicode in [8,13] and len(self.player_name) < 8: # any text char, except newline and backspace
                    try:
                        self.player_name.append( chr(e.unicode) )
                    except:
                        print "ERROR: Strange text key entered"
    def processInput(self, e):
        if self.cheats_enabled:
            self.console.processInput(e)
        if self.console.open:   return
        self.cont = True
        self.input.receiveInputEvent(e)
        if not e.released:
            if self.player.hp <= 0: return
            if self.cheats_enabled:
                if e.code == sf.Keyboard.H and e.control:
                    self.player.hp = self.player.max_hp
                    self.cheated = True
                elif e.code == sf.Keyboard.B and e.control:
                    self.player.bombs += 1
                    self.cheated = True
            self.cont = True
        else:
            if self.player.hp <= 0:
                if e.code == sf.Keyboard.BACK_SPACE and len(self.player_name) > 0: #backspace
                    self.eraseCharFromPlayerName()
                elif e.code == sf.Keyboard.RETURN: #enter
                    self.startNewGame()
            else:
                if self.cheats_enabled:
                    if e.code == sf.Keyboard.T and e.control:
                        self.entities.append( Berserker(200, 200) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.Y and e.control:
                        self.entities.append( Slinger(600, 200) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.U and e.control:
                        self.entities.append( WarRig(400, 160) )
                        self.entities[-1].createTurrets()
                        self.cheated = True
                    elif e.code == sf.Keyboard.I and e.control:
                        self.entities.append( Rock(random.random()*self.track_area.x, -30) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.O and e.control:
                        self.entities.append( QuickSand(random.random()*self.track_area.x, -20) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.P and e.control:
                        self.entities.append( Dummy(random.random()*self.track_area.x, random.random()*self.track_area.y) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.G and e.control:
                        self.generate_entities = not self.generate_entities
                        self.cheated = True
                    
    def pause(self):
        self.paused = not self.paused
        
    def changeInput(self, update_graphics=True):
        while (True):
            self.input_index = (self.input_index+1) % len(input.available_inputs)
            self.input = input.available_inputs[self.input_index]()
            if self.input.valid():
                break
        if update_graphics:
            self.updateGraphics()

    def appendCharToPlayerName(self, c):
        if len(self.player_name) < 8:
            self.player_name.append( chr(e.unicode) )
    def changePlayerNameChar(self, i, c):
        if i < len(self.player_name):
            self.player_name[i] = c
        elif i == len(self.player_name) and len(self.player_name) < 8:
            self.player_name.append(c)
    def getPlayerNameChar(self, i):
        if i < len(self.player_name):
            return self.player_name[i]
        return ''
    def eraseCharFromPlayerName(self, index=-1):
        if len(self.player_name) > 0:
            if index < 0 or index >= len(self.player_name):
                index = -1
            self.player_name.pop(index)
    def startNewGame(self):
        if len(self.player_name) == 0:   
            self.player_name = ['?']*5
        hs_index = self.getHSindex()
        if hs_index >= 0 and not self.cheated:
            self.highscores.pop()
            self.highscores.insert(hs_index, HighscoreEntry("".join(self.player_name), round(self.points), self.speed_level) )
        self.initialize(self.window, self.font, self.cheats_enabled, self.stretchView, self.superhot)
        #save highscores
        with open("./highscores", 'wb') as fh:
            pickle.dump(self.highscores, fh)
            
    def getHSindex(self):
        hs_index = -1
        for i, hse in enumerate(self.highscores):
            if self.points > hse.points:
                hs_index = i
                break
        return hs_index

Game = Game()

from utils import Vector, GUIText, Console
from powerup import RandomizePowerUp
from entities import *
from effects import TimedAction, NewEntityAction
import input

Game.build()