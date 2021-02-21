M, T2, T3, T4 = [int(i) for i in input().split()]

# data = [input().split() for _ in range(M)]
data = []

demand = T4*4 + T3*3 + T2*2 #550
teams = T4 + T3 + T2 #185
# print(f'demand {demand}, teams {teams}')

ingr_set = set()

for idx in range(M):
    item = input().split()
    ingrs = item[1:]
    for ingr in ingrs:
        ingr_set.add(ingr)
    ingrs.sort()
    data.append([idx, int(item[0]), ingrs])

# print(f'ingrs total {len(ingr_set)}')

data.sort(key=lambda x: int(x[1]), reverse=True)

# for item in data:
#     print(item)

deliveries = []
for_score = []
for counter in range(T2-1):
    pizza1 = data.pop(0)
    pizza2 = data.pop()
    ingrs = pizza1[2]
    ingrs.extend(pizza2[2])
    ingrs = set(ingrs)
    deliveries.append(
        (2, pizza1[0], pizza2[0])
    )
    for_score.append(len(ingrs)**2)

for counter in range(T3):
    pizza1 = data.pop(0)
    pizza2 = data.pop()
    pizza3 = data.pop()
    ingrs = pizza1[2]
    ingrs.extend(pizza2[2])
    ingrs.extend(pizza3[2])
    ingrs = set(ingrs)
    deliveries.append(
        (3, pizza1[0], pizza2[0], pizza3[0])
    )
    for_score.append(len(ingrs)**2)

for counter in range(T4-12):
    pizza1 = data.pop(0)
    pizza2 = data.pop()
    pizza3 = data.pop()
    pizza4 = data.pop()
    ingrs = pizza1[2]
    ingrs.extend(pizza2[2])
    ingrs.extend(pizza3[2])
    ingrs.extend(pizza4[2])
    ingrs = set(ingrs)
    deliveries.append(
        (4, pizza1[0], pizza2[0], pizza3[0], pizza4[0])
    )
    for_score.append(len(ingrs)**2)


for item in deliveries:
    print(item)

# print(sum(for_score))
