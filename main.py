#!/usr/bin/env python3
import argparse
import sys
from typing import List, Callable, Dict

parser = argparse.ArgumentParser(description="CSP solver for CS 4341")
parser.add_argument("input", type=str, help="")
parser.add_argument("-o", "--output", type=str, help="Optional output file; if none is given, output will be "
															 "written to stdout")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
args = parser.parse_args()

# Setup
vprint = print if args.verbose else lambda *x, **y: None
out = sys.stdout if args.output is None else open(args.output, "w")


variables = {} 																# Variable name -> value
bags = {}																	# Bag name -> Capacity
constraints: List[Callable[[Dict, Dict, Dict[str, List[str]]], bool]] = [] 	# Constraint functions
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
			variables[key] = item

		# Values
		elif section == 1:
			vprint("Registered bag {} with value {}".format(key, item))
			bags[key] = item

		# Fitting limit constraints
		elif section == 2:
			min_v = int(key)
			max_v = int(item)
			vprint("Registered fit constraint for {} <= x <= {}".format(min_v, max_v))

			def fit_limit_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				return all(map(lambda bag: min_v <= len(bag) <= max_v, curr.items()))
			constraints.append(fit_limit_constraint)

		# Unary inclusive constraints
		elif section == 3:
			vprint("Registered unary inclusive constraint; item {} can only be held by bag {}".format(item, vals[1:]))

			def unary_inclusive_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				contains_item = {bag_name: contents.contains(item) for bag_name, contents in curr}

				# No bag contains the item in question, so the constraint is satisfied by default
				if not any(contains_item.values()):
					return True

				# The item must be in the given bag and there can only be one instance of it
				return any(contains_item[k] for k in vals[1:]) and sum(contains_item) == 1
			constraints.append(unary_inclusive_constraint)

		# Unary exclusive constraints
		elif section == 4:
			vprint("Registered unary exclusive constraint; item {} cannot be held by bag {}".format(item, vals[1:]))

			def unary_exclusive_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				return not any(item in curr[k] for k in vals[1:])
			constraints.append(unary_exclusive_constraint)

		# Binary equals constraints
		elif section == 5:
			vprint("Registered binary equals constraint; items {} and {} must be in the same bag".format(item, key))

			def binary_equals_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				# If both items aren't in the set of all items taken this constraint is always satisfied
				all_items = {i for bag in curr.values() for i in bag}
				if len(all_items.intersection({item, key})) < 2:
					return True

				# Filter down to a list of bags that have one item or the other; it should be 1 for this to be satisfied
				return len(list(filter(lambda bag: item in bag or key in bag, curr.values()))) == 1
			constraints.append(binary_equals_constraint)

		# Binary inequality constraint
		elif section == 6:
			vprint("Registered binary inequality constraint; items {} and {} must not be in the same bag")

			def binary_not_equals_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				# If both items aren't in the set of all items taken this constraint is always satisfied
				all_items = {i for bag in curr.values() for i in bag}
				if len(all_items.intersection({item, key})) < 2:
					return True

				# Filter down to a list of bags that have one item or the other; it should be 2 for this to be satisfied
				return len(list(filter(lambda bag: item in bag or key in bag, curr.values()))) == 2
			constraints.append(binary_not_equals_constraint)

		# Binary simultaneous constraint
		elif section == 7:
			vprint("Registered binary simultaneous constraint; if present, items {} must be stored in {}, respectively"
				   .format(vals[:2], vals[2:]))

			def binary_simultaneous_constraint(vars_f: Dict, bags_f: Dict, curr: Dict) -> bool:
				# If neither item is in the set of all items taken, this returns true
				all_items = {i for bag in curr.values() for i in bag}
				if len(all_items.intersection(set(vals[:2]))) == 0:
					return True

				# Get the bag that the first item belongs to
				first_bag = list(filter(lambda bag: vals[0] in bag.values(), curr))[0]
				second_bag = vals[2] if first_bag == vals[3] else vals[3]
				# Make sure the other bag contains the second item
				return vals[1] in curr[second_bag]
			constraints.append(binary_simultaneous_constraint)


vprint("Loaded file!")
