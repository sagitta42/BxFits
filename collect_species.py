import pandas as pd
import numpy as np
import sys
import os

###### species to read from the fitter

COLUMNS = ['nu(Be7)', 'nu(pep)', 'nu(pp)', 'Bi210', 'C11', 'Kr85', 'Po210',\
    'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Po210shift', 'C11shift', 'chi2/ndof',\
    'C11_2', 'Po210_2']

### --------------------------------------------------------- ###

###### parameters that don't have the concept of error

ERRORLESS = ['chi2/ndof']

### --------------------------------------------------------- ###

###### special column the value of which is not read from the log file
###### but from the name of the log file

special_col = 'C11guess'
# special_col = 'Period'

### --------------------------------------------------------- ###

###### fitter format corresponding to our own column names

PARSER = {
 '#nu(^{7}Be)': 'nu(Be7)',
 '#nu(pep)': 'nu(pep)',
 '#nu(pp)': 'nu(pp)',

  '^{14}C': 'C14',

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
}

### --------------------------------------------------------- ###


def parse_file(filename):
    '''
    Extract information from a single log file. Return the dataframe (table)
    with the results (not saved as a file)
    '''

    # table template
	# columns: fit settings, species + errors (no error for the ones listed as ERRORLESS)
    df = pd.DataFrame( columns = [special_col] + COLUMNS  + [x + 'Error' for x in np.setdiff1d(COLUMNS,ERRORLESS)] + ['ExpSub', 'ExpTag'])

    # Example of a filename: data_Phase3_EO_22C11_TAUP_MI_Nov.log
    # -> special column will be 'Phase3'
    # spec = filename.split('_')[1]
    # fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MZ-nhits-emin92_CNO-pileup-penalty-met_hm
    # spec = filename.split('Period')[1].split('M')[0]
    # fit-mvPeriod2012-CNOhm-nhits.log
    # spec = filename.split('Period')[1].split('-')[0]

    # fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin92_CNO-pileup-penalty-met_hm_C11-shift-c11guess30
    spec = filename.split('c11guess')[1].split('.')[0]

    df.at[0, special_col] = float(spec)

    ### read fit info

    f = open(filename)
    lines = f.readlines()

    # start from the beginning of the file, find exposure
    found = False
    idx = 0
    while idx < len(lines) and not found:

        if 'Inserting [default.Major] exposure' in lines[idx]:
            df['ExpSub'] = float(lines[idx].split(':')[1].split('[')[1].split(' ')[0])

        # tagged is after sub, so if found, exit
        if 'Inserting [default.TFCtagged] exposure' in lines[idx]:
            df['ExpTag'] = float(lines[idx].split(':')[1].split('[')[1].split(' ')[0])
            found = True

        idx+=1

    # start from the end of the file, find the line with FIT PARAMETERS
    idx = len(lines)
    found = False
    while idx >= 0 and not found:
        idx -= 1
        found = 'FIT PARAMETERS' in lines[idx]

    if not found:
        print '########## FIT PARAMETERS not found!! ########'
        return pd.DataFrame()

    # now, starting from this index, move down and collect data
    for i in range(idx+1, len(lines)):
        # split the line by equal sign; left is species, right is values
        info = lines[i].split('=')
        # name of the species in the fitter
        species = info[0].strip()

        # species that are not defined for us
        if not species in PARSER: continue

        # species that we don't need and other stuff -> ignore and move to the next line
        if not PARSER[species] in COLUMNS: continue

        # mean value of the fit
        val = info[1].strip().split(' ')[0].strip()
        df[PARSER[species]] = float(val)

        ## assign error if it exists for given column
        if not PARSER[species] in ERRORLESS:
            # assign special values for fixed and railed
            if 'Fixed' in lines[i]:
                err = -1
            elif 'Possibly railed' in lines[i] or 'Railed' in lines[i]:
                err = -2
            else:
                # read the error for this species
                err = info[1].split('#pm')[1].strip().split(' ')[0].strip() # if '+/-' in lines[i] else 0

            df[PARSER[species] + 'Error'] = float(err)

    ## calculate weighted average for C11 and Po210 (complementary)
    for sp in ['C11', 'Po210']:
        df[sp + 'avg'] = (df[sp]*df['ExpSub'] + df[sp + '_2']*df['ExpTag']) / (df['ExpSub'] + df['ExpTag'])
        df[sp + 'avgError'] = df[sp + 'avg'] * np.sqrt( (df[sp + 'Error'] / df[sp])**2 + (df[sp + '_2Error'] / df[sp + '_2'])**2 )

    return df




def parse_folder(foldername):
    '''
    Get information from every log file in a given folder and save to a
    table called foldername_species.out
    '''
    # list of files in this folder
    files = os.listdir(foldername)
    files = [f for f in files if 'log' in f]

    # empty table
    df = pd.DataFrame()

    # add info from each log file in the folder
    nfiles = len(files)
    count = 0
    for f in files:
        print f
        # print every 100
        if (count + 1) % 100 == 0:
		    print count + 1, '/', nfiles

        df = pd.concat([df, parse_file(foldername + '/' + f)], ignore_index=True)
        count += 1

    # sort by special column (often year)
    df = df.sort_values(special_col)
    print df

    # save output file
    outname = foldername + '_species.out'
    df.to_csv(outname, index=False, sep = ' ')
    print('--> '+outname)



if __name__ == '__main__':
    # check if the species are all defined
    for col in COLUMNS:
        if not col in PARSER.values():
            print 'Species', col, 'is not in PARSER (line 19)!'
            sys.exit(1)

    # user input
    fname = sys.argv[1]
    if fname[-1] == '/': fname = fname[:-1]
    parse_folder(fname)
