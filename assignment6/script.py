import subprocess as s
import sys
import os 
import pstats
from pstats import SortKey

programme = "matmul_fast.py"

def usage():
    print("This is a script that runs cProfile on matmul_fast.py.\n It takes in 2 arguments:\n 1. input size to matmul_fast.py -- the dimension of the square matrices we are multiplying\n 2. number of functions we want from the cProfile output")
    
    
def main(argv):

    #checks for valid arguments
    if len(argv) != 3:
        usage()
        return
        
    #input parsing    
    input_size = argv[1]
    num_to_report = argv[2]
    profile_file = "profile.out"
    
    #Run cProfile and save results in terms of binary stats
    s.run(["python3", "-m", "cProfile", "-o", profile_file, programme, str(input_size)], capture_output=True)
    
    #read stats
    stats = pstats.Stats(profile_file)
    stats.strip_dirs()
    
    #find slowest function -- most time spent on that function itself
    print(f"\033[31mThe top {num_to_report} function that took up the most time themselves are given below:\033[0m\n")
    stats.sort_stats(SortKey.TIME).print_stats(int(num_to_report))
    
    #find function with most calls
    print(f"\033[31mThe top {num_to_report} functions that were called the most number of times are given below:\033[0m\n")
    stats.sort_stats(SortKey.CALLS).print_stats(int(num_to_report))
    
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
