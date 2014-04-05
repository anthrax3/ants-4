from constants import DIRECTIONS
from task_manager import TaskManager, Explore

class Ant(object):
	"""Base Class for Ants"""
	def __init__(self, world, image, direction, location):
		self.world = world
		self.image = image
		self.direction = direction
		self.location = location

	def neighbour(self, direction):
		x, y = self.location
		dx, dy = DIRECTIONS[direction%8]
		return (x+dx)%self.world.width, (y+dy)%self.world.height

	def move(self):
		new_location = self.neighbour(self.direction)		
		self.location = new_location

	def turn(self, n):
		self.direction = (self.direction + n) % 8

class WorkerAnt(Ant):
	"""WorkerAnt"""
	def __init__(self, world, image, direction, location):
		super(WorkerAnt, self).__init__(world, image, direction, location)
		self.task_manager = TaskManager()
		self.task_manager.add_task(Explore(self))
		self.task_manager.set_active_task("explore")