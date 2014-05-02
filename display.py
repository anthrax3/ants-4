class Entity(object):
	"""
	Base class for all drawable objects
	"""
	def __init__(self, world, location, size, image):
		self.world = world
		self.location = location
		self.size = size
		self.image = image

	def render(self, index=0):
		"""
		Draw the object into the screen
			- selects the portion of the image to draw from the "index" argument
		"""
		x, y = self.location
		x *= self.world.cell_size
		y *= self.world.cell_size
		w, h = self.size
		w *= self.world.cell_size
		h *= self.world.cell_size
		position = (x, y)
		patch_rect = (w*index, 0, w, h)
		self.world.canvas.blit(self.image, position, patch_rect)