#!/usr/bin/env python

import os, sys
from collections import namedtuple, Counter
from dataclasses import dataclass
from itertools import chain
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
from typing import List, Dict

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
TRACE = int(sys.argv[4]) if len(sys.argv) > 4 else 0

@dataclass
class Street:
    id_: int
    B: int
    E: int
    name: str
    L: int

@dataclass
class Car:
    id_: int
    path: List[str]

Streets, Cars = {}, []
stat_path_time = []
street_cars = Counter()
intersection_car_times = None
intersection_streets = Counter()
streets_car_times = {}

with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        Streets[name] = Street(len(Streets), int(B), int(E), name, int(L))
        intersection_streets[E] += 1

    for _ in range(V):
        P, *streets = fin.readline().split()
        assert len(streets) > 0, f'{P} {streets}'
        assert len(set(streets)) == len(streets)
        stat_path_time.append(sum(Streets[_].L for _ in streets))
        Cars.append(Car(len(Cars), streets))
        assert all(_ in Streets for _ in Cars[-1].path)

        street_cars[streets[0]] += 1
        if not intersection_car_times: intersection_car_times = [ [] for _ in range(I) ]
        t = 0
        for s in streets[1:]:
            L = Streets[s].L
            streets_car_times.setdefault(s, []).append(t + L//2)
            t += L
            intersection_car_times[Streets[s].E].append(t)

print(f'Simulation Time: {D}, Intersections: {I}, Streets: {S}, Cars: {V}, Bonus: {F}')

assert S == len(Streets)
assert V == len(Cars)

#print(f'stat path length: {pd.Series(stat_path_time).describe()}')
#print(f'\{intersection_streets.most_common(10)}')

n0, n1 = len(street_cars), len(Cars)
print(f'\n{n1} cars start on {n0} streets, avg: {n1/n0:.3f} cars on street at T0\n{street_cars.most_common(min(n1 - n0, 5))}')

# time_stdev = pd.Series([ statistics.stdev(t) for t in intersection_car_times if len(t) >= 2 ]).describe()
# print(f'\n{time_stdev}')

# s1 = pd.Series([ statistics.stdev(t) for t in streets_car_times.values() if len(t) >= 2 ]).describe()
# s2 = pd.Series([ statistics.mean(t) for t in streets_car_times.values() if len(t) >= 2 ]).describe()
#s3 = [ statistics.multimode(_ // (D // 100) for _ in t) for t in streets_car_times.values() if len(t) >= 2 ][:10]
# print(f'\n{s1}\n{s2}')

total_score = 0
Solution = {}

TimeWindow = int(sys.argv[2]) if len(sys.argv) > 2 else min(D // 10, D // 100, D // 1000)
if TimeWindow <= 0: TimeWindow = D
ExpectedDelay = int(sys.argv[3]) if len(sys.argv) > 3 else TimeWindow // 100

IntersectionStat = [ [] for _ in range(I) ]
IntersectionStreets = [ set() for _ in range(I) ]
for car in Cars:
    t = 0
    for street_name in car.path:
        street = Streets[street_name]
        intersection_id = street.E
        IntersectionStreets[intersection_id].add(street_name)

        t += street.L

        traffic_windows = IntersectionStat[intersection_id]
        time_frame = t // TimeWindow
        time_frame_plus_delay = (t + ExpectedDelay) // TimeWindow

        if len(traffic_windows) <= time_frame_plus_delay:
            traffic_windows.extend(Counter() for _ in range(len(traffic_windows), time_frame_plus_delay + 1))

        assert time_frame_plus_delay < len(IntersectionStat[intersection_id]), f'{time_frame_plus_delay} < {len(traffic_windows)}'
        traffic_windows[time_frame][street_name] += 1
        if ExpectedDelay > 0:
            traffic_windows[time_frame_plus_delay][street_name] += 1
        assert any(street_name in tf for time_frames in IntersectionStat[intersection_id] for tf in time_frames)


for i, traffic_windows in enumerate(IntersectionStat):
    total_street_cars = Counter()
    for time_frame, streets_stat in enumerate(traffic_windows):
        total_street_cars.update(streets_stat)
    total_cars = sum(total_street_cars.values())

    if TRACE and i == 499:
        print(f'Intersection {i}: {sum(total_street_cars.values())} {total_street_cars}')

    if not total_street_cars:
        continue

    stat = { k: [] for k in total_street_cars.keys() }

    # time_frame  I   II   III  IV
    # total       38  350  64   88  | 540
    # street_1    5   0    50   78  | 133
    # street_2    7   100  14   6   | 127
    # street_3    26  250   0   4   | 280

    for streets_stat in traffic_windows:
        if not streets_stat:
            continue

        tf_min_cars = min(_ for _ in streets_stat.values() if _ > 0)
        tf_total_cars = sum(streets_stat.values())
        # if tf_total_cars < total_cars // 10:
        #     continue

        time_frame_weight = tf_total_cars / total_cars
        if TRACE and i == 499:
            print(f'tf_min_cars: {tf_min_cars}, tf_total_cars: {tf_total_cars} / {total_cars} | {time_frame_weight}')

        for street_name in stat.keys():
            num_cars = streets_stat.get(street_name, 0)
            wtf_val = time_frame_weight * (num_cars // tf_min_cars)
            if TRACE and i == 499:
                print(f'\t{street_name}: {num_cars} {wtf_val}')
            stat[street_name].append(wtf_val)

    stat_avg = { n: sum(l) / len(l) for n, l in stat.items() if sum(l) > 0 }
    schedule = []

    max_proportion = max(stat_avg.values())
    min_proportion = min(stat_avg.values())
    max_min_diff = max_proportion / min_proportion
    if TRACE and i == 499:
        print(f'{min_proportion}\n{list(stat.items())[:10]}\n{stat_avg}')
    for street_name, proportion in stat_avg.items():
        if proportion >= min_proportion:
            schedule.append((street_name, max(1, round(2 * (proportion / min_proportion) / max_min_diff))))
            if TRACE and i == 499:
                print(f'\t{street_name}: {proportion} {schedule[-1][1]}')

    schedule.sort(lambda x: -x[1])
    # schedule = [ (n, 1) for n, _ in schedule ] # so facked up that this is actually more scores...
    Solution[i] = [(schedule[0][0], 1)] if len(schedule) == 1 else schedule

# $ >> ttime python sol_tmpl.py data/b.txt 10
# Simulation Time: 5070, Intersections: 7073, Streets: 9102, Cars: 1000, Bonus: 1000

# $ >> ttime python sol_tmpl.py data/c.txt 10                                                                                                                                                                                                                                       Simulation Time: 1640, Intersections: 10000, Streets: 35030, Cars: 1000, Bonus: 100
# Simulation Time: 1640, Intersections: 10000, Streets: 35030, Cars: 1000, Bonus: 100

# >> ttime python sol_tmpl.py data/d.txt 1000
# Simulation Time: 8071, Intersections: 8000, Streets: 95928, Cars: 1000, Bonus: 1000

# $ >> ttime python sol_tmpl.py data/e.txt 10
# Simulation Time: 676, Intersections: 500, Streets: 998, Cars: 1000, Bonus: 500

# $ >> ttime python sol_tmpl.py data/f.txt 10
# Simulation Time: 1992, Intersections: 1662, Streets: 10000, Cars: 1000, Bonus: 500

out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission_{TimeWindow}_{ExpectedDelay}.out'
print(f'\n*** output: {out_file} ***')
with open(out_file, 'w') as fo:
    fo.write(f'{len(Solution)}')
    for i, schedule in Solution.items():
        if schedule:
            fo.write(f'\n{i}\n{len(schedule)}\n')
            fo.writelines('\n'.join(s[0] + ' ' + str(s[1]) for s in schedule))
