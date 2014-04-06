from constants import DIRECTIONS
from task_manager import TaskManager, Explore, TakeFood
from display import Entity

class Ant(Entity):
	"""Base Class for Ants"""
	def __init__(self, world, image, direction, location):
		super(Ant, self).__init__(world, location, [world.cell_size]*2, image)
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

	def render(self):
		super(Ant, self).render(self.direction)

	def here(self):
		return self.world[self.location]

	def behind(self):
		return self.world[self.neighbour(self.direction + 4)]

	def ahead(self):
		return self.world[self.neighbour(self.direction)]

	def ahead_left(self):
		return self.world[self.neighbour(self.direction - 1)]

	def ahead_right(self):
		return self.world[self.neighbour(self.direction + 1)]

	def __nonzero__(self):
		return True


class WorkerAnt(Ant):
	"""WorkerAnt"""
	def __init__(self, world, image, direction, location):
		Ant.__init__(self, world, image, direction, location)
		self.task_manager = TaskManager()
		self.task_manager.add_task(Explore(self))
		self.task_manager.add_task(TakeFood(self))
		self.task_manager.set_active_task("explore")