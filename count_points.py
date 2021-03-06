
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
solution_file = sys.argv[2]

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
    slots: Dict[int, Optional[str]]
    street_to_slot: Dict[str, int]

Streets = {}
Cars = []


with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())
    Intersections = {index: Intersection(index=index, streets_in=[], streets_out=[],
                                         timeline=[],
                                         slots=defaultdict(lambda: None),
                                         street_to_slot={})
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

for intersection in Intersections.values():
    intersection.streets_in = [s for s in intersection.streets_in if s.encountered]
    intersection.streets_out = [s for s in intersection.streets_out if s.encountered]

@dataclass
class StreetOpen:
    ts: Set[int]
    period: int

@dataclass
class CarPosition:
    car_id: int
    current_path_i: int
    current_eta: int

def simulate_solution(solution):
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
        for i, street in streets.items():
            if street not in street_to_open_times:
                street_to_open_times[street] = StreetOpen(ts=set([i]), period=len(streets))
            else:
                street_to_open_times[street].ts.add(i)

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

    return early_bonus, completion_bonus

    
with open(solution_file, "r") as fp:
    solution = {}
    intersection_count = int(fp.readline().strip("\n "))

    for _ in range(intersection_count):
        index = int(fp.readline().strip("\n "))
        streets = int(fp.readline().strip("\n "))
        slots = {}
        t = 0
        for _ in range(streets):
            street, length = fp.readline().strip("\n ").split(" ")
            length = int(length)

            for _ in range(length):
                slots[t] = street
                t += 1

        solution[index] = slots

early_bonus, completion_bonus = simulate_solution(solution)
print(f"Early bonus: {early_bonus}, completion bonus: {completion_bonus}. Total: {early_bonus + completion_bonus}")
