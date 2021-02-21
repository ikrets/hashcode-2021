import numpy as np
import matplotlib.pyplot as plt
import sys

with open(sys.argv[1], "r") as fp:
    lines = fp.readlines()
    M, T2, T3, T4 = [int(i) for i in lines[0].strip("\n").split()]
    pizzas = []

    for p in range(M):
        pizza = lines[p + 1].strip("\n").split()
        I = int(pizza[0])
        ingridients = pizza[1:]
        pizzas.append((p, ingridients))

left_pizzas = M - 2 * T2
fillable_3_teams = left_pizzas // 3

pizzas_by_ingridient_count = sorted(pizzas, key=lambda p: len(p[1]), reverse=True)
plt.hist([len(p[1]) for p in pizzas], bins=40)
plt.savefig("data/e_histogram.png")

output = []
fillable_4 = min(M // 4, T4)
for m in range(fillable_4):
    output.append([4, pizzas_by_ingridient_count[m][0],
                      pizzas_by_ingridient_count[fillable_4 + m][0],
                      pizzas_by_ingridient_count[2 * fillable_4 + m][0],
                      pizzas_by_ingridient_count[3 * fillable_4 + m][0]])
    
fillable_3 = min((M - fillable_4 * 4) // 3, T3)
for m in range(fillable_3):
    base = fillable_4 * 4
    output.append([3, pizzas_by_ingridient_count[base + m][0],
                      pizzas_by_ingridient_count[base + fillable_3 + m][0],
                      pizzas_by_ingridient_count[base + 2 * fillable_3 + m][0]])

fillable_2 = min((M - fillable_4 * 4 - fillable_3 * 3) // 2, T2)
for m in range(fillable_2):
    base = fillable_4 * 4 + fillable_3 * 3
    output.append([2, pizzas_by_ingridient_count[base + m][0],
                      pizzas_by_ingridient_count[base + fillable_2 + m][0]])

total_score = 0
for o in output[1:]:
    team_size = int(o[0])
    ps = o[1:]

    total = sum(len(pizzas[p][1]) for p in ps)
    all_ingridients = set()
    for pizza in ps:
        all_ingridients.update(pizzas[pizza][1])
    total_score += len(all_ingridients)**2
print(f"Total score: {total_score}")

total_sum = 0
for o in output[1:]:
    total_sum += sum(len(pizzas[oo][1]) for oo in o)**2
print(f"Total sum with intersections ignored: {total_sum}")

def score(output):
    total_score = 0
    for o in output[1:]:
        all_ingridients = set()
        for pizza in o[1:]:
            all_ingridients.update(pizzas[pizza][1])
        total_score += len(all_ingridients) ** 2
    return total_score
        
with open(sys.argv[2], "w") as fp:
    fp.write(f"{len(output)}\n")
    for o in output:
        fp.write(f"{' '.join(str(o_elem) for o_elem in o)}\n")

