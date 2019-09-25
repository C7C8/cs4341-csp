#!/usr/bin/env python3
import argparse
import sys
from typing import Dict


# WARNING! This file contains massive amounts of python one-liner bullshit,
# which is... actually extraordinarily useful. Proceed at your own risk!
from constraints import *
from csp_utils import get_valid_moves

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
constraint_vars = []    # Variables affected by constraint


# Base constraint: An item cannot be in more than one bag
def single_bag_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
	all_items = {i for bag in curr.values() for i in bag}
	return len(set(all_items)) == len(all_items)


# Base constraint: No bag can be over-capacity
def capacity_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
	totals = {k: sum(map(lambda i: vars_f[i], items)) for k, items in curr.items()}
	return not any(s > bags_f[k] for k, s in totals.items())


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
constraints.append(single_bag_constraint)
capacity_constraint.vars = list(variables.keys())
constraints.append(capacity_constraint)
vprint("Registered single bag constraint: items may only appear in one bag")
vprint("Registered capacity constraint: no bag may be over capacity")

vprint("\nLoaded file {} with {} variables, {} bags, and {} constraints".format(args.input, len(variables), len(bags),
																			  len(constraints)))
vprint("Beginning constraint solving search")

moves = get_valid_moves(variables, bags, {}, constraints)
print("Yes!")
