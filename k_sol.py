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

with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        Streets[name] = Street(len(Streets), int(B), int(E), name, int(L))

    for _ in range(V):
        P, *streets = fin.readline().split()
        assert len(streets) > 0, f'{P} {streets}'
        assert len(set(streets)) == len(streets)
        stat_path_time.append(sum(Streets[_].L for _ in streets))
        Cars.append(Car(len(Cars), streets))
        assert all(_ in Streets for _ in Cars[-1].path)

print(f'Simulation Time: {D}, Intersections: {I}, Streets: {S}, Cars: {V}, Bonus: {F}\n')

assert S == len(Streets)
assert V == len(Cars)

print(f'stat path length: {pd.Series(stat_path_time).describe()}')

total_score = 0
Solution = {}

TimeWindow = int(sys.argv[2]) if len(sys.argv) > 2 else D // 10

IntersectionStat = [ [] for _ in range(I) ]
IntersectionStreets = [ set() for _ in range(I) ]
for car in Cars:
    t = 0
    for street_name in car.path:
        street = Streets[street_name]
        intersection_id = street.E
        IntersectionStreets[intersection_id].add(street_name)

        t += street.L

        traffic_from_streets = IntersectionStat[intersection_id]
        time_frame = t // TimeWindow
        time_frame_plus_window = time_frame + TimeWindow

        while len(traffic_from_streets) <= time_frame_plus_window:
            traffic_from_streets.append(Counter())

        assert time_frame_plus_window < len(IntersectionStat[intersection_id]), f'{time_frame_plus_window} < {len(traffic_from_streets)}'
        traffic_from_streets[time_frame][street_name] += 1
        traffic_from_streets[time_frame_plus_window][street_name] += 1
        assert any(street_name in tf for time_frames in IntersectionStat[intersection_id] for tf in time_frames)


for i, intersection in enumerate(IntersectionStat):
    intersection_streets = IntersectionStreets[i]
    if not intersection_streets:
        continue

    stat = { street_name: [] for street_name in intersection_streets }

    for time_frame, counter in enumerate(intersection):
        if not counter:
            continue

        total_cars = sum(counter.values())
        for street_name in intersection_streets:
            num_cars = counter.get(street_name, 0)
            stat[street_name].append(num_cars / total_cars)

        min_cars = min(_ for _ in counter.values() if _ > 0)
        for street_name, num_cars in counter.items():
            stat[street_name].append(num_cars // min_cars)

    stat_avg = { n: (sum(l) / len(l)) for n, l in stat.items() }
    schedule = []

    min_proportion = min(stat_avg.values())
    for street_name, proportion in stat_avg.items():
        schedule.append((street_name, max(1, round(proportion // min_proportion))))

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

out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission_{TimeWindow}.out'
with open(out_file, 'w') as fo:
    fo.write(f'{len(Solution)}')
    for i, schedule in Solution.items():
        if schedule:
            fo.write(f'\n{i}\n{len(schedule)}\n')
            fo.writelines('\n'.join(s[0] + ' ' + str(s[1]) for s in schedule))
