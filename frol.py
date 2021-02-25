import os, sys
from collections import namedtuple
from dataclasses import dataclass
from itertools import chain
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
from typing import List

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
    F: int
    encountered: int



@dataclass
class Car:
    id_: int
    path: List[str]

Streets = {}
Cars = []

with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        Streets[name] = Street(len(Streets), int(B), int(E), name, int(L), 0)

    for _ in range(V):
        P, *streets = fin.readline().split()
        assert len(streets) > 0, f'{P} {streets}'
        Cars.append(Car(len(Cars), streets))
        assert all(_ in Streets for _ in Cars[-1].path)
        for street in car.path:
            Streets[street].encountered += 1


print(f'Simulation Time: {D}, Intersections: {I}, Streets: {S}, Cars: {V}, Bonus: {F}\n')

assert S == len(Streets)
assert V == len(Cars)

total_score = 0
solution = []

d = 0
while d <= D:
    d += 1

class Light:
    s: Street
    duration: float

class Graph:
    i_to_ligts = defaultdict(list)

    def add_street(self, s: Street):
        l = Light(s, 0.5)
        i_to_s[s.E].append(l)

    def update_durations(self):
        # TODO me
        pass



out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission_{total_score}.out'
with open(out_file, 'w') as fo:
    g = ( ''.join(str(_) + '\n' for _ in solution ))
    fo.writelines(g)
