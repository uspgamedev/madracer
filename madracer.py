#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
import pickle
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
        return Vector(self.x, self.y);
    
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
        return "("+str(self.x)+", "+str(self.y)+")"
    def __repr__(self):
        return self.__str__()
#end class Vector

class Turret:
    def __init__(self, ent, widthSizeFactor=0.6):
        self.ent = ent
        self.wsf = widthSizeFactor
        self.spr = sf.Sprite(Game.images.rigturret)
        
    def draw(self, window, dir):
        w = self.ent.size.x*self.wsf
        h = w * self.spr.texture.height / self.spr.texture.width
        xoffset = (self.ent.size.x - w)/2
        yoffset = self.ent.size.y/2 - h/2
        x = self.ent.pos.x + xoffset + w/2
        y = self.ent.pos.y + yoffset + h/2
        angle = 0.0
        if dir != None:
            angle = math.atan2(dir.y, dir.x) + math.pi/2
        self.spr.position = (x, y) #sprite position
        self.spr.origin = (self.spr.texture.width/2, self.spr.texture.height/2) #sprite origin
        self.spr.ratio = (w/self.spr.texture.width, h/self.spr.texture.height) #scale factor
        self.spr.rotation = math.degrees(angle) #rotation angle (in degrees?)
        window.draw(self.spr)

def isInArray(value, array):
    return value in array

HighscoreEntry = namedtuple("HighscoreEntry", "name points level")
AnimationData = namedtuple("AnimationData", "tex rows cols num_frames fps sw sh")
PowerUpData = namedtuple("PowerUpData", "name chance image action")
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
    def playSound(self, sound):
        s = sf.Sound(sound)
        s.play()
        self.sounds.append(s)
        return s
    def playCollision(self):
        sound = self.__dict__["collision%i" % (1+int(random.random()*4))]
        return self.playSound(sound)
    def playHit(self):
        hit_sounds = [self.explosion, self.hit1, self.hit2, self.hit3, self.hit4]
        sound = random.choice(hit_sounds)
        return self.playSound(sound)
    def playBombExplosion(self):
        return self.playSound(self.bomb_explosion)
    def playFire(self):
        return self.playSound(self.fire)
    def playVehicleExplosion(self):
        return self.playSound(self.vehicle_explosion)
    def update(self):
        toremove = []
        for s in self.sounds:
            if s.status == sf.Sound.STOPPED:
                toremove.append(s)
        for s in toremove:
            self.sounds.remove(s)

class GUIText:
    #perhaps implement this inheriting from sf.Text instead of encapsulating it?
    HOR_LEFT = 0
    HOR_RIGHT = 1
    HOR_CENTER = 2
    CENTER = 3
    def __init__(self, txt, pos, align=HOR_LEFT, color=sf.Color.BLACK, size=20):
        self.txt = sf.Text(txt, Game.font, character_size=size)
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
        self.txt.string = s
        self.updateOrigin()
        
    def set_align(self, a):
        self.align = a
        self.updateOrigin()
        
    def position(self):
        return self.txt.position
    def set_position(self, pos):
        self.txt.position = pos if type(pos) == type([]) or type(pos) == type(()) else pos.toSFML()
        self.updateOrigin()
        
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
#******************************** ENTITIES ************************************
class BaseCar:
    def __init__(self, type, x, y, w, h, color, speed, hp, points):
        self.type = type
        self.pos = Vector(x,y)
        self.original_size = Vector(w,h)
        self.size = self.original_size * Game.scale_factor
        self.size.x = self.size.y * self.original_size.x / self.original_size.y
        self.color = color
        try:
            self.spr = sf.Sprite(Game.images[type])
        except:
            self.spr = None
        self.base_speed = speed
        self.stuck = False #if caught on quicksand
        self.hp = hp
        self.max_hp = hp
        self.show_life_bar = True
        self.ID = Game.getIDfor(self)
        self.point_value = points
        self.last_moved_dir = Vector(0,0)
        self.considers_game_speed = False
        
        self.maxbar = sf.RectangleShape((self.size.x, 5))
        self.maxbar.fill_color = sf.Color.BLACK
        
        self.curbar = sf.RectangleShape((self.size.x * self.hp/self.max_hp, 5))
        self.curbar.fill_color = sf.Color.RED

    def draw(self, window):
        self.drawEntity(window)
        self.drawHPBar(window)
    def drawEntity(self, window):
        w = self.size.x;
        h = self.size.y;
        x = self.pos.x + w/2;
        y = self.pos.y + h/2;
        angle = self.last_moved_dir.x * math.pi/8
        if self.type == 'warrig': 
            angle = 0.0
        self.spr.position = (x, y) #sprite position
        self.spr.origin = (self.spr.texture.width/2, self.spr.texture.height/2) #sprite origin
        self.spr.ratio = (w/self.spr.texture.width, h/self.spr.texture.height) #scale factor
        self.spr.rotation = math.degrees(angle) #rotation angle (in degrees?)
        window.draw(self.spr)
        
    def drawHPBar(self, window):
        if self.show_life_bar:
            #ctx.fillStyle = 'black'
            #ctx.fillRect(self.pos.x, self.pos.y+self.size.y+1, self.size.x, 5)
            self.maxbar.position = (self.pos.x, self.pos.y + self.size.y + 1)
            window.draw(self.maxbar)
            #ctx.fillStyle = 'red'
            #ctx.fillRect(self.pos.x, self.pos.y+self.size.y+1, self.size.x*self.hp/self.max_hp, 5)
            self.curbar.size = (self.size.x * self.hp/self.max_hp, 5)
            self.curbar.position = (self.pos.x, self.pos.y + self.size.y + 1)
            window.draw(self.curbar)
            
    def updateGraphics(self, oldfactor):
        relcenter = self.center() / (Game.original_track_area * oldfactor)
        self.size = self.original_size * Game.scale_factor
        self.size.x = self.size.y * self.original_size.x / self.original_size.y
        self.pos = (relcenter * (Game.track_area)) - self.size*0.5
        self.maxbar.size = (self.size.x, 5)
        self.curbar.size = (self.size.x * self.hp/self.max_hp, 5)

    def checkCollision(self, ent):
        notIntersects = self.pos.x > (ent.pos.x + ent.size.x)
        notIntersects = notIntersects or (self.pos.x + self.size.x) < ent.pos.x
        notIntersects = notIntersects or self.pos.y > (ent.pos.y + ent.size.y)
        notIntersects = notIntersects or (self.pos.y + self.size.y) < ent.pos.y
        return not notIntersects

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
        return self.pos + self.size*0.5 #self.pos.add(self.size.scale(0.5))

    def onDeath(self):
        pass

    def speed(self):
        s = self.base_speed
        if self.considers_game_speed:
            s = s * Game.speed_level + 5
        return Game.scale_factor.y * s * (1.0 - self.stuck*0.85) #0.85 is % of speed lost while stuck

    def move(self, dir):
        self.last_moved_dir = dir.copy()
        self.pos = self.pos + dir*self.speed() #self.pos.add(dir.scale(self.speed()))
        return self.limitInRect(Game.track_pos, Game.track_area)
#end class BaseCar

#************* Player ****************
class Player(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'player', x, y, 32, 60, 'black', 4, 150, 0)
        self.desired_move = Vector(0,0)
        self.bombs = 3
        self.max_shots = 25
        self.shots_available = self.max_shots
        self.shot_reload_time = 0.2
        self.cooldown_time = 0.1
        self.cooldown_elapsed = self.cooldown_time
        self.reload_elapsed = 0.0
        self.target = None
        self.shot_dmg = 20
        self.shot_speed = 15
        self.try_fire = False
        self.turret = Turret(self)

    def draw(self, window):
        BaseCar.drawEntity(self, window)
        BaseCar.drawHPBar(self, window)
        dir = None
        if self.target != None:
            dir = self.target.center() - self.center()
            dir.normalize()
        self.turret.draw(window, dir)

    def update(self, dt):
        moveDelta = self.desired_move.copy()
        moveDelta.normalize()
        self.move(moveDelta)
        CreateVehicleDustCloud(self)
        
        if self.shots_available < self.max_shots:
            self.reload_elapsed += dt
            if self.reload_elapsed > self.shot_reload_time:
                self.reload_elapsed = 0.0
                self.shots_available += 1
        
        self.target = None
        min_dist = Game.track_area.squaredLen()
        validTargets = ['berserker', 'slinger', 'warrig', 'rigturret']
        for i in xrange(1, len(Game.entities)):
            ent = Game.entities[i]
            if ent.hp <= 0 or not isInArray(ent.type, validTargets):
                continue
            dist = ent.center() - self.center()
            if dist.squaredLen() < min_dist: #yay raizes desnecessarias!
                min_dist = dist.squaredLen()
                self.target = ent
        
        self.cooldown_elapsed += dt
        if self.target != None and self.try_fire and self.cooldown_elapsed >= self.cooldown_time and self.shots_available > 0:
            dir = self.target.center() - self.center()
            dir.normalize()

            init_pos = self.center()
            projectile = Projectile(init_pos.x, init_pos.y, self.shot_dmg, self.shot_speed, dir, 2)
            projectile.cant_hit.append(self.type)
            Game.entities.append(projectile)
            self.shots_available -= 1
            self.reload_elapsed = 0.0
            self.cooldown_elapsed = 0.0

    def input(self, e):
        isDown = not e.released
        if e.code == sf.Keyboard.LEFT and (isDown or (not isDown and self.desired_move.x == -1)): #left 
            self.desired_move.x = -1*isDown
        elif e.code == sf.Keyboard.UP and (isDown or (not isDown and self.desired_move.y == -1)): #up
            self.desired_move.y = -1*isDown
        elif e.code == sf.Keyboard.RIGHT and (isDown or (not isDown and self.desired_move.x == 1)): #right
            self.desired_move.x = 1*isDown
        elif e.code == sf.Keyboard.DOWN and (isDown or (not isDown and self.desired_move.y == 1)): #down
            self.desired_move.y = 1*isDown
        elif e.code == sf.Keyboard.D:
            #shoot back!
            self.try_fire = isDown
        elif e.code == sf.Keyboard.S and not isDown and self.bombs > 0:
            #release bomb
            self.bombs -= 1
            bomb = Bomb(self.pos.x, self.pos.y, 1)
            Game.entities.append(bomb)

    def collidedWith(self, ent):
        ent.collidedWith(self)

    def onDeath(self):
        CreateVehicleExplosion(self)
#end class Player

#*********** Berserker ******************
class Berserker(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'berserker', x, y, 32, 60, 'red', 3.5, 25, 200)
        self.isChasing = True
        self.moveAwayElapsed = 0.0

    def update(self, dt):
        dir = Game.player.center() - self.center()
        dir.normalize()
        if not self.isChasing:
            dir = -dir
            self.moveAwayElapsed += dt
            if self.moveAwayElapsed > 0.7:
                self.isChasing = True
                self.moveAwayElapsed = 0.0
        self.move(dir)
        CreateVehicleDustCloud(self)

    def collidedWith(self, ent):
        if ent.type == 'player':
            ent.hp -= 20
            self.hp -= 5
            self.isChasing = False
        elif ent.type == 'berserker':
            ent.hp -= 0.5
            self.hp -= 0.5
        else:
            ent.collidedWith(self)
            return
        CreateVehicleCollision(self, ent)
        dir = self.center() - ent.center()
        dir.normalize()
        self.pos = self.pos + dir*(2*self.speed()) #self.pos.add(dir.scale(2*self.speed()));

    def onDeath(self):
        Game.CheckAndDropPowerUp(self.pos, 0.10)
        CreateVehicleExplosion(self)
#end class Berserker

#*********** Slinger ********************
class Slinger(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'slinger', x, y, 32, 60, 'purple', 2, 25, 200)
        self.time_to_shoot = 0.7
        self.cooldown = 0.0
        self.range = random.random()*200 + 100 #range in [100, 300]
        self.turret = Turret(self)

    def update(self, dt):
        dir = Game.player.center() - self.center()
        dist = dir.len()
        dir.normalize()
        
        if abs(dist - self.range) > 30:
            move_target = Game.player.pos + dir*(-self.range)
            move_dir = move_target - self.pos
            move_dir.normalize()
            self.move(move_dir)
        else:
            self.last_moved_dir = Vector(0,0)
        CreateVehicleDustCloud(self)
        
        self.cooldown += dt
        if self.cooldown > self.time_to_shoot:
            #SHOOT!
            init_pos = self.center()
            projectile = Projectile(init_pos.x, init_pos.y, 6, 15, dir, 2)
            projectile.cant_hit.append(self.type)
            Game.entities.append(projectile)
            self.cooldown = 0.0

    def draw(self, window):
        BaseCar.drawEntity(self, window)
        BaseCar.drawHPBar(self, window)
        dir = Game.player.center() - self.center()
        dir.normalize()
        self.turret.draw(window, dir)

    def collidedWith(self, ent):
        if ent.type == 'player':
            ent.hp -= 1
            self.hp -= 20
            self.cooldown -= self.time_to_shoot/3
        elif ent.type == 'berserker':
            ent.hp -= 0.5
            self.hp -= 8
        elif ent.type == 'slinger':
            ent.hp -= 0.5
            self.hp -= 0.5
        else:
            ent.collidedWith(self)
            return
        CreateVehicleCollision(self, ent)
        dir = self.pos - ent.pos
        dir.normalize()
        self.pos = self.pos + dir*(2*self.speed())

    def onDeath(self):
        Game.CheckAndDropPowerUp(self.pos, 0.15)
        CreateVehicleExplosion(self)
#end class Slinger

#*********** WarRig *********************
class WarRig(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'warrig', x, y, 40, 160, 'yellow', 1, 300, 1000)
        self.time_to_shoot = 1.0
        self.cooldown = 0.0

    def createTurrets(self):
        Game.entities.append(RigTurret(self, 5.0/16))
        Game.entities.append(RigTurret(self, 10.0/16))

    def update(self, dt):
        firing_pos = self.pos + self.size*(0.5, 0.16)
        dir = Game.player.center() - firing_pos
        dir.normalize()
        
        lastPos = self.pos.copy()
        self.move(dir)
        CreateVehicleDustCloud(self)
        posDiff = self.pos - lastPos
        
        self.cooldown += dt
        if self.cooldown > self.time_to_shoot:
            #SHOOT!
            init_pos = firing_pos
            projectile = Projectile(init_pos.x, init_pos.y, 10, 15, dir, 2)
            projectile.cant_hit.append(self.type)
            projectile.cant_hit.append('rigturret')
            Game.entities.append(projectile)
            self.cooldown = 0.0

    def collidedWith(self, ent):
        if ent.type == 'player':
            ent.hp -= 25
            self.hp -= 0.5
            self.cooldown -= self.time_to_shoot/3
        elif ent.type == 'berserker' or ent.type == 'slinger':
            ent.hp -= 1
            self.hp -= 0.5
        elif ent.type == 'rigturret':
            return
        elif ent.type == 'warrig':
            pass
        else:
            ent.collidedWith(self)
            return
        CreateVehicleCollision(self, ent)
        dir = ent.pos - self.pos
        dir.normalize()
        ent.pos = ent.pos + dir*(2*self.speed())

    def onDeath(self):
        Game.CheckAndDropPowerUp(self.pos, 1.0)
        CreateVehicleExplosion(self)
#end class WarRig

#*********** RigTurret ******************
class RigTurret(BaseCar):
    def __init__(self, rig, relative_yoffset):
        self.relative_yoffset = relative_yoffset
        self.yoffset = self.relative_yoffset * rig.size.y
        BaseCar.__init__(self, 'rigturret', rig.pos.x, rig.pos.y+self.yoffset, 40, 40, '#808000', 0, 40, 100)
        self.time_to_shoot = 0.5
        self.cooldown = 0.0
        self.show_life_bar = False
        self.rig = rig
        self.turret = Turret(self, 0.75)

    def draw(self, window):
        dir = Game.player.center() - self.center()
        dir.normalize()
        self.turret.draw(window, dir)

    def update(self, dt):
        if self.rig == None or self.rig.hp <= 0:
            self.hp = -1
            return
        self.pos = self.rig.pos + Vector(0, self.yoffset)

        self.cooldown += dt
        if self.cooldown > self.time_to_shoot:
            #SHOOT!
            init_pos = self.center()
            dir = Game.player.center() - init_pos
            dir.normalize()
            projectile = Projectile(init_pos.x, init_pos.y, 5, 15, dir, 2)
            projectile.color = '#000080'
            projectile.cant_hit.append(self.type)
            projectile.cant_hit.append('warrig')
            Game.entities.append(projectile)
            self.cooldown = 0.0

    def updateGraphics(self, oldfactor):
        BaseCar.updateGraphics(self, oldfactor)
        self.yoffset = self.relative_yoffset * self.rig.size.y
            
    def collidedWith(self, ent):
        if ent.type == 'player':
            self.hp -= 5
            self.cooldown -= self.time_to_shoot/3
        elif ent.type == 'berserker' or ent.type == 'slinger':
            ent.hp -= 1
            self.hp -= 0.5
        elif ent.type == 'warrig' or ent.type == 'rigturret':
            return
        else:
            ent.collidedWith(self)
            return
        CreateVehicleCollision(self, ent)
        dir = ent.pos - self.pos
        dir.normalize()
        ent.pos = ent.pos + dir*(2*self.speed())

    def onDeath(self):
        Game.CheckAndDropPowerUp(self.pos, 0.15)
        CreateVehicleExplosion(self)
#end class RigTurret

#/*********** Projectile *****************
class Projectile(BaseCar):
    def __init__(self, x, y, dmg, speed, dir, lifetime):
        BaseCar.__init__(self, 'projectile', x, y, 7, 7, 'blue', speed, 1, 0)
        self.dmg = dmg
        self.dir = dir.copy()
        self.lifetime = lifetime
        self.show_life_bar = False
        self.cant_hit = ['projectile', 'bomb', 'powerup', 'quicksand']
        s = Game.sounds.playFire()
        s.volume = 50

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0.0 or self.move(self.dir):
            self.hp = -1

    def collidedWith(self, ent):
        if isInArray(ent.type, self.cant_hit): 
            return
        self.hp = -1
        ent.hp -= self.dmg
        Game.sounds.playHit()        
        CreateExplosionAt(self, 20, 1, Game.animations['explosion%i'%(1+math.floor(random.random()*5))])
        if ent.type != 'player':
            #self means it is a projectile that hit something other than the player
            #meaning, player projectile hit enemy, or enemy shooting themselves, 
            #either way...
            self.point_value = 10
#end class Projectile

#*********** Bomb ************************
class Bomb(BaseCar):
    def __init__(self, x, y, speed):
        BaseCar.__init__(self, 'bomb', x, y, 30, 30, 'purple', speed, 1, 0)
        self.dmg = 100
        self.blast_radius = 140
        self.dir = Vector(0, 1)
        self.show_life_bar = False
        self.cant_hit = ['player', 'projectile', 'bomb', 'powerup', 'quicksand'] #bomb projectile doesnt hit
        self.cant_dmg = ['player', 'powerup'] #bomb area dmg does not apply
        self.considers_game_speed = True
        self.lifetime = 1.0
        
        self.countdown_text = GUIText("-", self.pos, GUIText.CENTER, sf.Color.RED, 20)
        self.countdown_text.txt.style = sf.Text.BOLD

    def draw(self, window):
        self.drawEntity(window)
        self.countdown_text.set_text( "%.1f" % (self.lifetime) )
        self.countdown_text.set_position(self.center())
        self.countdown_text.draw(window)

    def update(self, dt):
        self.lifetime -= dt
        if self.move(self.dir):
            self.hp = -1
        if self.lifetime <= 0:
            self.explode()

    def collidedWith(self, ent):
        if isInArray(ent.type, self.cant_hit): return
        self.point_value = 150
        self.explode()

    def explode(self):
        self.hp = -1
        CreateExplosionAt(self, self.blast_radius*2, 1, Game.animations.bomb_explosion)
        Game.sounds.playBombExplosion()
        for ent in Game.entities:
            if not isInArray(ent.type, self.cant_dmg):
                for off in [(0,0), (0,1), (1,0), (1,1)]:
                    #check against each entity corner point instead of just its center
                    pos = ent.pos + ent.size*off
                    dist = pos - self.center()
                    if dist.squaredLen() <= self.blast_radius**2:
                        if ent.type == 'bomb' and ent.hp > 0:
                            ent.explode()
                        ent.hp -= self.dmg
#end class Bomb

#*********** PowerUp ******************
class PowerUp(BaseCar):
    def __init__(self, x, y, action):
        BaseCar.__init__(self, 'powerup', x, y, 30, 30, 'green', 0.0, 1, 0)
        self.dir = Vector(0, 1)
        self.show_life_bar = False
        self.was_picked_up = False
        self.onPickup = action
        self.considers_game_speed = True

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

#*********** Rock ******************
class Rock(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'rock', x, y, 60, 60, 'black', 1, 1000, 5)
        self.dir = Vector(0, 1)
        self.show_life_bar = False
        self.considers_game_speed = True
        self.spr = sf.Sprite(Game.images['rock%i'%(round(random.random())) ])
        self.size.y = self.size.x * self.spr.texture.height / self.spr.texture.width
        self.should_explode = True

    def update(self, dt):
        if self.move(self.dir):
            self.hp = -1
            self.should_explode = False

    def collidedWith(self, ent):
        if ent.type == 'rock' or ent.type == 'quicksand':
            return
        if ent.type == 'projectile' or ent.type == 'powerup':
            ent.collidedWith(self)
            return
        ent.hp = -1 #K.O.!
        CreateVehicleCollision(self, ent)

    def onDeath(self):
        if self.should_explode:
            Game.CheckAndDropPowerUp(self.pos, 1)
            CreateVehicleExplosion(self)
#end class Rock

#*********** QuickSand ******************
class QuickSand(BaseCar):
    def __init__(self, x, y):
        BaseCar.__init__(self, 'quicksand', x, y, 40, 40, '#906000', 1, 1000, 5)
        self.dir = Vector(0, 1)
        self.show_life_bar = False
        self.considers_game_speed = True
        self.should_explode = True

    def update(self, dt):
        if self.move(self.dir):
            self.hp = -1
            self.should_explode = False

    def collidedWith(self, ent):
        if ent.type == 'rock' or ent.type == 'quicksand' or ent.type == 'projectile':
            return
        if not ent.stuck:
            ent.pos = ent.pos + self.dir*(self.speed()*0.8)
        ent.stuck = True

    def onDeath(self):
        if self.should_explode:
            Game.CheckAndDropPowerUp(self.pos, 1)
            Game.CheckAndDropPowerUp(self.pos, 1)
            CreateVehicleCollision(self, self)
#end class QuickSand

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
    Game.sounds.playVehicleExplosion()

def CreateVehicleCollision(ent1, ent2):
    #var pos = ent1.center().add(ent2.center().sub(ent1.center()).scale(0.5));
    pos = ent1.center() + (ent2.center()-ent1.center())*0.5
    size = (ent1.size.len()+ent2.size.len())/2
    CreateExplosion(pos, size, 1, Game.animations.vehicle_collision)
    Game.sounds.playCollision()

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

        
################################################################
class Game:
    fps = 30.0
    original_track_pos = Vector(100, 0)
    original_track_area = Vector(800, 700)
    
    try:
        with open("./highscores", 'rb') as fh:
            highscores = pickle.load(fh)
    except:
        highscores = [HighscoreEntry('-----', 0, 0.0) for i in xrange(10)]
    
    images = TextureManager()
    animations = AnimationManager(images)
    sounds = SoundManager()

    def __init__(self):
        self.music = sf.Music.from_file('sounds/music.ogg')
        self.scale_factor = Vector(1.0,1.0)
        def powerupFactory(x,y):
            return self.RandomizePowerUp(Vector(x,y), 1.0)
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
        def hpupAction():
            Game.player.hp += 150
            if Game.player.hp > Game.player.max_hp:
                Game.player.hp = Game.player.max_hp
        def bombupAction():
            Game.player.bombs += 1
        
        self.PowerUpTable = [PowerUpData('hpup', 0.65, self.images.hp_powerup, hpupAction), 
                             PowerUpData('bombup', 0.35, self.images.bomb_powerup, bombupAction)
        ]
        
    def initialize(self, window, font, cheatsEnabled):
        self.window = window
        self.font = font
        self.entities = []
        self.effects = []
        
        self.entCount = 0
        self.cont = True
        self.speed_level = 1.0
        self.points = 0.0
        self.track = sf.Sprite(self.images.track)
        self.track.texture_rectangle = sf.Rectangle((0, 2100), (self.original_track_area.x, self.original_track_area.y))
        self.delta_time = 1.0/self.fps
        self.actual_fps = self.fps
        self.music.play()
        self.music.loop = True
        
        self.paused = False
        self.cheats_enabled = cheatsEnabled
        self.cheated = False
        self.generate_entities = True
        
        self.updateGraphics()
        self.player_name = []
        self.player = Player(400*self.scale_factor.x, 400*self.scale_factor.y)
        self.entities.append(self.player)
        
        for gen in self.generators:
            gen.time_to_create = (gen.interval[1] - gen.interval[0])*random.random() + gen.interval[0]
        
        self.clock = sf.Clock()
        self.clock.restart()
        
    def initGraphics(self):
        self.track.ratio = self.scale_factor.toSFML()
        self.track.position = (self.track_pos).toSFML()
        
        barWidth = self.track_pos.x
        txtScale = self.scale_factor.x
        
        def createBar(x, w, color):
            bar = sf.RectangleShape((w, self.window.height))
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
            self.plaDataTxts.append(GUIText("-", (self.window.width, 45*txtScale + 40*(i)*txtScale), GUIText.HOR_RIGHT, sf.Color.WHITE, 18*txtScale))
        
        self.fixedHudText = []
        #text player keys: direita, right-align, branco *
        for i, s in enumerate(["Arrow keys", "D", "S", "Space"]):
            self.fixedHudText.append(GUIText(s, (self.window.width, (335+(i*18 + i*25))*txtScale), GUIText.HOR_RIGHT, sf.Color.WHITE, 18*txtScale))
        #text HSE points: esquerda, right-align, branco *
        hsY = 70*self.scale_factor.y
        for hse in Game.highscores:
            self.fixedHudText.append(GUIText("%i"%(hse.points), (barWidth-6, hsY), GUIText.HOR_RIGHT, sf.Color.WHITE, 18*self.scale_factor.y))
            hsY += 18*self.scale_factor.y
            mins = hse.level-1
            secs = mins*60 - int(mins)*60
            mins = int(mins)
            self.fixedHudText.append(GUIText("%im%is"%(mins,secs), (barWidth-6, hsY), GUIText.HOR_RIGHT, sf.Color.WHITE, 18*self.scale_factor.y))
            hsY += 45*self.scale_factor.y
        #text player data: direita, left_align, branco *
        self.fixedHudText.append(GUIText("Shots:\n\nBombs:\n\nSpeed:\n\nPoints", (self.window.width-barWidth+6,25*txtScale), GUIText.HOR_LEFT, hsCor, 18*txtScale))
        #text commands: direita, left_align, amarelado *
        self.fixedHudText.append(GUIText("Movement:\n\nFire:\n\nUse Bomb:\n\nPause:", (self.window.width-barWidth+6,315*txtScale), GUIText.HOR_LEFT, hsCor, 18*txtScale))
        #text points: esquerda, left-align, branco *
        #self.fixedHudText.append(GUIText("Points:", (0,25), GUIText.HOR_LEFT, hsCor, 18))
        #text highscore: esquerda, left-align, branco *
        self.fixedHudText.append(GUIText("Highscores:", (0,20*self.scale_factor.y), GUIText.HOR_LEFT, sf.Color.RED, 18*self.scale_factor.y))
        #text HSE names: esquerda, left-align, amarelado *
        hsNames = ""
        for i, hse in enumerate(Game.highscores):
            hsNames += str(i+1)+': '+hse.name + "\n\n\n"
        self.fixedHudText.append(GUIText(hsNames, (0, 50*self.scale_factor.y), GUIText.HOR_LEFT, hsCor, 18*self.scale_factor.y))

        self.pausedTxt = GUIText("PAUSED", (self.window.width/2, self.window.height/2), GUIText.CENTER, sf.Color.BLACK, 40*txtScale)
        self.pausedTxt.txt.style = sf.Text.BOLD
        self.pausedTxt.outline_color = sf.Color.RED
        
        self.gameOverTxt = GUIText("GAME OVER", (self.window.width/2, self.window.height/2), GUIText.CENTER, sf.Color.BLACK, 40*txtScale)
        self.gameOverTxt.txt.style = sf.Text.BOLD
        self.gameOverTxt.outline_color = sf.Color.RED
        
        restxt = "Type in highscore name (max 8 chars):\n\n\nPress ENTER to start a new game."
        self.restartTxt = GUIText(restxt, (self.window.width/2, self.window.height/2 + 40*txtScale), GUIText.HOR_CENTER, sf.Color.BLACK, 20*txtScale)
        self.restartTxt.txt.style = sf.Text.BOLD
        self.restartTxt.outline_color = sf.Color.RED
        
        self.plaNameTxt = GUIText("-", (self.window.width/2, self.window.height/2 + 70*txtScale), GUIText.HOR_CENTER, sf.Color.BLACK, 30*txtScale)
        self.plaNameTxt.txt.style = sf.Text.BOLD
        self.plaNameTxt.outline_color = sf.Color.RED
        
        self.targetDisplay = sf.RectangleShape()
        self.targetDisplay.fill_color = sf.Color.TRANSPARENT
        self.targetDisplay.outline_color = sf.Color.GREEN
        self.targetDisplay.outline_thickness = 2
        
    def updateGraphics(self):
        #to be executed when window changes size (ex.: change fullscreen status
        oldfactor = self.scale_factor
        self.scale_factor = Vector(self.window.width/1000.0, self.window.height/700.0)
        self.track_pos = self.original_track_pos * self.scale_factor
        self.track_area = self.original_track_area * self.scale_factor
        for ent in self.entities:
            ent.updateGraphics(oldfactor)
        for eff in self.effects:
            eff.updateGraphics(oldfactor)
        self.initGraphics()
        
    def getIDfor(self, ent):
        self.entCount += 1
        return self.entCount
    
    ####### DRAW
    def draw(self):
        self.window.draw(self.track)
        
        for bar in self.side_bars:
            self.window.draw(bar)
            
        #text point values: esquerda, right-align, branco
        #self.pointsTxt.set_text( "%i" % round(self.points) )
        #self.pointsTxt.draw(self.window)
        
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
            if self.player.target != None:
                tpos = self.player.target.pos - Vector(10,10)
                tsize = self.player.target.size + Vector(20,20)
                self.targetDisplay.position = tpos.toSFML()
                self.targetDisplay.size = tsize.toSFML()
                self.window.draw(self.targetDisplay)

    ####### UPDATE
    def update(self):
        ### debugging feature to run SUPER!HOT! (frame-per-frame)
        #if not self.cont: 
        #    return
        #self.cont = False

        elapsed = self.clock.restart()
        self.actual_fps = 1.0/elapsed.seconds
        
        dt = elapsed.seconds #1.0 / self.fps
        self.delta_time = dt
        
        self.sounds.update()
        
        if self.player.hp > 0 and not self.paused:
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
                                    factory = self.entityFactory[type]
                                    X = random.random()*self.track_area.x
                                    Y = -10
                                    if random.random() < 0.25 and isInArray(type, possibleBottomEntTypes):
                                        Y = self.track_area.y - 50
                                    self.entities.append(factory(X+self.track_pos.x, Y+self.track_pos.y))
                                    if type == 'warrig': #special case...
                                        self.entities[-1].createTurrets()
                                    #print "Generating entity "+type
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
            
            # update each effect
            for eff in list(self.effects):
                eff.update(dt)
                if eff.destroyed:
                    self.effects.remove(eff)
            
            # update game stats
            self.points += dt #+1 point per second
            self.speed_level += dt/60.0 #speed_level will increase by 1 each 60 secs
            
            #self.track_y -= self.speed_level + 5
            ty = self.track.texture_rectangle.top - (self.speed_level + 5)
            self.track.texture_rectangle = sf.Rectangle((0, ty), (self.original_track_area.x, self.original_track_area.y))
            if self.track.texture_rectangle.top <= -700:
                self.track.texture_rectangle = sf.Rectangle((0, 2100), (self.original_track_area.x, self.original_track_area.y))

    ####### INPUT
    def input(self, e):
        if not e.released:
            if self.player.hp <= 0: return
            if self.cheats_enabled:
                if e.code == sf.Keyboard.H:
                    self.player.hp = self.player.max_hp
                    self.cheated = True
                elif e.code == sf.Keyboard.B:
                    self.player.bombs += 1
                    self.cheated = True
            self.cont = True
            self.player.input(e)
        else:
            if self.player.hp <= 0:
                if e.code >= sf.Keyboard.A and e.code <= sf.Keyboard.Z and len(self.player_name) < 8: #A-Z
                    ic = 'A' if e.shift else 'a'
                    self.player_name.append( chr(ord(ic) + e.code) )
                elif e.code == sf.Keyboard.BACK_SPACE and len(self.player_name) > 0: #backspace
                    self.player_name.pop()
                elif e.code == sf.Keyboard.RETURN: #enter
                    if len(self.player_name) == 0:   
                        self.player_name = ['?']*5
                    hs_index = self.getHSindex()
                    if hs_index >= 0 and not self.cheated:
                        self.highscores.pop()
                        self.highscores.insert(hs_index, HighscoreEntry("".join(self.player_name), round(self.points), self.speed_level) )
                    self.initialize(self.window, self.font, self.cheats_enabled)
                    #save highscores
                    with open("./highscores", 'wb') as fh:
                        pickle.dump(self.highscores, fh)
            else:
                if self.cheats_enabled:
                    if e.code == sf.Keyboard.T:
                        self.entities.append( Berserker(200, 200) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.Y:
                        self.entities.append( Slinger(600, 200) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.U:
                        self.entities.append( WarRig(400, 160) )
                        self.entities[-1].createTurrets()
                        self.cheated = True
                    elif e.code == sf.Keyboard.I:
                        self.entities.append( Rock(random.random()*self.window.width, 0) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.O:
                        self.entities.append( QuickSand(random.random()*self.window.width, 0) )
                        self.cheated = True
                    elif e.code == sf.Keyboard.G:
                        self.generate_entities = not self.generate_entities
                        self.cheated = True
                if e.code == sf.Keyboard.SPACE:
                    #pause game
                    self.paused = not self.paused
                if not self.paused:
                    self.player.input(e)

    def getHSindex(self):
        hs_index = -1
        for i, hse in enumerate(self.highscores):
            if self.points > hse.points:
                hs_index = i
                break
        return hs_index

    def CheckAndDropPowerUp(self, pos, chanceToCreate):
        #print "checking for power dropping"
        pup = self.RandomizePowerUp(pos, chanceToCreate)
        if pup != None:
            self.entities.append(pup)

    def RandomizePowerUp(self, pos, chanceToCreate):
        #print "checking for power dropping"
        if random.random() <= chanceToCreate:
            itemIndex = random.random()
            cumulative = 0.0
            for pupdata in self.PowerUpTable:
                if itemIndex < pupdata.chance + cumulative:
                    pup = PowerUp(pos.x, pos.y, pupdata.action)
                    pup.spr = sf.Sprite(pupdata.image)
                    return pup
                cumulative += pupdata.chance
        return None
        
Game = Game()

################################################################

def executeGame(fullscreen, cheatsEnabled, vsync):
    windowtitle = "Mad Racer"
    if fullscreen:
        windowsize, _ = sf.VideoMode.get_desktop_mode()
        window = sf.RenderWindow(sf.VideoMode(*windowsize), windowtitle, sf.Style.FULLSCREEN)
    else:
        windowsize = (1000, 700)
        window = sf.RenderWindow(sf.VideoMode(*windowsize), windowtitle)
    
    try:
        font = sf.Font.from_file("arial.ttf")
    except IOError: 
        print "error"
        exit(1)
    
    Game.initialize(window, font, cheatsEnabled)
    
    icon = Game.images.player.to_image()
    window.icon = icon.pixels
    window.vertical_synchronization = vsync
    window.mouse_cursor_visible = False
    
    tfps = sf.Text("-", font, character_size=25)
    tfps.color = sf.Color.RED
    tfps.position = (window.width-250, window.height-60)
    showFps = True
    
    clock = sf.Clock()
    clock.restart()
    time_to_update = 0.0
    # start the game loop
    while window.is_open:
        # process events
        for event in window.events:
            # close window: exit
            if type(event) is sf.CloseEvent:
                window.close()
            if type(event) is sf.KeyEvent:
                if (event.code == sf.Keyboard.Q and event.control) or event.code == sf.Keyboard.ESCAPE:
                    window.close();
                elif event.code == sf.Keyboard.RETURN and event.control and event.released:
                    fullscreen = not fullscreen
                    if fullscreen:
                        windowsize, _ = sf.VideoMode.get_desktop_mode()
                        window.recreate(sf.VideoMode(*windowsize), windowtitle, sf.Style.FULLSCREEN)
                    else:
                        windowsize = (1000, 700)
                        window.recreate(sf.VideoMode(*windowsize), windowtitle)
                    Game.updateGraphics()
                    tfps.position = (window.width-250, window.height-60)
                elif event.code == sf.Keyboard.F and event.control and event.released:
                    showFps = not showFps
                else:
                    Game.input(event)
                
        window.clear() # clear screen

        elapsed = clock.restart()
        time_to_update += elapsed.seconds
        if time_to_update > 1.0/Game.fps:
            Game.update()
            time_to_update = 0.0

        Game.draw()
        
        if showFps:
            tfps.string = "WindowFPS: %.2f\nUpdateFPS: %.2f" % (1.0/elapsed.seconds, Game.actual_fps)
            window.draw(tfps)

        window.display() # update the window
                        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Python implementation of Mad Racer game.")
    parser.add_argument("--fullscreen", "-f", action="store_true", default=False, help="If the window should start fullscreen. self can be toggled during execution (default no)")
    parser.add_argument("--cheats", "-c", action="store_true", default=False, help="If cheats should be enabled.")
    parser.add_argument("--vsync", "-vs", action="store_true", default=False, help="If VSync should be enabled.")
    args = parser.parse_args()
    executeGame(args.fullscreen, args.cheats, args.vsync)