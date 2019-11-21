import pandas as pd
import numpy as np
import sys
import os

### --------------------------------------- ###
### ---------------- setup ---------------- ###
### --------------------------------------- ###

# species and neutrinos

# COLUMNS = ['C14']
COLUMNS = ['nu(Be7)', 'nu(pep)', 'Bi210', 'C11', 'Kr85', 'Po210',\
    'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Po210shift', 'C11shift', 'chi2/ndof',\
    'C11_2', 'Po210_2']
# COLUMNS = ['C14', 'chi2/ndof', 'LY', 'pp']
# COLUMNS = ['Bi210', 'C11', 'C14', 'C14_pileup', 'Ext_Bi214', Ext_K40', 'Ext_Tl208', 'Kr85', 'Pb214', 'Po210', 'nu(Be7)', 'nu(pp)', 'nu(CNO)', 'Minimized Likelihood Value']

def strname(species):
    return ''.join(species.split(' '))

PARSER = {
 '#nu(^{7}Be)': 'nu(Be7)',
 '#nu(pep)': 'nu(pep)',

 '^{210}Bi': 'Bi210',
 '^{11}C': 'C11',
 '^{85}Kr': 'Kr85',
 '^{210}Po': 'Po210',

 'Ext ^{214}Bi': 'Ext_Bi214',
 'Ext ^{40}K': 'Ext_K40',
 'Ext ^{208}Tl': 'Ext_Tl208',

 '^{11}MCshiftC': 'C11shift',
 '^{210}MCshiftPo': 'Po210shift',

 'chi^2/N-DOF': 'chi2/ndof',

 '^{11}C 2': 'C11_2',
 '^{210}Po 2': 'Po210_2'

 # '^{14}C': 'C14',
 # 'beta ly': 'LY',
 # '#nu(pp)': 'pp',


}

# parameters that don't have the concept of error
ERRORLESS = ['chi2/ndof']
# ERRORLESS = ['Minimized Likelihood Value']
#ERRORLESS = ['chiSquare', 'chiSquare/Ndof', 'p-value', 'MLV', 'LikelihoodP-value']

# alpha and beta resolution
#for i in range(6):
 #   PARSER['beta_resolution_' + str(i)] = 'betaRes' + str(i)
  #  PARSER['alpha_resolution_' + str(i)] = 'alphaRes' + str(i)

# echidna qc
#for i in range(5):
#    PARSER['echidna_^{' + str(i) + '}qc'] = 'echidnaQc' + str(i)



### ----------------------------------------- ###
### ---------------- parsing ---------------- ###
### ----------------------------------------- ###

special_col = 'Period'
# special_col = 'Year'

def parse_file(filename):
    ### set up table

    # table template
#    special_col = 'EneVar'
	# columns: fit settings, species + errors (no error for the ones listed as ERRORLESS)
    df = pd.DataFrame( columns = [special_col] + [strname(x) for x in COLUMNS]  + [strname(x) + 'Error' for x in np.setdiff1d(COLUMNS,ERRORLESS)] + ['ExpSub', 'ExpTag'])

    # oemer full comp names: nusol_cmpl_only_12_c19_log.log
#    spec = '20' + filename.split('_c19')[0].split('_')[-1]
    # oemer filenames: cl2_12_eo_mc_taup_40_80_c19_log.log
    # oemer MC with LY free/fixed: cl2_12_eo_mc_40_90_c19_log
    # spec = '20' + filename.split('/')[-1].split('_')[1]
    # Luca cross check file: fit-mvPeriodPhase2-CNOhm-nhits.log
    # spec = filename.split('Period')[1].split('-')[0]
    # Luca c11 guess: data_Phase3_EO_22C11_TAUP_MI_Nov.log
    spec = filename.split('_')[1]


    df.at[0, special_col] = spec

    ### read fit info

    f = open(filename)
    lines = f.readlines()

    # start from the beginning of the file, find exposure
    found = False
    idx = 0
    while idx < len(lines) and not found:

        if 'Inserting [default.Major] exposure' in lines[idx]:
            df['ExpSub'] = lines[idx].split(':')[1].split('[')[1].split(' ')[0]

        # tagged is after sub, so if found, exit
        if 'Inserting [default.TFCtagged] exposure' in lines[idx]:
            df['ExpTag'] = lines[idx].split(':')[1].split('[')[1].split(' ')[0]
            found = True

        idx+=1

    # start from the end of the file, find the line with FIT PARAMETERS
    idx = len(lines)
    found = False
    while idx >= 0 and not found:
        idx -= 1
        found = 'FIT PARAMETERS' in lines[idx]
        # found = 'SPECTRAL FIT' in lines[idx]

    # print idx, 'line'
    # now, starting from this index, move down and collect data
    for i in range(idx+1, len(lines)):
        info = lines[i].split('=')
        # info = lines[i].split(':')[-1].split('=')
        # print info
        species = info[0].strip()
        # species = info[0].split('Component')[-1].strip()
        # print species
        # stuff that we don't need e.g. number of bins used --> ignore and move to the next line
        if not species in PARSER: continue
        if not PARSER[species] in COLUMNS: continue
        # if not species in COLUMNS: continue
        val = info[1].strip().split(' ')[0].strip()
        df[PARSER[species]] = val
        # df[strname(species)] = val

        if not PARSER[species] in ERRORLESS:
            if 'Fixed' in lines[i]:
                err = -1
            elif 'Possibly railed' in lines[i] or 'Railed' in lines[i]:
                err = -2
            else:
                err = info[1].split('#pm')[1].strip().split(' ')[0].strip() # if '+/-' in lines[i] else 0
                # err = info[1].split('+/-')[1].strip().split(' ')[0].strip() # if '+/-' in lines[i] else 0

            df[PARSER[species] + 'Error'] = err

    # remove error for parameters that are not supposed to have it
#	cols = df.columns
#	for col in cols:
#		if col in ERRORLESS:
#			df = df.drop(col + 'Error', axis=1)

    return df
    # outname = filename.split('.')[0] + '.out'
    # df.to_csv(outname, sep = ' ', index=False)


def parse_folder(foldername):
    # list of files in this folder
    files = os.listdir(foldername)
    files = [f for f in files if 'log' in f]
    # empty table
    df = pd.DataFrame()
    # add info from each log file in the folder
    nfiles = len(files)
    count = 0
    for f in files:
        # print every 100
        if (count + 1) % 100 == 0:
		    print count + 1, '/', nfiles

        df = pd.concat([df, parse_file(foldername + '/' + f)], ignore_index=True)
        count += 1

    # output file
    outname = foldername + '_species.out'
    # outname = foldername.split('/')[-1] + '_species.out'
    df = df.sort_values(special_col)
    df.to_csv(outname, index=False, sep = ' ')
    print df
    print('--> '+outname)



if __name__ == '__main__':
    fname = sys.argv[1]
    if fname[-1] == '/': fname = fname[:-1]
    parse_folder(fname)
