import sys
import pandas as pd

def table(tname):
    ''' format the look like in Simone's table, value pm error '''

    # values from fits collected using collect_species.py
    df = pd.read_csv(tname, sep = ' ')
    df = df.set_index('Year')
    # species
    species = [c for c in df.columns if not 'Error' in c]
    # new string column for each species
    for sp in species:
        print '...', sp
        df[sp] = df[sp].map(str) + '+-' + df[sp + 'Error'].map(str)

    # transpose to have Simone look
    df = df[species].transpose(copy=True)
    # save
    df.to_csv(tname.split('.')[0] + '_table.csv')
    print 'DONE'


table(sys.argv[1])
