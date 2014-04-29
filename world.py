from ants import WorkerAnt, SoldierAnt
from random import randint, choice
from pygame import display, Surface
from display import Entity
from constants import GREEN, DIRECTIONS, YELLOW
from math import sqrt

class Cell(Entity):
	"""
	Data containers for each location in World
	"""
	def __init__(self, world, i, j, cell_size):
		self.obstacle = False
		self.food = 0
		self.home_scent = {}
		self.food_scent = {}
		self.ant = None
		self.home = -1
		super(Cell, self).__init__(world, (i, j), [cell_size]*2, world.images["cell"])

	## Adds food to the cell
	# @param amt The amount of food to be added
	def add_food(self, amt):
		self.food += amt
		return self

	## Adds home scent to the cell
	# @param amt The amount of scent to add
	# @param id The id of the nest the ant belongs to
	def add_home_scent(self, amt, id):
		"""
		adds home scent for the particular ant colony (depending on the id)
		"""
		if not id in self.home_scent:
			self.home_scent[id] = 0
		if not self.is_obstacle():
			self.home_scent[id] += amt
		else:
			self.home_scent[id] = 0
		return self

	## Adds food scent to the cell
	# @param amt The amount of scent to add
	# @param id The id of the nest the ant belongs to
	def add_food_scent(self, amt, id):
		if not id in self.food_scent:
			self.food_scent[id] = 0
		if not self.is_obstacle():
			self.food_scent[id] += amt
		else:
			self.food_scent[id] = 0
		return self

	## Gets food from the cell
	# @param amt The amount of food taken
	# Returns an amount of food if available
	def get_food(self, amt):
		if self.food < amt:
			food = self.food
			self.food = 0
			return food
		else:
			self.food -= amt
			return amt

	## Get the amount of food scent in the cell
	# @param id The id of the nest the ant belongs to
	def get_food_scent(self, id):
		return self.food_scent[id] if id in self.food_scent else 0

	## Get the amount of home scent in the cell
	# @param id The id of the nest the ant belongs to
	def get_home_scent(self, id):
		"""
		get home scent for the colony given by id
		"""
		return self.home_scent[id] if id in self.home_scent else 0

	def is_obstacle(self):
		"""
		Returns wheather the cell is a obstacle or not
		"""
		return bool(self.obstacle)

	def is_home(self):
		"""
		Returns wheather the cell is a home or not
		(independent of which colony the ant belongs)
		"""
		return self.home != -1

	## Checks if the cell is home cell of the ant
	# @param id The id of the nest the ant belongs to
	def is_own_home(self, id):
		return self.home == id

	## Checks if the home cell is of the enemy ants
	# @param id The id of the nest the ant belongs to
	def is_enemy_home(self, id):
		return self.is_home() and not self.is_own_home(id)

	## Checks if the cell has food (but should not be its own home)
	# @param id The id of the nest the ant belongs to
	def is_food(self, id):
		return bool(self.food) and not self.is_own_home(id)

	def has_ant(self):
		"""
		Check if the particular cell has an ant
		"""
		return bool(self.ant)

	def has_food(self):
		"""
		Checks if the cell has food
		"""
		return True if self.food > 0 else False

	## Convert the cell into a home cell
	# @param id The id of the nest
	def make_home(self, id):
		self.home = id
		return self

	def make_obstacle(self):
		"""
		Convert the cell into an obstacle if the cell is empty
		"""
		if not self.is_home() and not self.has_ant() and not self.has_food():
			self.obstacle = True
			for id in self.food_scent:
				self.food_scent[id] = 0
			for id in self.home_scent:
				self.home_scent[id] = 0
		return self

	def remove_obstacle(self):
		"""
		Removes obstacle from the cell
		"""
		self.obstacle = False
		return self

	## Evaporates the scent
	# @param rate The rate at which evporation happens
	# Follows the decay law
	def evaporate_scent(self, rate):
		for id in self.food_scent:
			food_scent_delta = self.food_scent[id] * rate
			self.food_scent[id] -= food_scent_delta
			if self.food_scent < .3:
				self.food_scent[id] = 0
		for id in self.home_scent:
			home_scent_delta = self.home_scent[id] * rate
			self.home_scent[id] -= home_scent_delta
			if self.home_scent[id] < .3:
				self.home_scent[id] = 0
		return self

	def nearby(self):
		"""
		Returns all nearby 8 cells
		"""
		x, y = self.location
		cells = []
		for dx, dy in DIRECTIONS:
			X, Y = (x+dx)%self.world.width, (y+dy)%self.world.height
			cells.append(self.world[(X, Y)])
		return cells

	def get_max_home_scent(self):
		"""
		Get the maximum home scent values amongst
		the scents of all colonies
		"""
		scent = self.home_scent.values()
		return max(scent) if scent else 0

	def get_max_food_scent(self):
		"""
		Get the maximum food scent values amongst
		the scents of all colonies
		"""
		scent = self.food_scent.values()
		return max(scent) if scent else 0

	def render(self):
		"""
		Extends the base class method
		Changes "index" to render the cell according to what it represents 
		(home, food, etc) and calls the super class
		Also renders scent levels with transparency depending on its strength
		"""
		self.image.set_alpha(255)
		if self.has_food():
			super(Cell, self).render(3)
		elif self.is_obstacle():
			super(Cell, self).render(2)
		elif self.has_food():
			super(Cell, self).render(4)

		max_home_scent = self.get_max_home_scent()
		if max_home_scent > 0:
			self.image.set_alpha(max_home_scent)
			super(Cell, self).render(4)
		
		max_food_scent = self.get_max_food_scent()
		if any(self.food_scent.values()):
			self.image.set_alpha(max_food_scent)
			super(Cell, self).render(5)
		return self

class Nest(Entity):
	"""
	Encapsulates a colony of ants
	"""
	def __init__(self, world, id, size, location, ant_count):
		self.id = id
		self.size = size
		self.world = world
		self.ant_count = ant_count
		super(Nest, self).__init__(world, location, size, None)
		self.image = Surface(self.size)
		self.image.fill(YELLOW)
		self.image.set_alpha(196)
		self.spawn_ants()
		self.mark_home()

	def mark_home(self):
		"""
		Converts the cell at its location to its nest
		"""
		width, height = self.size
		width /= self.world.settings["cell_size"]
		height /= self.world.settings["cell_size"]
		x, y = self.location
		for i in range(width):
			for j in range(height):
				self.world[(x+i,y+j)].make_home(self.id)

	def spawn_ants(self):
		"""
		Creates instances of ants and adds them into the world
		"""
		for ant in self.ant_count:
			x, y = self.location
			width, height = self.size
			for i in range(self.ant_count[ant]):
				direction = randint(1,8)
				location = x+randint(0,width/self.world.settings["cell_size"]), y+randint(0,height/self.world.settings["cell_size"])
				new_ant = ant(self.world, self.world.images["ant"], direction, location, self.id)
				self.world.add_ant(new_ant)

		

class World():
	"""
	Encapsulation of all objects in the simulation
	"""
	def __init__(self, width, height, images, settings):
		"""
		- Initialise the screen
		- Fill screen with "Cells"
		- Convert images to pygame format
		- Spawn ants, food sources, obstacles, ant home, etc
		"""
		self.settings = settings
		self.width = width
		self.height = height
		self.cell_size = settings["cell_size"]
		self.images = images

		self.canvas = display.set_mode((self.width*self.cell_size, self.height*self.cell_size))
		self.convert_images()

		self.cells = [[Cell(self, i, j, self.cell_size) for j in xrange(height)] for i in xrange(width)]

		self.counter = 0

		self.ants = {}
		self.nests = {}
		# self.spawn_worker_ants()
		# self.spawn_soldier_ants()
		self.create_walls()
		for i in xrange(4):
			self.spawn_foodsource()
		# self.create_home()
		self.spawn_colonies(2)

	def __getitem__(self, location):
		"""
		Returns the cell at the location
		"""
		x, y = location
		return self.cells[x%self.width][y%self.height]

	def convert_images(self):
		"""
		Convert images to pygame optimised format
		"""
		for name in self.images:
			self.images[name] = self.images[name].convert()

	def advance(self):
		"""
		Advance the simulation by one step
			- Update te ants
			- Evaporate all scents
		"""
		for i in self.ants:
			self.ants[i].task_manager.make_decision()

		self.evaporate_scent()
		return self

	def add_ant(self, ant):
		"""
		add a new ant into the world
		"""
		self.ants[self.counter] = ant
		self.counter += 1

	def spawn_foodsource(self):
		"""
		Spawns food sources
		"""
		x, y = randint(0,self.width-1), randint(0,self.height-1)
		for i in xrange(randint(2000, 5000)):
			dx = randint(-3,3)
			dy = choice([-1,1])*randint(0, int(sqrt(9-dx**2)))
			self.cells[(x+dx)%self.width][(y+dy)%self.height].add_food(1)

	def spawn_colonies(self, n=1):
		"""
		Creates colonies of ants
		"""
		for i in xrange(n):
			size = [self.settings["home_size"]*self.settings["cell_size"]]*2
			location = (
				randint(0, self.width - self.settings["home_size"]),
				randint(0, self.height - self.settings["home_size"])
				)
			nest = Nest(self, i, size, location, self.get_ant_count())
			self.nests[i] = nest

	def get_ant_count(self):
		"""
		Returns a list of no. of different types of ants
		"""
		return { 
			WorkerAnt: 100,
			SoldierAnt: 5
		}

	def create_walls(self):
		"""
		Generates obstacles at the edges
		(otherwise the ants jump from one edge to another)
		"""
		for i in xrange(self.width):
			self[(i, 0)].make_obstacle()
			self[(i, self.height-1)].make_obstacle()

		for j in xrange(self.height):
			self[(0, j)].make_obstacle()
			self[(self.width-1, j)].make_obstacle()

	def render(self):
		"""
		Draws the world and all its entities on the screen
		"""
		self.canvas.fill(GREEN)

		for cells in self.cells:
			for cell in cells:
				cell.render()

		for nest in self.nests.values():
			nest.render()

		for ant in self.ants.values():
			ant.render()

		display.update((0, 0), (self.width*self.cell_size, self.height*self.cell_size))
		return self

	def evaporate_scent(self):
		"""
		Evaporates all scent ( uses decay law ) at a rate defined in settings
		"""
		for cells in self.cells:
			for cell in cells:
				cell.evaporate_scent(self.settings["evaporation_rate"])
		return self