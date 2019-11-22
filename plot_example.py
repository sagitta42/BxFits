import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('examples/fits2012-2019_species.out', sep = ' ')
df.plot(x = 'Period', y = 'Bi210', yerr = 'Bi210Error')
plt.savefig('examples/bi210rate.png')
