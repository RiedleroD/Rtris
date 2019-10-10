#!usr/bin/python3
import os,sys,pygame,pygame.gfxdraw,random,time,math,numpy
from pygame.locals import *

pygame.init()
pygame.font.init()
screen=pygame.display.set_mode(pygame.display.list_modes()[0])
pygame.display.set_caption("RTris")
pygame.display.toggle_fullscreen()

BORDER_WIDTH=5
BLACK=(0,0,0)
WHITE=(255,255,255)
HEIGHT=screen.get_height()
WIDTH=screen.get_width()
SIZE=math.sqrt(HEIGHT**2+WIDTH**2)
LEFT_SIDE=0+BORDER_WIDTH
RIGHT_SIDE=WIDTH-BORDER_WIDTH
TOP_SIDE=0+BORDER_WIDTH
BOTTOM_SIDE=HEIGHT-BORDER_WIDTH
CENTERx=WIDTH//2
CENTERy=HEIGHT//2
CENTER=[CENTERx,CENTERy]
BLOCK_SIZE=HEIGHT/20

scorefont=pygame.font.SysFont("Arial",30)

class Block():
	alive=True
	def __init__(self,typ:int=random.randrange(7),x=0,y=0):
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
		x=self.x
		y=self.y
		omat=[[[x,y],[x,y],[x,y],[x,y]],
			[[x,y],[x,y],[x,y],[x,y]],
			[[x,y],[x,y],[x,y],[x,y]],
			[[x,y],[x,y],[x,y],[x,y]]]
		return numpy.add(omat,matrix).tolist()
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
			if func(rect):
				return True
		return False
	def all_rects(self,func):
		for rect in self.rects[self.rotation]:
			if not func(rect):
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
	def __init__(self):
		self.blocks=[]
		self.counter=1
		self.clock=pygame.time.Clock()
		self.dropped=0
		self.harddrop=0
		self.tetrisln=0
		self.threeln=0
		self.twoln=0
		self.oneln=0
		self.score=0
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
	def delline(self,line):
		for block in self.blocks:
			if not block.alive:
				rects2del=[]
				rects2fall=[]
				offset=0
				for rot in range(len(block.rects)):
					for rect in range(len(block.rects[rot])):
						if block.rects[rot][rect][1]==line:
							rects2del.append([rot,rect])
						elif block.rects[rot][rect][1]<line:
							rects2fall.append([rot,rect])
				for rot,rect in rects2fall:
					block.rects[rot][rect][1]+=1
				for rot,rect in rects2del:
					del block.rects[rot][rect-offset]
					offset+=1
	def get_alive(self):
		for block in self.blocks:
			if block.alive:
				return block
	def spawn(self,typ:int=None):
		if typ==None:
			typ=random.randrange(7)
		block=Block(typ=typ,x=4,y=0)
		for rect in block.rects[block.rotation]:
			if self.check_pos(rect)==-1:
				end(self.calcscore())
		self.blocks.append(block)
	def dontlettemout(self):
		for block in self.blocks:
			block.stayin()
	def move_alive(self,x,y):
		for block in self.blocks:
			if block.alive:
				allowed=True
				for rect in block.move_oop(x,y)[block.rotation]:
					if self.check_pos(rect)==-1:
						allowed=False
				if allowed:
					block.move(x,y)
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
		self.dontlettemout()
		if self.counter%round(50/(2**(speed/5)))==0:
			self.gravity()
		self.repopulate()
		self.kill_blocks()
		self.checklns()
		self.cleanup()
		if self.counter%3==0:
			self.keyfunc()
		self.counter+=1
	def kill_blocks(self):
		for block in self.blocks:
			if block.alive:
				for pos in block.get_poss():
					if self.check_pos([pos[0],pos[1]]) in (-1,-2):
						block.move(0,-1)
						block.die()
						self.dropped+=1
						break
	def gravity(self):
		if K_UP:
			return
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
	def keyfunc(self):
		if K_UP:
			self.move_alive(0,1)
	def cleanup(self):
		try:
			for block in range(len(self.blocks)):
				for rot in self.blocks[block].rects:
					if len(rot)==0:
						del self.blocks[block]
		except IndexError:
			pass
	def draw_score(self):
		score=self.calcscore()
		lns=self.tetrisln*4+self.threeln*3+self.twoln*2+self.oneln
		screen.blit(scorefont.render("Score: "+str(score),True,(255,255,255)),(CENTERx,0))
		screen.blit(scorefont.render("Lines: "+str(lns),True,(255,255,255)),(CENTERx,CENTERy))
		screen.blit(scorefont.render("Level: "+str(speed),True,(255,255,255)),(CENTERx,BOTTOM_SIDE-30))

def get_rect(x=0,y=0,width=1,height=1):
		return pygame.Rect(round(x*BLOCK_SIZE),round(y*BLOCK_SIZE),round(width*BLOCK_SIZE),round(height*BLOCK_SIZE))

def draw():
	screen.fill((0,0,0))
	board.draw_score()
	pygame.draw.rect(screen,(100,100,100),get_rect(0,0,10,20))
	for block in board.blocks:
		if block.alive:
			for x,y in block.get_shadow(board):
				pygame.draw.rect(screen,(125,125,125),get_rect(x,y,1,1))
		for x,y in block.rects[block.rotation]:
			pygame.draw.rect(screen,block.color,get_rect(x,y,1,1))
	pygame.display.flip()

def end(score):
	print("Final Score:",score)
	quit()

board=Board()
board.spawn(2)

running=True
K_LEFT=False
K_UP=False
K_DOWN=False
K_RIGHT=False
K_PAGEDOWN=False
K_PAGEUP=False
speed=0
cycle=0
while running:
	cycle+=1
	if cycle%3000==0:
		speed+=1
	for event in pygame.event.get():
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_q:
				running=False
			elif event.key==pygame.K_LEFT:
				board.move_alive(-1,0)
			elif event.key==pygame.K_RIGHT:
				board.move_alive(1,0)
			elif event.key==pygame.K_UP:
				K_UP=True
			elif event.key==pygame.K_DOWN:
				board.counter=1
				block=board.get_alive()
				while block.alive:
					block.move(0,1)
					board.kill_blocks()
				board.harddrop+=1
			elif event.key==pygame.K_PAGEUP:
				board.rotate_alive(1)
			elif event.key==pygame.K_PAGEDOWN:
				board.rotate_alive(-1)
		elif event.type==pygame.KEYUP:
			if event.key==pygame.K_UP:
				K_UP=False
	board.cycle(speed)
	draw()
	board.clock.tick(60)
	
