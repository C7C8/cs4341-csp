#!/usr/bin/env python3
import argparse
import sys

parser = argparse.ArgumentParser(description="CSP solver for CS 4341")
parser.add_argument("input", type=str, help="")
parser.add_argument("output", type=str, required=False, help="Optional output file; if none is given, output will be "
															 "written to stdout")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
args = parser.parse_args()

# Setup
vprint = print if args.verbose else lambda *x, **y: None
out = sys.stdout if args.output is not None else open(args.output, "w")
