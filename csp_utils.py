from typing import Dict, Tuple, List
from copy import deepcopy


def get_valid_moves(vars_f: Dict, bags_f: Dict, curr: Dict, constraints) -> List[Tuple[str, int]]:
	"""Get all valid moves for the given variables, bags, current state, and constraints"""
	ret = []
	for var in vars_f.keys():
		for bag in bags_f.keys():
			possible_universe = deepcopy(curr)
			if bag not in possible_universe.keys():
				possible_universe[bag] = []
			possible_universe[bag].append(var)

			if all(constraint(vars_f, bags_f, possible_universe) for constraint in constraints):
				ret.append((var, bag))

	return ret
