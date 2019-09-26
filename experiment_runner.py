import argparse
import os
import time
import subprocess
from statistics import mean

import pandas as pd

parser = argparse.ArgumentParser(description="Experiment runner")
parser.add_argument("data_dir", type=str, help="Data dir to grab input files from")
parser.add_argument("script", type=str, help="Path to script")
parser.add_argument("output", type=str, help="File to write output to")
parser.add_argument("--trials", "-t", type=int, default=5, help="Number of trials to run")
args = parser.parse_args()

data = pd.DataFrame(columns=["regular", "dumb"])
for file in os.listdir(args.data_dir):
	times = []
	dumb_times = []

	# Regular trials first
	print("Testing on {}".format(file))
	for trial in range(args.trials):
		ctime = time.time() * 1000
		subprocess.run([args.script, "-o", "/dev/null", args.data_dir + "/" + file])
		times.append((time.time() * 1000) - ctime)

	# Dumb trials
	print("Dumb testing on {}".format(file))
	for trial in range(args.trials):
		ctime = time.time() * 1000
		subprocess.run([args.script, "-do", "/dev/null", args.data_dir + "/" + file])
		dumb_times.append((time.time() * 1000) - ctime)

	data = data.append(pd.DataFrame({"regular": [mean(times)], "dumb": [mean(dumb_times)]}, index=[file]), sort=True)


data.to_csv(args.output)
print("Done!")

