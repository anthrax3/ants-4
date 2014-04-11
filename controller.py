from pygame import image, time, key, event, mouse
from pygame.constants import *
from world import World

class Simulation():
	"""Controls the simulation

		- Runs the main loop
		- Detects mouse, keyboard and other events
		- Loads the necessary images
		- Controls the framerate of the smiulation
	"""
	def __init__(self):
		self.clock = time.Clock()
		self.framerate = 60
		self.images = {}

		self.quit = False
		self.pause = False

		self.add_image("ant", "ant.png")
		self.add_image("grass", "grass.png")
		self.add_image("food", "food.png")
		self.add_image("home", "home.png")
		self.add_image("obstacle", "obstacle.png")
		self.add_image("home_scent", "home_scent.png")
		self.add_image("food_scent", "food_scent.png")
		self.add_image("cell", "cell.png")

		self.settings = {
		"no_of_ants": 50,
		"evaporation_rate": .95,
		"home_size": 10,
		"cell_size": 10
		}

		self.world = World(80, 60, self.images, self.settings)

	def add_image(self, name, path):
		"""	Loads an image"""
		self.images[name] = image.load('images/' + path)		

	def run(self):
		"""Runs the main loop till the user quits"""
		while self.quit is False and self.pause is False:
			self.main_loop()

	def main_loop(self):
		"""Updates the simulation
			- Draws the world and update it
			- Handles all user events
			- Controls frame rate
		"""
		self.world.render()
		self.world.advance()

		self.handle_events()

		self.clock.tick(self.framerate)

	def handle_events(self):
		"""Handles all keyboard, mouse and events like QUIT, etc"""
		self.handle_keyboard_events()
		self.handle_mouse_events()
		self.handle_general_events() 

	def handle_keyboard_events(self):
		keys = key.get_pressed()
		if keys[K_q] or keys[K_ESCAPE]:
			self.quit = True

	def handle_general_events(self):
		for evt in event.get():
			if evt.type == QUIT:
				self.quit = True

	def handle_mouse_events(self):
		pressed = mouse.get_pressed()
		x, y = mouse.get_pos()
		size = self.settings["cell_size"]
		cell = self.world[(x/size, y/size)]
		if pressed[0]:
			cell.make_obstacle()
		elif pressed[2]:
			if cell.is_obstacle():
				cell.remove_obstacle()