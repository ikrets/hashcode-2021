import sys
from dataclasses import dataclass
from typing import Set
from collections import Counter, defaultdict
from copy import copy
from llist import dllist
from tqdm import trange
import itertools

@dataclass
class Pizza:
    index: int    
    ingredients: Set[str]


def score_candidate(team_ingredients, pizza):
    return len(pizza.ingredients - team_ingredients) / len(pizza.ingredients)


input_file, output_file = sys.argv[1:3]

ingredient_frequency = Counter()
present = defaultdict(set)
with open(input_file, "r") as fp:
    lines = fp.readlines()
    M, T2, T3, T4 = [int(i) for i in lines[0].strip("\n").split()]
    pizzas = []

    for p in range(M):
        ingredients = set(lines[p + 1].strip("\n").split()[1:])
        ingredient_frequency.update(ingredients)
        pizzas.append(Pizza(index=p, ingredients=ingredients))

        for ingredient in ingredients:
            present[ingredient].add(p)

window = 10000

teams = []
sorted_pizzas = dllist(sorted(pizzas, key=lambda p: len(p.ingredients), reverse=True))
absent_indices = set()

def pick_team(sorted_pizzas, team_size):
    pizza1 = sorted_pizzas.popleft()
    team = [pizza1.index]
    ingredients = copy(pizza1.ingredients)
    for _ in range(team_size - 1):
        candidate = sorted_pizzas.first
        best_candidate_pizza_node = candidate
        best_score = score_candidate(ingredients, best_candidate_pizza_node.value)
        for _ in range(min(window, len(sorted_pizzas) - 1)):
            candidate = candidate.next
            score = score_candidate(ingredients, candidate.value)
            if score > best_score:
                best_candidate_pizza_node = candidate
                best_score = score

        best_candidate_pizza = sorted_pizzas.remove(best_candidate_pizza_node)
        ingredients.update(best_candidate_pizza.ingredients)
        team.append(best_candidate_pizza.index)
    
    return team
    

for t in trange(min(M // 4, T4)):
    teams.append(pick_team(sorted_pizzas, 4))

for t in trange(min((M - len(teams)) // 3, T3)):
    teams.append(pick_team(sorted_pizzas, 3))

for t in trange(min((M - len(teams)) // 2, T2)):
    teams.append(pick_team(sorted_pizzas, 2))

def score_teams(teams):
    total = 0
    for team in teams:
        team_ingredients = set(itertools.chain(*[pizzas[p].ingredients for p in team]))
        total += len(team_ingredients) ** 2
    return total

with open(output_file, "w") as fp:
    fp.write(f"{len(teams)}\n")
    for team in teams:
        fp.write(f"{len(team)} {' '.join(str(t) for t in team)}\n")
        
print(score_teams(teams))


        
        
        

