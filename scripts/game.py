#!/usr/bin/python
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
        self.ammo = sf.Texture.from_file("images/ammo.png")
        self.points = sf.Texture.from_file("images/points.png")
        self.speed = sf.Texture.from_file("images/speed.png")
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

class HighScores(sf.Drawable):
    def __init__(self):
        sf.Drawable.__init__(self)
        try:
            with open("./highscores", 'rb') as fh:
                self.scores = pickle.load(fh)
        except:
            self.scores = [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)]
        
    def updateGraphics(self, bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness):
        self.texts = []
        rect = sf.RectangleShape(bounds.size)
        rect.position = bounds.position
        rect.fill_color = background_color
        rect.outline_thickness = background_border_thickness
        rect.outline_color = title_color
        self.texts.append(rect)
        #text highscore: esquerda, left-align, branco *
        self.texts.append(GUIText("Highscores:", (bounds.left+bounds.width/2, bounds.top+2), GUIText.HOR_CENTER, title_color, 20))
        #text HSE points: esquerda, right-align, branco *
        hsY = self.texts[-1].bounds.bottom + 7
        for i, hse in enumerate(self.scores):
            #text HSE names: esquerda, left-align, amarelado *
            hsName = str(i+1)+': '+hse.name
            self.texts.append(GUIText(hsName, (bounds.left+2, hsY), GUIText.HOR_LEFT, names_color, 18))
            if show_values_below:
                hsY += 18
            self.texts.append(GUIText("%i"%(hse.points), (bounds.right-2, hsY), GUIText.HOR_RIGHT, values_color, 18))
            hsY += 18
            mins, secs = Game.getTimeFromSpeedLevel(hse.level)
            self.texts.append(GUIText("%im%is"%(mins,secs), (bounds.right-2, hsY), GUIText.HOR_RIGHT, values_color, 18))
            hsY += 24
            if not show_values_below:
                hsY += 3
        
    def InsertScore(self, name, points, speedLvl):
        hs_index = self.getHSindex(points)
        if hs_index >= 0:
            self.scores.pop()
            self.scores.insert(hs_index, HighscoreEntry(name, points, speedLvl) )
            self.save()
        
    def save(self):
        with open("./highscores", 'wb') as fh:
            pickle.dump(self.scores, fh)
            
    def getHSindex(self, points):
        hs_index = -1
        for i, hse in enumerate(self.scores):
            if points > hse.points:
                hs_index = i
                break
        return hs_index
        
    def draw(self, target, states):
        for text in self.texts:
            target.draw(text, states)
            
################################################################
class Game:
    fps = 30.0
    
    highscores = HighScores()
    
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
        self.player = Player(400, 400)
        self.updateGraphics()
        self.initGraphics()
        self.player_name = []
        self.entities.append(self.player)
        
        for gen in self.generators:
            gen.time_to_create = (gen.interval[1] - gen.interval[0])*random.random() + gen.interval[0]
        
        self.clock = sf.Clock()
        self.clock.restart()
        
    def initGraphics(self):
        
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
        
        #text player values: direita, right-align, branco
        self.plaData = PlayerHUD(self.player, (width, 5))
            
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
        
    def getIDfor(self, ent):
        self.entCount += 1
        return self.entCount
    
    def getTimeFromSpeedLevel(self, speedLvl):
        mins = speedLvl - 1
        secs = mins*60 - int(mins)*60
        mins = int(mins)
        return mins, secs
    
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
        
        self.window.draw(self.plaData)
        
        #draw elements
        for ent in self.entities:
            ent.draw(self.window)
        
        #draw effects
        for eff in self.effects:
            self.window.draw(eff)
        
        self.window.draw(self.input)
                
        if self.player.hp <= 0:
            self.window.draw(self.highscores)
            self.window.draw(self.gameOverTxt)
            if self.cheated:
                self.restartTxt.set_text("Press ENTER to start a new game.\nCheating disables highscores.")
            elif self.highscores.getHSindex(self.player.points) >= 0:
                self.plaNameTxt.set_text("".join(self.player_name))
                self.window.draw(self.plaNameTxt)
            else:
                self.restartTxt.set_text("Press ENTER to start a new game.")
            self.window.draw(self.restartTxt)
        else:
            if self.paused:
                self.window.draw(self.pausedTxt)
                self.window.draw(self.highscores)
                
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
            self.player.points += dt #+1 point per second
            self.speed_level += dt/60.0 #speed_level will increase by 1 each 60 secs
            
            self.plaData.update(dt)
            
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
                    self.player.points += ent.point_value
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
        if self.paused and self.player.hp > 0:
            self.highscores.updateGraphics(sf.Rectangle((120, 120),(200,475)), False, sf.Color.RED, sf.graphics.Color(160,160,0,255), sf.Color.WHITE,
                                           sf.Color(0,0,0,180), 3)
            self.input.updateGraphics(sf.Rectangle((680, 120),(200,475)), False, sf.Color.RED, sf.graphics.Color(160,160,0,255), sf.Color.WHITE,
                                      sf.Color(0,0,0,180), 3)
        else:
            self.input.disableGraphics()
        
    def changeInput(self, update_graphics=True):
        input_graphics_params = self.input.graphics_params
        while (True):
            self.input_index = (self.input_index+1) % len(input.available_inputs)
            self.input = input.available_inputs[self.input_index]()
            if self.input.valid():
                break
        if update_graphics:
            if len(input_graphics_params) > 0:
                self.input.updateGraphics(*input_graphics_params)
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
        if not self.cheated:
            self.highscores.InsertScore("".join(self.player_name), round(self.player.points), self.speed_level)
        self.initialize(self.window, self.font, self.cheats_enabled, self.stretchView, self.superhot)

Game = Game()

from utils import Vector, GUIText, Console, PlayerHUD
from powerup import RandomizePowerUp
from entities import *
from effects import TimedAction, NewEntityAction
import input

Game.build()