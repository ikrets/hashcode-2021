DATA = 'data/c_many_ingredients.in'


def read_pizzas(number):
    pizzas = {}
    with open(DATA) as f:
        f.readline()
        counter = 1
        for _ in range(number):
            pizzas[counter] = frozenset(f.readline().split()[1:])
            counter += 1
            if counter > number:
                return pizzas
    return pizzas


def read_data():
    with open(DATA) as f:
        m, t2, t3, t4 = tuple([int(x) for x in f.readline().split()])
    return m, t2, t3, t4


def count_new_elements_from_pizza(existing_elements: set, pizza_elements: set):
    old_count = len(existing_elements)
    new_count = len(existing_elements.union(pizza_elements))
    return new_count - old_count


def find_best_pizza(team_elements: set, pizzas: dict):
    if len(pizzas) == 0:
        return None

    best_pizza_number = list(pizzas.keys())[0]
    pizza = pizzas[best_pizza_number]
    max_new_elements = count_new_elements_from_pizza(team_elements, pizza)

    for number, elements in pizzas.items():
        tmp = count_new_elements_from_pizza(team_elements, set(elements))
        if tmp > max_new_elements:
            max_new_elements = tmp
            best_pizza_number = number
    print('best pizza is', best_pizza_number,
          'with number of new elements: ', max_new_elements, 'pizzas left:', len(pizzas))
    return best_pizza_number


def fill_teams(teams_count: int, people_in_team: int, pizzas: dict):
    teams = {}
    for _ in range(people_in_team):
        for team_idx in range(teams_count):
            if team_idx not in teams.keys():
                pizza_idxs = list()
                elements = set()
                teams[team_idx] = (pizza_idxs, elements)
            best_pizza = find_best_pizza(teams[team_idx][1], pizzas)
            if best_pizza is None:
                print('no best pizza found! current pizzas len = ',
                      len(pizzas))
                return teams
            new_pizza_idxs = list(teams[team_idx][0])
            new_pizza_idxs.append(best_pizza)

            new_elements = set(teams[team_idx][1])
            new_elements = new_elements.union(pizzas[best_pizza])

            teams[team_idx] = (new_pizza_idxs, new_elements)
            pizzas.pop(best_pizza)
    return teams


output = open('output', 'w')


def save(pizzas_idxs: list):
    global output
    string = str(len(pizzas_idxs))
    for i in pizzas_idxs:
        string += ' ' + str(i)
    string += '\n'
    output.write(string)


def main():
    m, t2, t3, t4 = read_data()
    pizzas = read_pizzas(m)
    print(len(pizzas))
    print(pizzas[len(pizzas) - 1])
    t2_teams = fill_teams(t2, 2, pizzas)
    t3_teams = fill_teams(t3, 3, pizzas)
    t4_teams = fill_teams(t4, 4, pizzas)
    print('\n\nDONE\n\n')

    for team_idx, selection in t2_teams.items():
        pizzas_idxs, _ = selection
        if len(pizzas_idxs) != 2:
            continue
        print(len(pizzas_idxs), *pizzas_idxs)
        save(pizzas_idxs)

    for team_idx, selection in t3_teams.items():
        pizzas_idxs, _ = selection
        if len(pizzas_idxs) != 3:
            continue
        print(len(pizzas_idxs), *pizzas_idxs)
        save(pizzas_idxs)

    for team_idx, selection in t4_teams.items():
        pizzas_idxs, _ = selection
        if len(pizzas_idxs) != 4:
            continue
        print(len(pizzas_idxs), *pizzas_idxs)
        save(pizzas_idxs)


if __name__ == "__main__":
    main()
