from time import sleep
import tqdm

for _ in tqdm.tqdm(range(10)):
    sleep(0.5)

print('Single-line loading bar test is done.')
