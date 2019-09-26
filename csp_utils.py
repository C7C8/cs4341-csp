from typing import Dict, Tuple, List
from copy import deepcopy


def get_valid_moves(vars_f: Dict, bags_f: Dict, universe: Dict, constraints) -> List[Tuple[str, int]]:
	"""Get all valid moves for the given variables, bags, universe state, and constraints"""
	ret = []
	unassigned_vars = set(vars_f.keys()).difference({i for bag in universe.values() for i in bag})
	for var in unassigned_vars:
		for bag in bags_f.keys():
			possible_universe = deepcopy(universe)
			if bag not in possible_universe.keys():
				possible_universe[bag] = []
			possible_universe[bag].append(var)

			if all(constraint(vars_f, bags_f, possible_universe) for constraint in constraints):
				ret.append((var, bag))

	return ret
