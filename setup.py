#!/usr/bin/python3
from cx_Freeze import setup, Executable
#run with python3 setup.py build
build_exe_options = {"excludes":["pydoc","scipy","numpy","OpenGL"],"optimize":2,"include_files":["./Readme.md","./LICENSE","./logo.svg"]}

setup(name = "Rtris",
      version = "1.0a4",
      description = "",
      options = { "build_exe" : build_exe_options },
      executables = [Executable("rtris.py")])
