# Backtracker Usage

*Author: Christopher Myers (crmyers)*

Usage, from `./backtracker.py -h`:

    usage: backtracker.py [-h] [-o OUTPUT] [--verbose] [--dumb] input
    
    CSP solver for CS 4341
    
    positional arguments:
      input
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Optional output file; if none is given, output will be
                            written to stdout
      --verbose, -v         Enable verbose output (file parsing, solver progress
                            logging)
      --dumb, -d            Disable all heuristics and use random shuffling

      
The simplest way to run the program is `./backtracker.py inputFile.txt`. It'll think about the input for a while before
spitting out a report in the specified format for this assignment. If you provide `-o [file]`, it'll write the output
to a file instead.

If you want to view a log of the solver's progress, use `-v` (verbose output). The indentation of the lines of the log
indicate the depth at which the program is operating (so you can implicitly see backtracking). This is some sample
output from running on input10.txt, excluding the standard report at the end:

    Registered variable A with value 2
    Registered variable B with value 3
    Registered variable C with value 3
    Registered variable D with value 2
    Registered bag a with value 4
    Registered bag b with value 4
    Registered bag c with value 4
    Registered unary inclusive constraint; item A can only be held by bag ['c']
    Registered unary inclusive constraint; item B can only be held by bag ['a']
    Registered single bag constraint: items may only appear in one bag
    Registered capacity constraint: no bag may be over capacity
    Loaded file data/base/input10.txt with 4 variables, 3 bags, and 4 constraints
    
    Beginning constraint solving search
    Processing universe {}: 8 possible changes 
    	Processing universe {'c': ['A']}: 6 possible changes 
    		Processing universe {'c': ['A'], 'a': ['B']}: 3 possible changes 
    			Processing universe {'c': ['A'], 'a': ['B'], 'b': ['C']}: 1 possible changes 
    				Processing universe {'c': ['A', 'D'], 'a': ['B'], 'b': ['C']}: 0 possible changes 
    Found a solution in 5 iterations (3.6 ms)!
    {'c': ['A', 'D'], 'a': ['B'], 'b': ['C']}
