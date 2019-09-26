from math import floor
from typing import Dict


# Base constraint: An item cannot be in more than one bag
def single_bag_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
	all_items = [i for bag in universe.values() for i in bag]
	return len(set(all_items)) == len(all_items)


# Base constraint: No bag can be over-capacity
def capacity_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
	totals = {k: sum(map(lambda i: vars_f[i], items)) for k, items in universe.items()}
	return not any(s > bags_f[k] for k, s in totals.items())


# Final constraint: All variables must be assigned.
def all_assigned_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
	all_items = {i for bag in universe.values() for i in bag}
	return len(all_items) == len(vars_f)


# Final constraint: All bags must be at least 90% filled (rounding down)
def fill_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
	totals = {k: sum(map(lambda i: vars_f[i], items)) for k, items in universe.items()}
	return not any(s < floor(0.9 * bags_f[k]) for k, s in totals.items())


def create_fit_limit_constraint(max_v, min_v, variables):
	def fit_limit_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		# Allow satisfying the min constraint before all variables have been allowed, otherwise this would always fail
		all_items = {i for bag in universe.values() for i in bag}
		if len(all_items) != len(vars_f):
			return all(map(lambda bag: len(bag) <= max_v, universe.items()))

		return all(map(lambda bag: min_v <= len(bag) <= max_v, universe.items()))

	fit_limit_constraint.vars = list(variables.keys())
	return fit_limit_constraint


def create_unary_inclusive_constraint(vals):
	item = vals[0]

	def unary_inclusive_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		contains_item = {bag_name: item in contents for bag_name, contents in universe.items()}

		# No bag contains the item in question, so the constraint is satisfied by default
		if not any(contains_item.values()):
			return True

		# The item must be in one of the given bags and there can only be one instance of it
		return any(k in contains_item.keys() and contains_item[k] for k in vals[1:]) and sum(contains_item.values()) == 1
	unary_inclusive_constraint.vars = [item]
	return unary_inclusive_constraint


def create_unary_exclusive_constraint(vals):
	def unary_exclusive_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		return not any(k in universe.keys() and vals[0] in universe[k] for k in vals[1:])
	unary_exclusive_constraint.vars = [vals[0]]
	return unary_exclusive_constraint


def create_binary_equals_constraint(vals):
	item1 = vals[0]
	item2 = vals[1]

	def binary_equals_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		# If both items aren't in the set of all items taken this constraint is always satisfied
		all_items = {i for bag in universe.values() for i in bag}
		if len(all_items.intersection({item2, item1})) < 2:
			return True

		# Filter down to a list of bags that have one item or the other; it should be 1 for this to be satisfied
		return len(list(filter(lambda bag: item2 in bag or item1 in bag, universe.values()))) == 1
	binary_equals_constraint.vars = [item1, item2]
	return binary_equals_constraint


def create_binary_not_equals_constraint(vals):
	item1 = vals[0]
	item2 = vals[1]

	def binary_not_equals_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		# If both items aren't in the set of all items taken this constraint is always satisfied
		all_items = {i for bag in universe.values() for i in bag}
		if len(all_items.intersection({item2, item1})) < 2:
			return True

		# Filter down to a list of bags that have one item or the other; it should be 2 for this to be satisfied
		return len(list(filter(lambda bag: item2 in bag or item1 in bag, universe.values()))) == 2
	binary_not_equals_constraint.vars = [item1, item2]
	return binary_not_equals_constraint


def create_binary_simultaneous_constraint(vals):
	def binary_simultaneous_constraint(vars_f: Dict, bags_f: Dict, universe: Dict) -> bool:
		# If both items aren't present, continue
		all_items = {i for bag in universe.values() for i in bag}
		if len(all_items.intersection(set(vals[:2]))) < 2:
			return True

		# Get the bag that the first item belongs to
		first_bag = list(filter(lambda bag: vals[0] in bag.values(), universe))[0]
		second_bag = vals[2] if first_bag == vals[3] else vals[3]
		# Make sure the other bag contains the second item
		return vals[1] in universe[second_bag]

	binary_simultaneous_constraint.vars = vals[:2]
	return binary_simultaneous_constraint
