import os, sys
from collections import namedtuple
from pprint import pprint
import pandas as pd
from tqdm import tqdm
import random

# File format
# The first line of the input file contains the following integer numbers separated by single spaces:
#     ● R – number of rows of the grid (1 ≤ R ≤ 10000)
#     ● C – number of columns of the grid (1 ≤ C ≤ 10000)
#     ● F – number of vehicles in the fleet (1 ≤ F ≤ 1000)
#     ● N – number of rides (1 ≤ N ≤ 10000)
#     ● B – per-ride bonus for starting the ride on time (1 ≤ B ≤ 10000)
#     ● T – number of steps in the simulation (1 ≤ T ≤ 10 )
#     9
#     N subsequent lines of the input file describe the individual rides, from ride 0 to ride N − 1 . Each line
#     contains the following integer numbers separated by single spaces:
#         ● a – the row of the start intersection (0 ≤ a < R)
#         ● b – the column of the start intersection (0 ≤ b < C)
#         ● x – the row of the finish intersection (0 ≤ x < R)
#         ● y – the column of the finish intersection (0 ≤ y < C)
#         ● s – the earliest start(0 ≤ s < T)
#         ● f – the latest finish (0 ≤ f ≤ T) , (f ≥ s + |x − a| + |y − b|)
#         ○ note that f can be equal to T – this makes the latest finish equal to the end of the simulation

in_file = sys.argv[1]

Ride = namedtuple('Ride', [ 'id', 'a', 'b', 'x', 'y', 's', 'f', 'dist_to_start', 'ride_dist', 'is_valid' ])
rides = []


def get_ride_dist(a, b, x, y):
    return abs(x - a) + abs(y - b)


with open(in_file) as fin:
    R, C, F, N, B, T = map(int, fin.readline().split())

    ride_id = -1
    for _ in range(N):
        ride_id += 1

        a, b, x, y, s, f = map(int, fin.readline().split())

        dist_to_start = a + b
        ride_dist = get_ride_dist(a, b, x, y)
        t_diff = f - s

        is_valid = True
        if f < dist_to_start or f < dist_to_start + ride_dist or t_diff < ride_dist:
            is_valid = False

        rides.append(Ride(ride_id, a, b, x, y, s, f, dist_to_start, ride_dist, is_valid))


assert len(rides) > 0 and len(rides) == N
print(f'RxC [{R}, {C}], F (vehicles): {F}, N (num rides): {N}, T (simu time): {T}\n')

class Car:
    def __init__(self):
        self.end_time = 0
        self.end_pos = (0, 0)

sol_file = sys.argv[2]
solution = []
with open(sol_file) as fin:
    for car_id, line in enumerate(fin.readlines()):
        if not line:
            continue

        n, *l = map(int, line.split())
        assert n == len(l), f'invalid number of rides for car {car_id}'
        solution.append(l)

assert len(solution) == F
print('validate...')

rides_used = set()
for car_id, ride_ids in enumerate(solution):
    x_end, y_end, t_end = 0, 0, 0

    for ride_id in ride_ids:
        assert ride_id not in rides_used, f'{ride_id}, {car_id}'
        rides_used.add(ride_id)

        ride = rides[ride_id]

        dist_to_start = get_ride_dist(x_end, y_end, ride.a, ride.b)

        start_time = t_end + dist_to_start
        start_time = max(ride.s, start_time)
        assert start_time + ride.ride_dist <= ride.f, f'{start_time} + {ride.ride_dist} <= ride.f | {car_id} {ride_id} {dist_to_start}'

        x_end = ride.x
        y_end = ride.y
        t_end = start_time + ride.ride_dist

print(f'...seems fine')

