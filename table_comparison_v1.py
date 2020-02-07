import os
import pandas as pd
import numpy as np
import sys

from collect_species import *


def table_comp_v1(folder):
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

        ## parameters that don't have errors 
        noerr_cols = ERRORLESS + special_cols + ['Emin','Emax', 'ExpSub', 'ExpTag']
        
        # replace mean with mean + error (string)
        columns = [c for c in df.columns if not 'Error' in c]
        for col in columns:
            print '~~~', col
            if not col in noerr_cols:
                df[col] = df[col].round(2)
                df[col + 'Error'] = df[col + 'Error'].round(2)
                df[col] = df[col].map(str) + '+-' + df[col + 'Error'].map(str)
                # remove Error columns
                df = df.drop(col + 'Error', axis=1)

        # transpose
        df = df.transpose()
        df.columns = [f.split('.')[0]]
        print df

        ## concat to massive one
        dfmas = pd.concat([dfmas, df], axis=1)

    outname = folder + '_comparison_v1.csv'
    dfmas.to_csv(outname, sep = ' ')
    print
    print '----------------'
    print '->', outname


if __name__ == '__main__':
    table_comp_v1(sys.argv[1])
