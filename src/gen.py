import random
import math
import sys
from copy import deepcopy
from simulation import Simulation

sys.setrecursionlimit(10000)

# simulation parameters
NUM_ROWS = 100
NUM_COLS = 100
SINK_POS = (NUM_ROWS // 2, NUM_COLS // 2)
DEG_OF_COVERAGE = 3
NUM_SENSORS = 500
SENSING_RANGE = 10
COMM_RANGE = 2 * SENSING_RANGE

# used to print metrics of a given solution
def print_metrics(sol):
	metrics = sol.get_metrics()
	print(f'Metrics:')
	print(f'\tCoverage Rate: {round(metrics[0] * 100, 2)}%')
	print(f'\tk-Coverage Rate: {round(metrics[1] * 100, 2)}%')
	print(f'\tConnectivity: {round(metrics[2] * 100, 2)}%')
	print(f'\t{len(sol.active_sensors)} / {NUM_SENSORS} active sensors', end=' ')
	print(f'({round(len(sol.active_sensors) / NUM_SENSORS * 100, 2)}%)')

# used to evaluate fitness based on the metrics
# of a given solution
def fitness(sol, optimal_metrics):
	metrics = sol.get_metrics()
	coverage_rate = metrics[0]
	k_coverage_rate = metrics[1]
	connectivity = metrics[2]
	inactivity = metrics[3]

	# reward hitting optimal metrics by
	# boosting score significantly
	if coverage_rate == optimal_metrics[0]:
		coverage_rate *= 10

	if k_coverage_rate == optimal_metrics[1]:
		k_coverage_rate *= 10

	if connectivity == optimal_metrics[2]:
		connectivity *= 10

	return (0.045*connectivity + 0.030*coverage_rate + 
		0.024*k_coverage_rate + 0.01*inactivity)

def main(quiet=False):

	# initialize simulation and deploy sensors
	SIM = Simulation(
	grid_size=(NUM_ROWS, NUM_COLS),
	sink_pos=SINK_POS,
	k=DEG_OF_COVERAGE
	)

	SIM.deploy_sensors(
	num_sensors=NUM_SENSORS,
	sensing_range=SENSING_RANGE,
	comm_range=COMM_RANGE
	)

	# optimal metrics for fitness comparison
	optimal = deepcopy(SIM)
	optimal.activate_random_sensors(NUM_SENSORS)
	optimal_metrics = optimal.get_metrics()

	final_score, final_sol = 0, None

	# initialize population with random solutions
	solutions = []
	pop_size = 10 + int(math.sqrt(NUM_SENSORS) / 2)
	for i in range(pop_size):
		new_sim = deepcopy(SIM)
		num_active = int(random.uniform(1, NUM_SENSORS))
		new_sim.activate_random_sensors(num_active)
		solutions.append(new_sim)

	num_gen = 0
	repeat_counter = 0
	repeat_threshold = 5
	while repeat_counter < repeat_threshold:
		num_gen += 1

		# evaluate fitness of solutions
		for j in range(len(solutions)):
			score = fitness(solutions[j], optimal_metrics)
			solutions[j] = (score, solutions[j])

		# determine best solutions based on score
		solutions.sort(reverse=True)
		solutions = solutions[:pop_size // 5]


		# print best solution of generation
		best_score = solutions[0][0]
		best_sol = solutions[0][1]
		if not quiet:
			print(f'---Gen {num_gen} Best Solution')
			print(f'Score: {best_score}')
			print(f'Active Sensors: {len(best_sol.active_sensors)} / {NUM_SENSORS}')
			print_metrics(best_sol)
			print()

		# determine highest score of all generations
		if best_score > final_score:
			final_score = best_score
			final_sol = best_sol
			repeat_counter = 0
		else:
			repeat_counter += 1

		# create new generation built from best solutions
		new_gen = []
		for j in range(pop_size):
			new_sim = deepcopy(random.choice(solutions)[1])

			# mutation_factor scales with size of sensors
			mutation_factor = random.choice([-3, -2, -1, 0, 1, 2, 3])
			if NUM_SENSORS > 100:
				mutation_factor = random.randrange(
					int(-NUM_SENSORS / 30), int(NUM_SENSORS / 30) + 1)

			# activate or deactivate sensors based on mutation factor
			if mutation_factor > 0:
				new_sim.activate_random_sensors(mutation_factor)
			elif mutation_factor < 0:
				new_sim.deactivate_random_sensors(abs(mutation_factor))

			new_gen.append(new_sim)

		# assign new_gen to solutions for next generation
		solutions = new_gen

	num_gen -= repeat_threshold
	return final_score, final_sol, num_gen


if __name__ == '__main__':
	score, sol, num_gen = main()
	print(f'Best solution found after {num_gen} generation(s)')
	print(f'Score: {score}')
	print_metrics(sol)
	# print(sol)
