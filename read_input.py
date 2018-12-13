import sys

def read_file(n, file='./input/sentences.txt'):
    training_set = []
    test_set = []
    i = 1
    with open(file, 'r') as ip:
        for line in ip:
            if i <= n:
                training_set.append(line.strip())
            elif i > n:
                if i > 2*n: break
                test_set.append(line.strip())
            i += 1
    return training_set, test_set
