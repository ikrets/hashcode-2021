import sys
import numpy as np
from copy import deepcopy
from os import path
import random
import tqdm

input_file = sys.argv[1]
n_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
output_file = sys.argv[3] if len(sys.argv) > 3 else None

with open(input_file, "r") as fp:
    lines = fp.readlines()
    M, T2, T3, T4 = map(int, lines[0].split())
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

    while whats_left() and len(available_pizzas) > min(whats_left()):
        # random_team_size = random.choice(whats_left())
        team_size = max(whats_left())
        random_indices = indices[current_index: current_index + team_size]
        current_index += team_size
        solution.append([team_size, *random_indices])
        available_pizzas.difference_update(random_indices)
        left[team_size] -= 1

    return solution

def score(solution):
    total_score = 0
    for o in solution[1:]:
        all_ingridients = set()
        for pizza in o[1:]:
            all_ingridients.update(pizzas[pizza][1])
        total_score += len(all_ingridients) ** 2
    return total_score


if output_file:
    random_solution = produce_random()
    with open(output_file, "w") as fp:
        fp.write(f"{len(random_solution)}\n")
        for s in random_solution:
            fp.write(f"{' '.join(str(ss) for ss in s)}\n")

random_scores = []
for i in tqdm.trange(n_iterations):
    random_scores.append(score(produce_random()))
    tqdm.tqdm.write(f"Current average score: {np.mean(random_scores):0.2f}, best: {np.max(random_scores)}")

print(np.mean(random_scores))
print(max(random_scores))

print(input_file)
output_file_tmpl = path.splitext(input_file)[0] + '_random'
best_score = np.max(random_scores)
try:
    print('starting endless search...')
    while True:
        sol = produce_random()
        sc = score(sol)
        if sc > best_score:
            print(f'\t* new best score found {best_score} -> {sc}')
            best_score = sc
            with open(output_file_tmpl + f'_{sc}.out', "w") as fp:
                fp.write(f"{len(sol)}\n")
                for s in sol:
                    fp.write(f"{' '.join(str(_) for _ in s)}\n")
except:
    print(f'\t*** final best score: {best_score} ***')
