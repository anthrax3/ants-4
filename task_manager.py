from random import randint, choice

class TaskManager():
	"""Decides and performs all actions of an Ant"""
	def __init__(self):
		self.tasks = {}
		self.active_task = None

	def add_task(self, task):
		self.tasks[task.name] = task

	def make_decision(self):
		self.active_task.perform_task()

		new_task = self.active_task.get_new_task()

		if new_task:
			self.active_task.end_task()
			self.set_active_task(new_task)

	def set_active_task(self, task_name):
		self.active_task = self.tasks[task_name]

class Task(object):
	"""Base class for a Task"""
	def __init__(self, name, ant):
		self.name = name
		self.ant = ant
		self.new_task = None

	def start_task(self):
		pass

	def perform_task(self):
		pass

	def end_task(self):
		pass

	def get_new_task(self):
		"""Get and reset new task"""
		new_task = self.new_task
		self.new_task = None
		return new_task

class Explore(Task):
	"""Ant Exploring Task"""
	def __init__(self, ant):
		super(Explore, self).__init__("explore", ant)
	
	def start_task(self):
		pass

	def perform_task(self):
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
			if food_nearby != None:
				ant.turn(food_nearby)
				self.new_task = "take food"
			elif ant.ahead().is_obstacle() or ant.ahead().has_ant():
				ant.turn(randint(1,3)-2)
			elif ant.ahead().is_home():
				ant.turn(4)
				ant.home_scent_strength = 40
			elif ant.ahead().food_scent > 1 and ant.food <= 0:
				ant.move()
				self.new_task = "follow food trail"
			else:
				ant.random_move()
		ant.reduce_food_scent(1).reduce_home_scent(1)

class TakeFood(Task):
	"""Gathering Food Task"""
	def __init__(self, ant):
		super(TakeFood, self).__init__("take food", ant)

	def perform_task(self):
		ant = self.ant
		food = ant.ahead().get_food(1)
		if food:
			ant.food = food
			ant.turn(4)
			self.new_task = "follow home trail"
		else:
			self.new_task = "explore"

	def end_task(self):
		self.ant.food_scent_strength = 40
		self.ant.home_scent_strength = 0


class DropFood(Task):
	"""Drop Food Task"""
	def __init__(self, ant):
		super(DropFood, self).__init__("drop food", ant)

	def perform_task(self):
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		if home_nearby !=None:
			ant.turn(home_nearby)
			ant.drop_food()
			ant.turn(4)
			self.new_task = "explore"
		else:
			self.new_task = "follow home trail"

	def end_task(self):
		self.ant.food_scent_strength = 0
		self.ant.home_scent_strength = 40

class FollowFoodTrail(Task):
	"""docstring for FollowFoodTrail"""
	def __init__(self, ant):
		super(FollowFoodTrail, self).__init__("follow food trail", ant)

	def start_task(self):
		pass

	def perform_task(self):
		ant = self.ant
		food_nearby = ant.locate_food_nearby()
		food_scent_nearby = ant.locate_food_scent_nearby()
		if food_nearby != None:
			ant.turn(food_nearby)
			self.new_task = "take food"
		elif ant.ahead().is_obstacle() or ant.ahead().has_ant():
			ant.turn(randint(1,3)-2)
		elif ant.ahead().is_home():
			ant.turn(4)
			ant.home_scent_strength = 40
		else:
			ant.turn(ant.rank_by_food_scent())
			ant.move()
		ant.reduce_home_scent(1).reduce_food_scent(1)

class FollowHomeTrail(Task):
	"""docstring for FollowFoodTrail"""
	def __init__(self, ant):
		super(FollowHomeTrail, self).__init__("follow home trail", ant)

	def start_task(self):
		pass

	def perform_task(self):
		ant = self.ant
		home_nearby = ant.locate_home_nearby()
		if ant.ahead().is_obstacle() or ant.ahead().has_ant() or ant.ahead().is_food():
			ant.turn(choice([-1, 1]))
		elif home_nearby != None:
			ant.turn(home_nearby)
			self.new_task = "drop food"
		else:
			ant.turn(ant.rank_by_home_scent())
			ant.move()
		ant.reduce_food_scent(1).reduce_home_scent(1)
