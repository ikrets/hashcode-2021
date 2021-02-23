import sys
from tqdm import tqdm

input_file, output_file = sys.argv[1:3]


class Ride:
    def __init__(self, idx, a, b, x, y, min_start, max_finish):
        self.idx = idx
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.min_start = min_start
        self.max_finish = max_finish

    def __str__(self):
        return f'{self.idx} {self.a} {self.b} {self.x} {self.y} {self.min_start} {self.max_finish}'

    @property
    def distance(self):
        return abs(self.a-self.x) + abs(self.b-self.y)


class Vehicle:
    def __init__(self, idx, row=0, col=0, steps_left=0, rides_done=None):
        self.idx = idx
        self.row = row
        self.col = col
        self.steps_left = steps_left
        self.rides_done = rides_done if rides_done is not None else []


    def __str__(self):
        return f'{self.idx} {self.row} {self.col} {self.steps_left} {self.rides_done}'


def distance(a, b, x, y):
    return abs(a-x) + abs(b-y)

ride_list = []

with open(input_file, "r") as f:
    first_line = f.readline()
    ROWS, COLS, VEHICLES, RIDES, BONUS, STEPS = map(int, first_line.split())
    print(ROWS, COLS, VEHICLES, RIDES, BONUS, STEPS)
    lines = f.readlines()
    for idx, line in enumerate(lines):
        ride = Ride(idx, *map(int, line.split()))
        ride_list.append(ride)

cars = [Vehicle(idx) for idx in range(VEHICLES)]

for step in tqdm(range(STEPS)):
    for car in cars:
        if len(ride_list):
            if car.steps_left == 0:
                if len(car.rides_done) > 0:
                    car.row, car.col = car.rides_done[-1].x, car.rides_done[-1].y
                ride_list.sort(
                    key=lambda ride: (
                        -distance(car.row, car.col, ride.a, ride.b), # to pop closest to car
                        ride.distance, # longest distance first
                    )
                )
                ride = ride_list.pop()
                car.steps_left = ride.distance + distance(car.row, car.col, ride.a, ride.b)
                if ride.distance <= STEPS:
                    car.rides_done.append(ride)
            car.steps_left -= 1



with open(output_file, "w") as f:
    for car in cars:
        M = len(car.rides_done)
        rides_idxes = " ".join([str(ride.idx) for ride in car.rides_done])
        f.write(f'{M} {rides_idxes}\n')
