import numpy as np

with open("data/e_many_teams.in", "r") as fp:
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

output = []
for m in range(T2):
    output.append([2, pizzas_by_ingridient_count[m][0]])
for m in range(T2, T2 + fillable_3_teams):
    output.append([3, pizzas_by_ingridient_count[m][0]])

for m in range(T2):
    output[m].append(pizzas_by_ingridient_count[m + T2 + fillable_3_teams][0])
for m in range(fillable_3_teams):
    output[T2 + m].extend([
        pizzas_by_ingridient_count[2 * T2 + fillable_3_teams + m][0],
        pizzas_by_ingridient_count[2 * T2 + 2 * fillable_3_teams + m][0]]
    )

int_stats = {2: [], 3: []}
total_score = 0
for o in output[1:]:
    team_size = int(o[0])
    ps = o[1:]

    total = sum(len(pizzas[p][1]) for p in ps)
    all_ingridients = set()
    for pizza in ps:
        all_ingridients.update(pizzas[pizza][1])
    int_stats[team_size].append(total - len(all_ingridients))
    total_score += len(all_ingridients)**2
print(f"Total score: {total_score}")

for team_size in [2, 3]:
    print(f"Teams size {team_size}: {np.mean(int_stats[team_size])} +- {np.std(int_stats[team_size])}")

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
        


    

with open("data/e_many_teams.out", "w") as fp:
    fp.write(f"{len(output)}\n")
    for o in output:
        fp.write(f"{' '.join(str(o_elem) for o_elem in o)}\n")

