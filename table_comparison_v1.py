import os
import pandas as pd
import numpy as np
import sys

from collect_species import *

# define columns we want (override what is in collect_species)
#collect_species.COLUMNS = ['nu(Be7)', 'nu(pep)',\
##          'nu(pp)',\
#          'nu(CNO)', 'Bi210', 'C11', 'Kr85', 'Po210',\
#     'Ext_Bi214', 'Ext_K40', 'Ext_Tl208',\
##        'Po210shift', 'C11shift',\
#        'chi2/ndof','MLV',\
#     'C11_2', 'Po210_2']


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
        noerr_cols = ERRORLESS + special_cols + ['Emin','Emax', 'RDmin', 'RDmax', 'RDbins', 'PSmin', 'PSmax', 'C11shift', 'Po210shift', 'ExpSub', 'ExpTag']
        
        # replace mean with mean + error (string)
        columns = [c for c in df.columns if not 'Error' in c]
        for col in columns:
            print '~~~', col
#            print df[col]
            if not col in noerr_cols:
                df[col] = df[col].round(2)
                df[col + 'Error'] = df[col + 'Error'].round(2)
                df[col] = df[col].map(str) + '+-' + df[col + 'Error'].map(str)
                # remove Error columns
                df = df.drop(col + 'Error', axis=1)

        # transpose
        df = df.transpose()
        df.columns = [os.path.splitext(f)[0]]
#        df.columns = [f.split('.')[0]]
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
