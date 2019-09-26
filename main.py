#!/usr/bin/env python3
import argparse
from copy import deepcopy
import sys
from collections import Counter

from constraints import *
from csp_utils import get_valid_moves

# WARNING! This project contains massive amounts of python one-liner bullshit,
# which is... actually extraordinarily useful. Proceed at your own risk!

parser = argparse.ArgumentParser(description="CSP solver for CS 4341")
parser.add_argument("input", type=str, help="")
parser.add_argument("-o", "--output", type=str, help="Optional output file; if none is given, output will be "
															 "written to stdout")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
args = parser.parse_args()

# Setup
vprint = print if args.verbose else lambda *x, **y: None
out = sys.stdout if args.output is None else open(args.output, "w")
variables = {} 			# Variable name -> value
bags = {}				# Bag name -> Capacity
constraints = [] 		# Constraint functions

# Constraint list building
with open(args.input, "r") as input:
	section = -1
	for line in input:
		# Comment / section delineation
		if line.startswith("#####"):
			section = section + 1
			continue

		vals = line.strip("\n").split(" ")
		key = vals[0]
		item = vals[1]

		# Variables
		if section == 0:
			vprint("Registered variable {} with value {}".format(key, item))
			variables[key] = int(item)

		# Values
		elif section == 1:
			vprint("Registered bag {} with value {}".format(key, item))
			bags[key] = int(item)

		# Fitting limit constraints
		elif section == 2:
			min_v = int(key)
			max_v = int(item)
			vprint("Registered fit constraint for {} <= x <= {}".format(min_v, max_v))
			constraints.append(create_fit_limit_constraint(max_v, min_v, variables))

		# Unary inclusive constraints
		elif section == 3:
			vprint("Registered unary inclusive constraint; item {} can only be held by bag {}".format(key, vals[1:]))
			constraints.append(create_unary_inclusive_constraint(vals))

		# Unary exclusive constraints
		elif section == 4:
			vprint("Registered unary exclusive constraint; item {} cannot be held by bag {}".format(key, vals[1:]))
			constraints.append(create_unary_exclusive_constraint(vals))

		# Binary equals constraints
		elif section == 5:
			vprint("Registered binary equals constraint; items {} and {} must be in the same bag".format(item, key))
			constraints.append(create_binary_equals_constraint(vals))

		# Binary inequality constraint
		elif section == 6:
			vprint("Registered binary inequality constraint; items {} and {} must not be in the same bag".format(item, key))
			constraints.append(create_binary_not_equals_constraint(vals))

		# Binary simultaneous constraint
		elif section == 7:
			vprint("Registered binary simultaneous constraint; if present, items {} must be stored in {}, evenly"
				   .format(vals[:2], vals[2:]))
			constraints.append(create_binary_simultaneous_constraint(vals))

single_bag_constraint.vars = list(variables.keys())
constraints.insert(0, single_bag_constraint)
capacity_constraint.vars = list(variables.keys())
constraints.insert(1, capacity_constraint)
vprint("Registered single bag constraint: items may only appear in one bag")
vprint("Registered capacity constraint: no bag may be over capacity")

vprint("\nLoaded file {} with {} variables, {} bags, and {} constraints".format(args.input, len(variables), len(bags),
																			  len(constraints)))
vprint("Beginning constraint solving search")


def csp(universe, next_moves=None):
	vprint("Processing universe {} ".format(universe))
	possible_moves = get_valid_moves(variables, bags, universe, constraints) if next_moves is None else next_moves

	if len(possible_moves) == 0:
		# Either we've found the solution or we have to backtrack some. Check final constraints, if they all pass
		# then just return this universe, otherwise return None to signal for backtracking
		if all_assigned_constraint(variables, bags, universe) and fill_constraint(variables, bags, universe):
			vprint("Found a solution!")
			return universe
		vprint("Dead end reached, backtracking!\n")
		return None

	# Minimum remaining heuristic: choose variables to expand in order of the ones that have the fewest possible
	# remaining values. This just decides on the order of variables, using some magic Python one liner bullshit.
	# The final list is assembled below.
	values_count = Counter(value[0] for value in possible_moves)
	values_sorted = list(sorted(values_count.keys(), key=lambda value: values_count[value]))

	# Least constraining value: sort variables by the number of possible universes that could come after them while
	# maintaining variable sorting from the MRV heuristic.
	possible_universes_grouped = {key: [] for key in values_count.keys()}
	for move in possible_moves:
		# Enact move in alternate universe, add it to the list
		alternate_universe = deepcopy(universe)
		if move[1] not in alternate_universe.keys():
			alternate_universe[move[1]] = []
		alternate_universe[move[1]].append(move[0])

		possible_universes_grouped[move[0]].append((alternate_universe, get_valid_moves(variables, bags, alternate_universe, constraints)))
	del possible_moves  # Reduce memory usage a bit

	possible_universes = []
	for variable in values_sorted:
		possible_universes.extend(sorted(possible_universes_grouped[variable], key=lambda move: len(move[1]), reverse=True))
	del possible_universes_grouped  # Reduce memory usage a bit

	# Now go through the possible moves!
	for next_universe in possible_universes:
		ret = csp(next_universe[0], next_universe[1])
		if ret is not None:
			return ret


result = csp({})
print("Result: {}".format(result))
