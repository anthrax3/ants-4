from ants import WorkerAnt
from random import randint

class Cell(object):
	"""Data containers for each location in World"""
	def __init__(self, food, home_scent, food_scent, obstacle, ant):
		self.obstacle = obstacle
		self.food = food
		self.home_scent = home_scent
		self.food_scent = food_scent
		self.ant = ant

	def add_food(self, amt):
		self.food += amt

	def add_home_scent(self, amt):
		self.home_scent += amt

	def add_food_scent(self, amt):
		self.food_scent += amt

	def is_obstacle(self):
		return bool(self.obstacle)

	def is_food(self):
		return bool(self.food)
		

class World(object):
	"""Encapsulation of all ojects"""
	def __init__(self, width, height, settings):
		self.width = width
		self.height = height
		self.settings = settings
		self.cells = [[Cell(0, 0, 0, False, None) for i in xrange(height)] for j in xrange(width)]

		self.counter = 0

		self.ants = {}
		self.spawn_ants()

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
			self.ants[i] = WorkerAnt(self, None, direction, location)
