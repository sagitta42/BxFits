from math import ceil

#----------------------------------------------------------

## ENTER YOUR CHOICES HERE

# total number of fits
NFITS_min = 0 # including
NFITS_max = 1100 # not including
# number of fits per one submission file
NBATCH = 100
# path to the input root files
INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/final_senp3_full' # full exposure
#INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/final_senp3_half' # half exposure
#INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/senst'

#----------------------------------------------------------

import sys
from creator import * 

#----------------------------------------------------------

def generator(outfolder, fit, CNO, var, penalty):
    '''
    0) outfolder: output folder for log and err files        
    1) fit: type of fit (ene, mv)            
    2) CNO: fit condition (fixed, lm, hm)
    3) var: energy variable (nhits, npmts, npmts_dt1, npmts_dt2)
    4) penalty: species to put penalty on (e.g. Bi210) (optional)
    '''

    ## ---------------------------------
    ## technical checks

    CNOoptions = ['fixed','lm', 'hm']
    if not CNO in CNOoptions:
        print '\nOptions for CNO:', ', '.join(CNOoptions) + '\n'
        return

    varoptions = ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2']        
    if not var in varoptions:
        print '\nOptions for energy variable:', ', '.join(varoptions) + '\n'
        return
    
    fitoptions = ['ene', 'mv']        
    if not var in varoptions:
        print '\nOptions for energy variable:', ', '.join(fitoptions) + '\n'
        return
    
    for pen in penalty:
        if not ((pen in ICC) or (pen == 'pp/pep') or penalty == 'none'):
            print '\nOptions for penalty:', ','.join(ICC.keys())
            return


    ## ---------------------------------

    ## init
    s = Submission(fit, CNO, var, penalty)
    
    print # readability
    print '#######################################'
    print
    
    
    # submission file for CNAF
    s.subfile(outfolder)
    
    print # readability
    
    ## corresponding cfg file
    fitfold = 'fitoptions'
    if not os.path.exists(fitfold):
        os.mkdir(fitfold)
    
    s.cfgfile() # create cfg file if needed

    ## corresponding species list
    specfold = 'species_list'
    if not os.path.exists(specfold):
        os.mkdir(specfold)

    s.iccfile() # create species list if needed

    print #readability
    print '#######################################'
    print


def main():
    userinput = sys.argv[1:]
    
    if not len(userinput) in [3,4]:
        print
        print 'Examples:'
        print 'python generator.py CNO=fixed fit=mv var=npmts,nhits'
        print
        sys.exit(1)

    ## options
    user = ['CNO', 'var', 'fit', 'penalty']
    opts = {}
    for opt in user:
        opts[opt] = 'none'

    for opt in user:
        for inp in sys.argv:
            if opt in inp:
                opts[opt] = inp.split('=')[1] if opt == 'fit' else inp.split('=')[1].split(',') # penalty can be a list; var is a list to loop on


    ## folder for given configuration (for submission files and output log file folder)
    outfolder = 'res_fit_' + opts['fit']

    if os.path.exists(outfolder):
        print 'Folder', outfolder, 'already exists!!'
        print '#######################################'
        return
    else:
        os.mkdir(outfolder)
    
    ## loop over variables and CNO and create a fit for each
    for CNO in opts['CNO']:
        for var in opts['var']:
            params = [outfolder, opts['fit'], CNO, var, opts['penalty']]
            print params
            generator(*params)


if __name__ == '__main__':
    main()
