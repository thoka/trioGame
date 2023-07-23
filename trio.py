from collections import defaultdict
from pprint import pprint
from random import shuffle
import numpy as np
import time

nchip = {
    1: 5,
    2: 6,
    3: 6,
    4: 6,
    5: 6,
    6: 6,
    7: 5,
    8: 5,
    9: 4,
}

N=92
NRUNS = 100000

chips = []
for c in sorted(nchip.keys()):
    chips.extend([c]*nchip[c])  

def get_trio_positions(reverse=True,n = 7):

    class i:
        def __init__(i,x,y):
            assert x>=0 and x<n
            assert y>=0 and y<n
            i.x,i.y,i.i = x,y,x+y*7
        def __repr__(i):
            return repr( (i.x,i.y,i.i) )

    def all_xy():   
        for x in range(0, n):
            for y in range(0,n):
                if x<n-3: 
                    yield [ i(x,y), i(x+1,y), i(x+2,y) ]
                    if reverse: yield [ i(x+2,y),   i(x+1,y)   , i(x,y) ]
                if y<n-3: 
                    yield [ i(x,y), i(x,y+1)   , i(x,y+2) ]
                    if reverse:
                        yield [ i(x,y+2),   i(x,y+1)   , i(x,y) ]
                if x<n-3 and y<n-3:
                    yield [ i(x,y), i(x+1,y+1) , i(x+2,y+2) ]
                    if reverse:
                       yield [ i(x+2,y+2), i(x+1,y+1) , i(x,y) ]

    return [p for p in all_xy()]    

trio_positions = get_trio_positions()

def filter(p, res):
    return (
        abs( res - (chips[p[0].i]*chips[p[1].i]) )  == chips[p[2].i]
    )

def info(p,res):
    a,b,c = chips[p[0].i], chips[p[1].i], chips[p[2].i]
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
        a,b,c = chips[p[0].i], chips[p[1].i], chips[p[2].i]
        res[a*b+c].append(p)
        res[a*b-c].append(p)

    return res

stats = [0]*N

missing_stats = defaultdict(int)
missing_count_stats = defaultdict(int)

def write_stats():
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
    summary = solutions()
    sol_count = [len(summary[i]) for i in range(1,N+1)]
    missing = 0
    last_non_missing = 0

    for i in range(0,N):
        stats[i] += sol_count[i]
        if sol_count[i] == 0:
            missing_stats[i] += 1
            missing += 1
    missing_count_stats[missing] += 1

    for i in range(0,N):
        if sol_count[i] == 0:
            last_non_missing = i
            break

    if runs%NRUNS == 0:
        # print(stats)
        write_stats()            
        last = lasttime
        lasttime = time.perf_counter_ns()
        print(f'{(lasttime-last)/NRUNS/1000:0.1f} µs per run')

    if last_non_missing < 81: 
        continue

    min_sol = min(sol_count)  


    if last_non_missing >= 75: 

        unique_solutions = [  len(set([info(s,r) for s in summary[r] ])) for r in range(1,N+1) ]
        min_count = min(unique_solutions[0:last_non_missing])

        if last_non_missing < 80:
            if min_count < 2:
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


    if min_sol>0: 

        N += 1

        stats = [0]*N

        missing_stats = defaultdict(int)
        missing_count_stats = defaultdict(int)

        # pprint(summary)







        

    


