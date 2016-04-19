#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from game import Game
from utils import Vector, GUIText, isInArray, Turret
from effects import CreateVehicleDustCloud, CreateVehicleCollision, CreateVehicleExplosion, CreateExplosionAt
import powerup

#******************************** ENTITIES ************************************
class BaseEntity:
    def __init__(self, type, x, y, w, h, color, speed, hp, points):
        self.type = type
        self.pos = Vector(x,y)
        self.size = Vector(w,h)
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
        
        self.shaders = [None]
        #if self.spr != None:
        #    self.shaders[0] = sf.Shader.from_file(fragment="scripts/outline.frag")
        #    self.shaders[0].set_currenttexturetype_parameter("texture")
        #    self.shaders[0].set_2float_parameter("stepSize", 5.0/self.spr.texture.width, 5.0/self.spr.texture.height)
        #    self.shaders[0].set_color_parameter("outlineColor", sf.Color.GREEN)

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
        for shade in self.shaders:
            window.draw(self.spr, sf.RenderStates(shader=shade))
        
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
        if center.y > pos.y + size.y:
            self.pos.y = pos.y + size.y - self.size.y/2
            moved = True
        #elif center.y < pos.y:
        #    self.pos.y = pos.y - self.size.y/2
        #    moved = True
        return moved

    def center(self):
        return self.pos + self.size*0.5 #self.pos.add(self.size.scale(0.5))

    def rect(self):
        return sf.Rectangle(self.pos.toSFML(), self.size.toSFML())
        
    def vertices(self):
        r = self.rect()
        vl = [ Vector(r.left,    r.top),
               Vector(r.right,    r.top),
               Vector(r.left, r.bottom),
               Vector(r.right, r.bottom)]
        return vl
        
    def onDeath(self):
        pass

    def speed(self):
        s = self.base_speed
        if self.considers_game_speed:
            s = s * (Game.speed_level + 5)
        return s * (1.0 - self.stuck*0.85) #0.85 is % of speed lost while stuck

    def move(self, dir):
        self.last_moved_dir = dir.copy()
        self.pos = self.pos + dir*self.speed()
        return self.limitInRect(Game.track_pos, Game.track_area)
#end class BaseCar

#************* Player ****************
class Player(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'player', x, y, 32, 60, sf.Color.GREEN, 4, 150, 0)
        self.bombs = 3
        self.max_shots = 25
        self.shots_available = self.max_shots
        self.shot_reload_time = 0.2
        self.cooldown_time = 0.1
        self.cooldown_elapsed = self.cooldown_time
        self.reload_elapsed = 0.0
        self.shot_dmg = 20
        self.shot_speed = 15
        self.points = 0
        self.turret = Turret(self)
        
    def draw(self, window):
        BaseEntity.drawEntity(self, window)
        BaseEntity.drawHPBar(self, window)
        dir = Game.input.target_dir()
        self.turret.draw(window, dir)

    def update(self, dt):
        moveDelta = Game.input.move_dir().copy()
        self.move(moveDelta)
        CreateVehicleDustCloud(self)
        
        if self.shots_available < self.max_shots:
            self.reload_elapsed += dt
            if self.reload_elapsed > self.shot_reload_time:
                self.reload_elapsed = 0.0
                self.shots_available += 1
        
        self.cooldown_elapsed += dt

    def fire(self):
        if self.cooldown_elapsed >= self.cooldown_time and self.shots_available > 0:
            dir = Game.input.target_dir()
            init_pos = self.center()
            projectile = Projectile(init_pos.x, init_pos.y, self.shot_dmg, self.shot_speed, dir, 2, sf.Color.GREEN)
            projectile.cant_hit.append(self.type)
            Game.entities.append(projectile)
            self.shots_available -= 1
            self.reload_elapsed = 0.0
            self.cooldown_elapsed = 0.0
            
    def release_bomb(self):
        if self.bombs > 0:
            #release bomb
            self.bombs -= 1
            bomb = Bomb(self.pos.x, self.pos.y, Vector(0,1), 1, 120, 200)
            Game.entities.append(bomb)
    def shoot_bomb(self):
        if self.bombs > 0 and Game.input.target_dir() != None:
            #shoot bomb
            self.bombs -= 1
            dir = Game.input.target_dir()
            bomb = Bomb(self.pos.x, self.pos.y, dir, 2, 90, 120)
            Game.entities.append(bomb)

    def collidedWith(self, ent):
        ent.collidedWith(self)

    def onDeath(self):
        CreateVehicleExplosion(self)
#end class Player

#*********** Berserker ******************
class Berserker(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'berserker', x, y, 32, 60, 'red', 3.5, 25, 200)
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
        powerup.CheckAndDropPowerUp(self.pos, 0.10)
        CreateVehicleExplosion(self)
#end class Berserker

#*********** Slinger ********************
class Slinger(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'slinger', x, y, 32, 60, 'purple', 2, 25, 200)
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
            projectile = Projectile(init_pos.x, init_pos.y, 6, 15, dir, 2, sf.graphics.Color(255,180,180,255) )
            projectile.cant_hit.append(self.type)
            Game.entities.append(projectile)
            self.cooldown = 0.0

    def draw(self, window):
        BaseEntity.drawEntity(self, window)
        BaseEntity.drawHPBar(self, window)
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
        powerup.CheckAndDropPowerUp(self.pos, 0.15)
        CreateVehicleExplosion(self)
#end class Slinger

#*********** WarRig *********************
class WarRig(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'warrig', x, y, 40, 160, 'yellow', 1, 300, 1000)
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
            projectile = Projectile(init_pos.x, init_pos.y, 10, 15, dir, 2, sf.Color.RED )
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
        powerup.CheckAndDropPowerUp(self.pos, 1.0)
        CreateVehicleExplosion(self)
#end class WarRig

#*********** RigTurret ******************
class RigTurret(BaseEntity):
    def __init__(self, rig, relative_yoffset):
        self.relative_yoffset = relative_yoffset
        self.yoffset = self.relative_yoffset * rig.size.y
        BaseEntity.__init__(self, 'rigturret', rig.pos.x, rig.pos.y+self.yoffset, 40, 40, '#808000', 0, 40, 100)
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
            projectile = Projectile(init_pos.x, init_pos.y, 5, 15, dir, 2, sf.graphics.Color(255,240,240,255))
            projectile.color = '#000080'
            projectile.cant_hit.append(self.type)
            projectile.cant_hit.append('warrig')
            Game.entities.append(projectile)
            self.cooldown = 0.0
 
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
        powerup.CheckAndDropPowerUp(self.pos, 0.15)
        CreateVehicleExplosion(self)
#end class RigTurret

#/*********** Projectile *****************
class Projectile(BaseEntity):
    def __init__(self, x, y, dmg, speed, dir, lifetime, color):
        BaseEntity.__init__(self, 'projectile', x, y, 7, 7, 'blue', speed, 1, 0)
        self.pos = self.pos - self.size*0.5
        self.dmg = dmg
        self.dir = dir.copy()
        self.lifetime = lifetime
        self.spr.color = color
        self.show_life_bar = False
        self.cant_hit = ['projectile', 'bomb', 'powerup', 'quicksand']
        s = Game.sounds.playFire(self.center())

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0.0 or self.move(self.dir):
            self.hp = -1

    def collidedWith(self, ent):
        if isInArray(ent.type, self.cant_hit): 
            return
        self.hp = -1
        ent.hp -= self.dmg
        Game.sounds.playHit(self.center())        
        CreateExplosionAt(self, 20, 1, Game.animations['explosion%i'%(1+math.floor(random.random()*5))])
        if ent.type != 'player':
            #self means it is a projectile that hit something other than the player
            #meaning, player projectile hit enemy, or enemy shooting themselves, 
            #either way...
            self.point_value = 10
#end class Projectile

#*********** Bomb ************************
class Bomb(BaseEntity):
    def __init__(self, x, y, dir, speed, dmg, radius):
        BaseEntity.__init__(self, 'bomb', x, y, 30, 30, 'purple', speed, 1, 0)
        self.dmg = dmg
        self.blast_radius = radius
        self.dir = dir
        self.show_life_bar = False
        self.cant_hit = ['player', 'projectile', 'powerup', 'quicksand'] #bomb projectile doesnt hit
        self.cant_dmg = ['player', 'powerup'] #bomb area dmg does not apply
        self.considers_game_speed = True
        self.lifetime = 1.0
        
        self.countdown_text = GUIText("-", self.pos, GUIText.CENTER, sf.Color.RED, 20)
        self.countdown_text.txt.style = sf.Text.BOLD

    def draw(self, window):
        self.drawEntity(window)
        self.countdown_text.set_text( "%.1f" % (self.lifetime) )
        self.countdown_text.position = self.center()
        window.draw(self.countdown_text)

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
        if self.hp <= 0:    return
        self.hp = -1
        CreateExplosionAt(self, self.blast_radius*2, 1, Game.animations.bomb_explosion)
        Game.sounds.playBombExplosion(self.center())
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

#*********** Rock ******************
class Rock(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'rock', x, y, 60, 60, 'black', 1, 1000, 5)
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
        if ent.type == 'projectile' or ent.type == 'powerup' or ent.type == 'bomb':
            ent.collidedWith(self)
            return
        ent.hp = -1 #K.O.!
        CreateVehicleCollision(self, ent)

    def onDeath(self):
        if self.should_explode:
            powerup.CheckAndDropPowerUp(self.pos, 1)
            CreateVehicleExplosion(self)
#end class Rock

#*********** QuickSand ******************
class QuickSand(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'quicksand', x, y, 40, 40, '#906000', 1, 1000, 5)
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
            powerup.CheckAndDropPowerUp(self.pos, 1)
            powerup.CheckAndDropPowerUp(self.pos, 1)
            CreateVehicleCollision(self, self)
#end class QuickSand

#*********** Dummy Entity: used as a static target in the map to test stuff ******************
class Dummy(BaseEntity):
    def __init__(self, x, y):
        BaseEntity.__init__(self, 'dummy', x, y, 60, 60, 'black', 0, 1000, 5)
        self.spr = sf.Sprite(Game.images.rock0)

    def update(self, dt):
        pass

    def collidedWith(self, ent):
        if ent.type == 'projectile' or ent.type == 'powerup' or ent.type == 'bomb':
            ent.collidedWith(self)
            return

    def onDeath(self):
        CreateVehicleExplosion(self)
        powerup.CheckAndDropPowerUp(self.pos, 1)
