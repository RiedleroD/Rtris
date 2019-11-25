#!/usr/bin/python3
import os
from time import localtime
import pygame
def getTime()->tuple:
	lt=localtime()
	return lt.tm_year,lt.tm_mon,lt.tm_mday,lt.tm_hour,lt.tm_min,lt.tm_sec
def getFileName(ext:str="png")->str:
	if ext.startswith('.'):
		ext=ext[1:]
	return "screenshot_%s.%s.%s-%s.%s.%s."%getTime()+ext
def dumppg(surface:pygame.Surface,path:str="./screenshots/")->str:
	f=os.path.join(path,getFileName(ext="png"))
	pygame.image.save(surface,f)
	return f
