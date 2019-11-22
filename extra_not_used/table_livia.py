import os
import pandas as pd
import numpy as np
import sys

from collect_species import *

fxd = '-Ext_K40-fixed' if 'fixed' in sys.argv[1] else ''

ORDER = [
'fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MZ-nhits-emin92_CNO-pileup-penalty' + fxd + 'met_hm',
'fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin92_CNO-pileup-penalty' + fxd + 'met_hm',
'fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-pileup-penalty' + fxd + 'met_hm',
'fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-penalty' + fxd + 'met_hm',
'fit-cno-mv-pdfs_new-PeriodPhase2MI-nhits-emin140_CNO-penalty' + fxd + 'met_hm',
'fit-cno-mv-pdfs_new-PeriodPhase3MI-nhits-emin140_CNO-penalty' + fxd + 'met_hm',
]

def table_livia(folder):
    ''' make table like in Luca's slides '''

    ## log files in the folder
    # files = os.listdir(folder)
    # files = [f for f in files if '.log' in f]

    dfmas = pd.DataFrame()

    for f in ORDER:
    # for f in files:
    # for ord in range(4):
        # f = dorder[ord]
        print '~~~', f

        df = parse_file(folder + '/' + f + '.log')
        df = df.drop('Period', axis=1) # all of these are Phase2
        df = df.astype(float)

        df['chi2/ndofError'] = np.NaN # NaN?
        for sp in ['C11', 'Po210']:
            # print df[[sp, sp+'Error', sp + '_2', sp + '_2Error', 'ExpTag', 'ExpSub']]
            # print '$', df[sp].loc[0], '$', df['ExpSub'].loc[0], '$'
            # print df[sp]*df['ExpSub']
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

        ## concat
        dff = pd.concat([dfcols, dferrs], axis=1)#, ignore_index=True)
        # print dff

        ## concat to massive one
        dfmas = pd.concat([dfmas, dff], axis=1)


    ## column order
    COLUMNS = ['nu(Be7)', 'nu(pep)', 'Bi210', 'C11avg', 'Kr85', 'Po210avg',\
        'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Po210shift', 'C11shift', 'chi2/ndof',\
        'C11', 'C11_2', 'Po210', 'Po210_2']
    dfmas = dfmas.loc[COLUMNS]

    print dfmas
    dfmas.to_csv(folder + '_livia.csv')


table_livia(sys.argv[1])

#
# def order(name):
#     if 'C11_Po210' in name or 'Po210_C11' in name: return 3
#     if 'C11' in name: return 2
#     if 'Po210' in name: return 1
#     return 0

folders = [
# 'luca_cross_check_phase2_ene',
# 'luca_cross_check_phase2_mv',
# 'luca_cross_check_phase3_ene'
# 'c11_guess'
# 'c11-22',
# 'c11-28'
]
# collect()
# for f in folders:
#     print '~~~~~~~~~~~', f
#     collect(f)
#     table(f)
