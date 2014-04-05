from random import randint

class TaskManager(object):
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
		self.next_task = None

	def start_task(self):
		pass

	def perform_task(self):
		pass

	def end_task(self):
		pass

	def get_new_task(self):
		"""Get and reset new task"""
		new_task = self.next_task
		self.next_task = None
		return new_task

class Explore(Task):
	"""Ant Exploring Task"""
	def __init__(self, ant):
		super(Explore, self).__init__("explore", ant)
	
	def perform_task(self):
		ant = self.ant
		world = ant.world
		ahead = world[ant.neighbour(ant.direction)]
		ahead_left = world[ant.neighbour(ant.direction - 1)]
		ahead_right = world[ant.neighbour(ant.direction + 1)]
		if any(cell.is_food() for cell in [ahead, ahead_right, ahead_left]):
			raise NotImplementedError
		elif ahead.is_obstacle():
			ant.turn(randint(1,3)-2)
		else:
			ant.move()
