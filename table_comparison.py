import os
import pandas as pd
import numpy as np
import sys

from collect_species import *


def table_comp(folder):
    '''
    A table comparing different settings
    Each log file in the folder is a different setting
    '''

    ## log files in the folder
    files = os.listdir(folder)
    files = [f for f in files if '.log' in f]

    # empty table
    dfmas = pd.DataFrame()

    for f in files:
        print
        print '~~~', f

        # collect fit results from this log file
        df = parse_file(folder + '/' + f)

        ## assign fake error columns for things that don't have errors
        noerr_cols = ERRORLESS + special_cols + ['Emin','Emax']
        for noerr in noerr_cols:
            df[noerr + 'Error'] = np.NaN

        ## calculate weighted average for C11 and Po210 (complementary)
        for sp in ['C11', 'Po210']:
            if not sp in df.columns: continue

            df[sp + 'avg'] = (df[sp]*df['ExpSub'] + df[sp + '_2']*df['ExpTag']) / (df['ExpSub'] + df['ExpTag'])
            df[sp + 'avgError'] = df[sp + 'avg'] * np.sqrt( (df[sp + 'Error'] / df[sp])**2 + (df[sp + '_2Error'] / df[sp + '_2'])**2 )


        ## separate columns and errors
        cols = [c for c in df.columns if not 'Error' in c and not 'Exp' in c]
        errs = [c + 'Error' for c in cols]
        dfcols =  df[cols].transpose()
        dfcols.columns = ['Mean']
        dferrs = df[errs].transpose()
        dferrs.columns = ['Error']
        dferrs.index = cols

        ## put mean and error side by side
        dff = pd.concat([dfcols, dferrs], axis=1)#, ignore_index=True)

        ## add multindex column
        dff.columns = pd.MultiIndex.from_product([[f.split('.')[0]], dff.columns])
        print
        print dff

        ## concat to massive one
        dfmas = pd.concat([dfmas, dff], axis=1)


    outname = folder + '_comparison.csv'
    dfmas.to_csv(outname, sep = ' ')
    print
    print '----------------'
    print '->', outname


if __name__ == '__main__':
    table_comp(sys.argv[1])
