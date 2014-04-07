from pygame import image, time, key, event
from pygame.constants import *
from world import World

class Simulation():
	"""Controls the simulation"""
	def __init__(self):
		self.clock = time.Clock()
		self.framerate = 60
		self.images = {}

		self.quit = False

		self.add_image("ant", "ant.png")
		self.add_image("grass", "grass.png")
		self.add_image("food", "food.png")
		self.add_image("home", "home.png")
		self.add_image("obstacle", "obstacle.png")
		self.add_image("home_scent", "home_scent.png")
		self.add_image("food_scent", "food_scent.png")
		self.add_image("cell", "cell.png")

		self.settings = {
		"no_of_ants": 10,
		"evaporation_rate": .1,
		"home_size": 10
		}

		self.world = World(80, 60, 10, self.images, self.settings)

	def add_image(self, name, path):
		self.images[name] = image.load('images/' + path)		

	def run(self):
		while self.quit is False:
			self.main_loop()

	def main_loop(self):
		self.world.render()
		self.world.advance()

		self.handle_events()

		self.clock.tick(self.framerate)

	def handle_events(self):
		keys = key.get_pressed()
		if keys[K_q] or keys[K_ESCAPE]:
			self.quit = True  
		for evt in event.get():
			if evt.type == QUIT:
				self.quit = True 