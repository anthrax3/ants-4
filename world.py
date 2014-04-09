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
		"""Get "amt" amount of food if available else returns whatever food is available"""
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

	def has_food(self):
		return True if self.food > 0 else False

	def make_home(self):
		self.home = True

	def make_obstacle(self):
		self.obstacle = True

	def evaporate_scent(self, rate):
		"""Evaporates scent ( decay law )"""
		self.food_scent *= rate
		self.home_scent *= rate
		if self.food_scent < .3:
			self.food_scent = 0
		if self.home_scent < .3:
			self.home_scent = 0

	def render(self):
		"""Changes "index" to render the cell according to what it represents 
		(home, food, etc) and calls the super class
		Also renders scent levels with transparency depending on its strength
		"""
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
			self.image.set_alpha(self.home_scent)
		super(Cell, self).render(index)
		
		if self.food_scent > 0:
			index = 5
			self.image.set_alpha(self.food_scent)
		super(Cell, self).render(index)

class World():
	"""Encapsulation of all objects in the simulation"""
	def __init__(self, width, height, cell_size, images, settings):
		"""
		- Initialise the screen
		- Fill screen with "Cells"
		- Convert images to pygame format
		- Spawn ants, food sources, obstacles, ant home, etc
		"""
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
		for i in xrange(1):
			self.spawn_foodsource()
		self.create_home()

	def __getitem__(self, location):
		"""Returns the cell at the location"""
		x, y = location
		return self.cells[x][y]

	def convert_images(self):
		"""Convert images to pygame optimised format"""
		for name in self.images:
			self.images[name] = self.images[name].convert()

	def advance(self):
		"""Advance the simulation by one step
			- Update te ants
			- Evaporate all scents
		"""
		for i in self.ants:
			self.ants[i].task_manager.make_decision()

		self.evaporate_scent()

	def spawn_ants(self):
		"""Spawns ants"""
		for i in xrange(self.settings["no_of_ants"]):
			direction = randint(0,7)
			location = [randint(1,self.width), randint(1,self.height)]
			location = [self.width/2-10, self.height/2-10]
			self.ants[i] = WorkerAnt(self, self.images["ant"], direction, location)

	def spawn_foodsource(self):
		"""Spawns food sources"""
		x, y = randint(0,self.width-1), randint(0,self.height-1)
		for i in xrange(randint(2000, 5000)):
			dx = randint(-3,3)
			dy = choice([-1,1])*randint(0, int(sqrt(9-dx**2)))
			self.cells[(x+dx)%self.width][(y+dy)%self.height].add_food(1)

	def create_home(self):
		"""Create a nest for ants"""
		n = self.settings["home_size"]
		x, y = self.width/2 -5, self.height/2 -5
		for i in xrange(n):
			for j in xrange(n):
				self.cells[x+i-1][y+j-1].make_home()

	def render(self):
		"""Draws the world on the screen"""
		self.canvas.fill(WHITE)

		for cells in self.cells:
			for cell in cells:
				cell.render()

		for ant in self.ants.values():
			ant.render()

		display.update((0, 0), (self.width*self.cell_size, self.height*self.cell_size))

	def evaporate_scent(self):
		"""Evaporates all scent ( uses decay law ) at a rate defined in settings"""
		for cells in self.cells:
			for cell in cells:
				cell.evaporate_scent(self.settings["evaporation_rate"])