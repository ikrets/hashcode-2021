import sys, json
from os import path
from itertools import chain, combinations
from math import factorial

pd, tqdm = None, None
try:
    import pandas as pd
    from tqdm import tqdm
except:
    pass

TRACE = False

in_file = sys.argv[1]
print(f'*** input filename: {in_file}\n')

I, uniq_ing, num_ing = [], set(), []

with open(in_file) as f:
    M, T2, T3, T4 = map(int, f.readline().split())
    print(f'\tM: {M} Team with 2: {T2}, 3: {T3}, 4: {T4}')

    for _ in range(M):
        I.append(set(f.readline().split()[1:]))
        uniq_ing.update(I[-1])
        num_ing.append(len(I[-1]))

assert len(I) == M
for i in I:
    assert all(_ in uniq_ing for _ in i)

print(f'\tunique ingredients: {len(uniq_ing)}\n')

if pd:
    num_ing = pd.Series(num_ing)
    num_ing_stat = num_ing.describe()
    print(f'\tStat for number of ingredients in pizzas:\n{num_ing_stat}\n\n')

uniq_index = { j: i for i, j in enumerate(uniq_ing) }
for i in range(M):
    I[i] = ( { uniq_index[_] for _ in I[i] }, i )

I.sort(key=lambda _: len(_[0]), reverse=True)

print('solve...')
team_size, idx_space_size = 4, (int(sys.argv[2]) if len(sys.argv) > 2 else 10)
num_teams = T4 + T3 + T2

space_comb = factorial(idx_space_size) // (factorial(team_size) * factorial(idx_space_size - team_size))
print(f'size of index space to search for best score: {idx_space_size}, combinations within this space: {space_comb}')

score_final, out = 0, []

next_idx = idx_space_size
idx_space, idx_used = set(range(next_idx)), set()

for c in (tqdm(range(num_teams)) if tqdm else range(num_teams)):
    if TRACE: print(f'c: {c}/{num_teams}...')
    if not tqdm and (c % max(num_teams//10, int(0.005*num_teams))) == 0:
        print(f'{100*c//num_teams}% [{c}/{num_teams}]...')

    if c == T4 or c == T4 + T3:
        team_size -= 1

    score, score_idx = 0, None

    if team_size <= len(idx_space):
        for idx in combinations(idx_space, team_size):
            idx_ing = set()
            for i in idx:
                idx_ing.update(I[i][0])

            new_score = len(idx_ing)
            if new_score > score:
                score = new_score
                score_idx = idx
                if TRACE: print(f'new_score: {new_score}, {score_idx}')
    else:
        assert False
        idx_ing = set().union(*chain(I[i][0] for i in idx_space))
        assert len(idx_ing) > 0
        score_idx = idx_space
        score = len(score_idx)

    all_ = [ (_ not in idx_used) for _ in score_idx ]
    assert all(all_), ' '.join(str(_) for _ in score_idx) + ': ' + ' '.join(str(_) for _ in all_) + f' {c}'
    idx_used.update(score_idx)

    src_idx = [ I[_][1] for _ in score_idx ]
    if TRACE: print(f'{src_idx}, {idx_used}')
    assert len(src_idx) == team_size
    src_idx = f'\n{team_size} ' + ' '.join(str(_) for _ in src_idx)
    out.append(src_idx)
    score_final += score ** 2

    assert len(score_idx) == team_size
    idx_space.difference_update(score_idx)

    space_size_increase, increase_space_size = team_size, c + 1 == T4 or c + 1 == T4 + T3
    if increase_space_size:
        new_size = len(idx_space) + space_size_increase
        space_size_increase += 2*(new_size) - new_size
    last_idx = min(M, next_idx + space_size_increase)
    idx_space.update(_ for _ in range(next_idx, last_idx))

    if not idx_space:
        break

    next_idx += space_size_increase


in_file_tag = path.splitext(in_file)[0]
out_file = f'{in_file_tag}_submission_{idx_space_size}_{score_final}.out'
print(f'*** output file: {out_file}')
with open(out_file, 'w') as f:
    f.write(f'{len(out)}')
    f.writelines(out)


print(f'*** Final Score: {score_final} ***')

known_scores, known_scores_file = {}, f'{in_file_tag}.scores'
if path.exists(known_scores_file):
    print(f'known scores exist for {in_file}...')
    known_scores = json.load(open(known_scores_file))

expected_score = known_scores.get(str(idx_space_size), 0)
if expected_score > 0:
    print(f'checking known score: {expected_score}...')
    assert score_final == expected_score, f'{score_final} == {expected_score}'
else:
    print(f'writing new one for {out_file}: {score_final}')
    known_scores[idx_space_size] = score_final
    json.dump(known_scores, open(known_scores_file, 'w'))
