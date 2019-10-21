from cx_Freeze import setup, Executable
build_exe_options = {"excludes":["pydoc"]}

setup(name = "Rtris",
      version = "1.0",
      description = "",
      options = { "build_exe" : build_exe_options },
      executables = [Executable("rtris.py")])
