import os, sys
from collections import namedtuple
from dataclasses import dataclass
from itertools import chain
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random
from typing import List


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

streets_by_enc = []

with open(in_file) as fin:
    D, I, S, V, F = map(int, fin.readline().split())

    for _ in range(S):
        B, E, name, L = fin.readline().split()
        Streets[name] = Street(len(Streets), int(B), int(E), name, int(L), 0)

    for _ in range(V):
        P, *streets = fin.readline().split()
        assert len(streets) > 0, f'{P} {streets}'
        car = Car(len(Cars), streets)
        Cars.append(car)
        assert all(_ in Streets for _ in Cars[-1].path)
        for street in car.path:
            Streets[street].encountered += 1


print(f'Simulation Time: {D}, Intersections: {I}, Streets: {S}, Cars: {V}, Bonus: {F}\n')

assert S == len(Streets)
assert V == len(Cars)


total_score = 0
solution = []



out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission_{total_score}.out'
# with open(out_file, 'w') as fo:
#     fo.write()
#     g = ( ''.join(str(_) + '\n' for _ in solution ))
#     fo.writelines(g)
