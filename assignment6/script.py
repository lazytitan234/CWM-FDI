import subprocess as s
import sys
import pstats
import re
from pstats import SortKey
import numpy as np
import time
import matplotlib.pyplot as plt

programme = "matmul_fast.py"

def usage():
    print(f"This is a script that runs cProfile on {programme}.\n"
    "It takes in 3 arguments:\n"
    "1. input size to matmul_fast.py -- the dimension of the square matrices we are multiplying\n"
    f"2. rep for {programme} -- number of times to perform matrix multiplication\n"
    "3. number of culprit functions we want from the cProfile output")
    
def pythonstd_matmul(size, rep):
    seed1 = 1.0
    seed2 = 2.0
    A = [[seed1 + ((i * 131 + j * 17) % 100) / 100.0 for j in range(size)] for i in range(size)]
    A = np.array(A)
    B = [[seed2 + ((i * 131 + j * 17) % 100) / 100.0 for j in range(size)] for i in range(size)]
    B = np.array(B)
    start = time.perf_counter()
    for i in range(rep):
        C = A @ B
    end = time.perf_counter()
    time_taken = end - start 
    return time_taken
    
    
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
    match_memory = re.search(r"Maximum resident set size \(kbytes\):\s+(\d+)", result0.stderr)
    peak_mem_kb = match_memory.group(1) if match_memory else "unknown"
    print(f"\033[31mThe peak memory usage of the programme is:\033[0m {peak_mem_kb} kB\n")
    
    #performance bottleneck detector -- consider how long python's standard matmul takes
    standard_time = pythonstd_matmul(int(input_size), int(rep))
    print(f"\033[31mThe time taken by numpy's matmul is:\033[0m {standard_time}s")
    
    #consider how long our matmul_fast3 took
    result = s.run(
        ["python3", programme, str(input_size), str(rep)],
        capture_output=True,
        text=True
    )

    match = re.search(r"MATMUL_FAST3_WALL_S=(\d+)", result.stdout)
    if match:
        wall_s = int(match.group(1))/ 10e9
        print(f"\033[31mTime taken by matmul_fast3 is \033[0m{wall_s}s\n")
        if wall_s > (5 * standard_time):
            print(f"\033[31mPython's standard Matmul using np is more than 5x faster. Potential inefficiency discovered.\033[0m")
    else:
        print("Could not find wall-clock time in output.")
        print("Program output was:")
        print(result.stdout)
        print(result.stderr)
    
    #consider scaling with input size:
    list_of_time_taken_matmulfast3 = []
    list_of_time_taken_numpy = []
    iteration_num = [i for i in range(16)]
    for i in range(1, 17):
        new_input_size = int(i * int(input_size) / 10)
        result = s.run(["/usr/bin/time", "-v", "python3", programme, str(new_input_size), str(rep)], capture_output=True, text=True)
        match = re.search(r"MATMUL_FAST3_WALL_S=(\d+)", result.stdout)
        if match:
            wall_s = int(match.group(1))/ 10e9
            list_of_time_taken_matmulfast3.append(wall_s)
        fast_result = pythonstd_matmul(int(new_input_size), int(rep))
        list_of_time_taken_numpy.append(fast_result)
        
    plt.plot(iteration_num, list_of_time_taken_matmulfast3, label='matmulfast3') 
    plt.plot(iteration_num, list_of_time_taken_numpy, label='numpy')
    
    plt.title("Visualisation of scaling of matmul_fast3 with input size")
    plt.xlabel("scaled input size")
    plt.ylabel("time taken by matmul_fast3 and numpy")
    plt.legend(loc="lower right")

    plt.show()
    
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
