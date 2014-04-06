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
		super(Cell, self).__init__(world, (i, j), [cell_size]*2, world.images["grass"])

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

	def is_food(self):
		return bool(self.food)

	def has_ant(self):
		return bool(self.ant)

	def render(self):
		if self.is_food():
			self.image = self.world.images["food"]
		elif self.is_obstacle():
			raise NotImplementedError
		else:
			self.image = self.world.images["grass"]
		super(Cell, self).render()
		

class World():
	"""Encapsulation of all objects"""
	def __init__(self, width, height, cell_size, images, settings):
		self.width = width
		self.height = height
		self.cell_size = cell_size
		self.images = images
		self.settings = settings

		self.canvas = display.set_mode((self.width*self.cell_size, self.height*self.cell_size))

		self.cells = [[Cell(self, i, j, self.cell_size) for j in xrange(height)] for i in xrange(width)]

		self.counter = 0

		self.ants = {}
		self.spawn_ants()
		self.spawn_foodsource()

	def __getitem__(self, location):
		x, y = location
		return self.cells[x][y]

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

	def render(self):
		self.canvas.fill(WHITE)

		for cells in self.cells:
			for cell in cells:
				cell.render()

		for ant in self.ants.values():
			ant.render()

		display.update((0, 0), (self.width*self.cell_size, self.height*self.cell_size))