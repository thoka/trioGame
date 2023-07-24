from collections import defaultdict
from pprint import pprint
from random import shuffle
import numpy as np
import time

import gc
gc.enable() 


nchip = {
    1: 5,
    2: 5, # 6
    3: 5, #6 
    4: 6,
    5: 6,
    6: 6,
    7: 5,
    8: 5,
    9: 6, # 4
}

N=92
MIN=50
NRUNS = 500000

chips = []
for c in sorted(nchip.keys()):
    chips.extend([c]*nchip[c])  


def get_trio_positions(reverse=True,n = 7):

    def i(x,y):
        return x+y*7
    
    def all_xy():   
        for x in range(0, n):
            for y in range(0,n):
                if x<n-3: 
                    yield ( i(x,y), i(x+1,y), i(x+2,y) )
                    if reverse: yield ( i(x+2,y),   i(x+1,y)   , i(x,y) )
                if y<n-3: 
                    yield ( i(x,y), i(x,y+1)   , i(x,y+2) )
                    if reverse:
                        yield ( i(x,y+2),   i(x,y+1)   , i(x,y) )
                if x<n-3 and y<n-3:
                    yield ( i(x,y), i(x+1,y+1) , i(x+2,y+2) )
                    if reverse:
                       yield ( i(x+2,y+2), i(x+1,y+1) , i(x,y) )

    return [p for p in all_xy()]    

trio_positions = get_trio_positions()

def filter(p, res):
    return (
        abs( res - (chips[p[0]]*chips[p[1]]) )  == chips[p[2]]
    )

def info(p,res):
    a,b,c = chips[p[0]], chips[p[1]], chips[p[2]]
    if a*b+c == res:
        return f'{a}*{b}+{c}'
    else:   
        return f'{a}*{b}-{c}'

def write_grid(f):
    for y in range(0,7):
        f.write(" ".join([str(chips[x+y*7]) for x in range(0,7)]))
        f.write("\n")
    f.write("\n")

def rows(chips=chips):
    s = [str(c) for c in chips] 
    return [ "".join(s[i:i+7]) for i in range(0,len(chips),7) ]

def write_solutions(f):
    res = []
    for r in range(1,N+1):
        i = set([info(s,r) for s in summary[r] ])
        i = ",".join(i)
        f.write(f'{r}:{i}\n')

def solutions():
    res = defaultdict(list)
    for p in trio_positions:
        a,b,c = chips[p[0]], chips[p[1]], chips[p[2]]
        res[a*b+c].append(p)
        res[a*b-c].append(p)
    return res

sol_count = [0]*100

def solutions_counter():
    # reuising the same array is faster than creating a new one
    for i in range(0,N+1):
        sol_count[i] = 0
    counter = sol_count
    # counter = defaultdict(int)
    for p in trio_positions:
        a,b,c = chips[p[0]], chips[p[1]], chips[p[2]]
        counter[a*b+c] +=1
        counter[a*b-c] +=1 
    return counter

stats = [0]*N

missing_stats = defaultdict(int)
missing_count_stats = defaultdict(int)

def write_stats():
    return
    # print(".",end="",flush=True)
    with open(f'{N}-stats.dat','w') as f:
        for i in range(0,N):
            f.write(f'{i+1} {stats[i]}\n')
    with open(f'{N}-missing.dat','w') as f:
        for i in range(0,N):
            f.write(f'{i+1} {missing_stats[i]}\n')
    with open(f'{N}-missing_count.dat','w') as f:
        for i in sorted(missing_count_stats.keys()):
            f.write(f'{i} {missing_count_stats[i]}\n')

runs = 0

lasttime = time.perf_counter_ns()

while True:
    runs+=1
    shuffle(chips)
    sol_count = solutions_counter()

    missing = 0
    last_non_missing = 0

    for i in range(1,N+1):
        stats[i-1] += sol_count[i]
        if sol_count[i] == 0:
            missing_stats[i-1] += 1
            missing += 1

    missing_count_stats[missing] += 1

    for i in range(1,N+1):
        if sol_count[i] == 0:
            last_non_missing = i-1
            break
    
    if runs%NRUNS == 0:
        # print(stats)
        #print(chr(27) + "[2J")
        print("\033c", end="")
        write_stats()            
        last = lasttime
        lasttime = time.perf_counter_ns()
        single_run_time = (lasttime-last)/NRUNS/1000
        print(f'{single_run_time:0.1f} µs per run')

        gc_stats = gc.get_stats(True)

        print()
        print(gc_stats)

        if single_run_time > 10:
            print("too slow, exiting")
            exit()
        

    if last_non_missing < MIN: 
        continue

    else: 

        summary = solutions()

        unique_solutions = [  len(set([info(s,r) for s in summary[r] ])) for r in range(1,N+1) ]
        min_count = min(unique_solutions[0:last_non_missing])
        
        if min_count < 1: 
            # this should never happen (but it does)
            continue

        if last_non_missing < 86:
            if min_count < 3:
                continue

        # write report

        ## rotate and mirror to normalize filename
        a = np.array(chips).reshape(-1,7)
        names = []

        for i in range(0,4):
            a = np.rot90(a)
            names.append( "".join([str(c) for c in a.flatten()]) )
        
        a = np.flip(a,0)
        
        for i in range(0,4):
            a = np.rot90(a)
            names.append( "".join([str(c) for c in a.flatten()]) )
        
        a = np.flip(a,1)

        for i in range(0,4):
            a = np.rot90(a)
            names.append( "".join([str(c) for c in a.flatten()]) )

        name = sorted(names)[0]    

        fn = f"{last_non_missing}-{min_count}--{'-'.join(rows(name))}.txt"
        with open(fn,'w') as f: 
            write_grid(f)
            write_solutions(f)








        

    


