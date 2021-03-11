import os, sys
from collections import defaultdict, namedtuple, Counter, deque
from dataclasses import dataclass, field
from itertools import chain
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
from typing import List, Dict, Tuple, Deque
import statistics

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
out_file = sys.argv[2]
print(f'*** Input [{in_file}], Solution: [{out_file}] ***')
TRACE = int(sys.argv[3]) if len(sys.argv) > 3 else 0

@dataclass
class Street:
    id_: int
    B: int
    E: int
    name: str
    L: int

Streets: Dict[str, Street] = {}

@dataclass
class Car:
    path: List[str]

Cars: List[Car] = []

stat_first_path_street = Counter()
stat_intersection_street = Counter()
stat_car_end_street = Counter()
stat_cars_through_intersectoin = Counter()

upper_bound_score = 0
with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        Streets[name] = Street(len(Streets), int(B), int(E), name, int(L))
        stat_intersection_street[E] += 1

    for v in range(V):
        P, *streets = fin.readline().split()
        assert int(P) > 1 and int(P) == len(set(streets)) == len(streets), f'{P} {streets}'
        Cars.append(Car(streets))
        assert all(_ in Streets for _ in Cars[-1].path)

        tt = sum(Streets[s].L for s in streets[1:])
        upper_bound_score += F + (D - tt) if tt <= D else 0

        stat_first_path_street[streets[1]] += 1
        stat_car_end_street[Streets[streets[-1]].B] += 1

        for s in streets:
            stat_cars_through_intersectoin[Streets[s].E] += 1

assert S == len(Streets)
assert V == len(Cars)

print(f'\nSimulation Time: {D}, Intersections: {I}, Streets: {S}, Cars: {V}, Bonus: {F}')
print(f'\nUpper bound total score: {upper_bound_score}')

print(f'\nTop starting streets: {len(stat_first_path_street)} {stat_first_path_street.most_common(10)}')
print(f'Top destination streets: {len(stat_car_end_street)} {stat_car_end_street.most_common(10)}')
print(f'Biggest Intersections: {len(stat_intersection_street)} {stat_intersection_street.most_common(10)}')
print(f'Busiest Intersections: {len(stat_cars_through_intersectoin)} {stat_cars_through_intersectoin.most_common(10)}')

total_score = 0

@dataclass
class Intersection:
    schedule: Dict[str, int]

    cycle_time: int = 0
    def __post_init__(self):
        self.cycle_time = sum(t for t in self.schedule.values())

    queues: Dict[str, Deque[Tuple[int, int]]] = field(default_factory=lambda: defaultdict(deque))

    def greenLight(self, t):
        assert len(self.schedule) >= 1
        if len(self.schedule) == 1:
            return next(iter(self.schedule.keys()))

        while t > self.cycle_time: t -= self.cycle_time
        for k, v in self.schedule.items():
            if t <= v:
                return k
            t -= v

        assert False


Is = [ None for _ in range(I) ] # list of intersections by id == index

with open(out_file) as fo:
    for _ in range(int(fo.readline())): # number of schedules (== intersections with assigned schedule)
        inter_id = int(fo.readline())
        assert 0 <= inter_id <= I, f'0 <= {inter_id} <= {I}: invalid intersection'
        assert Is[inter_id] == None, f'Schedule for intersection [{inter_id}] is duplicated!'

        num_traffic_light_slots = int(fo.readline())
        assert num_traffic_light_slots > 0

        schedule = {}
        for _ in range(num_traffic_light_slots):
            street_name, time_t = fo.readline().split()
            assert street_name in Streets, f'"{street_name}" not among {len(Streets)} known Streets'
            assert street_name not in schedule, f'{street_name} not in {sol.I[inter_id].keys()}: duplicated street schedule'
            assert int(time_t) > 0, f't {time_t} > 0 for {street_name} in intersection {inter_id}'
            schedule[street_name] = int(time_t)

        Is[inter_id] = Intersection(schedule)

assert sum(1 for i in Is if i) > 0, 'no schedules in solution'

assert type(Cars) == list
for i, car in enumerate(Cars):
    start_street = car.path.pop(0)
    inter_id = Streets[start_street].E
    if Is[inter_id]:
        Is[inter_id].queues[start_street].append((i, 0))
    else:
        Cars[i] = None

assert sum(1 for c in Cars if c) == sum(sum(len(l) for l in i.queues.values()) for i in Is if i) , f'{V} == {_s}'

print('\nSimulating schedule...')
total_score = 0
for t in tqdm(range(D+1)):
    for i, inter in enumerate(Is):
        if not inter:
            continue

        street = inter.greenLight(t+1)
        if TRACE: print(f'T[{t}] | inter: {i} - Green: {street}')
        if street not in inter.queues or not inter.queues[street]:
            continue

        car_id, arrival_time = inter.queues[street][0]
        if TRACE: print(f'\tcar [{car_id}] follows "{street}" At end at time: T{arrival_time}')
        if arrival_time > t:
            continue

        inter.queues[street].popleft()
        car = Cars[car_id]
        next_street_name = car.path.pop(0)
        next_street = Streets[next_street_name]
        if TRACE: print(f'\t\tnext_street -->> {next_street_name}')

        if not car.path:
            T = t + next_street.L
            if T <= D:
                add = F + (D - T)
                total_score += add
                if TRACE: print(f'\t\t[+] Score: {add}')
            else:
                if TRACE: print(f'\t\t[-] Score: too late at {T}')
        else:
            next_inter_id = next_street.E
            Is[next_inter_id].queues[next_street_name].append((car_id, t + next_street.L))

    if TRACE: print('------------------------------------------------------')

print(f'Total computed score: {total_score}')
