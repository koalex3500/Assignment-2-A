#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: Alexander Ko
Semester: "Fall 2024"
Professor: Leo Lu
The python code in this file is original work written by
Alexander Ko. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This is my Assignment 2A for OPS445 the purpose of this script will help with visuakizing the system memory usage
and can enter any specific program name

'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    # check the docs for an argparse option to store this as a boolean.
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    parser.add_argument('-H', '--human_readable', action='store_true', help='Display memory vaues in human_readable format') #This is added as check requires it,this line helps with human-readable format
    args = parser.parse_args()
    return args
# create argparse function
# -H human readable
# -r running only

def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    fill = int(percent * length) #this will calculate the number filled bars
    return '#' * fill + ' ' * (length-fill) #this is to return graph using '#' like i was shown in asssingment2a  sample output for ###


#This function will retrieve the total of the system memory in kB
#Will return int: TOtal System Memory.
def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    with open('/proc/meminfo', 'r') as mem_info:
     for line in mem_info:
      if 'MemTotal' in line:
       return int(line.split()[1]) #Extracts the memory value in kB

#This function will retrieve available system memory in kB.
#Will return the available system memory left
def get_avail_mem() -> int:
    "return total memory that is available"
    with open('/proc/meminfo', 'r') as mem_info:
     for line in mem_info:
      if 'MemAvailable' in line:
       return int(line.split()[1]) #extracts the memory value in kB

#This function will retrieve process IDs (PIDs) with the specific program name
#Will return list of the PIDs associated with the program
def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
    pids = os.popen('pidof ' + app_name).read().strip() #This will use the pidof command to find the PIDs
    return pids.split() if pids else [] #returns list of PIDs or an empty list if not found


#This function will retrieve the resident memory usage or RSS of the process by its PID from above
#Will return the mmeory used by the process in kB or like the sample output syas not found
def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    try:
     with open(f'/proc/{proc_id}/status') as smaps:
      for line in smaps:
       if 'VmHWM' in line:
        return int(line.split()[1]) #Extracts RSS value in kb
    except (FileNotFoundError):
     return 0 #This will return 0 if process doesnt exists

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

#This function will display memory usage in bar graph
def display_memory_bar(used_mem, total_mem, length, human_readable):
    percent_used = used_mem / total_mem #This calculates percentage of the memory used
    bar = percent_to_graph(percent_used, length) #this is generating bar graph
    if human_readable:
     used_mem_read = bytes_to_human_r(used_mem) #this will convert used memory to human-readable format
     total_mem_read = bytes_to_human_r(total_mem) #this will convert total memory to human-readable format
     print(f'Memory: [{bar}|{percent_used*100:.0f}%] {used_mem_read}/{total_mem_read}')
    else:
     print(f'Memory: [{bar}|{percent_used*100:.0f}%] {used_mem}/{total_mem}') #this one will print raw

if __name__ == "__main__":
    args = parse_command_args() #parse commalnd line argument
    total_mem = get_sys_mem()  #this will retrieve total system memory
    avail_mem = get_avail_mem() #this will retireve available system memory

    if not args.program:
     used_mem = total_mem - avail_mem #calculate used memory
     percent_used = used_mem / total_mem
     bar = percent_to_graph(percent_used, args.length)

     if args.human_readable:
      print(f"Memory: [{bar}|{percent_used*100:.0f}%] {bytes_to_human_r(used_mem)}/{bytes_to_human_r(total_mem)}")
     else:
      print(f"Memory: [{bar}|{percent_used*100:.0f}%] {used_mem}/{total_mem}")
    else:
     pids = pids_of_prog(args.program)
     if not pids:
      print(f"{args.program} not found")
     else:
      rss = 0
      for pid in pids:
       pid_rss = rss_mem_of_pid(pid)
       rss += pid_rss
       percent_used = pid_rss / total_mem
       bar= percent_to_graph(percent_used, args.length)

       if args.human_readable:
        print(f"{pid}: [{bar}|{percent_used*100:.0f}%] {bytes_to_human_r(pid_rss)}/{bytes_to_human_r(total_mem)}")
       else:
        print(f"{pid}: [{bar}|{percent_used*100:.0f}%] {pid_rss}/{total_mem}")

      percent_used = rss / total_mem
      bar = percent_to_graph(percent_used, args.length)
      if args.human_readable:
       print(f"{args.program}: [{bar}|{percent_used*100:.0f}%] {bytes_to_human_r(rss)}/{bytes_to_human_r(total_mem)}")
      else:
       print(f"{args.program}: [{bar}|{percent_used*100:.0f}%] {rss}/{total_mem}")
    # process args
    # if no parameter passed, 
    # open meminfo.
    # get used memory
    # get total memory
    # call percent to graph
    # print

    # if a parameter passed:
    # get pids from pidof
    # lookup each process id in /proc
    # read memory used
    # add to total used
    # percent to graph
    # take total our of total system memory? or total used memory? total used memory.
    # percent to graph.
