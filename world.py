from ants import WorkerAnt
from random import randint, choice
from pygame import display
from display import Entity
from constants import WHITE
from math import sqrt

class Cell(Entity):
	"""Data containers for each location in World"""
	def __init__(self, world, i, j, cell_size):
		self.obstacle = False
		self.food = 0
		self.home_scent = 0
		self.food_scent = 0
		self.ant = None
		self.home = False
		super(Cell, self).__init__(world, (i, j), [cell_size]*2, world.images["cell"])

	def add_food(self, amt):
		self.food += amt

	def add_home_scent(self, amt):
		self.home_scent += amt

	def add_food_scent(self, amt):
		self.food_scent += amt

	def get_food(self, amt):
		if self.food < amt:
			food = self.food
			self.food = 0
			return food
		else:
			self.food -= amt
			return amt

	def is_obstacle(self):
		return bool(self.obstacle)

	def is_home(self):
		return bool(self.home)

	def is_food(self):
		return bool(self.food)

	def has_ant(self):
		return bool(self.ant)

	def make_home(self):
		self.home = True

	def make_obstacle(self):
		self.obstacle = True

	def render(self):
		if self.is_food():
			index = 3
		elif self.is_obstacle():
			index = 2
		elif self.is_home():
			index = 1
		else:
			index = 0

		self.image.set_alpha(255)

		super(Cell, self).render(index)

		if self.home_scent > 0:
			index = 4
			self.image.set_alpha(self.home_scent*32)
		elif self.food_scent > 0:
			index = 5
			self.image.set_alpha(self.food_scent)

		super(Cell, self).render(index)

		

class World():
	"""Encapsulation of all objects"""
	def __init__(self, width, height, cell_size, images, settings):
		self.width = width
		self.height = height
		self.cell_size = cell_size
		self.images = images
		self.settings = settings

		self.canvas = display.set_mode((self.width*self.cell_size, self.height*self.cell_size))
		self.convert_images()

		self.cells = [[Cell(self, i, j, self.cell_size) for j in xrange(height)] for i in xrange(width)]

		self.counter = 0

		self.ants = {}
		self.spawn_ants()
		for i in xrange(10):
			self.spawn_foodsource()
		self.create_home()

	def __getitem__(self, location):
		x, y = location
		return self.cells[x][y]

	def convert_images(self):
		for name in self.images:
			self.images[name] = self.images[name].convert()

	def advance(self):
		for i in self.ants:
			self.ants[i].task_manager.make_decision()

	def spawn_ants(self):
		for i in xrange(self.settings["no_of_ants"]):
			direction = randint(0,7)
			location = [randint(1,self.width), randint(1,self.height)]
			self.ants[i] = WorkerAnt(self, self.images["ant"], direction, location)

	def spawn_foodsource(self):
		x, y = randint(0,self.width-1), randint(0,self.height-1)
		for i in xrange(randint(20, 50)):
			dx = randint(-3,3)
			dy = choice([-1,1])*randint(0, int(sqrt(9-dx**2)))
			self.cells[(x+dx)%self.width][(y+dy)%self.height].add_food(1)

	def create_home(self):
		n = self.settings["home_size"]
		x, y = self.width/2 -5, self.height/2 -5
		for i in xrange(n):
			for j in xrange(n):
				self.cells[x+i-1][y+j-1].make_home()

	def render(self):
		self.canvas.fill(WHITE)

		for cells in self.cells:
			for cell in cells:
				cell.render()

		for ant in self.ants.values():
			ant.render()

		display.update((0, 0), (self.width*self.cell_size, self.height*self.cell_size))