import subprocess as s
import sys
import os 
import pstats
import re
from pstats import SortKey

programme = "matmul_fast.py"

def usage():
    print(f"This is a script that runs cProfile on matmul_fast.py.\n"
    "It takes in 3 arguments:\n"
    "1. input size to matmul_fast.py -- the dimension of the square matrices we are multiplying\n"
    "2. rep for matmul_fast.py -- number of times to perform matrix multiplication\n"
    "3. number of functions we want from the cProfile output")
    
    
def main(argv):
    #checks for valid arguments
    if len(argv) != 4:
        usage()
        return
        
    #input parsing    
    input_size = argv[1]
    rep = argv[2]
    num_to_report = argv[3]
    profile_file = "profile.out"
    
    #Run cProfile and save results in an output file
    s.run(["python3", "-m", "cProfile", "-o", profile_file, programme, str(input_size), str(rep)], capture_output=True)
    
    #read stats
    stats = pstats.Stats(profile_file)
    stats.strip_dirs()
    
    #find slowest function -- most time spent on that function itself
    print(f"\033[31mThe top {num_to_report} function that took up the most time themselves are given below:\033[0m\n")
    stats.sort_stats(SortKey.TIME).print_stats(int(num_to_report))
    
    #find function with most calls
    print(f"\033[31mThe top {num_to_report} functions that were called the most number of times are given below:\033[0m\n")
    stats.sort_stats(SortKey.CALLS).print_stats(int(num_to_report))
    
    #run time to get wall clock and CPU time
    result0 = s.run(["/usr/bin/time", "-v", "python3", programme, str(input_size), str(rep)], capture_output=True, text=True)
    
    #print out wall clock and CPU time
    print(f"\033[31mThe following are overall timing statistics for the entire programme:\033[0m\n")
    print(result0.stderr)
    
    #run perf to get info on CPU
    result1 = s.run(["sudo", "perf", "stat", "-e", "cycles,instructions,cache-misses", "python3", programme, str(input_size), str(rep)], capture_output=True, text=True)
    
    #print out CPU stats
    print(f"\033[31mThe following are CPU stats for the entire programme:\033[0m\n")
    print(result1.stderr)
    
    #print out peak memory usage
    match = re.search(r"Maximum resident set size \(kbytes\):\s+(\d+)", result0.stderr)
    peak_mem_kb = match.group(1) if match else "unknown"
    print(f"\033[31mThe peak memory usage of the programme is:\033[0m {peak_mem_kb} kB")
    
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
