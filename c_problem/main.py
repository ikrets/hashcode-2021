

DATA = 'data/c_many_ingredients.in'


def read_pizzas(number):
    pizzas = {}
    with open(DATA) as f:
        f.readline()
        counter = 1
        for _ in range(number):
            pizzas[counter] = frozenset(f.readline().split()[1:])
            counter += 1
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

    best_pizza_number = pizzas.keys()[0]
    pizza = pizzas[best_pizza_number]
    max_new_elements = count_new_elements_from_pizza(team_elements, pizza)

    for number, elements in pizzas.items():
        tmp = count_new_elements_from_pizza(team_elements, set(elements))
        if tmp > max_new_elements:
            max_new_elements = tmp
            best_pizza_number = number
    return best_pizza_number


def main():
    m, t2, t3, t4 = read_data()
    pizzas = read_pizzas(m)
    print(len(pizzas))
    print(pizzas[len(pizzas) - 1])


if __name__ == "__main__":
    main()
