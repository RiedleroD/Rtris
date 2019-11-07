#!/usr/bin/python3
# coding: utf-8
import os,random,math,json
from subprocess import PIPE as subPIPE
from subprocess import Popen as subPopen
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame,pygame.freetype
from sys import argv
from urllib import request as req
from urllib.error import URLError
from re import match

K_DROP=False
confpath=os.path.abspath(os.path.expanduser("~/.rtrisconf"))

def get_git_head():
	try:
		curdir=os.path.abspath(os.path.dirname(__file__))
	except NameError:	#For when the script is compiled - the constant __file__ doesn't exist then
		return None
	headfile=os.path.join(curdir,".git/HEAD")
	if os.path.exists(headfile):
		with open(headfile,"r") as f:
			head=f.read()
		if head.startswith("ref:"):
			with open(os.path.abspath(os.path.join(curdir,".git/",head.split()[-1])),"r") as f:
				tag=f.read()
		else:
			tag=head
		return tag.replace(" ","").replace("\n","")
	else:
		return None

if not os.path.exists(confpath):
	strg={"left":pygame.K_LEFT,
		"right":pygame.K_RIGHT,
		"drop":pygame.K_UP,
		"idrop":pygame.K_DOWN,
		"rot":pygame.K_PAGEUP,
		"rot1":pygame.K_PAGEDOWN,
		"exit":pygame.K_ESCAPE,
		"pause":pygame.K_p}
	conf={"strg":strg,
		"fullscreen":False,
		"show_fps":True,
		"max_fps":60,
		"version":get_git_head(),
		"update_channel":2,
		"update":True}
	with open(confpath,"w+") as conffile:
		json.dump(conf,conffile,ensure_ascii=False)
else:
	with open(confpath,"r") as conffile:
		conf=json.load(conffile)
		strg=conf["strg"]

version=get_git_head()
if version!=None:
	conf["version"]=version
del version

try:
	update=conf["update"]
except KeyError:
	conf["update"]=True
	update=conf["update"]
debug=False

try:
	conf["max_fps"]
except KeyError:
	conf["max_fps"]=60

COPYRIGHT_YEAR="2019"
COPYRIGHT_HOLDER="Riedler"
AUTHORS="Rielder and Michael Federczuk"

USAGE="usage: %s" % (argv[0])
HELP="""\
%s
    Start Rtris, a Tetris clone written in Python.

    Options:
      -h, --help        display this summary and exit
      -V, --version     display version information and exit
      -d, --debug       print debug information
      -U, --update      update and exit
      -u, --no-update   don't automatically update

Report bugs at: https://github.com/RiedleroD/Rtris/issues
Rtris repository: https://github.com/RiedleroD/Rtris""" % (USAGE)
VERSION_INFO="""\
Rtris %s
Copyright (c) %s %s
License CC BY-SA 4.0: Creative Commons Attribution-ShareAlike 4.0 <http://creativecommons.org/licenses/by-sa/4.0>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by %s.""" % (conf["version"],COPYRIGHT_YEAR, COPYRIGHT_HOLDER, AUTHORS)

class Updater():
	def __init__(self,update_to:[0,1,2]=None):	#0→Stable,1→Prerelease,2→commit (in master branch),None→config option
		self.meth=update_to	#meth→method (hehe)
		if self.meth==None:
			try:
				self.meth=conf["update_channel"]
			except:
				self.meth=2
				conf["update_channel"]=self.meth
		try:
			self.current=conf["version"]
		except KeyError:
			self.current=None
			conf["version"]=None
		if self.meth not in (0,1,2):
			raise ValueError("Update method can only be 0, 1 or 2, instead it is "+str(self.meth)+".")
	def update(self)->bool:
		"""Returns True if updated, False if already newest version."""
		try:
			tag=self.get_latest_tag()
			if self.current!=tag:
				data=self.get_commit(tag)
				with open(__file__,"wb") as f:
					f.write(data)
				print("Updated from "+conf["version"]+" to "+tag+".")
				conf["version"]=tag
				return True
			else:
				print("Already newest",("Release.","Prerelease.","commit.")[conf["update_channel"]])
				return False
		except URLError as e:
			print("Couldn't update.",end=" ")
			dprint("Reason:",e,end="")
			print()
			return False
	def get_commit(self,tag:str)->bytes:
		data=req.urlopen("https://raw.githubusercontent.com/RiedleroD/Rtris/%s/rtris.py"%tag).read()
		return data
	def get_latest_tag(self)->str:
		if self.meth==2:
			info=json.load(req.urlopen("https://api.github.com/repos/RiedleroD/Rtris/commits/master"))
			latest=info["commit"]["url"].split("/")[-1]
		elif self.meth in (1,2):
			info=json.load(req.urlopen("https://api.github.com/repos/RiedleroD/Rtris/releases"))
			if self.meth==1:
				info=info[0]
			elif self.meth==0:
				for release in info:
					if not release["prerelease"]:
						info=release
						break
			latest=info["tag_name"]
		return latest

def opt_help(opt, arg):
	if arg != None:
		raise Exception("%s: too many arguments: 1" % (opt))
	print(HELP)
	exit(0)
def opt_version_info(opt, arg):
	if arg != None:
		raise Exception("%s: too many arguments: 1" % (opt))
	print(VERSION_INFO)
	exit(0)
def opt_update(opt, arg):
	if arg != None:
		raise Exception("%s: too many arguments: 1" % (opt))
	updater=Updater()
	updater.update()
	with open(confpath,"w+") as conffile:
		json.dump(conf,conffile,ensure_ascii=False)
	exit(0)

def dprint(*args, **kwargs):
	if debug:
		print(*args, **kwargs)
def opt_debug(opt, arg):
	global debug
	if arg != None:
		raise Exception("%s: too many arguments: 1" % (opt))
	debug=True

def opt_no_update(opt, arg):
	global update
	if arg != None:
		raise Exception("%s: too many arguments: 1" % (opt))
	dprint("skipped updating")
	update=False

# options are stored in this array here as tuples
# tuple[0]: array of single character strings representing the short options
# tuple[1]: array of strings representing the long options
# tuple[2]: boolean value that decides whether or not the option requires an
#            argument. if no argument is given, the handler will still be passed
#            a None value, so the handler has to check for a missing argument
# tuple[3]: the option handler function.
#            the first parameter will be the name of the option used in the
#            command line with the dashes. (e.g.: "-h", "--help", ...)
#            the second parameter will be the argument given to the option on
#            the command line. it doesn't matter what the value of tuple[2] is,
#            this parameter can either be a string or None
# tuple[4]: if True, the option is high priority and will be executed BEFORE
#            checking for invalid options and BEFORE the low priority options.
#            if False, the option is low priority and will be executed AFTER
#            checking for invalid options and AFTER the high priority options
# tuple[5]: number specifying the exact priority. options with higher priority
#            are executed before lower ones.
#           position of passed down argument decides what option to execute
#            first when priority is the same
options=[
	(["h"], ["help"],      False, opt_help,         True,  0),
	(["V"], ["version"],   False, opt_version_info, True,  0),
	(["d"], ["debug"],     False, opt_debug,        False, 1),
	(["U"], ["update"],    False, opt_update,       False, 0),
	(["u"], ["no-update"], False, opt_no_update,    False, 0)
]

if __name__=="__main__":
	args=[]
	hpoptqueue=[] # high priority option queue
	firstinvopt=None # first seen invalid option
	lpoptqueue=[] # low priority option queue
	ignopt=False
	i=1
	argc=len(argv)
	while i < argc:
		arg=argv[i]
		longmatch=None
		shortmatch=None
		if not ignopt:
			longmatch=match(r"^--([^=]+)(=(.*))?$", arg)
			shortmatch=match(r"^-([^-].*)$", arg)
		if longmatch != None:
			opt=longmatch.group(1)
			optarg=longmatch.group(3)
			option_found=False
			for option in options:
				if opt in option[1]:
					option_found=True
					if option[2] and optarg == None:
						if i + 1 < argc:
							optarg=argv[i + 1]
							i+=1
					if option[4]:
						hpoptqueue.append((option, "--" + opt, optarg))
					else:
						lpoptqueue.append((option, "--" + opt, optarg))
					break
			if not option_found and firstinvopt==None:
				firstinvopt="--" + opt
		elif shortmatch != None:
			opts=shortmatch.group(1)
			c=0
			l=len(opts)
			while c < l:
				opt=opts[c]
				option_found=False
				for option in options:
					if opt in option[0]:
						option_found=True
						optarg=None
						if option[2]:
							if c + 1 < l:
								optarg=opts[c + 1:]
								c=l
							elif i + 1 < argc:
								optarg=argv[i + 1]
								i+=1
						if option[4]:
							hpoptqueue.append((option, "-" + opt, optarg))
						else:
							lpoptqueue.append((option, "-" + opt, optarg))
						break
				if not option_found and firstinvopt==None:
					firstinvopt="-" + opt
				c+=1
		else:
			if not ignopt and arg == "--":
				ignopt=True
			else:
				args.append(arg)
		i+=1
	hpoptqueue.sort(key=lambda opt: opt[0][5], reverse=True)
	lpoptqueue.sort(key=lambda opt: opt[0][5], reverse=True)
	for opt in hpoptqueue:
		opt[0][3](opt[1], opt[2])
	if firstinvopt!=None:
		raise Exception("%s: invalid option" % (firstinvopt))
	for opt in lpoptqueue:
		opt[0][3](opt[1], opt[2])
	if len(args) > 0:
		raise Exception("too many arguments: %d" % (len(args)))

pygame.init()
pygame.freetype.init()
#I'm not particularly proud of this section...
try:
	from ctypes import windll	#windows specific
except:
	try:
		from AppKit import NSScreen	#Mac OS X specific
	except:
		try:
			w,h=subPopen(["xrandr | grep '*'"],shell=True,stdout=subPIPE).communicate()[0].split()[0].split(b"x")
		except Exception as e:
			dprint("Uhh... everything failed style")
			_dispinfo=pygame.display.Info()	#When everythin fails, I.E. on not windows-, linux- or MacOS-based machines.
			HEIGHT=_dispinfo.current_h
			WIDTH=_dispinfo.current_w
		else:
			dprint("Unix style")
			HEIGHT,WIDTH=int(h),int(w)
	else:
		dprint("MacOS style")
		macsize=NSScreen.screens()[0].frame().size	#this should work, according to https://stackoverflow.com/a/3129567/10499494, but I have noone to test it...
		HEIGHT=macsize.height
		WIDTH=macsize.width
else:
	dprint("Windows style")
	user32=windll.user32	#yep, windows fully through
	user32.SetProcessDPIAware()
	HEIGHT=user32.GetSystemMetrics(78)
	WIDTH=user32.GetSystemMetrics(79)

dprint("Window size: ",WIDTH,HEIGHT)

BORDER_WIDTH=5
BLACK=(0,0,0)
WHITE=(255,255,255)
SIZE=math.sqrt(HEIGHT**2+WIDTH**2)
LEFT_SIDE=0+BORDER_WIDTH
RIGHT_SIDE=WIDTH-BORDER_WIDTH
TOP_SIDE=0+BORDER_WIDTH
BOTTOM_SIDE=HEIGHT-BORDER_WIDTH
CENTERx=WIDTH//2
CENTERy=HEIGHT//2
CENTER=[CENTERx,CENTERy]
BLOCK_SIZE=HEIGHT/20

if conf["fullscreen"]:
	screen_mode=pygame.HWSURFACE | pygame.FULLSCREEN | pygame.NOFRAME
else:
	screen_mode=pygame.HWSURFACE | pygame.NOFRAME
screen=pygame.display.set_mode((WIDTH,HEIGHT),screen_mode)
del screen_mode
pygame.display.set_caption("RTris")

scorefont=pygame.freetype.SysFont("Linux Biolinum O,Arial,EmojiOne,Symbola,-apple-system",30)

def pygame_input(txt:str="")->str:
	char=""
	chars=txt
	while True:
		event=pygame.event.wait()
		if event.type==pygame.KEYDOWN:
			char=event.key
			if char==pygame.K_BACKSPACE:
				chars=chars[:-1]
			elif char in (pygame.K_ESCAPE,pygame.K_RETURN):
				break
			else:
				chars+=pygame.key.name(char)
		yield chars
		
class Block():
	alive=True
	def __init__(self,typ:int=random.randrange(7),x:int=0,y:int=0):
		"""
			 01	01
		0	0##	##				yellow
			1##	##
			 
			0##	##
			1##	##
		
			 012 	012
		1	0###	#			orange
			1#		#
			2		##
			
			0  #	##
			1###	 #
			2		 #
			
			 012	012
		2	0#		 #
			1###	 #			blue
			2		##
			
			0###	##
			1  #	#
			2		#
			
		
			 0123		0123
		3	0			  #		cyan
			1####		  #
			2			  #
			3			  #
			
			0			 #
			1			 #
			2####		 #
			3			 #
			
			
			 012	012
		4	0##		 #
			1 ##	##			red
			2		#
			
			0##		 #
			1 ##	##
			2		#
			
			 012	012
		5	0 ##	#			green
			1##		##
			2		 #
			
			0 ##	#
			1##		##
			2		 #
			
			 012	012
		6	0 #		 #			purple
			1###	##
			2		 #
			
			0		 #
			1###	 ##
			2 #		 #
		"""
		self.typ=typ
		self.x=x
		self.y=y
		self.rotation=0
		if typ==0:
			self.rects=self.rectmatrix([
			[[0,0],[0,1],[1,0],[1,1]],
			[[0,0],[0,1],[1,0],[1,1]],
			[[0,0],[0,1],[1,0],[1,1]],
			[[0,0],[0,1],[1,0],[1,1]]])
			self.color=(255,255,0)
		elif typ==1:
			self.rects=self.rectmatrix([
			[[0,0],[1,0],[2,0],[0,1]],
			[[0,0],[0,1],[0,2],[1,2]],
			[[0,1],[1,1],[2,1],[2,0]],
			[[0,0],[1,0],[1,1],[1,2]]])
			self.color=(255,127,0)
		elif typ==2:
			self.rects=self.rectmatrix([
			[[0,0],[0,1],[1,1],[2,1]],
			[[1,0],[1,1],[1,2],[0,2]],
			[[0,0],[1,0],[2,0],[2,1]],
			[[1,0],[0,0],[0,1],[0,2]]])
			self.color=(0,0,255)
		elif typ==3:
			self.rects=self.rectmatrix([
			[[0,1],[1,1],[2,1],[3,1]],
			[[2,0],[2,1],[2,2],[2,3]],
			[[0,2],[1,2],[2,2],[3,2]],
			[[1,0],[1,1],[1,2],[1,3]]])
			self.color=(0,255,255)
		elif typ==4:
			self.rects=self.rectmatrix([
			[[0,0],[1,0],[1,1],[2,1]],
			[[1,0],[1,1],[0,1],[0,2]],
			[[0,0],[1,0],[1,1],[2,1]],
			[[1,0],[1,1],[0,1],[0,2]]])
			self.color=(255,0,0)
		elif typ==5:
			self.rects=self.rectmatrix([
			[[2,0],[1,0],[1,1],[0,1]],
			[[0,0],[0,1],[1,1],[1,2]],
			[[2,0],[1,0],[1,1],[0,1]],
			[[0,0],[0,1],[1,1],[1,2]]])
			self.color=(0,255,0)
		elif typ==6:
			self.rects=self.rectmatrix([
			[[1,0],[0,1],[1,1],[2,1]],
			[[0,1],[1,0],[1,1],[1,2]],
			[[0,1],[1,1],[2,1],[1,2]],
			[[1,0],[1,1],[1,2],[2,1]]])
			self.color=(127,0,127)
		else:
			raise ValueError("Invalid block type: "+str(typ))
	def rectmatrix(self,matrix:list):
		return [[[matrix[j][i][0]+self.x,matrix[j][i][1]+self.y] for i in range(4)] for j in range(4)]
	def get_poss(self):
		return self.rects[self.rotation]
	def get_posxs(self):
		return [x for x,y in self.rects[self.rotation]]
	def get_posys(self):
		return [y for x,y in self.rects[self.rotation]]
	def stayin(self):
		while self.any_rect(lambda rect:rect[0]<0):
			self.move(1,0)
		while self.any_rect(lambda rect:rect[0]>9):
			self.move(-1,0)
		while self.any_rect(lambda rect:rect[1]<0):
			self.move(0,1)
		while self.any_rect(lambda rect:rect[1]>19):
			self.move(0,-1)
	def any_rect(self,func):
		for rect in self.rects[self.rotation]:
			if rect!=None and func(rect):
				return True
		return False
	def all_rects(self,func):
		for rect in self.rects[self.rotation]:
			if rect!=None and not func(rect):
				return False
		return True
	def move(self,x:int,y:int):
		for j in range(len(self.rects)):
			for i in range(len(self.rects[j])):
				self.rects[j][i][0]+=x
				self.rects[j][i][1]+=y
	def move_oop(self,x:int,y:int):
		return [[[i[0]+x,i[1]+y] for i in j] for j in self.rects]
	def rotate(self,clockwise:int):
		self.rotation-=clockwise
		self.rotation%=4
	def rotate_oop(self,clockwise:int):
		return self.rects[(self.rotation-clockwise)%4]
	def die(self):
		self.alive=False
		self.rects=[self.rects[self.rotation]]
		self.rotation=0
	def get_shadow(self,board):
		rects=self.rects[self.rotation]
		found=False
		movedown=0
		while movedown<=20:
			for rect in self.move_oop(0,movedown)[self.rotation]:
				if board.check_pos(rect) in (-1,-2):
					found=True
			if found:
				break
			movedown+=1
		if found:
			return self.move_oop(0,movedown-1)[self.rotation]
		else:
			raise ValueError("Couldn't find floor")

class Board():
	counter=1
	dropped=0
	harddrop=0
	tetrisln=0
	threeln=0
	twoln=0
	oneln=0
	score=0
	startdrop=True
	movecounter=0
	blinking=0
	paused=False
	ended=False
	has2drop=0
	def __init__(self):
		self.clock=pygame.time.Clock()
		self.blocks=[]
		self.clearing=[]
		self.rects2fall=[]
		self.upcoming=random.randrange(0,7)
		self.surface=pygame.Surface((10,20),pygame.HWSURFACE)
	def checklns(self):
		lns_count=0
		for line in range(20):
			found=True
			for px in range(10):
				if self.check_pos([px,line])!=-1:
					found=False
			if found:
				self.delline(line)
				lns_count+=1
		if lns_count==1:
			self.oneln+=1
		elif lns_count==2:
			self.twoln+=1
		elif lns_count==3:
			self.threeln+=1
		elif lns_count==4:
			self.tetrisln+=1
		elif lns_count==0:
			pass
		else:
			raise ValueError("lns_count is "+str(lns_count)+", but it can only be 0-4")
	def calcscore(self):
		return self.tetrisln*800+self.threeln*500+self.twoln*300+self.oneln*100+self.dropped+self.harddrop
	def delline(self,line:int):
		for block in self.blocks:
			if not block.alive:
				rects2del=[]
				rects2fall=[]
				for rot in range(len(block.rects)):
					for rect in range(len(block.rects[rot])):
						if block.rects[rot][rect]==None:
							pass
						elif block.rects[rot][rect][1]==line:
							rects2del.append([rot,rect])
						elif block.rects[rot][rect][1]<line:
							self.rects2fall.append([block,rot,rect])
				for rot,rect in rects2del:
					block.rects[rot][rect]=None
		self.clearing.append(line)
		self.blinking=150
	def get_alive(self):
		for block in self.blocks:
			if block.alive:
				return block
	def spawn(self,typ:int=None):
		if typ==None:
			typ=self.upcoming
			self.upcoming=random.randrange(0,7)
		block=Block(typ=typ,x=4,y=0)
		for rect in block.rects[block.rotation]:
			if self.check_pos(rect)==-1:
				self.ended=True
		self.blocks.append(block)
	def dontlettemout(self):
		for block in self.blocks:
			block.stayin()
	def move_alive(self,x:int,y:int,die_when_stopped:bool=False):
		for block in self.blocks:
			if block.alive:
				allowed=True
				for rect in block.move_oop(x,y)[block.rotation]:
					if self.check_pos(rect) not in (1,0):
						allowed=False
				if allowed:
					block.move(x,y)
				elif die_when_stopped:
					block.die()
	def rotate_alive(self,clockwise:int):
		for block in self.blocks:
			if block.alive:
				allowed=True
				for rect in block.rotate_oop(clockwise):
					if self.check_pos(rect) in (-1,-2):
						allowed=False
				if allowed:
					block.rotate(clockwise)
	def cycle(self,speed:int):
		if self.blinking>0 and not self.paused:
			self.blinking-=self.clock.get_time()
			if self.blinking<=0:
				self.clearing=[]
		elif not self.paused:
			self.dontlettemout()
			self.gravity(speed)
			self.kill_blocks()
			if self.blinking<=0:
				self.repopulate()
			self.cleanup()
			self.counter+=self.clock.get_time()
		if self.ended:
			return False
		else:
			return True
	def kill_blocks(self):
		k=False
		for block in self.blocks:
			if block.alive:
				for pos in block.get_poss():
					if self.check_pos([pos[0],pos[1]]) in (-1,-2):
						block.move(0,-1)
						block.die()
						k=True
						self.dropped+=1
						break
		if k:
			self.checklns()
	def gravity(self,speed):
		dropped=False
		for block,rot,rect in self.rects2fall:
			block.rects[rot][rect][1]+=1
		self.rects2fall=[]
		if K_DROP:
			if self.startdrop:
				self.movecounter=self.counter
			self.startdrop=False
			speed+=20
		while self.counter>self.movecounter:
			dropped=True
			if not K_DROP:
				self.startdrop=True
			self.movecounter+=(1000/(2**(speed/5)))
			for block in self.blocks:
				if block.alive:
					block.move(0,1)
	def repopulate(self):
		for block in self.blocks:
			if block.alive:
				return
		self.spawn()
	def check_pos(self,pos:[int,int]):
		if pos[1]==20:
			return -2
		elif pos[0]>9 or pos[1]>19 or pos[1]<0 or pos[0]<0:
			return None
		for block in self.blocks:
			for blockpos in block.get_poss():
				if blockpos==pos:
					if block.alive:
						return 1
					else:
						return -1
		return 0
	def cleanup(self):
		for block in reversed(range(len(self.blocks))):
			if not self.blocks[block].alive:
				if not any([rect!=None for rect in self.blocks[block].rects]):
					del self.blocks[block]
	def draw(self,curtain:list=[]):
		self.surface.fill((100,100,100))
		for block in self.blocks:
			if block.alive:
				for pos in block.get_shadow(self):
					self.surface.set_at(pos,(125,125,125))
			for pos in block.rects[block.rotation]:
				if pos!=None:
					self.surface.set_at(pos,block.color)
		for ln in self.clearing:
			if self.blinking>100:
				pygame.draw.line(self.surface,(255,255,255),(0,ln),(10,ln))
			elif self.blinking>50:
				pygame.draw.line(self.surface,(200,200,200),(0,ln),(10,ln))
		for line in curtain:
			pygame.draw.line(self.surface,(0,0,0),(0,line),(10,line))
	def pause(self):
		self.paused=not self.paused

def get_rect(x:float=0,y:float=0,width:float=1,height:float=1):
		return pygame.Rect(math.ceil(x*BLOCK_SIZE),math.ceil(y*BLOCK_SIZE),math.ceil(width*BLOCK_SIZE),math.ceil(height*BLOCK_SIZE))

class Button():
	pressed=False
	bgcolor=(255,255,255)
	color=(0,0,0)
	txt="Button"
	def __init__(self,x:int=0,y:int=0,width:int=WIDTH//10,height:int=HEIGHT//15,bgcolor:(int,int,int)=(255,255,255),txt:str="Button",txtcolor:(int,int,int)=(0,0,0),font:pygame.freetype.Font=scorefont,posmeth:[int,int]=(0,0)):
		self.bgcolor=bgcolor
		self.color=txtcolor
		self.txt=txt
		self.width=width
		self.height=height
		self.font=font
		text=font.render(txt,txtcolor)[0]
		self.surface=pygame.Surface((width,height))
		self.surface.fill(bgcolor)
		self.surface.blit(text,(width//2-text.get_width()//2,height//2-text.get_height()//2))
		self.rect=[None,None]
		if posmeth[0]==0:
			self.rect[0]=x-self.surface.get_width()//2
		elif posmeth[0]==1:
			self.rect[0]=x
		elif posmeth[0]==-1:
			self.rect[0]=x-self.surface.get_width()
		else:
			raise ValueError("Wrong position method (only -1,0,1 are allowed): "+str(posmeth))
		if posmeth[1]==0:
			self.rect[1]=y-self.surface.get_height()//2
		elif posmeth[1]==1:
			self.rect[1]=y
		elif posmeth[1]==-1:
			self.rect[1]=y-self.surface.get_height()
		else:
			raise ValueError("Wrong position method (only -1,0,1 are allowed): "+str(posmeth))
		self.rect=pygame.Rect(*self.rect,width,height)
	def press(self):
		self.pressed=True
	def collideswith(self,pos:[int,int])	-> bool:
		return self.rect.collidepoint(pos)
	def render(self)	->	pygame.Surface:
		text=self.font.render(self.txt,self.color)[0]
		self.surface.fill(self.bgcolor)
		self.surface.blit(text,(self.surface.get_width()//2-text.get_width()//2,self.surface.get_height()//2-text.get_height()//2))
		return self.surface

class MainGame():
	running=False
	speed=0
	cycle=0
	def __init__(self):
		self.screen=screen
		self.buttons={}
	def draw(self,curtain:list=[],headsup:str="",show_upcoming:bool=True):
		self.screen.fill((0,0,0))
		if self.running:
			if self.board.paused:
				text=scorefont.render("PAUSED",(255,255,255))[0]
				self.screen.blit(text,(CENTERx-text.get_width()//2,CENTERy-text.get_height()//2))
			else:
				score=self.board.calcscore()
				lns=self.board.tetrisln*4+self.board.threeln*3+self.board.twoln*2+self.board.oneln
				screen.blit(scorefont.render("Score: "+str(score),(255,255,255))[0],(11*BLOCK_SIZE,3*BLOCK_SIZE))
				screen.blit(scorefont.render("Lines: "+str(lns),(255,255,255))[0],(11*BLOCK_SIZE,4*BLOCK_SIZE))
				screen.blit(scorefont.render("Level: "+str(self.speed),(255,255,255))[0],(11*BLOCK_SIZE,5*BLOCK_SIZE))
				screen.blit(scorefont.render("Tetris': "+str(self.board.tetrisln),(255,255,255))[0],(11*BLOCK_SIZE,6*BLOCK_SIZE))
				screen.blit(scorefont.render("Triples: "+str(self.board.threeln),(255,255,255))[0],(11*BLOCK_SIZE,7*BLOCK_SIZE))
				screen.blit(scorefont.render("Doubles: "+str(self.board.twoln),(255,255,255))[0],(11*BLOCK_SIZE,8*BLOCK_SIZE))
				screen.blit(scorefont.render("Singles: "+str(self.board.oneln),(255,255,255))[0],(11*BLOCK_SIZE,9*BLOCK_SIZE))
				#pygame.draw.rect(screen,(125,125,125),get_rect(11.5,1.5,2.5,2.5))
				if show_upcoming:
					upcoming=Block(typ=self.board.upcoming,x=0,y=0)
					for x,y in upcoming.rects[0]:
						if upcoming.typ==0:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.5+x,0.5+y,1,1))
						elif upcoming.typ==1:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.65+x,0.65+y,1,1))
						elif upcoming.typ==2:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.65+x,0.35+y,1,1))
						elif upcoming.typ==3:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11+x,0.25+y,1,1))
						elif upcoming.typ==4:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.25+x,0.5+y,1,1))
						elif upcoming.typ==5:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.25+x,0.5+y,1,1))
						elif upcoming.typ==6:
							pygame.draw.rect(self.screen,[channel//3 for channel in upcoming.color],get_rect(11.25+x,0.35+y,1,1))
					for x,y in upcoming.rects[0]:
						pygame.draw.rect(self.screen,upcoming.color,get_rect(12+x*0.5,1+y*0.5,0.5,0.5))
				self.board.draw(curtain)
				self.screen.blit(pygame.transform.scale(self.board.surface,(HEIGHT//2,HEIGHT)),(0,0))
				if headsup!="" and type(headsup)==str:
					hutxt=scorefont.render(headsup,(255,255,255),(0,0,0))[0]
					self.screen.blit(hutxt,(5*BLOCK_SIZE-hutxt.get_width()//2,CENTERy-hutxt.get_height()//2))
				if conf["show_fps"]:
					self.screen.blit(scorefont.render(str(int(self.board.clock.get_fps())),(255,255,255))[0],(0,0))
		else:
			for name,button in self.buttons.items():
				self.screen.blit(button.surface,button.rect)
		pygame.display.flip()
	def end(self):
		for line in reversed(range(20)):
			self.draw(curtain=[l for l in range(line,20)],headsup="Game Over",show_upcoming=False)
			self.board.clock.tick(30)
		while self.running:
			event=pygame.event.wait()
			if event.type==pygame.KEYDOWN and event.key in (strg["exit"],pygame.K_RETURN):
				self.running=False
	def run(self):
		global K_DROP
		self.running=True
		while self.running:
			self.cycle+=self.board.clock.get_time()
			if (self.cycle//10)%3141<10:
				self.speed+=1
				while (self.cycle//10)%3141<10:
					self.cycle+=1
			for event in pygame.event.get():
				if event.type==pygame.KEYDOWN:
					if event.key==strg["exit"]:
						self.running=False
					elif event.key==strg["left"]:
						self.board.move_alive(-1,0)
					elif event.key==strg["right"]:
						self.board.move_alive(1,0)
					elif event.key==strg["drop"]:
						K_DROP=True
					elif event.key==strg["idrop"]:
						block=self.board.get_alive()
						if block!=None:
							self.board.counter=1
							self.board.movecounter=1
							while block.alive:
								block.move(0,1)
								self.board.kill_blocks()
							self.board.harddrop+=1
					elif event.key==strg["rot"]:
						self.board.rotate_alive(1)
					elif event.key==strg["rot1"]:
						self.board.rotate_alive(-1)
					elif event.key==strg["pause"] or event.key==pygame.K_PAUSE:
						self.board.pause()
				elif event.type==pygame.KEYUP:
					if event.key==strg["drop"]:
						K_DROP=False
			self.board.cycle(self.speed)
			self.draw()
			if self.board.ended:
				self.end()
			self.board.clock.tick(conf["max_fps"])
		self.speed=0
	def menu(self):
		self.buttons={}
		self.buttons["settings"]=Button(x=CENTERx,y=CENTERy,txt="Settings")
		self.buttons["start"]=Button(x=CENTERx,y=self.buttons["settings"].rect.top-10,txt="Start",posmeth=(0,-1))
		self.buttons["quit"]=Button(x=CENTERx,y=self.buttons["settings"].rect.bottom+10,txt="Quit",posmeth=(0,1))
		while True:
			self.draw()
			if self.checkbuttons():
				break
			if self.buttons["start"].pressed:
				self.buttons["start"].pressed=False
				self.board=Board()
				self.run()
			elif self.buttons["settings"].pressed:
				self.buttons["settings"].pressed=False
				self.settings()
				self.buttons={}
				self.buttons["settings"]=Button(x=CENTERx,y=CENTERy,txt="Settings")
				self.buttons["start"]=Button(x=CENTERx,y=self.buttons["settings"].rect.top-10,txt="Start",posmeth=(0,-1))
				self.buttons["quit"]=Button(x=CENTERx,y=self.buttons["settings"].rect.bottom+10,txt="Quit",posmeth=(0,1))
			elif self.buttons["quit"].pressed:
				self.buttons["quit"].pressed=False
				break
	def settings(self):
		self.buttons={
			"back":Button(x=CENTERx,y=BOTTOM_SIDE,txt="Back",posmeth=(0,-1)),
			"strgleft":Button(x=LEFT_SIDE,y=TOP_SIDE,txt="Left",posmeth=(1,1))}
		self.buttons["strgright"]=Button(x=LEFT_SIDE,y=self.buttons["strgleft"].rect.bottom+10,txt="Right",posmeth=(1,1))
		self.buttons["strgdrop"]=Button(x=LEFT_SIDE,y=self.buttons["strgright"].rect.bottom+10,txt="Drop",posmeth=(1,1))
		self.buttons["strgidrop"]=Button(x=LEFT_SIDE,y=self.buttons["strgdrop"].rect.bottom+10,txt="Inst. Drop",posmeth=(1,1))
		self.buttons["strgrot"]=Button(x=LEFT_SIDE,y=self.buttons["strgidrop"].rect.bottom+10,txt="Rotate \u21c0",posmeth=(1,1))
		self.buttons["strgrot1"]=Button(x=LEFT_SIDE,y=self.buttons["strgrot"].rect.bottom+10,txt="Rotate \u21bc",posmeth=(1,1))
		self.buttons["strgexit"]=Button(x=LEFT_SIDE,y=self.buttons["strgrot1"].rect.bottom+10,txt="Exit/Back",posmeth=(1,1))
		self.buttons["strgpause"]=Button(x=LEFT_SIDE,y=self.buttons["strgexit"].rect.bottom+10,txt="Pause",posmeth=(1,1))
		if conf["fullscreen"]:
			fulscrntxt="Fullscreen"
		else:
			fulscrntxt="Borderless"
		try:
			if conf["show_fps"]:
				fpstxt="Show FPS"
			else:
				fpstxt="Hide FPS"
		except KeyError:
			conf["show_fps"]=True
			fpstxt="Show FPS"
		self.buttons["fullscreen"]=Button(x=RIGHT_SIDE,y=TOP_SIDE,txt=fulscrntxt,posmeth=(-1,1))
		self.buttons["show_fps"]=Button(x=RIGHT_SIDE,y=self.buttons["fullscreen"].rect.bottom+10,txt=fpstxt,posmeth=(-1,1))
		self.buttons["max_fps"]=Button(x=RIGHT_SIDE,y=self.buttons["show_fps"].rect.bottom+10,txt="FPS: "+str(conf["max_fps"]),posmeth=(-1,1))
		if conf["update"]:
			updtcolr=(0,255,0)
		else:
			updtcolr=(255,0,0)
		self.buttons["update"]=Button(x=RIGHT_SIDE,y=self.buttons["max_fps"].rect.bottom+10,txtcolor=updtcolr,txt="Update",posmeth=(-1,1))
		uchans=["Stable","Devel","Canary"]
		self.buttons["uchannel"]=Button(x=RIGHT_SIDE,y=self.buttons["update"].rect.bottom+10,txt=uchans[conf["update_channel"]],posmeth=(-1,1))
		del updtcolr
		del fulscrntxt
		while True:
			self.draw()
			if self.checkbuttons() or self.buttons["back"].pressed:
				break
			if self.buttons["strgleft"].pressed:
				self.buttons["strgleft"].txt="["+pygame.key.name(strg["left"])+"]"
				self.buttons["strgleft"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["left"]=button.key
				self.buttons["strgleft"].pressed=False
				self.buttons["strgleft"].txt="Left"
				self.buttons["strgleft"].render()
			elif self.buttons["strgright"].pressed:
				self.buttons["strgright"].txt="["+pygame.key.name(strg["right"])+"]"
				self.buttons["strgright"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["right"]=button.key
				self.buttons["strgright"].pressed=False
				self.buttons["strgright"].txt="Right"
				self.buttons["strgright"].render()
			elif self.buttons["strgdrop"].pressed:
				self.buttons["strgdrop"].txt="["+pygame.key.name(strg["drop"])+"]"
				self.buttons["strgdrop"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["drop"]=button.key
				self.buttons["strgdrop"].pressed=False
				self.buttons["strgdrop"].txt="Drop"
				self.buttons["strgdrop"].render()
			elif self.buttons["strgidrop"].pressed:
				self.buttons["strgidrop"].txt="["+pygame.key.name(strg["idrop"])+"]"
				self.buttons["strgidrop"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["idrop"]=button.key
				self.buttons["strgidrop"].pressed=False
				self.buttons["strgidrop"].txt="Inst. Drop"
				self.buttons["strgidrop"].render()
			elif self.buttons["strgrot"].pressed:
				self.buttons["strgrot"].txt="["+pygame.key.name(strg["rot"])+"]"
				self.buttons["strgrot"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["rot"]=button.key
				self.buttons["strgrot"].pressed=False
				self.buttons["strgrot"].txt="Rotate \u21c0"
				self.buttons["strgrot"].render()
			elif self.buttons["strgrot1"].pressed:
				self.buttons["strgrot1"].txt="["+pygame.key.name(strg["rot1"])+"]"
				self.buttons["strgrot1"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["rot1"]=button.key
				self.buttons["strgrot1"].pressed=False
				self.buttons["strgrot1"].txt="Rotate \u21bc"
				self.buttons["strgrot1"].render()
			elif self.buttons["strgexit"].pressed:
				self.buttons["strgexit"].txt="["+pygame.key.name(strg["exit"])+"]"
				self.buttons["strgexit"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["exit"]=button.key
				self.buttons["strgexit"].pressed=False
				self.buttons["strgexit"].txt="Exit/Back"
				self.buttons["strgexit"].render()
			elif self.buttons["strgpause"].pressed:
				self.buttons["strgpause"].txt="["+pygame.key.name(strg["pause"])+"]"
				self.buttons["strgpause"].render()
				self.draw()
				button=self.wait4buttonpress()
				if button!=None:
					strg["pause"]=button.key
				self.buttons["strgpause"].pressed=False
				self.buttons["strgpause"].txt="Pause"
				self.buttons["strgpause"].render()
			elif self.buttons["fullscreen"].pressed:
				self.buttons["fullscreen"].pressed=False
				conf["fullscreen"]=not conf["fullscreen"]
				if conf["fullscreen"]:
					self.buttons["fullscreen"].txt="Fullscreen"
				else:
					self.buttons["fullscreen"].txt="Borderless"
				self.buttons["fullscreen"].render()
				pygame.display.toggle_fullscreen()
			elif self.buttons["show_fps"].pressed:
				self.buttons["show_fps"].pressed=False
				conf["show_fps"]=not conf["show_fps"]
				if conf["show_fps"]:
					self.buttons["show_fps"].txt="Show FPS"
				else:
					self.buttons["show_fps"].txt="Hide FPS"
				self.buttons["show_fps"].render()
			elif self.buttons["max_fps"].pressed:
				self.buttons["max_fps"].txt="["+str(conf["max_fps"])+"]"
				self.buttons["max_fps"].render()
				self.draw()
				for inpot in pygame_input(str(conf["max_fps"])):
					self.buttons["max_fps"].txt="["+inpot+"]"
					self.buttons["max_fps"].render()
					self.draw()
				try:
					conf["max_fps"]=abs(int(self.buttons["max_fps"].txt[1:-1]))
				except ValueError:
					pass
				self.buttons["max_fps"].txt="FPS: "+str(conf["max_fps"])
				self.buttons["max_fps"].render()
				self.buttons["max_fps"].pressed=False
			elif self.buttons["update"].pressed:
				self.buttons["update"].pressed=False
				conf["update"]=not conf["update"]
				if conf["update"]:
					self.buttons["update"].color=(0,255,0)
				else:
					self.buttons["update"].color=(255,0,0)
				self.buttons["update"].render()
			elif self.buttons["uchannel"].pressed:
				self.buttons["uchannel"].pressed=False
				conf["update_channel"]=(conf["update_channel"]+1)%3
				self.buttons["uchannel"].txt=uchans[conf["update_channel"]]
				self.buttons["uchannel"].render()
	def wait4buttonpress(self):
		while True:
			event=pygame.event.wait()
			if event.type==pygame.KEYDOWN:
				return event
			elif event.type==pygame.MOUSEBUTTONDOWN:
				return None
	def checkbuttons(self):
		event=pygame.event.wait()
		if event.type==pygame.MOUSEBUTTONUP and event.button==1:
			for name,button in self.buttons.items():
				if button.collideswith(event.pos):
					button.press()
		elif event.type==pygame.KEYDOWN and event.key==strg["exit"]:
			return True
		return False

if __name__=="__main__":
	try:
		dprint("""Configurations:
  strg:
    left:%s
    right:%s
    drop:%s
    idrop:%s
    rot:%s
    rot1:%s
    exit:%s
    pause:%s
  fullscreen:%s
  show_fps:%s
  max_fps:%s
  version:%s
  update_channel:%s
  update:%s"""%(
		conf["strg"]["left"],
		conf["strg"]["right"],
		conf["strg"]["drop"],
		conf["strg"]["idrop"],
		conf["strg"]["rot"],
		conf["strg"]["rot1"],
		conf["strg"]["exit"],
		conf["strg"]["pause"],
		conf["fullscreen"],
		conf["show_fps"],
		conf["max_fps"],
		conf["version"],
		conf["update_channel"],
		conf["update"]))
		try:
			if os.path.exists(os.path.join(os.path.dirname(__file__),".git/")):
				dprint("Skipped updating because of detected git repository")
				update=False
			if update:
				updater=Updater()
				if updater.update():
					with open(confpath,"w+") as conffile:
						json.dump(conf,conffile,ensure_ascii=False)
					os.execv(__file__,argv)
		except NameError:
			dprint("Skipped updating because this is compiled.")
		game=MainGame()
		game.menu()
	finally:
		with open(confpath,"w+") as conffile:
			json.dump(conf,conffile,ensure_ascii=False)

