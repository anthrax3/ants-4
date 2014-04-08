from constants import DIRECTIONS
from task_manager import TaskManager, Explore, TakeFood, FollowHomeTrail, FollowFoodTrail, DropFood
from display import Entity
from random import choice, randint

class Ant(Entity):
	"""Base Class for Ants"""
	def __init__(self, world, image, direction, location):
		super(Ant, self).__init__(world, location, [world.cell_size]*2, image)
		self.world = world
		self.image = image
		self.direction = direction
		self.location = location
		self.food = 0
		self.food_scent_strength = 0
		self.home_scent_strength = 0

	def neighbour(self, direction):
		x, y = self.location
		dx, dy = DIRECTIONS[(self.direction + direction)%8]
		return (x+dx)%self.world.width, (y+dy)%self.world.height

	def move(self):
		new_location = self.neighbour(0)		
		self.location = new_location
		self.behind().ant = None
		if not any([self.behind().is_obstacle(), self.behind().is_food(), self.behind().is_home()]):
			self.behind().add_home_scent(self.home_scent_strength)
			self.behind().add_food_scent(self.food_scent_strength) 
		self.here().ant = self

	def random_move(self):
		if randint(1,8) == 1:
			self.turn( choice([-1, 1]) )
		else:
			self.move()

	def reduce_home_scent(self, amt=1):
		self.home_scent_strength = max(0, self.home_scent_strength-amt)
		return self

	def reduce_food_scent(self, amt=1):
		self.food_scent_strength = max(0, self.food_scent_strength-amt)
		return self

	def turn(self, n):
		self.direction = (self.direction + n) % 8

	def render(self):
		if self.has_food():
			super(Ant, self).render(8)
		else:
			super(Ant, self).render(self.direction)

	def here(self):
		return self.world[self.location]

	def behind(self):
		return self.world[self.neighbour(4)]

	def ahead(self):
		return self.world[self.neighbour(0)]

	def ahead_left(self):
		return self.world[self.neighbour(-1)]

	def ahead_right(self):
		return self.world[self.neighbour(1)]

	def locate_food_nearby(self):
		directions = []
		if self.ahead().has_food():
			directions.append(0)
		else:
			for i in xrange(1, 8):
				if self.world[self.neighbour(i)].has_food():
					directions.append(i) 

		if directions:
			return choice(directions)
		else:
			return None

	def locate_home_nearby(self):
		directions = []
		if self.ahead().is_food():
			directions.append(0)
		else:
			for i in xrange(1, 8):
				if self.world[self.neighbour(i)].is_home():
					directions.append(i) 

		if directions:
			return choice(directions)
		else:
			return None

	def locate_home_scent_nearby(self):
		directions = []
		if self.ahead().home_scent > 0:
			directions.append(0)
		else:
			for i in xrange(-2, 3):
				if self.world[self.neighbour(i)].home_scent > 0:
					for x in xrange(1,11-5*abs(i)):
						directions.append(i) 

		if directions:
			return choice(directions)
		else:
			return None

	def locate_food_scent_nearby(self):
		directions = []
		if self.ahead().food_scent > 0:
			directions.append(0)
		else:
			for i in xrange(-2, 3):
				if self.world[self.neighbour(i)].food_scent > 0:
					for x in xrange(1,11-5*abs(i)):
						directions.append(i) 

		if directions:
			return choice(directions)
		else:
			return None

	def rank_by_food_scent(self):
		best_direction = 0
		best_direction_scent = 0
		for i in [0, -1, 1, -1, 2]:
			cell = self.world[self.neighbour(i)]
			if cell.food_scent > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.food_scent
		return best_direction

	def rank_by_home_scent(self):
		best_direction = 0
		best_direction_scent = 0
		for i in [0, -1, 1, -1, 2]:
			cell = self.world[self.neighbour(i)]
			if cell.home_scent > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.home_scent
		return best_direction

	def drop_food(self):
		self.food = 0

	def has_food(self):
		return bool(self.food)

	def __nonzero__(self):
		return True


class WorkerAnt(Ant):
	"""WorkerAnt"""
	def __init__(self, world, image, direction, location):
		Ant.__init__(self, world, image, direction, location)
		self.task_manager = TaskManager()
		self.task_manager.add_task(Explore(self))
		self.task_manager.add_task(TakeFood(self))
		self.task_manager.add_task(DropFood(self))
		self.task_manager.add_task(FollowFoodTrail(self))
		self.task_manager.add_task(FollowHomeTrail(self))
		self.task_manager.set_active_task("explore")