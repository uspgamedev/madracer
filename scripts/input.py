#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math
from game import Game
from utils import Vector, getEntClosestTo, raycastQuery, coneQuery

##########################################
# NOTES ABOUT INPUT
##########################################
#-While not particularly needed due to Python's duck typing, an input class should
# follow the base InputInterface class interface
#
#-The input class should process events or poll input on update to determine
# Game commands (as listed by InputInterface).
#
#-Game commands should then be passed along, there are 3 tiers of environment
# that receives commands:
#   -The Player: it polls target and move direction automatically, so there's no
#    need to pass those commands, and fire/bomb commands should be passed directly
#    to him.
#   -The Game: object that manages the game, and the input. Pause and ChangeInput
#    for example should be passed along to Game methods.
#   -The MainLoop: the loop controls the Game, and is not accessible from anywhere.
#    There are commands (like Toggle FPS/Fullscreen) that should be made available
#    to be read by the loop
#
#-The Game itself has its own KeyEvent handler to process cheats and text-input
# in the game over screen.
#########################################

class InputInterface:
    MOVE_LEFT = 0
    MOVE_RIGHT = 1
    MOVE_UP = 2
    MOVE_DOWN = 3
    FIRE = 4
    RELEASE_BOMB = 5
    SHOOT_BOMB = 6
    
    PAUSE = 7
    TOGGLE_FULLSCREEN = 8
    CHANGE_INPUT = 9
    CLOSE = 10
    TOGGLE_FPS_DISPLAY = 11
    
    def __init__(self, name):
        self.name = name
        self.loop_commands = []
        
    def drawPlayerTarget(self, window):
        # draw what is necessary to show the player target (where he'll shoot at)
        pass
    
    def command_list(self):
        # return input-specific command list: list of (command/key) pairs
        return []
        
    def target_dir(self):
        # how to get player target, given that it might change with input (autoaim, mouse target, etc)
        return None
        
    def move_dir(self):
        return Vector(0,0)
        
    def receiveInputEvent(self, e):
        pass
        
    def update(self, dt):
        pass
        
    def valid(self):
        # if this input method can be used. If not, Game will skip it when changing
        # inputs. Particularly needed for "optional" plug-and-play methods such as
        # gamepads.
        return True
        
class KeyboardInput(InputInterface):
    def __init__(self):
        InputInterface.__init__(self, 'Keyboard')
        self.target = None
        self.try_fire = False
        self.targetDisplay = sf.RectangleShape()
        self.targetDisplay.fill_color = sf.Color.TRANSPARENT
        self.targetDisplay.outline_color = sf.Color.GREEN
        self.targetDisplay.outline_thickness = 2
        
    def drawPlayerTarget(self, window):
        tpos = self.target.pos - Vector(10,10)
        tsize = self.target.size + Vector(20,20)
        self.targetDisplay.position = tpos.toSFML()
        self.targetDisplay.size = tsize.toSFML()
        window.draw(self.targetDisplay)
        
    def command_list(self):
        # return input-specific command list: list of (command/key) pairs
        return [("Movement", "Arrow keys"),
                ("Targeting", "Auto/Near"),
                ("Fire", "D"),
                ("Use Bomb", "S"),
                ("Shoot Bomb", "W"),
                ("Pause", "Space"),
                ("Fullscreen", "F1"),
                ("Input Mode", "F2"),
                ("Close", "CTRL+Q"),
                ("Show FPS", "CTRL+F")]
        
    def target_dir(self):
        # how to get player target, given that it might change with input (autoaim, mouse target, etc)
        dir = None
        if self.target != None:
            dir = self.target.center() - Game.player.center()
            dir.normalize()
        return dir
        
    def move_dir(self):
        #return self.desired_move
        dir = Vector(0,0)
        if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT): #left 
            dir.x = -1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT): #right
            dir.x = 1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP): #up
            dir.y = -1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN): #down
            dir.y = 1
        return dir
        
    def receiveInputEvent(self, e):
        if type(e) != sf.KeyEvent:  return
        isDown = not e.released
        if Game.player.hp > 0 and not Game.paused:
            if e.code == sf.Keyboard.S and not isDown:
                Game.player.release_bomb()
            elif e.code == sf.Keyboard.W and not isDown:
                Game.player.shoot_bomb()
            elif e.code == sf.Keyboard.D:
                #shoot back!
                self.try_fire = isDown
        else:
            pass
            
        if (e.code == sf.Keyboard.Q and e.control) or e.code == sf.Keyboard.ESCAPE:
            # CLOSE
            self.loop_commands.append(InputInterface.CLOSE)
        elif e.code == sf.Keyboard.F1 and e.released:
            # TOGGLE FULLSCREEN
            self.loop_commands.append(InputInterface.TOGGLE_FULLSCREEN)
        elif e.code == sf.Keyboard.F and e.control and e.released:
            # TOGGLE SHOW FPS
            self.loop_commands.append(InputInterface.TOGGLE_FPS_DISPLAY)
        elif e.code == sf.Keyboard.F2 and e.released:
            Game.changeInput()
        elif e.code == sf.Keyboard.SPACE and e.released:
            Game.pause()
            #Game.paused = True
        
    def update(self, dt):
        self.target = getEntClosestTo(Game.player.center())
                
        if self.target_dir() != None and self.try_fire:
            Game.player.fire()
            
########################################
        
class MouseKeyInput(InputInterface):
    def __init__(self):
        InputInterface.__init__(self, 'Mouse&Key')
        self.try_fire = False
        self.mouseDisplay = sf.CircleShape(15, 5)
        self.mouseDisplay.fill_color = sf.Color.TRANSPARENT
        self.mouseDisplay.outline_color = sf.Color.GREEN
        self.mouseDisplay.outline_thickness = 2
        bounds = self.mouseDisplay.local_bounds
        self.mouseDisplay.origin = bounds.width/2, bounds.height/2
        
        self.targetDisplay = sf.RectangleShape()
        self.targetDisplay.fill_color = sf.Color.TRANSPARENT
        self.targetDisplay.outline_color = sf.graphics.Color(0,210,0,255)
        self.targetDisplay.outline_thickness = 2
        
    def drawPlayerTarget(self, window):
        mouse = sf.Mouse.get_position(Game.window)
        target = getEntClosestTo(mouse)
        if target != None:
            tpos = target.pos - Vector(10,10)
            tsize = target.size + Vector(20,20)
            self.targetDisplay.position = tpos.toSFML()
            self.targetDisplay.size = tsize.toSFML()
            window.draw(self.targetDisplay)
    
        self.mouseDisplay.position = mouse
        window.draw(self.mouseDisplay)
        
    def command_list(self):
        # return input-specific command list: list of (command/key) pairs
        return [("Movement", "W/A/S/D"),
                ("Targeting", "Mouse"),
                ("Fire", "L-Mouse"),
                ("Use Bomb", "E"),
                ("Shoot Bomb", "R-Mouse"),
                ("Pause", "Space"),
                ("Fullscreen", "F1"),
                ("Input Mode", "F2"),
                ("Close", "CTRL+Q"),
                ("Show FPS", "CTRL+F")]
        
    def target_dir(self):
        # how to get player target, given that it might change with input (autoaim, mouse target, etc)
        mouse = sf.Mouse.get_position(Game.window)
        target = getEntClosestTo(mouse)
        dir = target.center() if target != None else Vector(mouse.x, mouse.y)
        dir = dir - Game.player.center()
        dir.normalize()
        return dir
        
    def move_dir(self):
        #return self.desired_move
        dir = Vector(0,0)
        if sf.Keyboard.is_key_pressed(sf.Keyboard.A): #left 
            dir.x = -1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.D): #right
            dir.x = 1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.W): #up
            dir.y = -1
        if sf.Keyboard.is_key_pressed(sf.Keyboard.S): #down
            dir.y = 1
        return dir
        
    def receiveInputEvent(self, e):
        if Game.player.hp > 0 and not Game.paused:
            if type(e) == sf.KeyEvent and e.code == sf.Keyboard.E and e.released:
                Game.player.release_bomb()
            elif type(e) == sf.MouseButtonEvent:
                if e.button == sf.Mouse.RIGHT and e.released: #mouse right
                    Game.player.shoot_bomb()
                elif e.button == sf.Mouse.LEFT: #mouse left
                    #shoot back!
                    self.try_fire = not e.released
            
        if type(e) == sf.KeyEvent:
            if (e.code == sf.Keyboard.Q and e.control) or e.code == sf.Keyboard.ESCAPE:
                # CLOSE
                self.loop_commands.append(InputInterface.CLOSE)
            elif e.code == sf.Keyboard.F1 and e.released:
                # TOGGLE FULLSCREEN
                self.loop_commands.append(InputInterface.TOGGLE_FULLSCREEN)
            elif e.code == sf.Keyboard.F and e.control and e.released:
                # TOGGLE SHOW FPS
                self.loop_commands.append(InputInterface.TOGGLE_FPS_DISPLAY)
            elif e.code == sf.Keyboard.F2 and e.released:
                Game.changeInput()
            elif e.code == sf.Keyboard.SPACE and e.released:
                Game.pause()
        
    def update(self, dt):
        if self.try_fire:
            Game.player.fire()

########################################
        
class GamePadInput(InputInterface):
    X = 0
    SQUARE = 1
    CIRCLE = 2
    TRIANGLE = 3
    LEFT_BUTTON = 4
    LEFT_TRIGGER = 5
    RIGHT_BUTTON = 6
    RIGHT_TRIGGER = 7
    SELECT = 8
    START = 9
    
    LEFT_HOR_AXIS = 0  # + is right
    LEFT_VER_AXIS = 1  # + is down
    RIGHT_HOR_AXIS = 3 # + is right
    RIGHT_VER_AXIS = 2 # + is down
    # POV HAT is considered as 2 axis, which give values either "at rest" (0) or "pressed" (maxValue-100)
    # strange that vertical direction is flipped in relation to the other axes
    HAT_HOR = 7 # + is right
    HAT_VER = 6 # + is up
    def __init__(self):
        InputInterface.__init__(self, 'GamePad')
        self.try_fire = False
        self.target = Vector(0,0)
        self.move = Vector(0,0)
        
        self.targetDirDisplay = sf.VertexArray(sf.PrimitiveType.LINES, 2*4)
        for i in xrange(2*4):
            self.targetDirDisplay[i].color = sf.Color.GREEN
        
        self.targetDisplay = sf.RectangleShape()
        self.targetDisplay.fill_color = sf.Color.TRANSPARENT
        self.targetDisplay.outline_color = sf.graphics.Color(0,210,0,255)
        self.targetDisplay.outline_thickness = 2
        
        self.text_index = 0
        self.textCursor = sf.RectangleShape()
        self.textCursor.fill_color = sf.Color.TRANSPARENT
        self.textCursor.outline_color = sf.Color.BLUE
        self.textCursor.outline_thickness = 2
        self.textCursor.size = 30*0.6, 1
        
    def updateTargetDir(self, dist):
        d = self.target
        d.normalize()
        arrowStart = Game.player.center() + d*10
        self.targetDirDisplay[0].position = arrowStart.toSFML()
        arrowBase = Game.player.center() + d*dist
        self.targetDirDisplay[1].position = arrowBase.toSFML()
        
        arrowLeft = arrowBase + d.perpendicular()*10
        arrowRight = arrowBase - d.perpendicular()*10
        self.targetDirDisplay[2].position = arrowLeft.toSFML()
        self.targetDirDisplay[3].position = arrowRight.toSFML()
        
        arrowTip = arrowBase + d*20
        self.targetDirDisplay[4].position = arrowTip.toSFML()
        self.targetDirDisplay[5].position = arrowLeft.toSFML()
        
        self.targetDirDisplay[6].position = arrowTip.toSFML()
        self.targetDirDisplay[7].position = arrowRight.toSFML()
        
    def drawPlayerTarget(self, window):
        target = None
        #dist = (Game.track_area*0.5 - Game.player.center()).len()
        dist = Game.player.center().len()
        dist = min(dist, Game.track_area.len()/2)
        #query = raycastQuery(Game.player.center(), self.target)
        query = coneQuery(Game.player.center(), self.target, math.pi/4)
        if len(query) > 0:
            dist, target = query[0]
    
        self.updateTargetDir(dist)
        window.draw(self.targetDirDisplay)
        if target != None:
            tpos = target.pos - Vector(10,10)
            tsize = target.size + Vector(20,20)
            self.targetDisplay.position = tpos.toSFML()
            self.targetDisplay.size = tsize.toSFML()
            window.draw(self.targetDisplay)
            
        if Game.player.hp <= 0 and Game.getHSindex() >= 0:
            tpos = Game.plaNameTxt.char_pos(self.text_index)
            self.textCursor.position = tpos.x, tpos.y + 30
            window.draw(self.textCursor)

    def command_list(self):
        # return input-specific command list: list of (command/key) pairs
        return [("Movement", "L-Stick"),
                ("Targeting", "R-Stick"),
                ("Fire", "R-Button"),
                ("Use Bomb", "X"),
                ("Shoot Bomb", "R-Trigger"),
                ("Pause", "O"),
                ("Fullscreen", "L-Button"),
                ("Input Mode", "Triangle"),
                ("Close", "START"),
                ("Show FPS", "L-Trigger")]
        
    def target_dir(self):
        # how to get player target, given that it might change with input (autoaim, mouse target, etc)
        target = None
        #query = raycastQuery(Game.player.center(), self.target)
        query = coneQuery(Game.player.center(), self.target, math.pi/4)
        if len(query) > 0:
            target = query[0].entity
        dir = (target.center() - Game.player.center() ) if target != None else self.target.copy()
        dir.normalize()
        return dir
        
    def move_dir(self):
        return self.move
        
    def receiveInputEvent(self, e):
        if Game.player.hp > 0 and not Game.paused:
            if type(e) == sf.JoystickButtonEvent:
                if e.button == GamePadInput.RIGHT_TRIGGER and e.released and (self.target.x != 0 or self.target.y != 0):
                    Game.player.shoot_bomb()
                elif e.button == GamePadInput.RIGHT_BUTTON:
                    self.try_fire = e.pressed
                elif e.button == GamePadInput.X and e.released:
                    Game.player.release_bomb()
            if type(e) == sf.JoystickMoveEvent:
                if e.axis == GamePadInput.LEFT_HOR_AXIS:
                    self.move.x = e.position/100 if abs(e.position) >= 1 else 0.0
                if e.axis == GamePadInput.LEFT_VER_AXIS:
                    self.move.y = e.position/100 if abs(e.position) >= 1 else 0.0
                if e.axis == GamePadInput.RIGHT_HOR_AXIS:
                    self.target.x = e.position/100 if abs(e.position) >= 1 else 0.0
                if e.axis == GamePadInput.RIGHT_VER_AXIS:
                    self.target.y = e.position/100 if abs(e.position) >= 1 else 0.0
        elif Game.player.hp <= 0:
            if type(e) == sf.JoystickButtonEvent:
                if e.button == GamePadInput.X and e.released:
                    Game.startNewGame()
                elif e.button == GamePadInput.CIRCLE and e.released:
                    Game.eraseCharFromPlayerName(self.text_index)
                    if self.text_index > len(Game.player_name):
                        self.text_index = len(Game.player_name)
            if type(e) == sf.JoystickMoveEvent and Game.getHSindex() >= 0:
                if e.axis == GamePadInput.LEFT_HOR_AXIS or e.axis == GamePadInput.HAT_HOR:
                    if abs(e.position) >= 1:
                        self.text_index += int(e.position / abs(e.position))
                        if self.text_index < 0:
                            self.text_index = 0
                        elif self.text_index > len(Game.player_name):
                            self.text_index = len(Game.player_name)
                if e.axis == GamePadInput.LEFT_VER_AXIS or e.axis == GamePadInput.HAT_VER:
                    if abs(e.position) >= 1:
                        chars = list("abcdefghijklmnopqrstuvwxyz0123456789!?.;:'<>@#$%^&*()-=_+[]{}\/|ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                        c = Game.getPlayerNameChar(self.text_index)
                        if c == '':
                            cindex = 0
                        else:
                            cindex = chars.index(c)
                        cindex = int(cindex + (e.position / abs(e.position)))
                        if cindex < 0:
                            cindex = len(chars) - 1
                        elif cindex >= len(chars):
                            cindex = 0
                        c = chars[cindex]
                        Game.changePlayerNameChar(self.text_index, c)

            
        if type(e) == sf.JoystickButtonEvent:
            if e.button == GamePadInput.START:
                # CLOSE
                self.loop_commands.append(InputInterface.CLOSE)
            elif e.button == GamePadInput.LEFT_BUTTON and e.released:
                # TOGGLE FULLSCREEN
                self.loop_commands.append(InputInterface.TOGGLE_FULLSCREEN)
            elif e.button == GamePadInput.LEFT_TRIGGER and e.released:
                # TOGGLE SHOW FPS
                self.loop_commands.append(InputInterface.TOGGLE_FPS_DISPLAY)
            elif e.button == GamePadInput.TRIANGLE and e.released:
                Game.changeInput()
            elif e.button == GamePadInput.CIRCLE and e.released:
                Game.pause()
                
        if type(e) == sf.JoystickConnectEvent and e.disconnected == True:
            Game.changeInput()
        
    def update(self, dt):
        if self.try_fire and (self.target.x != 0 or self.target.y != 0):
            Game.player.fire()
            
    def valid(self):
        return sf.Joystick.is_connected(0)
            
######################

available_inputs = [KeyboardInput, MouseKeyInput, GamePadInput]