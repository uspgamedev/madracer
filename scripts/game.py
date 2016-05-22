#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
import pickle
from collections import namedtuple

try:
    font = sf.Font.from_file("arial.ttf")
except IOError: 
    print "ERROR: can't load font"
    exit(1)

HighscoreEntry = namedtuple("HighscoreEntry", "name points level")
AnimationData = namedtuple("AnimationData", "tex rows cols num_frames fps sw sh")
class EntityGenerator:
    def __init__(self, name, interval, entities, number):
        self.name = name
        self.interval = interval
        self.entities = entities
        self.number = number
        self.time_to_create = 0.0

##############################################################
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
            sp = (pos - Game.track_pos) #- (Game.player.pos - Game.track_pos)
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

##############################################################
class HighScores(sf.Drawable):
    def __init__(self):
        sf.Drawable.__init__(self)
        try:
            with open("./highscores", 'rb') as fh:
                self.scores = pickle.load(fh)
        except:
            self.scores = {1: [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)],
                           2: [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)],
                           3: [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)],
                           4: [HighscoreEntry('-----', 0, 1.0) for i in xrange(10)]
                          }
        
    def updateGraphics(self, hsID, bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness):
        self.texts = []
        self.createGraphicsForHS("Highscores (%i players):", hsID, bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness)
    
    def updateAllGraphics(self, initPos, size, xOffset, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness):
        self.texts = []
        xplus = 0
        for i in xrange(4):
            self.createGraphicsForHS("%i Players", i+1, sf.Rectangle((initPos[0]+xplus, initPos[1]), size), show_values_below, title_color, names_color, values_color, background_color, background_border_thickness)
            xplus += xOffset + size[0]
    
    def createGraphicsForHS(self, titleFormat, hsID, bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness):
        rect = sf.RectangleShape(bounds.size)
        rect.position = bounds.position
        rect.fill_color = background_color
        rect.outline_thickness = background_border_thickness
        rect.outline_color = title_color
        self.texts.append(rect)
        #text highscore: esquerda, left-align, branco *
        self.texts.append(GUIText(titleFormat%(hsID), (bounds.left+bounds.width/2, bounds.top+2), GUIText.HOR_CENTER, title_color, 20))
        #text HSE points: esquerda, right-align, branco *
        hsY = self.texts[-1].bounds.bottom + 7
        for i, hse in enumerate(self.scores[hsID]):
            #text HSE names: esquerda, left-align, amarelado *
            hsName = str(i+1)+': '+hse.name
            self.texts.append(GUIText(hsName, (bounds.left+2, hsY), GUIText.HOR_LEFT, names_color, 18))
            if show_values_below:
                hsY += 18
            self.texts.append(GUIText("%i"%(hse.points), (bounds.right-2, hsY), GUIText.HOR_RIGHT, values_color, 18))
            mins, secs = Game.getTimeFromSpeedLevel(hse.level)
            if not show_values_below:
                hsY += 18
                self.texts.append(GUIText("%im%is"%(mins,secs), (bounds.right-2, hsY), GUIText.HOR_RIGHT, values_color, 18))
            else:
                self.texts.append(GUIText("%im%is"%(mins,secs), (bounds.left+2, hsY), GUIText.HOR_LEFT, values_color, 18))
            hsY += 24
            if not show_values_below:
                hsY += 3
        
    def InsertScore(self, players):
        #self.players[0].name, round(self.players[0].points), self.players[0].speed_level
        
        N = len(players)
        def comp(p1, p2):
            diff = p2.points - p1.points
            if diff != 0:
                return int(diff/abs(diff))
            return 0
        players.sort(comp)
        name = ";".join([pla.name for pla in players])
        points = sum([pla.points for pla in players])
        speedLvl = max([pla.speed_level for pla in players])
    
        hs_index = self.getHSindex(N, points)
        if hs_index >= 0:
            self.scores[N].pop()
            self.scores[N].insert(hs_index, HighscoreEntry(name, points, speedLvl) )
            self.save()
        
    def save(self):
        with open("./highscores", 'wb') as fh:
            pickle.dump(self.scores, fh)
            
    def getHSindex(self, id, points):
        hs_index = -1
        for i, hse in enumerate(self.scores[id]):
            if points > hse.points:
                hs_index = i
                break
        return hs_index
        
    def draw(self, target, states):
        for text in self.texts:
            target.draw(text, states)
            
###############################################################
# GAME STATES
class GameState(sf.Drawable):
    def __init__(self):
        sf.Drawable.__init__(self)
        self.stacktop_draw = False
        self.entities = [] #POG pra o Game poder pegar lista de entidades sem ter q testar q State que eh
        
    def pushToGame(self):
        Game.states.append(self)
        
    def onPopFromGame(self):
        pass
        
    # if return False, state is deleted from Game.
    def update(self, dt):
        return True
        
    def processInput(self, e):
        pass
        
    def draw(self, target, states):
        pass
        
    def getWindowImage(self):
        ssTex = sf.RenderTexture(Game.window.view.size.x, Game.window.view.size.y)
        ssTex.active = True
        #self.InitOpenGLContext(ssTex)
        ssTex.clear()
        #self.screenshotting = renderMode
        ssTex.draw(self)
        #self.screenshotting = 0
        ssTex.display()
        Game.window.active = True
        #self.InitOpenGLContext(self.window)
        return ssTex
        
class LocalGame(GameState):
    def __init__(self, player_data):
        GameState.__init__(self)
        self.entities = []
        self.effects = []
        BaseEntity.entCount = 0
        self.speed_level = 1.0
        self.track = Track()
        self.music = sf.Music.from_file('sounds/music.ogg')
        self.music.play()
        self.music.loop = True
        self.music.volume = 80
        sf.Listener.set_direction((0,1,0))
        
        self.cheated = False
        self.generate_entities = True
        
        plaX = [200,400,600,800] #FIXME
        plaColors = [sf.Color.GREEN, sf.Color.BLUE, sf.Color.RED, sf.Color.MAGENTA]
        self.players = []
        for i, (plaName, plaPreset, plaInputID) in enumerate(player_data):
            player = Player(plaX.pop(0), 400, i, plaColors.pop(0), plaName, plaPreset, plaInputID, len(player_data)>1)
            self.players.append(player)
            self.entities.append(player)
        self.initGraphics()

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
            EntityGenerator('obstacles', [10.0, 50.0], [('quicksand',0.6), ('rock',0.4)], lambda: round(Game.states[-1].speed_level)),
            EntityGenerator('obstaclesSimple', [1.0, 5.0], [('rock',1.0)], lambda: 1),
            EntityGenerator('powerups', [10.0, 50.0], [('powerup',1.0)], lambda: round(Game.states[-1].speed_level)),
            EntityGenerator('berserkers', [1.0, 5.0], [('berserker',1.0)], lambda: round(Game.states[-1].speed_level)),
            EntityGenerator('slingers', [2.0, 8.0], [('slinger',1.0)], lambda: round(Game.states[-1].speed_level)),
            EntityGenerator('enemiesSimple', [2.0, 12.0], [('berserker',0.6), ('slinger',0.4)], lambda: 2*math.floor(Game.states[-1].speed_level)),
            EntityGenerator('allenemies', [10.0, 30.0], [('berserker',0.4), ('slinger',0.4), ('warrig',0.2)], lambda: 2*math.floor(Game.states[-1].speed_level)),
            EntityGenerator('rigs', [60.0, 60.0], [('warrig',1.0)], lambda: round(Game.states[-1].speed_level) - 1)
        ]
        for gen in self.generators:
            gen.time_to_create = (gen.interval[1] - gen.interval[0])*random.random() + gen.interval[0]
            
        self.pause_screen = PauseScreen(self.players)
        
    def game_finished(self):
        for player in self.players:
            if player.hp > 0:   return False
        return True
        
    def initGraphics(self):
        barWidth = Game.track_pos.x
        width, height = Game.window.view.size
        
        def createBar(x, w, color):
            bar = sf.RectangleShape((w, height))
            bar.fill_color = color
            bar.position = x, 0
            return bar
        self.side_bars = [
            createBar(0, barWidth, sf.Color.BLACK),
            createBar(Game.track_pos.x+Game.track_area.x, barWidth, sf.Color.BLACK),
            createBar(Game.track_pos.x-3, 3, sf.graphics.Color(112,112,112,255)),
            createBar(Game.track_pos.x+Game.track_area.x, 3, sf.graphics.Color(112,112,112,255)),
            createBar(Game.track_pos.x-6, 3, sf.graphics.Color(112,0,0,255)),
            createBar(Game.track_pos.x+Game.track_area.x+3, 3, sf.graphics.Color(112,0,0,255))]
                
    def update(self, dt):
        if not self.game_finished():
            # update game stats
            self.speed_level += dt/60.0 #speed_level will increase by 1 each 60 secs
            for player in self.players:
                if player.hp > 0:
                    player.points += dt #+1 point per second
                    player.speed_level = self.speed_level
            
            listenerPos = self.players[0].center() - Game.track_pos #FIXME
            listenerPos = (listenerPos / Game.track_area)*100
            sf.Listener.set_position((listenerPos.x,listenerPos.y,0))
            
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
                                    X = random.random()*Game.track_area.x
                                    newEnt = self.entityFactory[type](X+Game.track_pos.x, 0)                                        
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
                    for player in self.players:
                        if player.hp > 0:  #FIXME: points should go to a single player - the one who killed this ent
                            player.points += ent.point_value
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

            self.track.update(self.speed_level)
            
            #check if paused
            self.checkIfPlayerPaused()
        else:
            return False
        return True
        
    def onPopFromGame(self):
        lastScreen = self.getWindowImage()
        gameOver = GameOverScreen(self.players, self.cheated, lastScreen)
        gameOver.pushToGame()
        
    def processInput(self, e):
        for player in self.players:
            if player.hp > 0:
                player.input.processInput(e)
        
        if type(e) is sf.FocusEvent and e.lost:
            self.pause_screen.pushToGame(None)
            return
        self.checkIfPlayerPaused()
        
        if type(e) is sf.KeyEvent:
            if not e.released:
                if self.game_finished(): return
                if Game.cheats_enabled:
                    if e.code == sf.Keyboard.H and e.control:
                        for player in self.players:
                            player.hp = player.max_hp
                        self.cheated = True
                    elif e.code == sf.Keyboard.B and e.control:
                        for player in self.players:
                            player.bombs += 1
                        self.cheated = True
            elif not self.game_finished():
                if Game.cheats_enabled:
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
                        self.entities.append( Rock(random.random()*Game.track_area.x, -30) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.O and e.control:
                        self.entities.append( QuickSand(random.random()*Game.track_area.x, -20) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.P and e.control:
                        self.entities.append( Dummy(random.random()*Game.track_area.x, random.random()*Game.track_area.y) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.G and e.control:
                        self.generate_entities = not self.generate_entities
                        self.cheated = True
  
    def checkIfPlayerPaused(self):
        if input.InputMethod.PAUSE in Game.loop_commands:
            pla = Game.loop_commands.pop(input.InputMethod.PAUSE)
            self.pause_screen.pushToGame(pla)
  
    def draw(self, target, states):
        target.draw(self.track, states)
        
        for bar in self.side_bars:
            target.draw(bar, states)
        
        #draw elements
        for ent in self.entities:
            ent.draw(target)
        
        #draw effects
        for eff in self.effects:
            target.draw(eff, states)
        
        # gotta do this separately to ensure player's UI are on top of entities and effects
        for player in self.players:
            player.drawUI(target)

class PauseScreen(GameState):
    def __init__(self, players):
        GameState.__init__(self)
        self.players = players
        self.paused_player = None
        width, height = Game.window.view.size
        self.whoPaused = GUIText("nobody", (width/2, height/2 - 25), GUIText.CENTER, sf.Color.BLACK, 18)
        self.whoPaused.text_outline_color = sf.Color.RED
        self.whoPaused.text_outline_thickness = 1
        
        self.pausedTxt = GUIText("PAUSED", (width/2, height/2), GUIText.CENTER, sf.Color.BLACK, 40)
        self.pausedTxt.style = sf.Text.BOLD
        self.pausedTxt.text_outline_color = sf.Color.RED
        self.pausedTxt.text_outline_thickness = 1
        
    def pushToGame(self, player):
        Game.highscores.updateGraphics(len(self.players), sf.Rectangle((100, 120),(220,475)), False, sf.Color.RED, sf.graphics.Color(160,160,0,255), sf.Color.WHITE,
                                           sf.Color(0,0,0,180), 3)
        if player != None:
            player.input.updateGraphics(sf.Rectangle((680, 120),(220,475)), False, sf.Color.RED, sf.graphics.Color(160,160,0,255), sf.Color.WHITE,
                                      sf.Color(0,0,0,180), 3)
            self.paused_player = player
            self.paused_player.paused = True
            self.whoPaused.text = player.name
        else:
            self.paused_player = True
            self.whoPaused.text = ""
        GameState.pushToGame(self)
        
    def onPopFromGame(self):
        if type(self.paused_player) != bool:
            self.paused_player.input.disableGraphics()
        
    def update(self, dt):
        if type(self.paused_player) != bool:
            return self.paused_player.paused
        return self.paused_player
        
    def processInput(self, e):
        if type(self.paused_player) != bool:
            self.paused_player.input.processInput(e)
        else:
            for pla in self.players:
                pla.input.processInput(e)
        if input.InputMethod.PAUSE in Game.loop_commands:
            if type(self.paused_player) != bool:
                self.paused_player.paused = False
            else:
                self.paused_player = False
            Game.loop_commands.pop(input.InputMethod.PAUSE)
        if type(e) is sf.FocusEvent:
            if type(self.paused_player) != bool:
                self.paused_player.paused = e.lost
            else:
                self.paused_player = e.lost
        
    def draw(self, target, states):
        target.draw(self.whoPaused, states)
        target.draw(self.pausedTxt, states)
        target.draw(Game.highscores, states)

class GameOverScreen(GameState):
    def __init__(self, players, cheated, GOSTex):
        GameState.__init__(self)
        self.active = True
        self.players = players
        self.cheated = cheated
        self.gos_tex = GOSTex #GOSTex = GameOver Screen Texture
        self.gos_spr = sf.Sprite(self.gos_tex.texture)
        width, height = Game.window.view.size
                
        self.gameOverTxt = GUIText("GAME OVER", (width/2, height/2), GUIText.CENTER, sf.Color.BLACK, 40)
        self.gameOverTxt.style = sf.Text.BOLD
        self.gameOverTxt.text_outline_color = sf.Color.RED
        self.gameOverTxt.text_outline_thickness = 1
        
        restxt = "Press any key to return to main menu."
        self.restartTxt = GUIText(restxt, (width/2, height/2 + 40), GUIText.HOR_CENTER, sf.Color.BLACK, 20)
        self.restartTxt.style = sf.Text.BOLD
        self.restartTxt.text_outline_color = sf.Color.RED
        self.restartTxt.text_outline_thickness = 1
        
        Game.highscores.updateGraphics(len(players), sf.Rectangle((100, 120),(220,475)), False, sf.Color.RED, 
                                       sf.graphics.Color(160,160,0,255), sf.Color.WHITE, sf.Color(0,0,0,180), 3)
        
    def onPopFromGame(self):
        if not self.cheated:
            Game.highscores.InsertScore(self.players)

    def update(self, dt):
        return self.active
        
    def processInput(self, e):
        if type(e) in [sf.KeyEvent, sf.JoystickButtonEvent] and e.released:
            self.active = False
        
    def draw(self, target, states):
        target.draw(self.gos_spr, states)
        target.draw(Game.highscores, states)
        target.draw(self.gameOverTxt, states)
        hs_index = Game.highscores.getHSindex(len(self.players), sum([pla.points for pla in self.players]))
        if self.cheated:
            self.restartTxt.text = "Press any key to return to main menu.\nCheating disables highscores."
        elif hs_index >= 0:
            self.restartTxt.text = "Press any key to return to main menu.\nEntered Highscores in #%s!" % (hs_index+1)
        target.draw(self.restartTxt, states)
       
class MainMenuScreen(GameState):
    def __init__(self):
        GameState.__init__(self)
        self.active = True
        self.stacktop_draw = True
        width, height = Game.window.view.size
        self.track = Track(True)
        
        self.title = GUIText("MAD Racer!", (width/2, 20), GUIText.HOR_CENTER, sf.Color.BLACK, 60)
        self.title.style = sf.Text.BOLD
        self.title.text_outline_color = sf.Color.RED
        self.title.text_outline_thickness = 1

        def cmdValueActiveChanged(cv):
            cv.outline_color = sf.Color.BLUE if cv.active else sf.Color.RED
        def buttonActiveChanged(cv):
            cv.outline_color = sf.Color.GREEN if cv.active else sf.Color.BLACK
        
        self._activeindex = 0
        self._hor_activeindex = 1
        self.players = []
        self.presets = [None] * 4
        self.pla_inputIDs = [None] * 4
        y = 90
        for i in xrange(4):
            x = width/5 - 10
            platxt = GUIText("Player %i:" % (i+1), (x, y+8), GUIText.HOR_RIGHT, sf.Color.BLACK, 18)
            platxt.style = sf.Text.BOLD
            platxt.text_outline_color = sf.Color.RED
            platxt.text_outline_thickness = 1
            
            x += 15
            planame = TextEntry("", sf.Rectangle((x, y), (width/5, 33)),
                                20, sf.Color.WHITE, sf.Color(0,0,0,180), 3, sf.Color.RED, sf.Color.WHITE)
            planame.onActiveChanged = cmdValueActiveChanged
            planame.active = False
            planame.max_text_length = 12
            if i == self.active_index:
                planame.active = True
                
            x += width/5 + 30
            plainput = FrameText("-------", sf.Rectangle((x, y), (width/5, 33)),
                                20, sf.Color.WHITE, sf.Color(0,0,0,180), 3, sf.Color.RED, GUIText.HOR_CENTER)
            plainput.onActiveChanged = cmdValueActiveChanged
            plainput.active = False
            
            x += width/5 + 30
            gamePadID = FrameText("------", sf.Rectangle((x, y), (width/5, 33)),
                                20, sf.Color.WHITE, sf.Color(0,0,0,180), 3, sf.Color.RED, GUIText.HOR_CENTER)
            gamePadID.onActiveChanged = cmdValueActiveChanged
            gamePadID.active = False
                
            self.players.append( (platxt, planame, plainput, gamePadID) )
            
            y += 50
        
        y += 20
        self.errormsg = GUIText("", (width/2, y), GUIText.HOR_CENTER, sf.Color.BLACK, 20)
        self.errormsg.style = sf.Text.BOLD
        self.errormsg.text_outline_color = sf.Color.RED
        self.errormsg.text_outline_thickness = 1
        self.errormsg_lifetime = 5.0
        self.errormsg_elapsed = 0.0
        
        self.buttons = []
        y += 40
        def addButton(name, y):
            button = FrameText(name, sf.Rectangle((width*.5 - width/8, y), (width/4, 33)),
                                24, sf.Color.GREEN, sf.Color(100,100,0,255), 3, sf.Color.BLACK, GUIText.HOR_CENTER)
            button.onActiveChanged = buttonActiveChanged
            button.active = False
            self.buttons.append(button)
            return 60
            
        y += addButton("Start Game", y)
        y += addButton("Create Input Preset", y)
        y += addButton("Highscores", y)
        y += addButton("Exit", y)
        
    @property
    def active_index(self):
        return self._activeindex
    @active_index.setter
    def active_index(self, i):
        prev = self.get_active_entry()
        self._activeindex = i
        maxind = len(self.players) + len(self.buttons) - 1
        if self._activeindex < 0:   self._activeindex = maxind
        if self._activeindex > maxind:   self._activeindex = 0
        if self._activeindex <= 3:
            prev_hor = self.hor_active_index
            self.hor_active_index = self.hor_active_index
            if self.hor_active_index == 1 and prev_hor != 1:
                self.hor_active_index = 2
        curr = self.get_active_entry()
        if prev != curr:
            prev.active = False
            curr.active = True
        
    @property
    def hor_active_index(self):
        return self._hor_activeindex
    @hor_active_index.setter
    def hor_active_index(self, i):
        prev = self.get_active_entry()
        self._hor_activeindex = i
        
        lastIndex = 2
        if self.presets[self.active_index] != None and self.presets[self.active_index].device_type() == input.Binding.DEVICE_JOYSTICK:
            lastIndex = 3
        
        if self._hor_activeindex < 1:   self._hor_activeindex = lastIndex
        if self._hor_activeindex > lastIndex:   self._hor_activeindex = 1
        curr = self.get_active_entry()
        if prev != curr:
            prev.active = False
            curr.active = True
    
    def get_active_entry(self):
        if self.active_index <= 3:
            return self.players[self.active_index][self.hor_active_index]
        else:
            return self.buttons[self.active_index-4]
        
    def update(self, dt):
        self.track.update(2.0)
        if self.errormsg.text != "":
            self.errormsg_elapsed += dt
            if self.errormsg_elapsed > self.errormsg_lifetime:
                self.errormsg_elapsed = 0.0
                self.errormsg.text = ""
        return self.active
        
    def processInput(self, e):
        if self.active_index <= 3 and self.hor_active_index == 1:
            self.players[self.active_index][1].processInput(e)
        
        if type(e) == sf.KeyEvent and e.released:
            if e.code == sf.Keyboard.DOWN:
                self.active_index += 1
            if e.code == sf.Keyboard.UP:
                self.active_index -= 1
            if e.code == sf.Keyboard.RIGHT and self.active_index <= 3:
                self.hor_active_index += 1
            if e.code == sf.Keyboard.LEFT and self.active_index <= 3:
                self.hor_active_index -= 1
            if e.code == sf.Keyboard.RETURN:
                self.handleButtons()
        elif type(e) == sf.JoystickMoveEvent:
            if e.axis == sf.Joystick.POV_X and abs(e.position) >= 1:
                self.active_index -= int(e.position/abs(e.position))
            if e.axis == sf.Joystick.POV_Y and abs(e.position) >= 1 and self.active_index <= 3:
                self.hor_active_index += int(e.position/abs(e.position))
        elif type(e) == sf.JoystickButtonEvent and e.released:
            if e.button in range(4):
                self.handleButtons(e.joystick_id)
        elif type(e) == sf.JoystickConnectEvent:
            if e.disconnected and e.joystick_id in self.pla_inputIDs:
                ind = self.pla_inputIDs.index(e.joystick_id)
                prev = self.active_index
                self.active_index = ind
                self.pla_inputIDs[self.active_index] = None
                self.handleJoystickIDChange(None)
                self.active_index = prev
                
    def handleButtons(self, joyID=None):
        if self.active_index <= 3:
            if self.hor_active_index == 2:
                self.handlePresetChange(joyID)
            elif self.hor_active_index == 3:
                self.handleJoystickIDChange(joyID)
        elif self.active_index == 4: #start
            self.handleStartGame()
        elif self.active_index == 5: #create input
            self.handleCreateInputPreset()
        elif self.active_index == 6: #highscores
            hsscreen = HighscoresScreen()
            hsscreen.pushToGame()
        elif self.active_index == 7: #exit
            self.active = False
            
    def handlePresetChange(self, joyID=None):
        preset = input.InputManager.PopPreset()
        if self.presets[self.active_index] != None:
            input.InputManager.PushPreset(self.presets[self.active_index].name)
        self.presets[self.active_index] = preset
        if preset != None:
            self.get_active_entry().text = preset.name
            if preset.device_type() == input.Binding.DEVICE_JOYSTICK:
                self.handleJoystickIDChange(joyID)
            else:
                self.handleJoystickIDChange(-1)
        else:
            self.get_active_entry().text = "-------"
            self.handleJoystickIDChange(-1)
        
    def handleJoystickIDChange(self, joyID=None):
        if joyID == -1:
            joyID = None
        elif not joyID:
            joyID = input.InputManager.PopJoyID()
        if self.pla_inputIDs[self.active_index] != None:
            input.InputManager.PushJoyID(self.pla_inputIDs[self.active_index])
        self.pla_inputIDs[self.active_index] = joyID
        if joyID != None:
            self.players[self.active_index][3].text = "Joystick #%s" % (joyID+1)
        else:
            self.players[self.active_index][3].text = "-------"
            
    def handleStartGame(self):
        plaIndexes = [i for i in xrange(4) if self.players[i][1].text != ""]
        if len(plaIndexes) <= 0:
            self.showError("No players added...")
            return
        planames = [self.players[i][1].text for i in plaIndexes]
        for i, pn in enumerate(planames):
            for j, pn2 in enumerate(planames):
                if i != j and pn == pn2:
                    self.showError("Players %i and %i have equal names." % (i+1, j+1))
                    return
        plapresets = [self.presets[i] for i in plaIndexes]
        if None in plapresets:
            nind = plapresets.index(None)
            self.showError("Invalid preset for player %i" % (plaIndexes[nind]+1))
            return
        for p in plapresets:
            for p2 in plapresets:
                if p != p2 and p.conflictsWith(p2):
                    self.showError("Presets %s and %s have conflicting bindings." % (p.name, p2.name))
                    return
        plainputsIDs = [self.pla_inputIDs[i] for i in plaIndexes]
        for i, piid in enumerate(plainputsIDs):
            if plapresets[i].device_type() != input.Binding.DEVICE_JOYSTICK:    continue
            if piid == None:
                self.showError("Player %i has no Joystick ID selected." % (i+1))
                return
            for j, piid2 in enumerate(plainputsIDs):
                if plapresets[j].device_type() != input.Binding.DEVICE_JOYSTICK:    continue
                if i != j and piid != None and piid == piid2:
                    self.showError("Players %i and %i are using the same Joystick." % (i+1, j+1))
                    return
        localGame = LocalGame(zip(planames, plapresets, plainputsIDs))
        localGame.pushToGame()
        
    def handleCreateInputPreset(self):
        keyselect = InputBindingsScreen()
        keyselect.pushToGame()
        
    def draw(self, target, states):
        target.draw(self.track, states)
        target.draw(self.title, states)
        for i, (platxt, planame, plainput, gamepadID) in enumerate(self.players):
            target.draw(platxt, states)
            target.draw(planame, states)
            target.draw(plainput, states)
            if self.presets[i] != None and self.presets[i].device_type() == input.Binding.DEVICE_JOYSTICK:
                target.draw(gamepadID, states)
        target.draw(self.errormsg, states)
        for button in self.buttons:
            target.draw(button, states)
        
    def showError(self, s):
        self.errormsg.text = s
        self.errormsg_elapsed = 0.0
        
class InputBindingsScreen(GameState):
    def __init__(self):
        GameState.__init__(self)
        self.active = True
        width, height = Game.window.view.size
        self.track = Track(True)
        
        self.frame = sf.RectangleShape((width*.8, height*.84))
        self.frame.position = (width*.1, height*.08)
        self.frame.fill_color = sf.graphics.Color(0,0,0,180)
        self.frame.outline_thickness = 3
        self.frame.outline_color = sf.Color.RED
        
        self.title = GUIText("Define input method bindings", (width/2, 20), GUIText.HOR_CENTER, sf.Color.BLACK, 24)
        self.title.style = sf.Text.BOLD
        self.title.text_outline_color = sf.Color.RED
        self.title.text_outline_thickness = 1
        
        def cmdValueActiveChanged(cv):
            cv.outline_color = sf.Color.BLUE if cv.active else sf.Color.RED
        def buttonActiveChanged(cv):
            cv.outline_color = sf.Color.GREEN if cv.active else sf.Color.BLACK
        
        self.preset = input.Preset()
        self.mark_event = False
        cmds = [('Preset Name', None),
                ('Move Left', input.InputMethod.MOVE_LEFT),
                ('Move Right', input.InputMethod.MOVE_RIGHT), 
                ('Move Up', input.InputMethod.MOVE_UP),
                ('Move Down', input.InputMethod.MOVE_DOWN),
                ('Fire', input.InputMethod.FIRE),
                ('Shoot Bomb', input.InputMethod.SHOOT_BOMB),
                ('Release Bomb', input.InputMethod.RELEASE_BOMB),
                ('Pause', input.InputMethod.PAUSE),
                ('Toggle Fullscreen', input.InputMethod.TOGGLE_FULLSCREEN),
                ('Change Input', input.InputMethod.CHANGE_INPUT),
                ('Close', input.InputMethod.CLOSE),
                ('Toggle FPS Display', input.InputMethod.TOGGLE_FPS_DISPLAY),
                ('Targeting Type', None),
                ('Target Left', None),
                ('Target Right', None),
                ('Target Up', None),
                ('Target Down', None)]
        self.cmds_order = [cmd[0] for cmd in cmds]
        self.target_types = {
            input.InputMethod.AUTO_TARGETING:   "Auto Targeting",
            input.InputMethod.POINT_TARGETING:   "Mouse Targeting",
            input.InputMethod.DIRECTIONAL_TARGETING:   "Directional Targeting"
        }
        self._activeindex = 0
        self.objects = {}
        x = width*.2 + width*.8*.08
        y = height*.1
        for i, (text, key) in enumerate(cmds):
            cmdtext = GUIText(text, (x, y+8), GUIText.HOR_RIGHT, sf.Color.WHITE, 18)
            cmdtext.style = sf.Text.BOLD
            #cmdtext.outline_color = sf.Color.RED
            #cmdtext.outline_thickness = 1
            
            cmdvalue = TextEntry("", sf.Rectangle((x+5, y), (width/5, 33)),
                                20, sf.Color.WHITE, sf.Color(180,180,180,180), 3, sf.Color.RED, sf.Color.WHITE, GUIText.HOR_CENTER)
            
            cmdvalue.onActiveChanged = cmdValueActiveChanged
            cmdvalue.active = False
            if i == self.active_index:
                cmdvalue.max_text_length = 12
                cmdvalue.active = True
            else:
                cmdvalue.cursor.fill_color = sf.Color.TRANSPARENT
            if i == self.cmds_order.index('Targeting Type'):
                cmdvalue.text = self.target_types[self.preset.targeting_type]
            
            self.objects[text] = (key, cmdtext, cmdvalue)
            
            if i == 9:
                x *= 2.5
                y = height*.1
            elif i == self.cmds_order.index('Targeting Type')-1:
                y += 50*3
            else:
                y += 50

        self.errormsg = GUIText("", (width/2, y+20), GUIText.HOR_CENTER, sf.Color.BLACK, 20)
        self.errormsg.style = sf.Text.BOLD
        self.errormsg.text_outline_color = sf.Color.RED
        self.errormsg.text_outline_thickness = 1
        self.errormsg_lifetime = 5.0
        self.errormsg_elapsed = 0.0

        self.ok_button = FrameText("DONE", sf.Rectangle((width*.9 - width/6 - 30, y+10), (width/6, 33)),
                                24, sf.Color.GREEN, sf.Color(100,100,0,255), 3, sf.Color.BLACK, GUIText.HOR_CENTER)
        self.ok_button.onActiveChanged = buttonActiveChanged
        self.ok_button.active = False
        self.cancel_button = FrameText("BACK", sf.Rectangle((width*.1 + width*.8*.04, y+10), (width/6, 33)),
                                24, sf.Color.RED, sf.Color(100,100,0,255), 3, sf.Color.BLACK, GUIText.HOR_CENTER)
        self.cancel_button.onActiveChanged = buttonActiveChanged
        self.cancel_button.active = False
               
    def onPopFromGame(self):
        if self.preset.valid() == "":
            input.InputManager.AddPreset(self.preset)
               
    @property
    def active_index(self):
        return self._activeindex
    @active_index.setter
    def active_index(self, i):
        prev = self.get_active_entry()
        self._activeindex = i
        lastIndex = len(self.cmds_order)-5
        if self.preset.targeting_type == input.InputMethod.DIRECTIONAL_TARGETING:
            lastIndex = len(self.cmds_order)-1
        if self._activeindex < -2:   self._activeindex = lastIndex
        elif self._activeindex > lastIndex:   self._activeindex = -2
        curr = self.get_active_entry()
        if prev != curr:
            prev.active = False
            curr.active = True
        
    def get_active_entry(self):
        if self.active_index >= 0:
            return self.objects[self.cmds_order[self.active_index]][2]
        elif self.active_index == -1:
            return self.ok_button
        elif self.active_index == -2:
            return self.cancel_button
        return None
        
    def update(self, dt):
        self.track.update(2.0)
        if self.errormsg.text != "":
            self.errormsg_elapsed += dt
            if self.errormsg_elapsed > self.errormsg_lifetime:
                self.errormsg_elapsed = 0.0
                self.errormsg.text = ""
        return self.active
        
    def get_opposite_cmd(self, cmd):
        if "Down" in cmd:
            return cmd.replace("Down", "Up")
        if "Up" in cmd:
            return cmd.replace("Up", "Down")
        if "Left" in cmd:
            return cmd.replace("Left", "Right")
        if "Right" in cmd:
            return cmd.replace("Right", "Left")
        return ""
        
    def handleEnter(self):
        if self.active_index == -1:
            preval = self.preset.valid()
            if input.InputManager.HasPreset(self.preset.name):
                self.errormsg.text = "INVALID: preset already exists"
            elif preval == "":
                self.active = False
            else:
                self.errormsg.text = "INVALID: "+preval
        elif self.active_index == -2:
            self.active = False
        else:
            self.mark_event = True
            self.get_active_entry().outline_color = sf.Color.GREEN
        
    def processInput(self, e):
        if self.active_index == self.cmds_order.index('Preset Name'):
            self.get_active_entry().processInput(e)
            self.preset.name = self.get_active_entry().text
            
        if self.mark_event:
            cmd = self.cmds_order[self.active_index]
            key, _, cmdvalue = self.objects[cmd]
            if input.Binding.isBindableEvent(e):
                bind = input.Binding(e)
                if not self.preset.can_add_binding(bind):
                    self.errormsg.text = "Can't add binding - already used"
                    return
                
                if key != None:
                    self.preset.bindings[key] = bind
                elif cmd in ['Target Left', 'Target Right', 'Target Up', 'Target Down']:
                    tbkey = cmd.split()[-1].lower()
                    self.preset.targeting_bindings[tbkey] = bind
                cmdvalue.text = str(bind)
                self.mark_event = False
                self.get_active_entry().outline_color = sf.Color.BLUE
                opcmd = self.get_opposite_cmd(cmd)
                if bind.is_axis() and opcmd != "":
                    opbind = bind.get_opposite_axis_binding()
                    if not self.preset.can_add_binding(opbind):
                        self.errormsg.text = "Can't add opposite bind - already used."
                        return
                    opkey, _, opcmdvalue = self.objects[opcmd]
                    if opkey != None:
                        self.preset.bindings[opkey] = opbind
                    elif opcmd in ['Target Left', 'Target Right', 'Target Up', 'Target Down']:
                        tbkey = opcmd.split()[-1].lower()
                        self.preset.targeting_bindings[tbkey] = opbind
                    opcmdvalue.text = str(opbind)
                
        elif type(e) == sf.KeyEvent and e.released:
            if e.code == sf.Keyboard.DOWN:
                self.active_index += 1
            if e.code == sf.Keyboard.UP:
                self.active_index -= 1
            if e.code == sf.Keyboard.LEFT and self.active_index == self.cmds_order.index('Targeting Type'):
                self.preset.targeting_type -= 1
                if self.preset.targeting_type < 0:  self.preset.targeting_type = 0
                self.get_active_entry().text = self.target_types[self.preset.targeting_type]
            if e.code == sf.Keyboard.RIGHT and self.active_index == self.cmds_order.index('Targeting Type'):
                self.preset.targeting_type += 1
                if self.preset.targeting_type > 2:  self.preset.targeting_type = 2
                self.get_active_entry().text = self.target_types[self.preset.targeting_type]
            if e.code == sf.Keyboard.RETURN and not self.active_index in [self.cmds_order.index('Preset Name'),self.cmds_order.index('Targeting Type')]:
                self.handleEnter()
        elif type(e) == sf.JoystickMoveEvent:
            if e.axis == sf.Joystick.POV_X and abs(e.position) >= 1:
                self.active_index -= int(e.position/abs(e.position))
            if e.axis == sf.Joystick.POV_Y and abs(e.position) >= 1 and self.active_index == self.cmds_order.index('Targeting Type'):
                self.preset.targeting_type += int(e.position/abs(e.position))
                if self.preset.targeting_type < 0:  self.preset.targeting_type = 0
                if self.preset.targeting_type > 2:  self.preset.targeting_type = 2
                self.get_active_entry().text = self.target_types[self.preset.targeting_type]
        elif type(e) == sf.JoystickButtonEvent and e.released:
            if e.button in range(4) and not self.active_index in [self.cmds_order.index('Preset Name'),self.cmds_order.index('Targeting Type')]:
                self.handleEnter()
                
    def draw(self, target, states):
        target.draw(self.track, states)
        target.draw(self.frame, states)
        target.draw(self.title, states)
        for i, cmd in enumerate(self.cmds_order):
            if i >= len(self.cmds_order)-4 and self.preset.targeting_type != input.InputMethod.DIRECTIONAL_TARGETING:
                break
            key, cmdtext, cmdvalue = self.objects[cmd]
            target.draw(cmdtext, states)
            target.draw(cmdvalue, states)
        target.draw(self.ok_button, states)
        target.draw(self.cancel_button, states)
        target.draw(self.errormsg, states)
      
class HighscoresScreen(GameState):
    def __init__(self):
        GameState.__init__(self)
        self.active = True
        self.stacktop_draw = True
        width, height = Game.window.view.size
        self.track = Track(True)
                
        self.title = GUIText("HIGHSCORES", (width/2, 20), GUIText.HOR_CENTER, sf.Color.BLACK, 40)
        self.title.style = sf.Text.BOLD
        self.title.text_outline_color = sf.Color.RED
        self.title.text_outline_thickness = 1
        
        Game.highscores.updateAllGraphics((24, 120), (220,500), 24,
                                            True, 
                                            sf.Color.RED, sf.graphics.Color(160,160,0,255), sf.Color.WHITE, 
                                            sf.Color(0,0,0,180), 3)

    def update(self, dt):
        self.track.update(2.0)
        return self.active
        
    def processInput(self, e):
        if type(e) in [sf.KeyEvent, sf.JoystickButtonEvent] and e.released:
            self.active = False
        
    def draw(self, target, states):
        target.draw(self.track, states)
        target.draw(Game.highscores, states)
        target.draw(self.title, states)
          
################################################################
class Game(object):
    fps = 30.0
    
    highscores = HighScores()
    
    images = TextureManager()
    animations = AnimationManager(images)
    sounds = SoundManager()

    def __init__(self):
        pass
    def build(self):
        self.track_pos = Vector(100, 0)
        self.track_area = Vector(800, 700)
        self.loop_commands = {}
        self.console = Console({'game': self})
        self.console.initGraphics(sf.Rectangle((100, 3), (800, 700/2)) )
        
    def initialize(self, window, font, cheatsEnabled, stretchView, superhot):
        self.window = window
        self.font = font
        self.superhot = superhot
        self.cont = True
        self.actual_fps = self.fps
        self.delta_time = 1.0/self.fps
        self.cheats_enabled = cheatsEnabled
        self.stretchView = stretchView
        self.updateGraphics()
        self.clock = sf.Clock()
        self.clock.restart()
        
        self.states = [MainMenuScreen()]
        #aefdaefaef
        
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
    
    def getTimeFromSpeedLevel(self, speedLvl):
        mins = speedLvl - 1
        secs = mins*60 - int(mins)*60
        mins = int(mins)
        return mins, secs
    
    ####### DRAW
    def draw(self):
        for i, state in enumerate(self.states):
            if not state.stacktop_draw or (state.stacktop_draw and i == len(self.states)-1):
                self.window.draw(state)
                
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
        
        if len(self.states) <= 0:
            self.window.close()
            return
        
        if not self.console.open:
            state = self.states[-1]
            running = state.update(dt)
            if not running:
                self.states.remove(state)
                state.onPopFromGame()

    ####### INPUT
    def processInput(self, e):
        if type(e) is sf.KeyEvent:
            self.cont = True
            if e.code == sf.Keyboard.ESCAPE and e.system:
                self.window.close()
                return
        input.InputManager.processEvent(e)
        if self.cheats_enabled:
            self.console.processInput(e)
        if self.console.open:   return
        
        if len(self.states) > 0:
            self.states[-1].processInput(e)
            if input.InputMethod.CLOSE in self.loop_commands:
                state = self.states.pop()
                state.onPopFromGame()
                self.loop_commands.pop(input.InputMethod.CLOSE)
        else:
            self.window.close()

    @property
    def entities(self):
        if len(self.states) > 0:
            return self.states[-1].entities
        return []
            
Game = Game()

from utils import Vector, GUIText, Console, PlayerHUD, Track, TextEntry, FrameText
from powerup import RandomizePowerUp
from entities import *
from effects import TimedAction, NewEntityAction
import input

Game.build()