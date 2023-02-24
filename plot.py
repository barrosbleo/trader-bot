import sys
import matplotlib
#matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt



data = pd.read_csv('RSI.csv')

data.plot()

plt.show()

plt.savefig(sys.stdout.buffer)
sys.stdout.flush()