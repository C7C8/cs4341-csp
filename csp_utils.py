from typing import Dict, Tuple, List, Callable


def get_valid_moves(vars_f: Dict, bags_f: Dict, curr: Dict, constraints: List[Callable]) -> List[Tuple[str, int]]:
	"""Get all valid moves for the given variables, bags, current state, and constraints"""
	ret = []
	for var in vars_f.keys():
		for bag in bags_f.keys():
			possible_universe = curr.copy()
			if bag not in possible_universe.keys():
				possible_universe[bag] = []
			possible_universe[bag].append(var)

			if all(map(lambda constraint: constraint(vars_f, bags_f, possible_universe), constraints)):
				ret.append((var, bag))

	return ret