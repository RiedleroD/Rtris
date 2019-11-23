#!/usr/bin/python3
# coding: utf-8
import os,random,math,json
from subprocess import PIPE as subPIPE
from subprocess import Popen as subPopen
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
import pygame,pygame.freetype
from sys import argv
from urllib import request as req
from urllib.error import URLError
from re import fullmatch
from commoncodes import CommonCode,settb
settb(False)

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

defstrg={
	"left":pygame.K_LEFT,
	"right":pygame.K_RIGHT,
	"drop":pygame.K_UP,
	"idrop":pygame.K_DOWN,
	"rot":pygame.K_PAGEUP,
	"rot1":pygame.K_PAGEDOWN,
	"exit":pygame.K_ESCAPE,
	"pause":pygame.K_p}
defaults={
	"strg":defstrg,
	"fullscreen":False,
	"show_fps":True,
	"max_fps":60,
	"version":get_git_head(),
	"update_channel":0,
	"update":True}

if not os.path.exists(confpath):
	strg=defstrg
	conf=defaults
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

for setting,default in defaults.items():
	try:
		conf[setting]
	except KeyError:
		conf[setting]=default
for setting,default in defstrg.items():
	try:
		conf["strg"][setting]
	except KeyError:
		conf["strg"][setting]=default

update=conf["update"]
debug=False

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
      -w, --window      (fullscreen,1|borderless,0) set window mode
      -f, --fps         <FPS> set maximum fps

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
				self.meth=0
				conf["update_channel"]=self.meth
		try:
			self.current=conf["version"]
		except KeyError:
			self.current=None
			conf["version"]=None
		if self.meth not in (0,1,2):
			raise CommonCode("Update method can only be 0, 1 or 2, instead it is "+str(self.meth)+".")
	def update(self)->bool:
		"""Returns True if updated, False if already newest version."""
		try:
			tag=self.get_latest_tag()
			if self.current!=tag:
				data=self.get_commit(tag)
				with open(__file__,"wb") as f:
					f.write(data)
				print("Updated from "+str(conf["version"])+" to "+tag+".")
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

def opt_help(opt, args):
	if args != []:
		raise CommonCode(4,opt,args)
	print(HELP)
	exit(0)
def opt_version_info(opt, args):
	if args != []:
		raise CommonCode(4,opt,args)
	print(VERSION_INFO)
	exit(0)
def opt_update(opt, args):
	if args != []:
		raise CommonCode(4,opt,args)
	updater=Updater()
	updater.update()
	with open(confpath,"w+") as conffile:
		json.dump(conf,conffile,ensure_ascii=False)
	exit(0)

def dprint(*args, **kwargs):
	if debug:
		print(*args, **kwargs)
def opt_debug(opt, args):
	global debug
	if args != []:
		raise CommonCode(4,opt,args)
	debug=True
	settb(True)

def opt_no_update(opt, args):
	global update
	if args != []:
		raise CommonCode(4,opt,args)
	dprint("skipped updating")
	update=False

def opt_fps(opt, args):
	if args==[]:
		raise CommonCode(3,opt,"FPS")
	elif len(args)>1:
		raise CommonCode(4,opt,args)
	else:
		arg=args[0]
		try:
			if int(arg)<0:
				raise CommonCode(11,opt,arg,">=0")
			else:
				conf["max_fps"]=int(arg)
		except ValueError:
			raise CommonCode(10,opt,arg)

def opt_window(opt, args):
	if args==[]:
		raise CommonCode(3,opt,"Window Mode")
	elif len(args)>1:
		raise CommonCode(4,opt,args)
	else:
		arg=args[0].lower()
		try:
			arg=int(arg)
		except ValueError:
			if arg in ("borderless","windowed","window","false","w"):
				conf["fullscreen"]=False
			elif arg in ("fullscreen","full","true","f"):
				conf["fullscreen"]=True
			else:
				raise CommonCode(7,opt,arg,": can only be one of (borderless,windowed,window,false,w,0,fullscreen,full,true,f,1)")
		else:
			if arg in (0,1):
				conf["fullscreen"]=bool(arg)
			else:
				raise CommonCode(11,opt,str(arg),"0,1")

# options are stored in this array here as tuples
# tuple[0]: array of single character strings representing the short options
# tuple[1]: array of strings representing the long options
# tuple[2]: boolean value that decides whether or not the option requires an argument. if no argument is given, the handler will still be passed a None value, so the handler has to check for a missing argument
# tuple[3]: the option handler function. The first parameter will be the name of the option used in the command line with the dashes. (e.g.: "-h", "--help", ...) the second parameter will be the argument given
#           to the option on the command line. it doesn't matter what the value of tuple[2] is, this parameter can either be a string or None
# tuple[4]: if True, the option is high priority and will be executed BEFORE checking for invalid options and BEFORE the low priority options. if False, the option is low priority and will be executed AFTER
#           checking for invalid options and AFTER the high priority options
# tuple[5]: number specifying the exact priority. options with higher priority are executed before lower ones. position of passed down argument decides what option to execute first when priority is the same
options=[
	(["h"], ["help"],      0, opt_help,         6),
	(["V"], ["version"],   0, opt_version_info, 5),
	(["d"], ["debug"],     0, opt_debug,        4),
	(["u"], ["no-update"], 0, opt_no_update,    3),
	(["U"], ["update"],    0, opt_update,       2),
	(["w"], ["window"],    1, opt_window,       1),
	(["f"], ["fps"],       1, opt_fps,			0)]

if __name__=="__main__":
	invalid=""
	isvalue=False
	optqueue=[]
	for i,arg in enumerate(argv):
		if isvalue:
			isvalue=False
			continue
		match=fullmatch(r"^-(-(?P<l>[^-].+)|(?P<s>[^-]))$",arg)
		if match==None:
			if arg.startswith("-") or arg.endswith("-"):
				invalid+="\n  Invalid argument: "+arg
			else:
				continue
		else:
			unknown=True
			for option in options:
				if (match.group("s") in option[0]) or (match.group("l") in option[1]):
					values=[]
					unknown=False
					if option[2] and i+option[2]+1<=len(argv):
						values=argv[i+1:i+option[2]+1]
						isvalue=option[2]
					optqueue.append([option,arg,values])
					break
			if unknown:
				raise CommonCode(5,arg)
	if invalid:
		raise CommonCode(64,invalid)
	optqueue.sort(key=lambda opt: opt[0][4], reverse=True)
	for opt in optqueue:
		opt[0][3](opt[1], opt[2])
	dprint("Options:",*[arg[1]+":"+"&".join([str(value) for value in arg[2:]]) for arg in optqueue],sep="\n  ",flush=True)

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
			dprint("\"Last Resort\" style")
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
	HEIGHT=user32.GetSystemMetrics(79)
	WIDTH=user32.GetSystemMetrics(78)

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
scorefont25=pygame.freetype.SysFont("Linux Biolinum O,Arial,EmojiOne,Symbola,-apple-system",25)

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
	def __init__(self,typ:int=random.randrange(7),x:int=0,y:int=0,rects:list=None,alive:bool=True):
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
		self._rotation=0
		self.alive=alive
		if typ==0:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[0,0],[0,1],[1,0],[1,1]],
				[[0,0],[0,1],[1,0],[1,1]],
				[[0,0],[0,1],[1,0],[1,1]],
				[[0,0],[0,1],[1,0],[1,1]]])
			self.color=(255,255,0)
		elif typ==1:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[0,0],[1,0],[2,0],[0,1]],
				[[0,0],[0,1],[0,2],[1,2]],
				[[0,1],[1,1],[2,1],[2,0]],
				[[0,0],[1,0],[1,1],[1,2]]])
			self.color=(255,127,0)
		elif typ==2:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[0,0],[0,1],[1,1],[2,1]],
				[[1,0],[1,1],[1,2],[0,2]],
				[[0,0],[1,0],[2,0],[2,1]],
				[[1,0],[0,0],[0,1],[0,2]]])
			self.color=(0,0,255)
		elif typ==3:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[0,1],[1,1],[2,1],[3,1]],
				[[2,0],[2,1],[2,2],[2,3]],
				[[0,2],[1,2],[2,2],[3,2]],
				[[1,0],[1,1],[1,2],[1,3]]])
			self.color=(0,255,255)
		elif typ==4:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[0,0],[1,0],[1,1],[2,1]],
				[[1,0],[1,1],[0,1],[0,2]],
				[[0,0],[1,0],[1,1],[2,1]],
				[[1,0],[1,1],[0,1],[0,2]]])
			self.color=(255,0,0)
		elif typ==5:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[2,0],[1,0],[1,1],[0,1]],
				[[0,0],[0,1],[1,1],[1,2]],
				[[2,0],[1,0],[1,1],[0,1]],
				[[0,0],[0,1],[1,1],[1,2]]])
			self.color=(0,255,0)
		elif typ==6:
			if not (type(rects)==list and len(rects)==4):
				self.rects=self.rectmatrix([
				[[1,0],[0,1],[1,1],[2,1]],
				[[0,1],[1,0],[1,1],[1,2]],
				[[0,1],[1,1],[2,1],[1,2]],
				[[1,0],[1,1],[1,2],[2,1]]])
			self.color=(127,0,127)
		else:
			raise ValueError("Invalid block type: "+str(typ))
		del self.x
		del self.y
		if type(rects)==list:
			if len(rects)==4:
				self.rects=rects
			elif len(rects)==1 and not self.alive:
				self.rects=rects
		elif rects!=None:
			raise ValueError("rects can't be %s, it has to be a list with a length of 4.")
		if not self.alive:
			self.die()
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
	def move_oop(self,x:int,y:int,rects:list=None):
		return [[[i[0]+x,i[1]+y] for i in j] for j in (self.rects if rects==None else rects)]
	def rotate(self,clockwise:int):
		self.rotation-=clockwise
		self.rotation%=4
	def rotate_oop(self,clockwise:int):
		return self.rects[(self.rotation-clockwise)%4]
	def die(self):
		self.alive=False
		self.rects=[self.rects[self.rotation]]
		self._rotation=self.rotation
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
			return self.move_oop(-20,movedown-1)[self.rotation]
	def append_rects(self,rects:list):
		try:
			rects[0][0][0]
		except (TypeError,IndexError):
			if not self.alive:
				self.rects[0]+=rects
			else:
				self.rects[self.rotation]+=rects
		else:
			if not self.alive:
				self.rects[0]+=rects[0]
			else:
				for a,b,c,d in rects:
					self.rects[0]+=a
					self.rects[1]+=b
					self.rects[2]+=c
					self.rects[3]+=d
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
	spdslope=41/35
	def __init__(self,mode:int=0,bheight:int=5,blines:int=25):
		self.clock=pygame.time.Clock()
		if mode==1:
			self.blocks=generate_mush(bheight,7)
		else:
			self.blocks=[]
		self.mode=mode
		self.blines=blines	#actually b-lines, but that'd be invalid
		self.clearing=[]
		self.rects2fall=[]
		self.upcoming=sorted(range(7),key=lambda x:random.random())
		self.surface=pygame.Surface((10,20),pygame.HWSURFACE)
	def checklns(self):
		lns_count=0
		deleted=False
		for line in range(20):
			found=True
			for px in range(10):
				if self.check_pos([px,line])!=-1:
					found=False
			if found:
				self.delline(line)
				lns_count+=1
				deleted=True
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
		if deleted and self.mode==1:
			self.checkbmode()
	def checkbmode(self):
		if self.get_cleared()>=self.blines:
			self.ended=True
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
	def fuse_blocks(self):
		newblocks=[Block(i,rects=[[],[],[],[]],alive=False) for i in range(7)]
		for block in self.blocks:
			if not block.alive:
				newblocks[block.typ].append_rects([rect for rect in block.rects[0] if rect!=None])
			else:
				newblocks.append(block)
		wedonotwantthat=([[]],[[],[],[],[]])
		for i in reversed(range(len(newblocks))):
			if newblocks[i].rects in wedonotwantthat:
				del newblocks[i]
		self.blocks=newblocks
	def spawn(self,typ:int=None):
		if self.paused:
			return
		if typ==None:
			typ=self.upcoming.pop(0)
			if len(self.upcoming)==0:
				self.upcoming=sorted(range(7),key=lambda x:random.random())
		block=Block(typ=typ,x=4,y=0)
		for rect in block.rects[block.rotation]:
			if self.check_pos(rect)==-1:
				self.ended=True
		self.blocks.append(block)
	def dontlettemout(self):
		for block in self.blocks:
			block.stayin()
	def move_alive(self,x:int,y:int,die_when_stopped:bool=False):
		forbidden=(-2,-1)
		if self.paused:
			return
		for block in self.blocks:
			if block.alive:
				allowed=all(self.check_pos(rect) not in forbidden for rect in block.move_oop(x,y)[block.rotation])
				if allowed:
					block.move(x,y)
				else:
					if die_when_stopped:
						block.die()
					if x==0 and y>0:
						bubble=0
						while any(self.check_pos(rect) in forbidden for rect in block.move_oop(x,y-bubble)[block.rotation]):
							bubble+=1
						block.move(x,1+y-bubble)
	def rotate_alive(self,clockwise:int):
		if self.paused:
			return
		for block in self.blocks:
			if block.alive:
				if all(self.check_pos(rect) in (0,1) for rect in block.rotate_oop(clockwise)):
					block.rotate(clockwise)
				elif block.alive and all(self.check_pos(rect) in (0,1) for rect in block.move_oop(1,0,[block.rotate_oop(clockwise)])[0]):
					block.rotate(clockwise)
					block.move(1,0)
				elif block.alive and all(self.check_pos(rect) in (0,1) for rect in block.move_oop(0,1,[block.rotate_oop(clockwise)])[0]):
					block.rotate(clockwise)
					block.move(0,1)
				elif block.alive and all(self.check_pos(rect) in (0,1) for rect in block.move_oop(-1,0,[block.rotate_oop(clockwise)])[0]):
					block.rotate(clockwise)
					block.move(-1,0)
	def cycle(self,speed:float):
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
			self.fuse_blocks()
			self.remove_nonesense()
	def remove_nonesense(self):	#yes, I know it's spelled nonsense, but this function removes 'None' rects
		for block in self.blocks:
			for rotation in range(len(block.rects)):
				for i in reversed(range(len(block.rects[rotation]))):
					if block.rects[rotation][i]==None:
						del block.rects[rotation][i]
	def gravity(self,speed:float):
		if self.paused:
			return
		dropped=False
		for block,rot,rect in self.rects2fall:
			block.rects[rot][rect][1]+=1
		self.rects2fall=[]
		if K_DROP:
			if self.startdrop:
				self.movecounter=self.counter
			self.startdrop=False
			speed/=30
		while self.counter>self.movecounter:
			dropped=True
			if not K_DROP:
				self.startdrop=True
			self.movecounter+=speed
			self.move_alive(0,1)
	def repopulate(self):
		if self.paused:
			return
		for block in self.blocks:
			if block.alive:
				return
		self.spawn()
	def check_pos(self,pos:[int,int])->int:
		"""
Returns an int corresponding to what there is at the specified location.
	-2	→	below the field
	None→	anywhere outside the field but below
	-1	→	dead block
	0	→	nothing
	1	→	alive block
If there are multiple blocks on the same field (which shouldn't happen), then the older one gets returned."""
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
			if self.blocks[block].rects==None or all([rect==None for rect in self.blocks[block].rects]):
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
	def get_cleared(self):
		return self.tetrisln*4+self.threeln*3+self.twoln*2+self.oneln

def get_rect(x:float=0,y:float=0,width:float=1,height:float=1):
		return pygame.Rect(math.ceil(x*BLOCK_SIZE),math.ceil(y*BLOCK_SIZE),math.ceil(width*BLOCK_SIZE),math.ceil(height*BLOCK_SIZE))

def generate_mush(height:int=4,intensity:int=7):
	blocks=[[],[],[],[],[],[],[]]
	assert intensity<10 and intensity>0,"Mush intensity can only be smaller than 10 and bigger than 0"
	assert height<18 and height>0,"Mush height can only be smaller than 18 and bigger than 0."
	poss=[[x,y] for x in range(10) for y in range(20-height,20)]
	for _pos in range(0,-10+height*10,10):
		del poss[_pos+random.randrange(0,10)]
	for _rect in range(intensity*height):
		blocks[random.randrange(7)].append(poss.pop(random.randrange(len(poss))))
	return [Block(typ=i,rects=[rects],alive=False) for i,rects in enumerate(blocks) if len(rects)!=0]
			

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
		if text.get_width()>self.surface.get_width():
			text=pygame.transform.smoothscale(text,(self.surface.get_width(),text.get_height()))
		self.surface.fill(self.bgcolor)
		self.surface.blit(text,(self.surface.get_width()//2-text.get_width()//2,self.surface.get_height()//2-text.get_height()//2))
		return self.surface

class MainGame():
	running=False
	speed=0
	_speed=800
	cycle=0
	spdslope=41/35
	mode=0
	bheight=5
	blines=25
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
					upcoming=Block(typ=self.board.upcoming[0],x=0,y=0)
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
	def end(self,state:int=0):
		for line in reversed(range(20)):
			self.draw(curtain=[l for l in range(line,20)],headsup=("Game Over","You Win")[state],show_upcoming=False)
			self.board.clock.tick(30)
		while self.running:
			event=pygame.event.wait()
			if event.type==pygame.KEYDOWN and event.key in (strg["exit"],pygame.K_RETURN):
				self.running=False
	def run(self):
		global K_DROP
		self.running=True
		origspeed=self.speed
		self._speed=800
		for x in range(origspeed):
			self._speed/=self.spdslope
		while self.running:
			if not self.board.paused:
				self.cycle+=self.board.clock.get_time()
				lines=self.board.get_cleared()
				if lines//10>self.speed-origspeed:
					self.speed+=1
					self._speed/=self.spdslope
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
			self.board.cycle(self._speed)
			self.draw()
			if self.board.ended:
				if self.mode==1 and self.board.get_cleared()>=self.blines:
					state=1
				else:
					state=0
				self.end(state)
			self.board.clock.tick(conf["max_fps"])
		self.speed=0
	def menu(self):
		while True:
			self.buttons={}
			self.buttons["settings"]=Button(x=CENTERx,y=CENTERy,txt="Settings")
			self.buttons["start"]=Button(x=CENTERx,y=self.buttons["settings"].rect.top-10,txt="Start",posmeth=(0,-1))
			self.buttons["quit"]=Button(x=CENTERx,y=self.buttons["settings"].rect.bottom+10,txt="Quit",posmeth=(0,1))
			self.draw()
			if self.checkbuttons():
				break
			if self.buttons["start"].pressed:
				self.buttons["start"].pressed=False
				if self.selectmode():
					self.board=Board(self.mode,self.bheight,self.blines)
					self.run()
			elif self.buttons["settings"].pressed:
				self.buttons["settings"].pressed=False
				self.settings()
			elif self.buttons["quit"].pressed:
				self.buttons["quit"].pressed=False
				break
	def selectmode(self):
		gms=["A","B"]	#Game modes
		self.buttons={
			"speed":Button(x=LEFT_SIDE,y=CENTERy-5,txt="Speed: %s"%self.speed,posmeth=(1,-1)),
			"mode":Button(x=LEFT_SIDE,y=CENTERy+5,txt="Mode: %s"%(gms[self.mode]),posmeth=(1,1)),
			"back":Button(x=CENTERx-5,y=BOTTOM_SIDE,txt="Back",posmeth=(-1,-1)),
			"start":Button(x=CENTERx+5,y=BOTTOM_SIDE,txt="Start",posmeth=(1,-1))}
		if self.mode==1:
			self.buttons["height"]=Button(x=self.buttons["mode"].rect.right+10,y=CENTERy+5,txt="Height: %s"%self.bheight,posmeth=(1,1))
			self.buttons["blines"]=Button(x=self.buttons["height"].rect.right+10,y=CENTERy+5,txt="Lines: %s"%self.blines,posmeth=(1,1),font=scorefont25)
		while True:
			self.draw()
			if self.checkbuttons() or self.buttons["back"].pressed:
				return False
			elif self.buttons["start"].pressed:
				return True
			elif self.buttons["speed"].pressed:
				self.buttons["speed"].txt="["+str(self.speed)+"]"
				self.buttons["speed"].render()
				self.draw()
				for inpot in pygame_input(str(self.speed)):
					self.buttons["speed"].txt="["+inpot+"]"
					self.buttons["speed"].render()
					self.draw()
				try:
					self.speed=abs(int(self.buttons["speed"].txt[1:-1]))
				except ValueError:
					pass
				self.buttons["speed"].txt="Speed: "+str(self.speed)
				self.buttons["speed"].render()
				self.buttons["speed"].pressed=False
			elif self.buttons["mode"].pressed:
				self.buttons["mode"].pressed=False
				self.mode+=1
				self.mode%=2
				if self.mode==0:
					del self.buttons["height"]
					del self.buttons["blines"]
				else:
					self.buttons["height"]=Button(x=self.buttons["mode"].rect.right+10,y=CENTERy+5,txt="Height: %s"%self.bheight,posmeth=(1,1))
					self.buttons["blines"]=Button(x=self.buttons["height"].rect.right+10,y=CENTERy+5,txt="Objective: %s"%self.blines,posmeth=(1,1),font=scorefont25)
				self.buttons["mode"].txt="Mode: %s"%(gms[self.mode])
				self.buttons["mode"].render()
			elif self.mode==1 and self.buttons["height"].pressed:
				self.buttons["height"].pressed=False
				self.bheight%=17
				self.bheight+=1
				self.buttons["height"].txt="Height: %s"%self.bheight
				self.buttons["height"].render()
			elif self.mode==1 and self.buttons["blines"].pressed:
				self.buttons["blines"].pressed=False
				self.buttons["blines"].txt="[%s]"%self.blines
				self.buttons["blines"].render()
				self.draw()
				for inpot in pygame_input(str(self.blines)):
					self.buttons["blines"].txt="[%s]"%inpot
					self.buttons["blines"].render()
					self.draw()
				try:
					self.blines=(lambda blines:blines if blines>0 else self.blines)(abs(int(self.buttons["blines"].txt[1:-1])))
				except ValueError:
					pass
				self.buttons["blines"].txt="Objective: %s"%self.blines
				self.buttons["blines"].render()
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
		dprint("Configurations:\n  strg:\n    left:%s\n    right:%s\n    drop:%s\n    idrop:%s\n    rot:%s\n    rot1:%s\n    exit:%s\n    pause:%s\n  fullscreen:%s\n  show_fps:%s\n  max_fps:%s\n  version:%s\n  update_channel:%s\n  update:%s"%(conf["strg"]["left"],conf["strg"]["right"],conf["strg"]["drop"],conf["strg"]["idrop"],conf["strg"]["rot"],conf["strg"]["rot1"],conf["strg"]["exit"],conf["strg"]["pause"],conf["fullscreen"],conf["show_fps"],	conf["max_fps"],conf["version"],conf["update_channel"],conf["update"]))
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

