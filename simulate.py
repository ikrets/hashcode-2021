import os, sys
from collections import namedtuple
from dataclasses import dataclass
from itertools import chain, permutations, combinations_with_replacement, product
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
import numpy as np
from typing import List, Optional, Tuple
import multiprocessing

from collections import defaultdict

# ● The rst line contains ve numbers:
# ○ an integer D (1 ≤ D ≤ 10 4)  - the duration of the simulation, in seconds,
# ○ an integer I (2 ≤ I ≤ 10 5) - the number of intersections (with IDs from 0 to I -1 ),
# ○ an integer S (2 ≤ S ≤ 10 5) - the number of streets,
# ○ an integer V (1 ≤ V ≤ 10 3) - the number of cars,
# ○ an integer F (1 ≤ F ≤ 10 3) - the bonus points for each car that reaches # its destination before time D
#
#   ● The next S lines contain descriptions of streets. Each line contains:
#   ○ two integers B and E (0 ≤ B < I , 0 ≤ E < I ) - the intersections at the start and the end of the street, respectively,
#   ○ the street name (a string consisting of between 3 and 30 lowercase ASCII characters a -z and the character - ),
#   ○ an integer L (1 ≤ L ≤ D ) - the time it takes a car to get from the beginning to the end of that street.
#
#   ● The next V lines describe the paths of each car. Each line contains:
#   ○ an integer P (2 ≤ P ≤ 10 3) - the number of streets that the car wants to travel,
#   ○ followed by P names of the streets: The car starts at the end of the first street
#     (i.e. it waits for the green light to move to the next street)
#     and follows the path until the end of the last street. The path of a car is
#     always valid, i.e. the streets will be connected by intersections.

in_file = sys.argv[1]

@dataclass
class Street:
    id_: int
    B: int
    E: int
    name: str
    L: int
    encountered: int
    starting: bool = False



@dataclass
class Car:
    id_: int
    path: List[str]

@dataclass
class Intersection:
    index: int    
    streets_in: List[Street]
    streets_out: List[Street]
    timeline: List[Tuple[int, Street]]

Streets = {}
Cars = []

with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())
    Intersections = {index: Intersection(index=index, streets_in=[], streets_out=[],
                                         timeline=[])
                    for index in range(I)}

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        s = Street(len(Streets), int(B), int(E), name, int(L), 0)
        Streets[name] = s
        Intersections[s.B].streets_out.append(s)
        Intersections[s.E].streets_in.append(s)

    for _ in range(V):
        P, *streets = fin.readline().split()
        assert len(streets) > 0, f'{P} {streets}'
        car = Car(len(Cars), streets)
        Cars.append(car)
        assert all(_ in Streets for _ in Cars[-1].path)
        for street in car.path[:-1]:
            Streets[street].encountered += 1

cars_by_path_length = sorted(Cars, key=lambda c: sum(Streets[s].L for s in c.path))
for car in cars_by_path_length:
    t = 0
    for i, street_name in enumerate(car.path[:-1]):
        street = Streets[street_name]
        Intersections[street.E].timeline.append((t, street))
        t += Streets[car.path[i + 1]].L

timelines = {index: [None for _ in range(D)] for index in range(I)}
max_timeline_step = {index: 0 for index in range(I)}
collisions = 0
for index, intersection in Intersections.items():
    for t, street_name in intersection.timeline:
        if timelines[index][t] is None:
            timelines[index][t] = street_name
            max_timeline_step[index] = max(t, 
                                           max_timeline_step[index])
        else:
            for tt in range(t + 1, D):
                if timelines[index][tt] is None:
                    timelines[index][tt] = street_name
                    max_timeline_step[index] = max(tt, 
                                                max_timeline_step[index])
                    break
        

trials = 10000
cores = 8

def calculate(index):
    solution = {}
    non_empty_streets = [s.name for s in Intersections[index].streets_in
                            if Streets[s.name].encountered]
    min_lateness = float("inf")
    for _ in range(trials):
        schedule = np.random.permutation(non_empty_streets)
        where_street = {s: i for i, s in enumerate(schedule)}
        lateness = 0

        for t, street in Intersections[index].timeline:
            lateness += (t % len(schedule) - where_street[street.name]) % len(schedule)
        
        if lateness < min_lateness:
            min_lateness = lateness
            solution[index] = schedule
    
    return solution

pool = multiprocessing.Pool(processes=cores)
solution = {}
for index_solution in tqdm(pool.imap_unordered(calculate, np.arange(I)),
                           total=I):
    solution.update(index_solution)

out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission.out'
solution = {index: streets for index, streets in solution.items() if len(streets)}
with open(out_file, 'w') as fo:
    fo.write(f"{len(solution)}\n")

    for intersection_index, streets in solution.items():
        if len(streets):
            fo.write(f"{intersection_index}\n")
            fo.write(f"{len(streets)}\n")
            for i in range(len(streets)):
                fo.write(f"{streets[i]} 1\n")
