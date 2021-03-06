from random import randint, choice

class TaskManager():
	"""
	Decides and performs all actions of an Ant
	"""
	def __init__(self):
		self.tasks = {}
		self.active_task = None

	def add_task(self, task):
		"""
		Adds a new task
		"""
		self.tasks[task.name] = task

	def make_decision(self):
		"""
		Performs the active task
		Checks for new task
		If new task is present end the current task and
		start the new task
		"""
		self.active_task.perform_task()

		new_task = self.active_task.get_new_task()

		if new_task:
			self.active_task.end_task()
			self.set_active_task(new_task)
			self.active_task.start_task()

	def set_active_task(self, task_name):
		"""
		Sets the active task
		"""
		self.active_task = self.tasks[task_name]

class Task(object):
	"""
	Base class for a Task
	"""
	def __init__(self, name, ant):
		self.name = name
		self.ant = ant
		self.new_task = None

	def start_task(self):
		"""
		Actions at the beginning of a new task
		"""
		pass

	def perform_task(self):
		"""
		Actions done for a task
		each time a task is performed reduce the health by one
		"""
		self.ant.reduce_health(.001)

	def end_task(self):
		"""
		Actions at the end of a new task
		"""
		pass

	def get_new_task(self):
		"""Returns and resets new task"""
		new_task = self.new_task
		self.new_task = None
		return new_task

class Explore(Task):
	"""
	Ant Exploring Task
	"""
	def __init__(self, ant):
		super(Explore, self).__init__("explore", ant)

	def perform_task(self):
		"""
		 If ant has food - 
			 find home nearby and drop food there, else
			 find home scent nearby and switch to follow home trail task, else
			 make a random move
		 If ant is searching for food
		 	 if food is found switch to take food task, else
		 	 find a food scent trail,
		 	 reverse direction if it finds home nearby
		 Reduce it scent strength by an unit
		"""
		ant = self.ant
		if ant.has_food():
			home_nearby = ant.locate_home_nearby()
			home_scent_nearby = ant.locate_home_scent_nearby()
			if home_nearby != None:
				self.new_task = "drop food"
			elif home_scent_nearby != None:
				ant.turn(home_scent_nearby)
				self.new_task = "follow home trail"
			else:
				ant.random_move()
		else:
			food_nearby = ant.locate_food_nearby()
			food_scent_nearby = ant.locate_food_scent_nearby()
			if ant.here().is_own_home(ant.get_nest_id()):
				ant.move()
			elif food_nearby != None:
				ant.turn(food_nearby)
				self.new_task = "take food"
			elif ant.ahead().is_own_home(ant.get_nest_id()):
				ant.turn(choice([3, 4, 5]))
				ant.home_scent_strength = 40
			elif food_scent_nearby != None:
				ant.turn(food_scent_nearby)
				self.new_task = "follow food trail"
			else:
				ant.random_move()
		ant.reduce_food_scent_strength(1).reduce_home_scent_strength(1)
		super(Explore, self).perform_task()

class TakeFood(Task):
	"""
	Gathers food from the cell
	If food is present it takes the food otherwise it returns to explore mode
	"""
	def __init__(self, ant):
		super(TakeFood, self).__init__("take food", ant)

	def perform_task(self):
		"""
		Take food if available otherwise return to explore mode
		"""
		ant = self.ant
		food = ant.ahead().get_food(1)
		if food:
			ant.take_food(food)
			ant.turn(4)
			self.new_task = "follow home trail"
		else:
			self.new_task = "explore"
		super(TakeFood, self).perform_task()

	def end_task(self):
		"""
		Increase food_scent_strength
		and reduce home_scent_strength
		"""
		self.ant.set_food_scent_strength(40)
		self.ant.set_home_scent_strength(0)


class DropFood(Task):
	"""
	Drop the food inside the nest
	Randomly walks inside the nest and drops the food
	and returns to explore mode
	"""
	def __init__(self, ant):
		super(DropFood, self).__init__("drop food", ant)

	def start_task(self):
		self.ant.set_food_scent_strength(0)
		self.ant.set_home_scent_strength(40)

	def perform_task(self):
		"""
		If ant reaches home drop the food inside the home
		otherwise follow a home trail
		"""
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		if home_nearby !=None:
			ant.turn(home_nearby)
			ant.move()
			if randint(1,10) == 1:
				ant.drop_food()
				self.new_task = "explore"
		else:
			self.new_task = "follow home trail"
		super(DropFood, self).perform_task()	

	def end_task(self):
		"""
		Increase home scent strength and reduce food scent strength
		"""
		self.ant.set_food_scent_strength(0)
		self.ant.set_home_scent_strength(40)

class FollowFoodTrail(Task):
	"""
	Follows food trail if it finds a food scent nearby
	"""
	def __init__(self, ant):
		super(FollowFoodTrail, self).__init__("follow food trail", ant)

	def start_task(self):
		pass

	def perform_task(self):
		"""
		if food is found take food_scent_strength
		otherwise rank cells based on scent and follow it
		if scent trail is lost, return to explore mode
		"""
		ant = self.ant
		food_nearby = ant.locate_food_nearby()
		# food_scent_nearby = ant.locate_food_scent_nearby()
		if food_nearby != None:
			ant.turn(food_nearby)
			self.new_task = "take food"
		elif ant.ahead().is_obstacle() or ant.ahead().has_ant():
			ant.turn(randint(1,3)-2)
		elif ant.ahead().is_own_home(ant.get_nest_id()) and not ant.here().is_own_home(ant.get_nest_id()):
			ant.turn(4)
			ant.home_scent_strength = 40
		else:
			ant.turn(ant.rank_by_food_scent())
			ant.move()
		ant.reduce_home_scent_strength(1).reduce_food_scent_strength(1)
		super(FollowFoodTrail, self).perform_task()

class FollowHomeTrail(Task):
	"""
	Follows a home trail if it finds home scent 
	"""
	def __init__(self, ant):
		super(FollowHomeTrail, self).__init__("follow home trail", ant)

	def start_task(self):
		pass

	def perform_task(self):
		"""
			If home is reached drop the food_scent_strength
			If trail is lost return to explore mode
			else rank the cell by home scent strength and follow itself
		"""
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		if not ant.has_food():
			self.new_task = "explore"
		elif ant.ahead().is_obstacle() or ant.ahead().has_ant():
			ant.turn(choice([-1, 1]))
		elif ant.ahead().is_food(ant.get_nest_id()):
			ant.turn(4)
			self.ant.food_scent_strength = 40
		elif home_nearby != None:
			ant.turn(home_nearby)
			self.new_task = "drop food"
		else:
			new_direction = ant.rank_by_home_scent()
			if new_direction:
				ant.turn(new_direction)
				ant.move()
			else:
				ant.random_move()
		ant.reduce_food_scent_strength(1).reduce_home_scent_strength(1)
		super(FollowHomeTrail, self).perform_task()

class ReturnHome(Task):
	"""
	Return home if the ant is roaming outside
	"""
	def __init__(self, ant):
		super(ReturnHome, self).__init__("return home", ant)		

	def start_task(self):
		self.ant.set_home_scent_strength(0)
		self.ant.set_food_scent_strength(0)

	def perform_task(self):
		"""
		Follow home trail and return home
		"""
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		if ant.ahead().is_obstacle() or ant.ahead().is_food(ant.get_nest_id()) or ant.ahead().has_ant():
			ant.turn(choice([-1, 1]))
		elif home_nearby != None:
			ant.turn(home_nearby)
			ant.move()
			self.new_task = "guard nest"
		else:
			new_direction = ant.rank_by_home_scent()
			if new_direction:
				ant.turn(new_direction)
				ant.move()
			else:
				ant.random_move()
		super(ReturnHome, self).perform_task()

class GuardNest(Task):
	"""
	Guards the nest
	If it sees an enemy ant it attacks it
	"""
	def __init__(self, ant):
		super(GuardNest, self).__init__("guard nest", ant)

	def start_task(self):
		self.ant.set_home_scent_strength(2)
		self.ant.set_food_scent_strength(0)

	def perform_task(self):
		"""
		Travel along the walls of the nest
		"""
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		enemy_ant_nearby = ant.get_enemy_ant_nearby()
		if enemy_ant_nearby:
			ant.attack(enemy_ant_nearby)
		if not home_nearby:
			self.new_task = "return home"
		elif not ant.ahead().is_own_home(ant.get_nest_id()):
			ant.turn(choice([-1, 1]))
		else:
			ant.move()
		super(GuardNest, self).perform_task()

class ProduceAnts(Task):
	"""
	Randomly produce new ants
	"""
	def __init__(self, ant):
		super(ProduceAnts, self).__init__("produce ants", ant)

	def perform_task(self):
		"""randomly produce new ants"""
		if self.ant.is_hungry():
			self.new_task = "have food"
		elif randint(1,100) == 1:
			self.ant.nest.add_new_ant_randomly()
		super(ProduceAnts, self).perform_task()
		
class FindFood(Task):
	"""Finds food if hungry"""
	def __init__(self, ant):
		super(FindFood, self).__init__("find food", ant)

	def perform_task(self):
		"""find food"""
		super(FindFood, self).perform_task()
