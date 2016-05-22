#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
import random, math, pickle
from game import Game
from utils import Vector, getEntClosestTo, raycastQuery, coneQuery, ConeQueryType, GUIText

class InputManager(object):
    def __init__(self):
        try:
            with open("./input_presets", 'rb') as fh:
                self.presets = pickle.load(fh)
        except:
            self.presets = {}
        self.preset_queue = self.presets.keys()
        self.preset_queue.sort()
        sf.Joystick.update()
        self.joyid_queue = self.ConnectedJoystickIDs()
        
    def AddPreset(self, preset):
        if self.HasPreset(preset.name) or len(preset.valid()) > 0: return
        self.presets[preset.name] = preset
        self.preset_queue.append(preset.name)
        self.SavePresets()
    
    def DeletePreset(self, preset_name):
        if self.HasPreset(preset_name):
            del self.preset[preset_name]
    
    def HasPreset(self, preset_name):
        return preset_name in self.presets
        
    def SavePresets(self):
        with open("./input_presets", 'wb') as fh:
            pickle.dump(self.presets, fh)
            
    def PresetList(self):
        keys = self.presets.keys()
        keys.sort()
        return keys
        
    def PopPreset(self):
        if len(self.preset_queue) <= 0: return None
        return self.presets[self.preset_queue.pop(0)]
    def PushPreset(self, preset_name):
        if not preset_name in self.presets or preset_name in self.preset_queue: 
            return
        self.preset_queue.append(preset_name)
        
    def ConnectedJoystickIDs(self):
        return [id for id in xrange(sf.Joystick.COUNT) if sf.Joystick.is_connected(id)]
        
    def PopJoyID(self):
        if len(self.joyid_queue) <= 0: return None
        return self.joyid_queue.pop(0)
    def PushJoyID(self, id):
        if not id in self.ConnectedJoystickIDs() or id in self.joyid_queue: 
            return
        self.joyid_queue.append(id)
    
    def processEvent(self, e):
        if type(e) == sf.JoystickConnectEvent:
            id_in_queue = e.joystick_id in self.joyid_queue
            if e.connected and not id_in_queue:
                self.joyid_queue.append(e.joystick_id)
            elif e.disconnected and id_in_queue:
                self.joyid_queue.remove(e.joystick_id)
                
class Binding(object):
    DEVICE_MOUSE_KEYBOARD = 0
    DEVICE_JOYSTICK = 1
    event_attrs = {
        sf.KeyEvent: ['code', 'control', 'shift', 'alt', 'system'],
        sf.MouseWheelEvent: ['delta'],
        sf.MouseButtonEvent: ['button'],
        sf.JoystickMoveEvent: ['axis', 'position'],
        sf.JoystickButtonEvent: ['button']
    }
    @staticmethod
    def isBindableEvent(e):
        # check type
        if not type(e) in Binding.event_attrs:  return False
        # check status
        if type(e) == sf.KeyEvent:
            return e.released
        elif type(e) == sf.MouseWheelEvent:
            return e.delta != 0
        elif type(e) == sf.MouseButtonEvent:
            return e.released
        elif type(e) == sf.JoystickMoveEvent:
            return abs(e.position) >= 1
        elif type(e) == sf.JoystickButtonEvent:
            return e.released
        return False
        
    #-----
    def __init__(self, e):
        self.type = type(e)
        if not self.type in Binding.event_attrs:
            print "Unrecognized input event to binding!"
            return
        self.attrs = dict( [(k, getattr(e, k)) for k in Binding.event_attrs[self.type]] )
        
    def checkEvent(self, e):
        if type(e) == self.type:
            for k in Binding.event_attrs[self.type]:
                eventAttrValue = getattr(e, k)
                selfAttrValue = self.attrs[k]
                if self.type == sf.MouseWheelEvent or (self.type == sf.JoystickMoveEvent and k == 'position'): #special cases that must check direction instead of value
                    eventAttrValue /= abs(eventAttrValue)
                    selfAttrValue /= abs(selfAttrValue)
                if eventAttrValue != selfAttrValue:
                    return False #type ok, but a attr value is different
                return Binding.isBindableEvent(e) #type and attr values OK
        return False #type mismatch
        
    def value(self, id):
        v = None
        if self.type == sf.KeyEvent:
            key = sf.Keyboard.is_key_pressed(self.attrs['code'])
            if self.attrs['control']:
                key = key and (sf.Keyboard.is_key_pressed(sf.Keyboard.L_CONTROL) or sf.Keyboard.is_key_pressed(sf.Keyboard.R_CONTROL))
            if self.attrs['shift']:
                key = key and (sf.Keyboard.is_key_pressed(sf.Keyboard.L_SHIFT) or sf.Keyboard.is_key_pressed(sf.Keyboard.R_SHIFT))
            if self.attrs['alt']:
                key = key and (sf.Keyboard.is_key_pressed(sf.Keyboard.L_ALT) or sf.Keyboard.is_key_pressed(sf.Keyboard.R_ALT))
            if self.attrs['system']:
                key = key and (sf.Keyboard.is_key_pressed(sf.Keyboard.L_SYSTEM) or sf.Keyboard.is_key_pressed(sf.Keyboard.R_SYSTEM))
            v = int(key)
        elif self.type == sf.MouseWheelEvent:
            v = 0 #wheel has no value getter
        elif self.type == sf.MouseButtonEvent:
            v = int(sf.Mouse.is_button_pressed(self.attrs['button']))
        elif self.type == sf.JoystickMoveEvent and sf.Joystick.is_connected(id) and sf.Joystick.has_axis(id, self.attrs['axis']):
            ax_pos = sf.Joystick.get_axis_position(id, self.attrs['axis'])
            if (ax_pos * self.attrs['position']) > 0: #axis values have same sign (same position direction)
                v = abs(ax_pos)/100 if abs(ax_pos) >= 1 else 0.0
            else:
                v = 0.0
        elif self.type == sf.JoystickButtonEvent and sf.Joystick.is_connected(id) and sf.Joystick.get_button_count(id) >= self.attrs['button']:
            v = int(sf.Joystick.is_button_pressed(id, self.attrs['button']))
        return v
    
    def __str__(self):
        def getSignStr(v):
            if v >= 0:  return '+'
            return '-'
            
        if self.type == sf.KeyEvent:
            code_to_name = dict( [(v,k) for k,v in sf.Keyboard.__dict__.items()] )
            s = ""
            if self.attrs['system']:
                s += "SYSTEM+"
            if self.attrs['control']:
                s += "CTRL+"
            if self.attrs['shift']:
                s += "SHIFT+"
            if self.attrs['alt']:
                s += "ALT+"
            s += code_to_name[self.attrs['code']]
            return s
        elif self.type == sf.MouseWheelEvent:
            return "M-Wheel (%s)" % (getSignStr(self.attrs['delta']))
        elif self.type == sf.MouseButtonEvent:
            code_to_name = dict( [(v,k) for k,v in sf.Mouse.__dict__.items()] )
            buttcode = self.attrs['button']
            if buttcode in code_to_name:
                return "M-"+code_to_name[buttcode]
            return "M-Button "+str(buttcode)
        elif self.type == sf.JoystickMoveEvent:
            return "AXIS %s (%s)" % (self.attrs['axis'], getSignStr(self.attrs['position']))
        elif self.type == sf.JoystickButtonEvent:
            return "Button "+str(self.attrs['button'])
        return "<UNRECOGNIZED>"
    
    def device_type(self):
        if self.type in [sf.JoystickMoveEvent, sf.JoystickButtonEvent]:
            return Binding.DEVICE_JOYSTICK
        return Binding.DEVICE_MOUSE_KEYBOARD
        
    def is_axis(self):
        if self.type in [sf.MouseWheelEvent, sf.JoystickMoveEvent]:
            return True
        return False
        
    def get_opposite_axis_binding(self):
        if self.type == sf.MouseWheelEvent:
            opEvent = sf.MouseWheelEvent()
            opEvent.delta = -self.attrs['delta']
            return Binding(opEvent)
        elif self.type == sf.JoystickMoveEvent:
            opEvent = sf.JoystickMoveEvent()
            opEvent.axis = self.attrs['axis']
            opEvent.position = -self.attrs['position']
            return Binding(opEvent)
        return None
        
class Preset:
    def __init__(self):
        self.bindings = {
            InputMethod.MOVE_LEFT: None,
            InputMethod.MOVE_RIGHT: None,
            InputMethod.MOVE_UP: None,
            InputMethod.MOVE_DOWN: None,
            InputMethod.FIRE: None,
            InputMethod.RELEASE_BOMB: None,
            InputMethod.SHOOT_BOMB: None,
            InputMethod.PAUSE: None,
            InputMethod.TOGGLE_FULLSCREEN: None,
            InputMethod.CHANGE_INPUT: None,
            InputMethod.CLOSE: None,
            InputMethod.TOGGLE_FPS_DISPLAY: None
        }
        self.targeting_type = 0
        self.targeting_bindings = {
            'up': None,
            'down': None,
            'left': None,
            'right': None
        }
        self.name = ""
        
    def conflictsWith(self, preset):
        if self.name == preset.name:    return True
        if self.targeting_type == InputMethod.POINT_TARGETING and self.targeting_type == preset.targeting_type:
            return True
        mybinds = self.all_bindings
        otherbinds = preset.all_bindings
        for b in mybinds:
            for ob in otherbinds:
                if str(b) == str(ob):
                    return True
        return False
        
    @property
    def all_bindings(self):
        allBindings = self.bindings.values() 
        if self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
            allBindings += self.targeting_bindings.values()
        return allBindings
        
    def valid(self):
        if len(self.name) <= 0: return "Name cannot be empty"
        allBindings = self.all_bindings
            
        dev_type = None
        for bind in allBindings:
            if bind == None:
                return "Undefined binding"
            if dev_type == None:
                dev_type = bind.device_type()
            if dev_type != bind.device_type():
                return "Mixing Keyboard&Mouse/Joystick input"
            for bind2 in allBindings:
                if bind != bind2 and str(bind) == str(bind2):
                    return "Repeated bindings"
        return ""
            
    def can_add_binding(self, b):
        allBindings = self.all_bindings
        for bind in allBindings:
            if str(bind) == str(b):
                return False
        return True
        
    def device_type(self):
        return self.bindings.values()[0].device_type()
        
class InputMethod(sf.Drawable):
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
    
    AUTO_TARGETING = 0
    POINT_TARGETING = 1
    DIRECTIONAL_TARGETING = 2
    
    def __init__(self, player, preset, id):
        sf.Drawable.__init__(self)
        self.name = preset.name
        self.player = player
        self.texts = []
        self.graphics_params = ()
        self.id = id
        self.bindings = preset.bindings
        self.targeting_type = preset.targeting_type
        self.targeting_bindings = preset.targeting_bindings
        self.target = None
        self.try_fire = False
        
        self.targetDisplay = sf.RectangleShape()
        self.targetDisplay.fill_color = sf.Color.TRANSPARENT
        self.targetDisplay.outline_color = self.player.color#sf.graphics.Color(0,210,0,255)
        self.targetDisplay.outline_thickness = 2
        
        if self.targeting_type == InputMethod.POINT_TARGETING:
            self.mouseDisplay = sf.CircleShape(15, 5)
            self.mouseDisplay.fill_color = sf.Color.TRANSPARENT
            self.mouseDisplay.outline_color = self.player.color
            self.mouseDisplay.outline_thickness = 2
            bounds = self.mouseDisplay.local_bounds
            self.mouseDisplay.origin = bounds.width/2, bounds.height/2
        elif self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
            self.targetDirDisplay = sf.VertexArray(sf.PrimitiveType.LINES, 2*4)
            for i in xrange(2*4):
                self.targetDirDisplay[i].color = self.player.color
        
    def move_dir(self):
        dir = Vector(0,0)
        if not self.valid():    return dir
        dir.x = -self.action_value(InputMethod.MOVE_LEFT)
        if dir.x == 0:
            dir.x = self.action_value(InputMethod.MOVE_RIGHT)
        dir.y = -self.action_value(InputMethod.MOVE_UP)
        if dir.y == 0:
            dir.y = self.action_value(InputMethod.MOVE_DOWN)
        if dir.squaredLen() > 1:
            dir.normalize()
        return dir
        
    def processInput(self, e):
        if self.device_type() == Binding.DEVICE_JOYSTICK and type(e) == sf.JoystickConnectEvent:
            if self.graphics_enabled():
                self.updateGraphics(*self.graphics_params)
            
    
        if not self.valid():    return
        cmd = self.processBindings(e)
        if cmd == None: return
        
        if self.player.hp > 0 and not self.player.paused:
            if cmd == InputMethod.RELEASE_BOMB:
                self.player.release_bomb()
            elif cmd == InputMethod.SHOOT_BOMB:
                self.player.shoot_bomb()
            
        if cmd in [InputMethod.CLOSE, InputMethod.TOGGLE_FULLSCREEN, InputMethod.TOGGLE_FPS_DISPLAY, InputMethod.PAUSE]:
            Game.loop_commands[cmd] = self.player
        elif cmd == InputMethod.CHANGE_INPUT:
            self.player.changeInput()
        
    def update(self, dt):
        if not self.valid():
            if not self.player.paused:
                Game.loop_commands[InputMethod.PAUSE] = self.player
            return
        self.target = self.update_target()
        target_dir = self.target_dir()
        self.try_fire = self.action_value(InputMethod.FIRE)
        if self.try_fire and target_dir != None and (target_dir.x != 0.0 or target_dir.y != 0.0):
            self.player.fire()

    def target_dir(self):
        # how to get player target, given that it might change with input (autoaim, mouse target, etc)
        if not self.valid():    return None
        dir = (self.target.center() - self.player.center() ) if self.target != None else self.targeting_dir()
        if dir != None:
            dir.normalize()
        return dir
        
    def valid(self):
        # if this input method can be used. If not, Game will skip it when changing
        # inputs. Particularly needed for "optional" plug-and-play methods such as
        # gamepads.
        if self.id != None:
            return sf.Joystick.is_connected(self.id)
        return True
       
    def graphics_enabled(self):
        return len(self.texts) > 0
    def disableGraphics(self):
        self.texts = []
        self.graphics_params = ()
    def updateGraphics(self, bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness):
        self.graphics_params = (bounds, show_values_below, title_color, names_color, values_color, background_color, background_border_thickness)
        self.texts = []
        rect = sf.RectangleShape(bounds.size)
        rect.position = bounds.position
        rect.fill_color = background_color
        rect.outline_thickness = background_border_thickness
        rect.outline_color = title_color
        self.texts.append(rect)
        #text commands: direita, left_align, amarelado *
        #text player keys: direita, right-align, branco *
        self.texts.append(GUIText(self.name, (bounds.left+bounds.width/2, bounds.top+2), GUIText.HOR_CENTER, title_color, 20))
        ckY = self.texts[-1].bounds.bottom + 7
        
        if self.valid():
            cmdNames = {
                InputMethod.MOVE_LEFT: 'Move Left',
                InputMethod.MOVE_RIGHT: 'Move Right',
                InputMethod.MOVE_UP: 'Move Up',
                InputMethod.MOVE_DOWN: 'Move Down',
                InputMethod.FIRE: 'Fire',
                InputMethod.SHOOT_BOMB: 'Shoot Bomb',
                InputMethod.RELEASE_BOMB: 'Release Bomb',
                InputMethod.PAUSE: 'Pause',
                InputMethod.TOGGLE_FULLSCREEN: 'Fullscreen',
                InputMethod.CHANGE_INPUT: 'Change Input',
                InputMethod.CLOSE: 'Close',
                InputMethod.TOGGLE_FPS_DISPLAY: 'FPS Display',
            }
            txtData = [(cmdNames[cmd], str(bind)) for cmd, bind in self.bindings.items()]
            target_types = {
                InputMethod.AUTO_TARGETING:   "Auto",
                InputMethod.POINT_TARGETING:   "Mouse",
                InputMethod.DIRECTIONAL_TARGETING:   "Directional"
            }
            txtData.append( ("Targeting", target_types[self.targeting_type]) )
            if self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
                txtData += [("Target " + cmd[0].upper() + cmd[1:], str(bind)) for cmd, bind in self.targeting_bindings.items()]
            
            for cmd, value in txtData:
                self.texts.append(GUIText(cmd, (bounds.left+2, ckY), GUIText.HOR_LEFT, names_color, 18))
                if show_values_below:
                    ckY += 18
                self.texts.append(GUIText(value, (bounds.right-2, ckY), GUIText.HOR_RIGHT, values_color, 18))
                ckY += 24
                if not show_values_below:
                    ckY += 3
        else:
            ckY += 10
            self.texts.append(GUIText("INVALID METHOD", (bounds.left+bounds.width/2, ckY), GUIText.HOR_CENTER, names_color, 18))
            ckY += 32
            self.texts.append(GUIText("Joystick Disconnected", (bounds.left+bounds.width/2, ckY), GUIText.HOR_CENTER, values_color, 18))
            
    def drawPlayerTarget(self, window, states):
        if self.target == None: return
        tpos = self.target.pos - Vector(10,10)
        tsize = self.target.size + Vector(20,20)
        self.targetDisplay.position = tpos.toSFML()
        self.targetDisplay.size = tsize.toSFML()
        window.draw(self.targetDisplay, states)
    
    def drawTargeting(self, window, states):
        if self.targeting_type == InputMethod.POINT_TARGETING:
            mouse = sf.Mouse.get_position(Game.window)
            self.mouseDisplay.position = mouse
            window.draw(self.mouseDisplay, states)
        elif self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
            d = self.targeting_dir()
            d.normalize()
            dist = 100
            if self.target != None:
                dist = self.target.center() - self.player.center()
                dist = dist.len()
            arrowStart = self.player.center() + d*10
            self.targetDirDisplay[0].position = arrowStart.toSFML()
            arrowBase = self.player.center() + d*dist
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
            window.draw(self.targetDirDisplay)
    
    def draw(self, target, states):
        if self.valid():
            if self.target_dir() != None:
                self.drawPlayerTarget(target, states)
            self.drawTargeting(target, states)
        for text in self.texts:
            target.draw(text, states)
      
    def processBindings(self, e):
        for cmd, binding in self.bindings.items():
            if binding.checkEvent(e):
                return cmd
        return None
        
    def action_value(self, cmd):
        return self.bindings[cmd].value(self.id)
    
    def targeting_dir(self):
        if self.targeting_type == InputMethod.AUTO_TARGETING:
            return None
        elif self.targeting_type == InputMethod.POINT_TARGETING:
            mouse = sf.Mouse.get_position(Game.window)
            dir = Vector(mouse.x, mouse.y) - self.player.center()
            dir.normalize()
            return dir
        elif self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
            dir = Vector(0.0, 0.0)
            dir.x += self.targeting_bindings['right'].value(self.id)
            dir.x -= self.targeting_bindings['left'].value(self.id)
            dir.y += self.targeting_bindings['down'].value(self.id)
            dir.y -= self.targeting_bindings['up'].value(self.id)
            dir.normalize()
            return dir
        return None
        
    def update_target(self):
        if self.targeting_type == InputMethod.AUTO_TARGETING:
            return getEntClosestTo(self.player.center())
        elif self.targeting_type == InputMethod.POINT_TARGETING:
            mouse = sf.Mouse.get_position(Game.window)
            return getEntClosestTo(mouse)
        elif self.targeting_type == InputMethod.DIRECTIONAL_TARGETING:
            query = coneQuery(self.player.center(), self.targeting_dir(), math.pi/4, ConeQueryType.ANGLE_TO_DIR)
            if len(query) > 0:
                return query[0].entity
        return None
            
    def device_type(self):
        return self.bindings.values()[0].device_type()
        
InputManager = InputManager()