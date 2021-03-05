import os, sys
from collections import namedtuple
from dataclasses import dataclass
from itertools import chain, permutations, combinations_with_replacement, product
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
import numpy as np
from typing import Deque, List, Optional, Set, Tuple, Dict
import multiprocessing
from collections import deque

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

@dataclass
class StreetOpen:
    ts: Set[int]
    period: int

@dataclass
class CarPosition:
    car_id: int
    current_path_i: int
    current_eta: int

def simulate_schedules(solution):
    street_queues: Dict[str, Deque[CarPosition]] = defaultdict(deque)
    street_transit: Dict[str, Set[CarPosition]] = defaultdict(list)
    car_intersection_waiting_time: Dict[Tuple[int, int], int] = defaultdict(lambda: 0)
    intersection_miss_open_slot: Dict[int, List[int]] = defaultdict(list)

    early_bonus = 0
    completion_bonus = 0

    for car in Cars:
        street_queues[car.path[0]].appendleft(CarPosition(car_id=car.id_, current_path_i=0,
                                                      current_eta=0))

    street_to_open_times: Dict[str, StreetOpen] = {}
    for _, streets in solution.items():
        for i, street in enumerate(streets):
            street_to_open_times[street] = StreetOpen(ts=set([i]), period=len(streets))

    for t in range(D):
        street_names = list(street_queues.keys())
        for street_name in street_names:
            queue = street_queues[street_name]
            if not queue:
                continue

            open_times = street_to_open_times[street_name]
            if t % open_times.period in open_times.ts:
                leaving_car = queue.pop()
                leaving_car.current_path_i += 1
                next_street_name = Cars[leaving_car.car_id].path[leaving_car.current_path_i]
                leaving_car.current_eta = Streets[next_street_name].L
                street_transit[next_street_name].append(leaving_car)

            for car in queue:
                car_intersection_waiting_time[(car.car_id, Streets[street_name].E)] += 1
            
            if not queue:
                street_queues.pop(street_name)

        street_names = list(street_transit.keys())
        for street_name in street_names:
            transits = street_transit[street_name]

            for transit in transits:
                transit.current_eta -= 1
                if transit.current_eta == 0:
                    transits.remove(transit)
                    if not street_transit[street_name]:
                        street_transit.pop(street_name)

                    # car has arrived
                    if len(Cars[transit.car_id].path) == transit.current_path_i + 1:
                        completion_bonus += F
                        early_bonus += D - t
                    else:
                        street_queues[street_name].appendleft(transit)
                        open_times = street_to_open_times[street_name]
                        missed_open_times = [missed_t for missed_t in open_times.ts if missed_t <= (t + 1) % open_times.period]
                        missed = max(missed_open_times) if missed_open_times else max(open_times.ts)
                        intersection_miss_open_slot[Streets[street_name].E].append((t + 1 - missed) % open_times.period)

    return early_bonus, completion_bonus, car_intersection_waiting_time, intersection_miss_open_slot

cars_to_path_length = {c.id_: sum(Streets[s].L for s in c.path) for c in Cars}
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
        

trials = 100
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

early_bonus, completion_bonus, car_intersection_waiting_time, interesection_miss_open_slot = simulate_schedules(solution)
print(f"Early bonus: {early_bonus}, completion bonus: {completion_bonus}")

intersection_total_waiting_time = defaultdict(list)
for (car_id, interesection_id), waiting_time in car_intersection_waiting_time.items():
    intersection_total_waiting_time[interesection_id].append(waiting_time)

sorted_by_length = sorted(range(I), key=lambda i: len(Intersections[i].streets_in), reverse=True)

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(20, 10))
axes[0].plot([np.mean(intersection_total_waiting_time[i]) for i in sorted_by_length])
axes[0].set_title("average waiting time")
axes[1].plot([np.mean(interesection_miss_open_slot[i]) for i in sorted_by_length])
axes[1].set_title("average late to the open slot")
axes[2].plot([len(Intersections[i].streets_in) for i in sorted_by_length])
axes[2].set_title("intersection size")
plt.tight_layout()
plt.savefig("intersection_waiting_size.png")

with open(out_file, 'w') as fo:
    fo.write(f"{len(solution)}\n")

    for intersection_index, streets in solution.items():
        if len(streets):
            fo.write(f"{intersection_index}\n")
            fo.write(f"{len(streets)}\n")
            for i in range(len(streets)):
                fo.write(f"{streets[i]} 1\n")
