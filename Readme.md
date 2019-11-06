# Rtris

A game that works pretty much like classic Tetris, but [open-source](https://github.com/RiedleroD/Rtris) and playable on PC.
Licensed under `CC BY-SA 4.0`.

If you want to contribute, just do it. If there's something about your contribution that I don't like, I'll tell you or change it myself. Just do it.
If you want to be a playtester, write an email to riedler@gelse.net or join the playtesting group on [Telegram](t.me/RtrisTest). Or just write an issue as soon as you find one.

### Command-line arguments

| Short | Long | Description|
|--|--|--|
|-h|--help|Displays a help message|
|-V|--version|Displays the Version of the script|
|-U|--update|Updates the script instantly and exits|
|-u|--no-update|Skips automatic update|
|-d|--debug|Prints debug messages|

### CHANGELOG

v1.0<sub>unfinished</sub>
- v1.0a4
  - heavy optimization
  - you can now double-click Rtris.py and it executes directly
  - added automatic updater
    - you can disable it in the settings
    - you can change the update channel in the settings
    - skips update if git repo is detected
    - automatically grabs version from .git folder if existent
  - added command-line arguments
  - added Logo
  - added debug messages
  - added max. FPS setting
- v1.0a3
	- added the option to show fps
	- heavy optimisations (up to 3 times faster on my Laptop)
	- framerate now doesn't influence how fast the game is
	- added line clear animation
	- added LICENSE
	- added Changelog to Readme
- v1.0a2
	- added setup.py for compiling
	- fixed bugs
		- speed now resets properly between runs
		- Pause screen doesn't crash the game anymore
		- Shebang is now in the proper format
		- fixed issues with multiple monitors

- v1.0a1
	- added Readme.md
	- enhanced settings
		- added config file (settings now get saved)
		- added Fullscreen/Borderless setting

v0.3

- Changed font to Linux Biolinum O, or, if not found, Arial
- various smaller improvements & optimisations
- Pause Screen now covers the whole screen
- collision now works again
- added main menu
	- added start button (duh)
	- added settings
		- added control settings
	- it now goes there instead of closing the game when the player loses#
- silenced pygame

v0.2

- added Death screen
- you can now pause with the PAUSE key.

v0.1

- Initial game ~~do not play~~

