from dataclasses import dataclass
import numpy as np
import sys
from pathlib import Path
import random

input_file, output_file = [Path(p) for p in sys.argv[1:3]]

@dataclass
class Ride:
    index: int
    a: int
    b: int
    x: int
    y: int
    s: int
    f: int

    @property
    def length(self):
        return abs(self.x - self.a) + abs(self.y - self.b)
        
def read_int_line(fp):
    return [int(i) for i in fp.readline().strip("\n").split(" ")]

class Problem:
    def __init__(self, path):
        fp = path.open("r")
        self.R, self.C, self.F, self.N, self.B, self.T = read_int_line(fp)
        self.rides = []
        self.problem_df = []
        
        for index in range(self.N):
            self.rides.append(Ride(index, *read_int_line(fp)))
            
        for field in ["a", "b", "x", "y", "s", "f"]:
            setattr(self, field, np.array([getattr(p, field) for p in self.rides]))
            

problem = Problem(input_file)
rides_by_start = sorted(problem.rides, key=lambda r: r.s)

taxi_free_from = {t: 0 for t in range(problem.F)}
taxi_position = {t: [0, 0] for t in range(problem.F)}
taxi_rides = {t: [] for t in range(problem.F)}

def distance_to_start(taxi, ride):
    pos = taxi_position[taxi]
    return abs(pos[0] - ride.a) + abs(pos[1] - ride.b)

def end_time(taxi, ride):
    return distance_to_start(taxi, ride) + ride.length

def ride_possible(taxi, ride, current_time):
    start_time = current_time + distance_to_start(taxi, ride)
    end_time = start_time + ride.length

    return start_time >= ride.s and end_time <= ride.f
    
current_ride = 0
for t in range(problem.T):
    if current_ride >= len(rides_by_start):
        break

    possible_taxis = [i for i in range(problem.F) if taxi_free_from[i] <= t]
    no_next = False

    for taxi in possible_taxis:
        # action = random.choice(["pick", "skip", "drop"])
        action = "pick"
        ride = rides_by_start[current_ride]
        if not ride_possible(taxi, ride, t):
            continue

        if action == "pick":
            no_next = True
            taxi_rides[taxi].append(ride)
            taxi_free_from[taxi] = end_time(taxi, ride)
            taxi_position[taxi] = [ride.x, ride.y]
            current_ride += 1
            if current_ride >= len(rides_by_start):
                break

        elif action == "drop":
            no_next = True
            current_ride += 1
            if current_ride >= len(rides_by_start):
                break
        else:
            continue
    
    if len(possible_taxis) == problem.F and not no_next:
        current_ride += 1

with output_file.open("w") as fp:
    for rides in taxi_rides.values():
        fp.write(f"{str(len(rides))}")
        if rides: 
            fp.write(" ")

        fp.write(" ".join(str(int(ride.index)) for ride in rides))
        fp.write("\n")

            
            
