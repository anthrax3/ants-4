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

		self.settings = {
		"no_of_ants": 10
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