import os
import pandas as pd
import numpy as np
import sys

from collect_species import *

## list of files
folder = sys.argv[1]
# folder = 'luca_cross_check_phase3_ene'
FILES = os.listdir(folder)


def collect():
    # folders
    files = [f for f in FILES if not '.' in f]

    for f in files:
        print f
        parse_folder(folder + '/' + f)



def table():
    ''' make table like in Luca's slides '''

    files = [f for f in FILES if '_species' in f]

    dfmas = pd.DataFrame()

    for f in files:
        print '~~~', f

        df = pd.read_csv(folder + '/' + f, sep = ' ')
        df = df.drop('Period', axis=1) # all of these are Phase2

        df['chi2/ndofError'] = np.NaN # NaN?
        df['C11avg'] = (df['C11']*df['ExpSub'] + df['C11_2']*df['ExpTag']) / (df['ExpSub'] + df['ExpTag'])
        df['C11avgError'] = df['C11avg'] * np.sqrt( (df['C11Error'] / df['C11'])**2 + (df['C11_2Error'] / df['C11_2'])**2 )


        ## separate columns and errors
        cols = [c for c in df.columns if not 'Error' in c and not 'Exp' in c]
        errs = [c + 'Error' for c in cols]
        dfcols =  df[cols].transpose()
        dfcols.columns = ['Mean']
        dferrs = df[errs].transpose()
        dferrs.columns = ['Error']
        dferrs.index = cols

        ## concat
        dff = pd.concat([dfcols, dferrs], axis=1)#, ignore_index=True)
        print dff

        ## concat to massive one
        dfmas = pd.concat([dfmas, dff], axis=1)


    ## column order
    COLUMNS = ['nu(Be7)', 'nu(pep)', 'Bi210', 'C11avg', 'Kr85', 'Po210',\
        'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Po210shift', 'C11shift', 'chi2/ndof', 'C11', 'C11_2']
    dfmas = dfmas.loc[COLUMNS]

    print dfmas
    dfmas.to_csv(folder + '.csv')


# collect()
table()
