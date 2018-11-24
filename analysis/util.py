import numpy as np

def shuffle(x, y):
    m = x.shape[0]
    rand_perm = np.random.permutation(m)
    x = x[rand_perm]
    y = y[rand_perm]
    return x, y

def batch_iter(x, y, batch_size):
    num_batches = int(np.ceil(x.shape[0] / batch_size))
    for i in range(num_batches):
        start = i * batch_size
        end = start + batch_size
        yield i, x[start:end], y[start:end]
