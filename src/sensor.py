import math

class Sensor:

	def __init__(self, s_id, pos, sensing_radius, comm_radius):
		'''Constructor

		Args:
			s_id: sensor id (int)
			pos: point representing position of the sensor
			(Point)
			sensing_radius: the sensing radius (int)
			comm_radius: the communication radius (int)

		Returns:
			None
		'''
		self.id = s_id
		self.pos = pos
		self.sensing_radius = sensing_radius
		self.comm_radius = comm_radius

	def init_comm_neighbors(self, sensors):
		'''Initializes list of communication neighbors
		for a sensor. O(n) TC where n is the number of 
		sensors.

		Args:
			sensors: list of all sensors (list of Sensors)

		Returns:
			None
		'''
		self.comm_neighbors = set()
		for s in sensors.values():
			if s != self and self.in_comm_range(s.pos):
				self.comm_neighbors.add(s)
				s.comm_neighbors.add(self)

	def in_comm_range(self, point):
		'''Checks if a point is in the communication
		range of a sensor.

		Args:
			point: the point to check (Point)

		Returns:
			The distance to the point from the sensor
			if the point is within the communication range,
			else None.
		'''
		return (self.pos.x - point.x)**2 + (self.pos.y - point.y)**2 <= self.comm_radius**2


	def __repr__(self):
		'''Used to print the sensor's id.

		Args:
			None

		Returns:
			String representation of the sensor.
		'''
		return f'S({self.id})'

