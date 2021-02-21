from itertools import chain, combinations
from math import factorial
# import pandas as pd
# from tqdm import tqdm

M, T2, T3, T4 = map(int, input().split())

print(f'M: {M} Team with 2: {T2}, 3: {T3}, 4: {T4}\n')

uniq_ing, num_ing = set(), []
I = []
i = M
while i:
    I.append(set(input().split()[1:]))
    uniq_ing.update(I[-1])
    num_ing.append(len(I[-1]))
    i -= 1

assert len(I) == M
for i in I:
    assert all(_ in uniq_ing for _ in i)

print(f'uniq ings: {len(uniq_ing)}\n')

# num_ing = pd.Series(num_ing)
# num_ing_stat = num_ing.describe()
# print(f'number of ings stat:\n{num_ing_stat}\n\n')

uniq_index = { j: i for i, j in enumerate(uniq_ing) }
for i in range(M):
    I[i] = ( { uniq_index[_] for _ in I[i] }, i )

I.sort(key=lambda _: len(_[0]), reverse=True)
# print(I[:10])

# for i in range(1, 11):
#     j0 = i * M // 11
#     print(j0, len(I[j0][0]), list(I[j0][0])[:10])
#     j1 = i * (T4 + T3 + T2) // 11
#     print('\t', j1, len(I[j1][0]), list(I[j1][0])[:10])
#     j2 = i * 10000 // 11
#     print('\t\t', j2, len(I[j2][0]), list(I[j2][0])[:10])

#exit()
# comb = {}
# for i in tqdm(range(M)):
#     ing0 = I[i]
#     for j in range(i, M):
#         ing1 = I[j]
#         uniq_01 = ing0 | ing1
#         comb[(i, j)] = uniq_01

        # for k in range(j, M):
        #     ing2 = I[k]
        #     for l in range(k, M):
        #         ing3 = I[l]
        #         uniq_ing = ing0 | ing1 | ing2 | ing3
        #         comb[(i, j, k, l)] = uniq_ing

TRACE = False
print('solve...')
cur_max = 4
idx_space_size = 30
next_idx = idx_space_size
idx_space = set(range(next_idx))
idx_used = set()

window_comb = factorial(idx_space_size) // (factorial(cur_max) * factorial(idx_space_size - cur_max))
print(f'window size: {idx_space_size}, combinations within window: {window_comb}')

score_final = 0
out= []

ITS = T4 + T3 + T2
for c in range(ITS):
    if TRACE: print(f'c: {c}...')
    if c % (ITS // 100) == 0:
        print(f'{c}/{ITS}...')

    if c == T4 or c == T4 + T3:
        cur_max -= 1

    score, score_idx = 0, None

    for idx in combinations(idx_space, cur_max):
        idx_ing = set()
        for i in idx:
            idx_ing.update(I[i][0])

        new_score = len(idx_ing)
        if new_score > score:
            score = new_score
            score_idx = idx
            if TRACE: print(f'new_score: {new_score}, {score_idx}')

    src_idx = ( I[_][1] for _ in score_idx )
    if TRACE: print(f'{src_idx}, {idx_used}')
    assert all(_ not in idx_used for _ in src_idx)
    idx_used.update(src_idx)

    src_idx = f'\n{cur_max} ' + ' '.join(str(_) for _ in src_idx)
    out.append(src_idx)
    score_final += score ** 2

    for _ in range(cur_max):
        idx_space.remove(score_idx[_])
        idx_space.add(next_idx + _)

    next_idx += cur_max

with open(f'c_submission_{idx_space_size}.out', 'w') as f:
    f.write(f'{len(out)}')
    f.writelines(out)

print(f'Final Score: {score_final}')

