﻿#!/usr/bin/python
# -*- coding: utf-8 -*-

import sfml as sf
from scripts.game import Game, input, font

################################################################

def executeGame(fullscreen, cheatsEnabled, vsync, stretch, input_index, superhot):
    windowtitle = "Mad Racer"
    if fullscreen:
        windowsize, _ = sf.VideoMode.get_desktop_mode()
        window = sf.RenderWindow(sf.VideoMode(*windowsize), windowtitle, sf.Style.FULLSCREEN)
    else:
        windowsize = (1000, 700)
        window = sf.RenderWindow(sf.VideoMode(*windowsize), windowtitle)
    
    Game.input_index = input_index
    Game.initialize(window, font, cheatsEnabled, stretch, superhot)
    
    icon = Game.images.player.to_image()
    window.icon = icon.pixels
    window.vertical_synchronization = vsync
    window.mouse_cursor_visible = False
    
    tfps = sf.Text("-", font, character_size=25)
    tfps.color = sf.Color.RED
    def updateFPStextPos():
        tfps.position = 100, 5
    updateFPStextPos()
    showFps = False
    
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
            elif type(event) is sf.ResizeEvent:
                Game.updateGraphics()
            else:
                Game.processInput(event)
        
        for cmd, player in Game.loop_commands.items():
            if cmd == input.InputMethod.TOGGLE_FULLSCREEN:
                fullscreen = not fullscreen
                if fullscreen:
                    windowsize, _ = sf.VideoMode.get_desktop_mode()
                    window.recreate(sf.VideoMode(*windowsize), windowtitle, sf.Style.FULLSCREEN)
                else:
                    windowsize = (1000, 700)
                    window.recreate(sf.VideoMode(*windowsize), windowtitle)
                window.icon = icon.pixels
                window.vertical_synchronization = vsync
                window.mouse_cursor_visible = False
                Game.updateGraphics()
                updateFPStextPos()
            elif cmd == input.InputMethod.TOGGLE_FPS_DISPLAY:
                showFps = not showFps
        Game.loop_commands = {}
        
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
    parser.add_argument("--stretch", "-s", action="store_true", default=False, help="If true, graphics will be stretched to fit window. If false (default), graphics will "+
        "maintain the original intended aspect-ratio, but might cause black bars on window borders due to unused empty space.")
    methods = ['Crap']#[im.__name__.lower()[:-5] for im in input.available_inputs]
    parser.add_argument("--input", "-i", choices=methods, default=methods[0], help="Starting input method to use. It can also be changed at anytime in-game." )
    parser.add_argument("--superhot", "-sh", action="store_true", default=False, help="If true, SUPER!HOT!")
    args = parser.parse_args()
    
    input_index = methods.index(args.input)
    executeGame(args.fullscreen, args.cheats, args.vsync, args.stretch, input_index, args.superhot)