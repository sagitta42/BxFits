import pandas as pd
import numpy as np
import sys
import os

###### species to read from the fitter

COLUMNS = ['nu(Be7)', 'nu(pep)',\
#          'nu(pp)',\
          'nu(CNO)', 'Bi210', 'C11', 'Kr85', 'Po210',\
     'Ext_Bi214', 'Ext_K40', 'Ext_Tl208',\
#        'Po210shift', 'C11shift',\
        'chi2/ndof','MLV',\
     'C11_2', 'Po210_2']

#COLUMNS = ['C11shift', 'MLV', 'chi2/ndof', 'C11']

#COLUMNS = ['nu(CNO)', 'MLV', 'Po210', 'Po210_2']

### --------------------------------------------------------- ###

###### parameters that don't have the concept of error

ERRORLESS = ['chi2/ndof', 'MLV']

### --------------------------------------------------------- ###

###### special column the value of which is not read from the log file
###### but from the name of the log file

#special_cols = ['Period', 'TFC', 'Var']
special_cols = ['TFC', 'Var'] #, 'Emin', 'Emax', 'RDmin', 'RDmax', 'RDbin']
# special_cols = ['Period', 'TFC', 'Var', 'FV']
#special_cols = ['Period']
#special_cols = []

### --------------------------------------------------------- ###

###### old format of the log file
###### some differences in parsing

# OLD_FORMAT = True
OLD_FORMAT = False

### --------------------------------------------------------- ###
###### fitter format corresponding to our own column names

PARSER = {
 '#nu(^{7}Be)': 'nu(Be7)',
 '#nu(pep)': 'nu(pep)',
 '#nu(pp)': 'nu(pp)',
 '#nu(CNO)': 'nu(CNO)',

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
 'Minimized -2Ln(Likelihood)': 'MLV',
# 'Minimized Likelihood Value': 'MLV',

 '^{11}C 2': 'C11_2',
 '^{210}Po 2': 'Po210_2',

## old format
#  '^{11}C_2': 'C11_2',
#  '^{210}Po_2': 'Po210_2'

}

### --------------------------------------------------------- ###

##### variables and their parser values
# used for systematics
# format to look for min and max energy
fmt_ene = 'is set to' if OLD_FORMAT else '=> float:'

VARPARSER = {
    'Emin': 'minimum_energy ' + fmt_ene, 
    'Emax': 'maximum_energy ' + fmt_ene
}

for x in ['bins','max','min']:
    VARPARSER['RD' + x] = 'multivariate_rdist_fit_' + x
for x in ['max','min']:
    VARPARSER['PS' + x] = 'multivariate_ps_fit' + x

### --------------------------------------------------------- ###


def parse_file(filename):
    '''
    Extract information from a single log file. Return the dataframe (table)
    with the results (not saved as a file)
    '''

    # table template
	# columns: fit settings, species + errors (no error for the ones listed as ERRORLESS)
    df = pd.DataFrame( columns = special_cols + COLUMNS  + [x + 'Error' for x in np.setdiff1d(COLUMNS,ERRORLESS)] + ['ExpSub', 'ExpTag'])

    ## special column that is read from filename, not from the log file
    ## (has to be in the special_cols list anyway)

    # filename example:
    # fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin92_CNO-pileup-penalty-met_hm_C11-shift-c11guess30
    # spec = filename.split('c11guess')[1].split('.')[0]
    # df.at[0, 'C11guess'] = float(spec)

    ### read fit info

    f = open(filename)
    lines = f.readlines()


    # start from top, find fitter input info
    idx = 0
    found = False
    while idx < len(lines) and not found:
        idx += 1
        found = 'Getting data from' in lines[idx] # an. fit

#    finp = lines[idx].split(' ')[-1].split('/')[-1] # e.g. PeriodAll_FVpep_TFCLNGS.root
    finp = lines[idx].split('c19')[0].split('/')[-1]
    specs = {}
#    specs['Period'] = 'X'
#    specs['Period'] = finp.split('_')[0].split('Period')[1] # e.g. PeriodAll
#    specs['FV'] = finp.split('_')[1][2:] # e.g. pep
    specs['TFC'] = finp.split('TFC')[1].split('_')[0] # e.g. LNGS
    specs['Var'] = lines[idx+1].split('final_')[1].split('_pp')[0] # e.g. nhits

    for spec_col in special_cols:
        df.at[0, spec_col] = specs[spec_col]

    # start from the beginning of the file, find exposure
    found = False
    idx = 0
    # format to look for exposure
    fmt_exp = 'Default:' if OLD_FORMAT else 'default.'

    while idx < len(lines) and not found:
        for var in VARPARSER:
            if VARPARSER[var] in lines[idx]:
                df[var] = ene_min_max(lines[idx])


        if 'Inserting [' + fmt_exp + 'Major] exposure' in lines[idx]:
            df['ExpSub'] = float(lines[idx].split(':')[-1].split('[')[1].split(' ')[0])

        # tagged exposure is the last in the file, so if found, exit
        if 'Inserting [' + fmt_exp + 'TFCtagged] exposure' in lines[idx]:
            df['ExpTag'] = float(lines[idx].split(':')[-1].split('[')[1].split(' ')[0])
            found = True

        idx+=1

#    print df

    # start from the end of the file, find the line with FIT PARAMETERS
    idx = len(lines)-1
    found = False
    while idx >= 0 and not found:
        found = 'FIT PARAMETERS' in lines[idx]
        idx -= 1

    if not found:
        print '########## FIT PARAMETERS not found!! ########'
        print filename
        print '#########'
        return pd.DataFrame()

    # now, starting from this index, move down and collect data
    for i in range(idx+2, len(lines)):
        # split the line by equal sign; left is species, right is values
        info = lines[i].split(':')[-1].split('=') if OLD_FORMAT else lines[i].split('=')

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
        if sp in df and sp + '_2' in df:
            df[sp + 'avg'] = (df[sp]*df['ExpSub'] + df[sp + '_2']*df['ExpTag']) / (df['ExpSub'] + df['ExpTag'])
            df[sp + 'avgError'] = df[sp + 'avg'] * ((df[sp + 'Error'] / df[sp])**2 + (df[sp + '_2Error'] / df[sp + '_2'])**2)**0.5 # using np.sqrt doesn't work with NaN

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
        # print f
        # print every file (if small amount)
        if nfiles < 100:
            print f
        else:
            # print every 100
            if (count + 1) % 100 == 0:
		    print count + 1, '/', nfiles

        df = pd.concat([df, parse_file(foldername + '/' + f)], ignore_index=True)
        count += 1

    # sort by special column (often year)
    # df = df.sort_values('nu(CNO)')
    if not len(special_cols) == 0: df = df.sort_values(special_cols)
    print df.head(10)

    # save output file
    outname = foldername + '_species.out'
    df.to_csv(outname, index=False, sep = ' ')
    print('--> '+outname)




def ene_min_max(line):
    '''
    helper function to extract min and max energy from log line
    '''
    return int(line.split(' ')[-1] if OLD_FORMAT else line.split('[')[1].split(']')[0])



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
