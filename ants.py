from constants import DIRECTIONS
from task_manager import TaskManager, Explore, TakeFood, FollowHomeTrail, FollowFoodTrail, DropFood
from display import Entity
from random import choice, randint

class Ant(Entity):
	"""A virtual base class for Ants"""
	def __init__(self, world, image, direction, location):
		super(Ant, self).__init__(world, location, [world.cell_size]*2, image)
		self.world = world
		self.image = image
		self.direction = direction
		self.location = location
		self.food = 0
		self.food_scent_strength = 0
		self.home_scent_strength = 0

		self.task_manager = TaskManager()

	def neighbour(self, direction):
		"""Returns location of neighbouring cell in a direction 
		relative to the ant direction"""
		x, y = self.location
		dx, dy = DIRECTIONS[(self.direction + direction)%8]
		return (x+dx)%self.world.width, (y+dy)%self.world.height

	def move(self):
		"""Move the ant by a unit,
		Leave a scent trail,
		remove the ant from its old cell, and
		update the current cell ant with itself
		"""
		new_location = self.neighbour(0)		
		if self.world[new_location].is_obstacle():
			self.turn(choice([-1, 1]))
		else:
			self.location = new_location
			self.behind().ant = None
			if not self.behind().is_obstacle():
				self.behind().add_home_scent(self.home_scent_strength).add_food_scent(self.food_scent_strength)
			for cell in self.here().nearby():
				cell.add_home_scent(self.home_scent_strength/1.).add_food_scent(self.food_scent_strength/1.)
			self.here().ant = self
		return self

	def random_move(self):
		"""Ant makes a move forward or turns randomly"""
		if randint(1,8) == 1:
			self.turn( choice([-1, 1]) )
		else:
			self.move()

	def reduce_home_scent(self, amt=1):
		"""Reduce home scent by 'amt'"""
		self.home_scent_strength = max(0, self.home_scent_strength-amt)
		return self

	def reduce_food_scent(self, amt=1):
		"""Reduce food scent by 'amt'"""
		self.food_scent_strength = max(0, self.food_scent_strength-amt)
		return self

	def turn(self, n):
		"""Changes direction n times"""
		self.direction = (self.direction + n) % 8

	def render(self):
		"""Render itself"""
		if self.has_food():
			super(Ant, self).render(8)
		else:
			super(Ant, self).render(self.direction)

	def here(self):
		"""The cell it is standing on"""
		return self.world[self.location]

	def behind(self):
		"""The cell just behind"""
		return self.world[self.neighbour(4)]

	def ahead(self):
		"""The cell just ahead"""
		return self.world[self.neighbour(0)]

	def ahead_left(self):
		"""The cell just ahead-left"""
		return self.world[self.neighbour(-1)]

	def ahead_right(self):
		"""The cell just ahead-right"""
		return self.world[self.neighbour(1)]

	def locate_food_nearby(self):
		"""Locate all sources nearby and return any one randomly
		return None if no food source is found"""
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
		"""Locate home cell nearby and return any one randomly
		return None if not found"""
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
		"""Scan the 5 directions near the direction of the ant for home scent and
		return one random direction
		return None if not found
		"""
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
		"""Scan the 5 directions near the direction of the ant for food scent and
		return one random direction
		return None if not found
		"""
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
		"""Scan the 5 directions near the direction of the ant for food scent and
		return the direction with the strongest scent
		return None if not found
		"""
		best_direction = 0
		best_direction_scent = 0
		for i in [0, -1, 1, -1, 2]:
			cell = self.world[self.neighbour(i)]
			if cell.has_ant() or cell.is_obstacle():
				continue
			I = max(1, abs(i))
			if cell.food_scent*1./I > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.food_scent
		return best_direction

	def rank_by_home_scent(self):
		"""Scan the 5 directions near the direction of the ant for home scent and
		return the direction with the strongest scent
		return None if not found
		"""
		best_direction = 0
		best_direction_scent = 0
		for i in [0, -1, 1, -1, 2]:
			cell = self.world[self.neighbour(i)]
			if cell.has_ant() or cell.is_obstacle():
				continue
			I = max(1, abs(i))
			if cell.home_scent*1./I > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.home_scent
		return best_direction if best_direction_scent > .3 else None

	def drop_food(self):
		"""
		Set food to zero
		Update the food values of the home cell it reached
		"""
		self.food = 0

	def has_food(self):
		return bool(self.food)

	def __nonzero__(self):
		return True


class WorkerAnt(Ant):
	"""Ants that explores for foodsource and collects food"""
	def __init__(self, world, image, direction, location):
		"""
		Tasks assigned:
			- Explore
			- TakeFood
			- DropFood
			- FollowFoodTrail
			- FollowHomeTrail
		Default task:
			- Explore
		"""
		Ant.__init__(self, world, image, direction, location)
		self.task_manager.add_task(Explore(self))
		self.task_manager.add_task(TakeFood(self))
		self.task_manager.add_task(DropFood(self))
		self.task_manager.add_task(FollowFoodTrail(self))
		self.task_manager.add_task(FollowHomeTrail(self))
		self.task_manager.set_active_task("explore")


class QueenAnt(Ant):
	"""Ants that produces offsprings and populates the colony"""
	def __init__(self, world, image, direction, location):
		"""
		Tasks assigned:
			- HaveFood
			- Produce offsprings
		Default task:
			- Have Food
		"""
		Ant.__init__(self, world, image, direction, location)
		raise NotImplementedError