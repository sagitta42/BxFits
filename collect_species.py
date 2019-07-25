import pandas as pd
import numpy as np
import sys
import os

### --------------------------------------- ###
### ---------------- setup ---------------- ###
### --------------------------------------- ###

# species and neutrinos

COLUMNS = ['Bi210', 'C11', 'C14', 'C14_pileup', 'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Kr85', 'Pb214', 'Po210', 'nu(Be7)', 'nu(pp)', 'Minimized Likelihood Value']

def strname(species):
    return ''.join(species.split(' '))

#PARSER = {
#'Bi210': 'Bi210',
#'C11': 'C11',
#'14C': 'C14',
#
#'#nu(pp)': 'nu(pp)',
#'#nu(^{7}Be)': 'nu(Be7)',
#'#nu(pep)': 'nu(pep)',
#'#nu(CNO)': 'nu(CNO)',
#'#nu(^{8}B)': 'nu(B8)',
#
#'^{210}Po': 'Po210',
#'^{210}Po_2': 'Po210_2',
#'^{85}Kr': 'Kr85',
#'^{11}C_2': 'C11_2',
#'^{10}C_2': 'C10_2',
#'^{6}He_2': 'He6_2',
#
#'Ext ^{208}Tl': 'Tl208',
#'Ext ^{214}Bi': 'Bi214',
#'Ext ^{40}K': 'K40',
#
#'Minimized Likelihood Value': 'MLV',
#'chi^2/N-DOF': 'chiSquare/Ndof',

#'Likelihood p-value': 'LikelihoodP-value'
#'beta_ly': 'betaLY',
#'fCher': 'fCher',
#'pt': 'pt',
#'gc': 'gc',
#'^{11}C_qch': 'C11qch',
#'^{210}Po_qch': 'Po210qch',
#'C14_pileup': 'C14_pileup',
#'chi^2': 'chiSquare',
#'p-value': 'p-value',
#}

# parameters that don't have the concept of error
ERRORLESS = ['Minimized Likelihood Value']
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


def parse_file(filename):
    ### set up table

    # table template
	# columns: fit settings, species + errors (no error for the ones listed as ERRORLESS)
    df = pd.DataFrame( columns = ['Year'] + cols  + [strname(x) + 'Error' for x in np.setdiff1d(COLUMNS,ERRORLESS)] )
    # example: fit_2012.log 
    year = filename.split('/')[-1][4:8]
    df.at[0, 'Year'] = int(year)

    ### read fit info

    f = open(filename)
    lines = f.readlines()

    # start from the end of the file, find the line with FIT PARAMETERS
    idx = len(lines)
    found = False
    while idx >= 0 and not found:
        idx -= 1
        found = 'SPECTRAL FIT' in lines[idx]

    # now, starting from this index, move down and collect data
    for i in range(idx+1, len(lines)):
        info = lines[i].split(':')[-1].split('=')
        # print info
        species = info[0].split('Component')[-1].strip()
        # stuff that we don't need e.g. number of bins used --> ignore and move to the next line
        if not species in COLUMNS: continue
        val = info[1].strip().split(' ')[0].strip()
        df[strname(species)] = val
		
        if not species in ERRORLESS:
            if 'Fixed' in lines[i] or 'Possibly railed' in lines[i] or 'Railed' in lines[i]:
                err = 0
            else:
                err = info[1].split('+/-')[1].strip().split(' ')[0].strip() # if '+/-' in lines[i] else 0
            
            df[species + 'Error'] = err

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
    outname = foldername.split('/')[-1] + '_species.out'
    df = df.sort_values('Year')
    df.to_csv(outname, index=False, sep = ' ')
    print('--> '+outname)



if __name__ == '__main__':
    fname = sys.argv[1]
    if fname[-1] == '/': fname = fname[:-1]
    parse_folder(fname)
