from collections import defaultdict

INPUT_FILE = 'd_metropolis_evgenii/input'
OUTPUT_FILE = 'd_metropolis_evgenii/output'

CARS_ID = 1


class Ride:
    id = 0
    sx = 0
    sy = 0
    st = 0
    fx = 0
    fy = 0
    ft = 0
    picked = False

    def dist(self):
        return abs(self.sx - self.fx) + abs(self.sy - self.fy)

class Car:
    def __init__(self):
        global CARS_ID
        self.id = int(CARS_ID)
        CARS_ID += 1

    vacant = True
    x = 0
    y = 0
    rides = []
    current = Ride() # empty ride

    # def do_ride():
    #     assert not self.vacant
    #     if self.current.fx > self.x:
    #         self.x += 1
    #         return
    #     elif self.current.fx < self.x:
    #         self.x -= 1
    #         return
    #     if self.current.fy > self.y:
    #         self.y += 1
    #         return
    #     elif self.current.fy < self.y:
    #         self.y -= 1
    #         return

    #     self.vacant = True


def read_data():
    rides = []
    with open(INPUT_FILE, 'r') as f:
        counter = 0
        for line in f.readlines()[1:]:
            sx, sy, ex, ey, st, et = line.split()
            r = Ride()
            r.id = counter
            counter += 1
            r.sx, r.sy, r.st = int(sx), int(sy), int(st)
            r.ex, r.ey, r.et = int(ex), int(ey), int(et)
            rides.append(r)
    return rides


def read_setup():
    with open(INPUT_FILE) as f:
        return [int(x) for x in f.readline().split()]


def write_result(car_rides):
    f = open(OUTPUT_FILE, 'w')
    for idx, rides in car_rides.items():
        string  = str(len(rides))
        for r in rides:
            string += ' ' + str(r)
        f.write(string + '\n')


def count_time_to_start(c: Car(), r: Ride(), current_time: int):
    time_to_ride_start_point = current_time + abs(r.sx - c.x) + abs(r.sy - c.y)
    return max(time_to_ride_start_point, r.st)


def count_vacant_ts(c: Car(), r: Ride(), current_time: int):
    ride_start = count_time_to_start(c, r, current_time)
    next_vacant_time = ride_start + abs(r.sx - r.ex) + abs(r.sy - r.ey)
    return next_vacant_time


def select_best_ride(c: Car(), rides, t: int):
    assert (len(rides) > 0)
    best_ride = 0
    best_time_to_start = count_time_to_start(c, rides[0], t)
    for i, r in enumerate(rides):
        time_to_start = count_time_to_start(c, r, t)
        if time_to_start + r.dist() > r.ft:
            continue
        if best_time_to_start > time_to_start:
            best_ride = i
            best_time_to_start = time_to_start

    return rides.pop(best_ride)

def simulate(cars, rides, t):
    vacant_cars = defaultdict(list)
    vacant_cars[0] = cars
    cars_rides = defaultdict(list)
    for ts in range(t):
        print(ts)
        for c in vacant_cars[ts]:
            new_ride = select_best_ride(c, rides, ts)
            next_vacant_ts = count_vacant_ts(c, new_ride, ts)
            if next_vacant_ts <= t:
                cars_rides[c.id].append(new_ride.id)
            vacant_cars[next_vacant_ts].append(c)
    return cars_rides



def main():
    r, c, f, n, b, t = read_setup()
    cars = [Car() for _ in range(f)]
    rides = read_data()
    result = simulate(cars, rides, t)
    write_result(result)
    print(len(rides))


if __name__ == '__main__':
    main()
