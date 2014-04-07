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
	
	def perform_task(self):
		ant = self.ant
		world = ant.world
		if ant.ahead().is_food():
			self.new_task = "take food"
		elif ant.ahead_left().is_food():
			ant.turn(1)
			self.new_task = "take food"
		elif ant.ahead_left().is_food():
			ant.turn(-1)
			self.new_task = "take food"
		elif ant.ahead().is_obstacle() or ant.ahead().has_ant():
			ant.turn(randint(1,3)-2)
		elif ant.ahead().is_home():
			ant.turn(4)
		else:
			if randint(1,8)==1:
				ant.turn(choice([-1,1]))
			else:
				ant.move()
				ant.behind().ant = None
				if not any([ant.behind().is_obstacle(), ant.behind().is_food(), ant.behind().is_home()]):
					ant.behind().add_home_scent(1)
				ant.here().ant = ant

class TakeFood(Task):
	"""Gathering Food Task"""
	def __init__(self, ant):
		super(TakeFood, self).__init__("take food", ant)

	def perform_task(self):
		ant = self.ant
		world = ant.world
		food = ant.ahead().get_food(1)
		if food:
			ant.turn(4)
			self.new_task = "explore"
		else:
			self.new_task = "explore"

	def end_task(self):
		pass#self.ant.turn(choice([-1, 1]))