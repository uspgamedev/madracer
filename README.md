# MadRacer
Mad-Max inspired top-down racing/shooter Python/SFML game.

## Background
Initially devised as a simple web-based (HTML5/JS) game for a challenge to a mobile gaming company admission process, MadRacer evolved to a Python/SFML implementation with improved mechanics and new features.

## Features
Mad-Max inspired top-down racing/shooter game: dodge enemies and obstacles while destroying them with shots and bombs. Time alive and actions performed (enemies killed, shots hit, powerups collected, etc) contribute to your score.
* 3 different types of enemies.
* 2 different types of map obstacles.
* 2 different types of power-ups.
* The longer you remain alive, the more enemies appear and the faster the track and obstacles move along.
* Enemies are kinda dumb, yet still provides an interesting challenge.
* Supports 3 different input configurations. An input-method also defines how targeting works:
  * Keyboard-only: targeting is nearest enemy.
  * Keyboard and Mouse: targeting is nearest enemy to the mouse position.
  * GamePad (plug-and-play): targeting is nearest enemy in a cone towards selected direction.
* Locally-saved, persistent top-10 high scores.

## How to play
Game requirements are simple:
* Latest Python v2 version.
* [Python-SFML](http://www.python-sfml.org/index.html)

To execute the game:

1. Go to the root directory of the repository.
2. Execute **python madracer.py** to start the game.
3. Enjoy!
4. Note: execute **python madracer.py --help** to display command-line arguments help.

While in-game...:
* We think it is pretty straight-forward to play the game, but if you're having difficulties, both keyboard-based input-methods use SPACE to pause the game. In the pause-screen, the available commands are displayed.
