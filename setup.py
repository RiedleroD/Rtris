#!/usr/bin/python3
from cx_Freeze import setup, Executable
#run with python3 setup.py build
build_exe_options = {"excludes":["pydoc","scipy","numpy","OpenGL","pygame.joystick","pygame._numpysndarray","pygame._numpysurfarray","pygame.mixer","pygame.mixer_music"],"optimize":2,"include_files":["./Readme.md","./LICENSE","./logo.svg","./gamedata/"]}

setup(name = "Rtris",
      version = "1.0a4",
      description = "",
      options = { "build_exe" : build_exe_options },
      executables = [Executable("rtris.py")])
