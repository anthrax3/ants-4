from constants import DIRECTIONS
from task_manager import TaskManager, Explore, TakeFood, FollowHomeTrail, FollowFoodTrail, DropFood
from task_manager import ExploreNest, ReturnHome
from task_manager import FindNest, RaidNest, Escape
from display import Entity
from random import choice, randint

class Ant(Entity):
	"""A virtual base class for Ants"""
	def __init__(self, world, image, direction, location, nest_id):
		super(Ant, self).__init__(world, location, [world.cell_size]*2, image)
		self.world = world
		self.image = image
		self.nest_id = nest_id
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
		new_cell = self.world[new_location]
		if new_cell.is_obstacle() or new_cell.has_ant() or new_cell.is_food(self.get_nest_id()):
			self.turn(choice([-1, 1]))
		else:
			self.location = new_location
			self.behind().ant = None
			if not self.behind().is_obstacle():
				self.behind().add_home_scent(self.home_scent_strength, self.get_nest_id()).add_food_scent(self.food_scent_strength, self.get_nest_id())
			for cell in self.here().nearby():
				cell.add_home_scent(self.home_scent_strength/1., self.get_nest_id()).add_food_scent(self.food_scent_strength/1., self.get_nest_id())
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
		self.home_scent_strength = max(0, self.home_scent_strength*.98)
		return self

	def reduce_food_scent(self, amt=1):
		"""Reduce food scent by 'amt'"""
		self.food_scent_strength = max(0, self.food_scent_strength*.98)
		return self

	def turn(self, n):
		"""Changes direction n times"""
		self.direction = (self.direction + n) % 8

	def render(self):
		"""Render itself"""
		if self.has_food():
			super(Ant, self).render(8)
		else:
			# super(Ant, self).render(self.direction)
			super(Ant, self).render(self.get_nest_id()*7)

	def get_nest_id(self):
		return self.nest_id

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
		if self.ahead().is_food(self.get_nest_id):
			directions.append(0)
		else:
			for i in xrange(1, 8):
				if self.world[self.neighbour(i)].is_food(self.get_nest_id()):
					directions.append(i) 

		if directions:
			return choice(directions)
		else:
			return None

	def locate_home_nearby(self):
		"""Locate home cell nearby and return any one randomly
		return None if not found"""
		directions = []
		if self.ahead().is_own_home(self.get_nest_id()):
			directions.append(0)
		else:
			for i in xrange(1, 8):
				if self.world[self.neighbour(i)].is_own_home(self.get_nest_id()):
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
		if self.ahead().get_home_scent(self.get_nest_id()) > 0:
			directions.append(0)
		else:
			for i in xrange(-2, 3):
				if self.world[self.neighbour(i)].get_home_scent(self.get_nest_id()) > 0:
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
		if self.ahead().get_food_scent(self.get_nest_id()) > 0:
			directions.append(0)
		else:
			for i in xrange(-2, 3):
				if self.world[self.neighbour(i)].get_food_scent(self.get_nest_id()) > 0:
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
			if cell.get_food_scent(self.get_nest_id())*1./I > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.get_food_scent(self.get_nest_id())
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
			if cell.get_home_scent(self.get_nest_id())*1./I > best_direction_scent:
				best_direction = i
				best_direction_scent = cell.get_home_scent(self.get_nest_id())
		return best_direction if best_direction_scent > .3 else None

	def drop_food(self):
		"""
		Set food to zero
		Update the food values of the home cell it reached
		"""
		self.here().food += self.food
		self.food = 0

	def has_food(self):
		return bool(self.food)

	def __nonzero__(self):
		return True


class WorkerAnt(Ant):
	"""Ants that explores for foodsource and collects food"""
	def __init__(self, world, image, direction, location, nest_id):
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
		Ant.__init__(self, world, image, direction, location, nest_id)
		self.task_manager.add_task(Explore(self))
		self.task_manager.add_task(TakeFood(self))
		self.task_manager.add_task(DropFood(self))
		self.task_manager.add_task(FollowFoodTrail(self))
		self.task_manager.add_task(FollowHomeTrail(self))
		self.task_manager.set_active_task("explore")


class QueenAnt(Ant):
	"""Ants that produces offsprings and populates the colony"""
	def __init__(self, world, image, direction, location, nest_id):
		"""
		Tasks assigned:
			- HaveFood
			- Produce offsprings
		Default task:
			- Have Food
		"""
		Ant.__init__(self, world, image, direction, location, nest_id)
		raise NotImplementedError


class SoldierAnt(Ant):
	"""Ants that produces offsprings and populates the colony"""
	def __init__(self, world, image, direction, location, nest_id):
		"""
		Tasks assigned:
			- Explore nest
			- attack enemy ants
			- return home
		Default task:
			- Explore nest
		"""
		Ant.__init__(self, world, image, direction, location, nest_id)
		self.task_manager.add_task(ExploreNest(self))
		self.task_manager.add_task(ReturnHome(self))
		self.task_manager.set_active_task("explore nest")

class EnemyAnt(Ant):
	"""Ants that produces offsprings and populates the colony"""
	def __init__(self, world, image, direction, location, nest_id):
		"""
		Tasks assigned:
			- Find nest
			- Steal food
			- Escape from soldier ants
		Default task:
			- find nest
		"""
		Ant.__init__(self, world, image, direction, location, nest_id)
		self.task_manager.add_task(FindNest(self))
		self.task_manager.add_task(RaidNest(self))
		self.task_manager.add_task(Escape(self))
		self.task_manager.set_active_task("find nest")