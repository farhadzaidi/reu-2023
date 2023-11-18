
class Point:

	def __init__(self, pos, s_id=None):
		'''Constructor

		Args:
			pos: (x, y) coordinate (tuple)
			s_id: sensor id (int)

		Returns:
			None
		'''
		self.pos = pos
		self.x = pos[0]
		self.y = pos[1]
		self.coverage = 0
		self.s_id = s_id

	def __repr__(self):
		'''Used to print the position of the point

		Args:
			None

		Returns:
			String representation of positon
			based on whether it holds a sensor
			or not.
		'''
		if self.s_id:
			return f'S{self.pos}'

		return f'P{self.pos}'
