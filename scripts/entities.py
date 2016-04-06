#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from game import Game
from utils import Vector, GUIText, isInArray, Turret
from effects import CreateVehicleDustCloud, CreateVehicleCollision, CreateVehicleExplosion, CreateExplosionAt
import powerup

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
            projectile = Projectile(init_pos.x, init_pos.y, self.shot_dmg, self.shot_speed, dir, 2, sf.Color.GREEN)
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
        powerup.CheckAndDropPowerUp(self.pos, 0.10)
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
            projectile = Projectile(init_pos.x, init_pos.y, 6, 15, dir, 2, sf.graphics.Color(255,180,180,255) )
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
        powerup.CheckAndDropPowerUp(self.pos, 0.15)
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
            projectile = Projectile(init_pos.x, init_pos.y, 5, 15, dir, 2, sf.graphics.Color(255,240,240,255))
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
        powerup.CheckAndDropPowerUp(self.pos, 0.15)
        CreateVehicleExplosion(self)
#end class RigTurret

#/*********** Projectile *****************
class Projectile(BaseCar):
    def __init__(self, x, y, dmg, speed, dir, lifetime, color):
        BaseCar.__init__(self, 'projectile', x, y, 7, 7, 'blue', speed, 1, 0)
        self.dmg = dmg
        self.dir = dir.copy()
        self.lifetime = lifetime
        self.spr.color = color
        self.show_life_bar = False
        self.cant_hit = ['projectile', 'bomb', 'powerup', 'quicksand']
        s = Game.sounds.playFire(self.center())
        #s.volume = 50

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
            powerup.CheckAndDropPowerUp(self.pos, 1)
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
            powerup.CheckAndDropPowerUp(self.pos, 1)
            powerup.CheckAndDropPowerUp(self.pos, 1)
            CreateVehicleCollision(self, self)
#end class QuickSand