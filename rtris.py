#!usr/bin/python3
import os,sys,pygame,pygame.gfxdraw,random,time,math,numpy

pygame.init()
pygame.font.init()
screen=pygame.display.set_mode(pygame.display.list_modes()[0],pygame.FULLSCREEN)
pygame.display.set_caption("RTris")

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

scorefont=pygame.font.SysFont("Linux Biolinum O,Arial",30)

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
	counter=1
	dropped=0
	harddrop=0
	tetrisln=0
	threeln=0
	twoln=0
	oneln=0
	score=0
	paused=False
	ended=False
	def __init__(self):
		self.clock=pygame.time.Clock()
		self.blocks=[]
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
		if not self.paused:
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
		if self.ended:
			return False
		else:
			return True
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
			self.move_alive(0,1,die_when_stopped=True)
	def cleanup(self):
		try:
			for block in range(len(self.blocks)):
				for rot in self.blocks[block].rects:
					if len(rot)==0:
						del self.blocks[block]
		except IndexError:
			pass
	def draw(self,speed:int):
		self.surface.fill((100,100,100))
		score=self.calcscore()
		lns=self.tetrisln*4+self.threeln*3+self.twoln*2+self.oneln
		scoretxt=scorefont.render("Score: "+str(score),True,(255,255,255))
		lnstxt=scorefont.render("Lines: "+str(lns),True,(255,255,255))
		tetristxt=scorefont.render("Tetris': "+str(self.tetrisln),True,(255,255,255))
		threetxt=scorefont.render("Triples: "+str(self.threeln),True,(255,255,255))
		twotxt=scorefont.render("Doubles: "+str(self.twoln),True,(255,255,255))
		onetxt=scorefont.render("Singles: "+str(self.oneln),True,(255,255,255))
		leveltxt=scorefont.render("Level: "+str(speed),True,(255,255,255))
		screen.blit(scoretxt,(11*BLOCK_SIZE,3*BLOCK_SIZE))
		screen.blit(lnstxt,(11*BLOCK_SIZE,4*BLOCK_SIZE))
		screen.blit(leveltxt,(11*BLOCK_SIZE,5*BLOCK_SIZE))
		screen.blit(tetristxt,(11*BLOCK_SIZE,6*BLOCK_SIZE))
		screen.blit(threetxt,(11*BLOCK_SIZE,7*BLOCK_SIZE))
		screen.blit(twotxt,(11*BLOCK_SIZE,8*BLOCK_SIZE))
		screen.blit(onetxt,(11*BLOCK_SIZE,9*BLOCK_SIZE))
	def pause(self):
		self.paused=not self.paused

def get_rect(x:float=0,y:float=0,width:float=1,height:float=1):
		return pygame.Rect(math.ceil(x*BLOCK_SIZE),math.ceil(y*BLOCK_SIZE),math.ceil(width*BLOCK_SIZE),math.ceil(height*BLOCK_SIZE))

class Button():
	pressed=False
	color=(255,255,255)
	txtcolor=(0,0,0)
	def __init__(self,x:int=0,y:int=0,width:int=WIDTH//10,height:int=HEIGHT//15,bgcolor:(int,int,int)=(255,255,255),txt:str="",txtcolor:(int,int,int)=(0,0,0),font:pygame.font.Font=scorefont):
		self.color=bgcolor
		self.text=font.render(txt,True,txtcolor)
		self.surface=pygame.Surface((width,height))
		self.surface.fill(bgcolor)
		self.surface.blit(self.text,(self.surface.get_width()//2-self.text.get_width()//2,self.surface.get_height()//2-self.text.get_height()//2))
		self.rect=pygame.Rect(x-self.surface.get_width()//2,y-self.surface.get_height()//2,width,height)
	def press(self):
		self.pressed=True
	def collideswith(self,pos:[int,int]):
		return self.rect.collidepoint(pos)

class MainGame():
	running=False
	speed=0
	cycle=0
	def __init__(self):
		self.board=Board()
		self.screen=screen
		self.buttons={}
	def draw(self,curtain:list=[],headsup:str="",show_upcoming:bool=True):
		self.screen.fill((0,0,0))
		if self.running:
			if self.board.paused:
				text=scorefont.render("PAUSED",True,(255,255,255))
				self.screen.blit(text,(CENTERx-text.get_width()//2,CENTERy-text.get_height()//2))
			else:
				self.board.draw(self.speed)
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
				
				for block in self.board.blocks:
					if block.alive:
						for x,y in block.get_shadow(self.board):
							pygame.draw.rect(self.board.surface,(125,125,125),(x,y,1,1))
					for x,y in block.rects[block.rotation]:
						pygame.draw.rect(self.board.surface,block.color,(x,y,1,1))
				for line in curtain:
					pygame.draw.rect(self.board.surface,(0,0,0),(0,line,10,1))
				self.screen.blit(pygame.transform.scale(self.board.surface,(HEIGHT//2,HEIGHT)),(0,0))
				if headsup!="" and type(headsup)==str:
					hutxt=scorefont.render(headsup,True,(255,255,255),(0,0,0))
					self.screen.blit(hutxt,(5*BLOCK_SIZE-hutxt.get_width()//2,CENTERy-hutxt.get_height()//2))
		else:
			for name,button in self.buttons.items():
				self.screen.blit(button.surface,button.rect)
		pygame.display.flip()
	def end(self):
		for line in reversed(range(20)):
			self.draw(curtain=[l for l in range(line,20)],headsup="Game Over",show_upcoming=False)
			self.board.clock.tick(30)
		while True:
			event=pygame.event.wait()
			if event.type==pygame.KEYDOWN and event.key in (pygame.K_q,pygame.K_RETURN,pygame.K_ESCAPE):
				break
	def run(self):
		global K_UP
		self.running=True
		while self.running:
			self.cycle+=1
			if self.cycle%3000==0:
				self.speed+=1
			for event in pygame.event.get():
				if event.type==pygame.KEYDOWN:
					if event.key==pygame.K_q:
						self.running=False
					elif event.key==pygame.K_LEFT:
						self.board.move_alive(-1,0)
					elif event.key==pygame.K_RIGHT:
						self.board.move_alive(1,0)
					elif event.key==pygame.K_UP:
						K_UP=True
					elif event.key==pygame.K_DOWN:
						self.board.counter=1
						block=self.board.get_alive()
						while block.alive:
							block.move(0,1)
							self.board.kill_blocks()
						self.board.harddrop+=1
					elif event.key==pygame.K_PAGEUP:
						self.board.rotate_alive(1)
					elif event.key==pygame.K_PAGEDOWN:
						self.board.rotate_alive(-1)
					elif event.key==pygame.K_p or event.key==pygame.K_PAUSE:
						self.board.pause()
				elif event.type==pygame.KEYUP:
					if event.key==pygame.K_UP:
						K_UP=False
			self.board.cycle(self.speed)
			self.draw()
			if self.board.ended:
				self.end()
				return
			self.board.clock.tick(60)
	def menu(self):
		self.buttons["start"]=Button(x=CENTERx,y=CENTERy,txt="Start")
		self.buttons["settings"]=Button(x=CENTERx,y=CENTERy+self.buttons["start"].rect.height*1.1,txt="Settings")
		while True:
			self.draw()
			if self.checkbuttons():
				break
			if self.buttons["start"].pressed:
				self.buttons["start"].pressed=False
				self.run()
	def checkbuttons(self):
		for event in pygame.event.get():
			if event.type==pygame.MOUSEBUTTONUP and event.button==1:
				for name,button in self.buttons.items():
					if button.collideswith(event.pos):
						button.press()
			elif event.type==pygame.KEYDOWN and event.key==pygame.K_q:
				return True
		return False



K_UP=False

if __name__=="__main__":
	game=MainGame()
	game.menu()
