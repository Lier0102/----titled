from tqdm import tqdm, trange

val = 0

for i in trange(100000000):
    val += 3

print(val)