import random
from point import Point
from sensor import Sensor

class Simulation:

	def __init__(self, grid_size, sink_pos, k):
		''' Constructor
		Args:
			grid_size: size of the grid (tuple)
			sink_pos: position of the sink (tuple)
			k: degree of coverage (int)
		Returns:
			None
		'''
		if grid_size:
			self.grid = [[Point((r, c)) for c in range(grid_size[0])] 
				for r in range(grid_size[1])]
			
		self.sink_pos = Point(sink_pos)
		self.k = k

		self.sensors = {}
		self.active_sensors = {}
		self.parent_sensors = []
		
		self.covered_points = set()
		self.k_covered_points = set()

	def deploy_sensors(self, num_sensors, sensing_range, comm_range):
		'''Used for initial random sensor deployment.

		Args:
			num_sensors: number of sensors to deploy (int)
			sensing_range: sensing range (int)
			comm_range: communication range (int)

		Returns:
			None
		'''
		self.sensor_positions = set()
		for i in range(num_sensors):
			s_id = i + 1

			s_pos = random.choice(random.choice(self.grid))
			while s_pos in self.sensor_positions:
				s_pos = random.choice(random.choice(self.grid))

			self.sensor_positions.add(s_pos)
			s_pos.s_id = s_id

			s = Sensor(s_id, s_pos, sensing_range, comm_range)
			self.sensors[s_id] = s
			self.grid[s.pos.x][s.pos.y] = s_pos

	def activate_random_sensors(self, num):
		'''Randomly activates a given number of sensors
		from a list of inactive sensors.

		Args:
			num: number of sensors to activate (int)

		Returns:
			None
		'''
		inactive_sensors = []
		for s_id in self.sensors:
			if s_id not in self.active_sensors:
				inactive_sensors.append(self.sensors[s_id])

		if num > len(inactive_sensors):
			num = len(inactive_sensors)

		rand_sensors = random.sample(inactive_sensors, num)
		for i in range(len(rand_sensors)):
			s = rand_sensors[i]
			self.active_sensors[s.id] = s

			if s.in_comm_range(self.sink_pos):
				self.parent_sensors.append(s)

			s.init_comm_neighbors(self.active_sensors)
			self.update_coverage(s)

	def deactivate_random_sensors(self, num):
		'''Randomly deactivates a given number of sensors
		from a list of active sensors.
		'''
		if num > len(self.active_sensors):
			num = len(self.active_sensors)

		rand_sensors = random.sample(list(self.active_sensors), num)
		for i in range(len(rand_sensors)):
			s_id = rand_sensors[i]
			self.active_sensors.pop(s_id)

			s = self.sensors[s_id]
			if s.in_comm_range(self.sink_pos):
				self.parent_sensors.remove(s)

			for nei in s.comm_neighbors:
				nei.comm_neighbors.remove(s)
			s.comm_neighbors = set()

			self.update_coverage(s, deactivate=True)

	def update_coverage(self, s, deactivate=False):
		'''Updates coverage of points covered by a sensor.
		Only updates coverage of critical points if they are
		defined, otherwise updates coverage of all points.

		Args:
			s: sensor to check viscinity of (Sensor)

		Returns:
			None
		'''
		def update(p):
			if not deactivate:
				p.coverage += 1
				self.covered_points.add(p)
				if p.coverage == self.k:
					self.k_covered_points.add(p)
			else:
				p.coverage -= 1
				if p.coverage == 0:
					self.covered_points.remove(p)
				if p.coverage < self.k and p in self.k_covered_points:
					self.k_covered_points.remove(p)

		visited = set()
		cx, cy = s.pos.pos

		def dfs(r, c):
			if r < 0 or r >= len(self.grid):
				return

			if c < 0 or c >= len(self.grid[r]):
				return

			if (r, c) in visited:
				return

			if ((s.pos.x - r)**2 + (s.pos.y - c)**2) > s.sensing_radius**2:
				return

			visited.add((r, c))
			p = self.grid[r][c]
			update(p)

			# right
			dfs(r, c + 1)
			# left
			dfs(r, c - 1)
			# up
			dfs(r - 1, c)
			# down
			dfs(r + 1, c)

		dfs(cx, cy)

	def connected_sensors(self):
		'''Find all sensors connected to a parent sensor
		via communication neighbors.

		Args:
			None

		Returns:
			The set of all sensors connected to a parent
			sensor via communication neighbors
		'''
		visited = set()
		if not self.parent_sensors:
			return visited

		source = self.parent_sensors[0]
		q = [source]

		while q:
			s = q.pop(0)
			visited.add(s.id)
			for nei in s.comm_neighbors:
				if nei.id not in visited:
					q.append(nei)
					visited.add(nei.id)

		return visited

	def get_metrics(self):
		'''Gets metrics for each simulation.

		Args:
			None

		Returns:
			The rate of coverage, k-coverage, connectiviy, and
			inactivity in the simulation.
		'''
		num_points = len(self.grid) * len(self.grid[0])

		coverage_rate = len(self.covered_points) / num_points
		k_coverage_rate = len(self.k_covered_points) / num_points

		if len(self.active_sensors) > 0:
			connectivity = len(self.connected_sensors()) / len(self.active_sensors)
		else:
			connectivity = 0

		inactivity = (len(self.sensors) - len(self.active_sensors)) / len(self.sensors)

		return [coverage_rate, k_coverage_rate, connectivity, inactivity]

	def __lt__(self, other):
		'''Used for comparing different solution sets.
		If two solution sets have the same score, then
		return any of them

		Args:
			other: the other solution set (Simulation)

		Returns:
			Normal less than operation if self
			is not a Simulation object, else 
			return self.
		'''
		if isinstance(self, Simulation):
			return self
		else:
			return self < other

	def __repr__(self):
		RED = '\033[91m'
		GREEN = '\033[92m'
		YELLOW = '\033[93m'
		BLUE = '\033[96m'
		END = '\033[0m'
		
		'''Used to print the grid.

		Args:
			None

		Returns:
			String representing the grid.
		'''
		res = ''

		for r in range(len(self.grid)):
			for c in range(len(self.grid[0])):
				if self.grid[r][c].s_id:
					if self.grid[r][c].s_id in self.active_sensors:
						res += f'{GREEN}A{END} '
					else:
						res += f'{RED}I{END} '
				else:
					if self.grid[r][c].coverage >= self.k:
						res += f'{BLUE}k{END} '
					elif self.grid[r][c].coverage > 0:
						res += f'{YELLOW}1{END} '
					else:
						res += '0 '

			res += '\n'

		return res
