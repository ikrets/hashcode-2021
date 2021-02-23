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

Ride = namedtuple('Ride', [ 'id', 'a', 'b', 'x', 'y', 's', 'f', 'dist_to_start', 'ride_dist' ])
rides = []

stat_start_point_dist = []
stat_ride_length = []
stat_should_assign_immediatelly = 0
stat_cant_start_on_time = 0
stat_invalid_rides = 0

def get_ride_dist(a, b, x, y):
    return abs(x - a) + abs(y - b)


with open(in_file) as fin:
    R, C, F, N, B, T = map(int, fin.readline().split())

    T0 = T # first ever ride

    ride_id = -1
    for _ in range(N):
        ride_id += 1

        a, b, x, y, s, f = map(int, fin.readline().split())
        T0 = min(T0, s)

        dist_to_start = a + b
        ride_dist = get_ride_dist(a, b, x, y)
        t_diff = f - s

        stat_ride_length.append(ride_dist)
        stat_start_point_dist.append(dist_to_start)
        if s < dist_to_start:
            stat_cant_start_on_time += 1

        is_valid = True
        if f < dist_to_start or f < dist_to_start + ride_dist or t_diff < ride_dist:
            stat_invalid_rides += 1
            is_valid = False
        elif s < dist_to_start:
            stat_should_assign_immediatelly += 1

        if is_valid:
            rides.append(Ride(ride_id, a, b, x, y, s, f, dist_to_start, ride_dist))


assert len(rides) > 0 and len(rides) == N - stat_invalid_rides
print(f'RxC [{R}, {C}], F (vehicles): {F}, N (num rides): {N}, T (simu time): {T}\n')

print(f'\tStart point distance:\n{pd.Series(stat_start_point_dist).describe()}\n\n')
print(f'\tRide length:\n{pd.Series(stat_ride_length).describe()}\n\n')
print(f'\tShould assign immediatelly: {stat_should_assign_immediatelly}')
print(f'\tCant start a ride on time: {stat_cant_start_on_time}')
print(f'\tCant fulfill a ride at all: {stat_invalid_rides}')

class Car:
    def __init__(self):
        self.end_time = 0
        self.end_pos = (0, 0)

cars = [ Car() for _ in range(F) ]
solution = [ [] for _ in range(F) ]
assert len(cars) > 0 and len(cars) == F and len(cars) == len(solution)

rides.sort(key=lambda _: (_.s, _.ride_dist))
blacklist = set()

total_score = 0
t = T0
progress = tqdm(total=T)
while len(blacklist) < len(rides) and t < T:
    t_min = 0

    aval_cars = [ i for i, c in enumerate(cars) if c.end_time <= t ]
    if len(aval_cars) <= 0:
        t += 1
        continue

    t_next = T

    for ride in rides:
        if ride.id in blacklist:
            continue

        if t != ride.s: # ! assign only on tick
            t_next = min(t_next, ride.s)
            continue

        found_car = False
        for i in aval_cars:
            car = cars[i]

            dist_to_start = get_ride_dist(*car.end_pos, ride.a, ride.b)

            if car.end_time + dist_to_start <= t: # ! assumes current t == ride.s
                if t + ride.dist_to_start <= ride.f:
                    found_car = True
                    car.end_time = t + ride.ride_dist
                    car.end_pos = (ride.x, ride.y)
                    solution[i].append(ride.id)
                    total_score += ride.ride_dist + (B if t == ride.s else 0)
                    break


        blacklist.add(ride.id)

    t = t_next
    progress.update(t)

progress.close()
print(f'Total score: {total_score}')


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
        assert start_time + ride.ride_dist <= ride.f

        start_time = max(ride.s, start_time)
        assert start_time + ride.ride_dist <= ride.f

        x_end = ride.x
        y_end = ride.y
        t_end = start_time + ride.ride_dist

print(f'...seems fine')

out_file = os.path.splitext(os.path.basename(in_file))[0] + f'_submission_{total_score}.out'
with open(out_file, 'w') as fo:
    g = ( str(len(car)) + ('' if len(car) <= 0 else (' ' + ' '.join(str(_) for _ in car))) + '\n' for car in solution)
    fo.writelines(g)

