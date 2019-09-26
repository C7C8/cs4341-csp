#!/usr/bin/env python3
import argparse
import sys
import time
from collections import Counter
from copy import deepcopy

from constraints import *
from csp_utils import get_valid_moves

# WARNING! This project contains massive amounts of python one-liner bullshit,
# which is... actually extraordinarily useful. Proceed at your own risk!

parser = argparse.ArgumentParser(description="CSP solver for CS 4341")
parser.add_argument("input", type=str, help="")
parser.add_argument("-o", "--output", type=str, help="Optional output file; if none is given, output will be "
															 "written to stdout")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output (file parsing, solver progress logging)")
parser.add_argument("--dumb", "-d", action="store_true", help="Disable all heuristics and use random shuffling")
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

capacity_constraint.vars = list(variables.keys())
constraints.insert(0, capacity_constraint)
vprint("Registered single bag constraint: items may only appear in one bag")
vprint("Registered capacity constraint: no bag may be over capacity")

vprint("Loaded file {} with {} variables, {} bags, and {} constraints\n".format(args.input, len(variables), len(bags),
																			  len(constraints)))
vprint("Beginning constraint solving search")
iterations = 0


def csp(universe, next_moves=None, depth=0):
	global iterations
	iterations += 1
	possible_moves = get_valid_moves(variables, bags, universe, constraints) if next_moves is None else next_moves
	vprint("".join(["\t" for n in range(depth)]) + "Processing universe {}: {} possible changes ".format(universe, len(possible_moves)))

	if len(possible_moves) == 0:
		# Either we've found the solution or we have to backtrack some. Check final constraints, if they all pass
		# then just return this universe, otherwise return None to signal for backtracking
		if all_assigned_constraint(variables, bags, universe) and fill_constraint(variables, bags, universe):
			return universe
		return None

	# Minimum remaining heuristic: choose variables to expand in order of the ones that have the fewest possible
	# remaining values. This just decides on the order of variables, using some magic Python one liner bullshit.
	# The final list is assembled below.
	values_count = Counter(value[0] for value in possible_moves)
	values_sorted = list(sorted(values_count.keys(), key=lambda value: values_count[value]))

	# Most constrained / degree heuristic: group by number of occurrences so we can sort those groups
	# by variables that are involved in the most constraints
	values_count_grouped = {}
	for variable, count in values_count.items():
		if count not in values_count_grouped:
			values_count_grouped[count] = []
		values_count_grouped[count].append(variable)
	values_sorted.clear()

	# Sort each list by the number of constraints that appear on each variable...
	for count, vbls in values_count_grouped.items():
		values_count_grouped[count] = sorted(vbls,
									 key=lambda var: sum([var in constraint.vars for constraint in constraints]), reverse=True)

	# ...and finally group them all back together again into values_sorted. This list now represents a combination of
	# the minimum remaining values heuristic with most constrained / degree heuristic as a tiebreaker.
	for count in sorted(values_count_grouped.keys()):
		values_sorted.extend(values_count_grouped[count])
	del values_count_grouped

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
		# This "sorted" bit is the core of the least-constraining values engine; it prioritizes values for variables
		# where the number of future possibilities is greatest (i.e. the value is least constraining).
		possible_universes.extend(sorted(possible_universes_grouped[variable], key=lambda move: len(move[1]), reverse=True))
	del possible_universes_grouped  # Reduce memory usage a bit

	# Now go through the possible moves!
	for next_universe in possible_universes:
		ret = csp(next_universe[0], next_universe[1], depth + 1)
		if ret is not None:
			return ret


ctime = time.time() * 1000
result = csp({})
total_time = (time.time() * 1000) - ctime
if result is None:
	vprint("Failed to find a solution, took {} iterations and {:.1f}ms".format(iterations, total_time))
	print("no solution", file=out)
	if args.output is not None:
		out.close()


# Print report
vprint("Found a solution in {} iterations ({:.1f} ms)!".format(iterations, total_time))
vprint("{}\n".format(result))
for bag, items in result.items():
	print("{} {}".format(bag, " ".join(items)), file=out)
	print("number of items: {}".format(len(items)), file=out)
	weight = sum(variables[item] for item in items)
	print("total weight: {}/{}".format(weight, bags[bag]), file=out)
	print("wasted capacity: {}\n".format(bags[bag] - weight), file=out)

if args.output is not None:
	out.close()
