import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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

def conf_matrix_plot(cm, labels):
    df_cm = pd.DataFrame(cm, index=labels, columns=labels)
    plt.figure(figsize = (10,7))
    sn.heatmap(df_cm, annot=True, cmap="plasma", fmt="g")
    plt.show()