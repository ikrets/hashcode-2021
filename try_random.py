import sys
import numpy as np
from copy import deepcopy
import random
import tqdm

input_file = sys.argv[1]
n_iterations = int(sys.argv[2])

with open(sys.argv[1], "r") as fp:
    lines = fp.readlines()
    M, T2, T3, T4 = [int(i) for i in lines[0].strip("\n").split()]
    pizzas = []

    for p in range(M):
        pizza = lines[p + 1].strip("\n").split()
        I = int(pizza[0])
        ingridients = pizza[1:]
        pizzas.append((p, ingridients))

def produce_random():
    available_pizzas = set(range(M))
    left = {2: T2, 3: T3, 4: T4}
    def whats_left():
        return [i for i, v in left.items() if v]

        
    solution = []
    indices = list(range(M))
    random.shuffle(indices)
    current_index = 0

    while len(available_pizzas) > min(whats_left()):
        random_team_size = random.choice(whats_left())
        random_indices = indices[current_index: current_index + random_team_size]
        current_index += random_team_size
        solution.append([random_team_size, *random_indices])
        available_pizzas.difference_update(random_indices)
        left[random_team_size] -= 1

    return solution
        

    

def score(solution):
    total_score = 0
    for o in solution[1:]:
        all_ingridients = set()
        for pizza in o[1:]:
            all_ingridients.update(pizzas[pizza][1])
        total_score += len(all_ingridients) ** 2
    return total_score

random_scores = []
for i in tqdm.trange(n_iterations):
    random_scores.append(score(produce_random()))
    tqdm.tqdm.write(f"Current average score: {np.mean(random_scores):0.2f}")

print(np.mean(random_scores))

