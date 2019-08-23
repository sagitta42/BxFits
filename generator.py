import sys
from creator import * 

#----------------------------------------------------------

def generator(params):
    '''
    params is a dictionary containing the following keys:

    CNO: fit condition (fixed, lm, hm)
    var: energy variable (nhits, npmts, npmts_dt1, npmts_dt2)
    fit: type of fit (ene, mv)            
    inputs: period to fit (all, YYYY)
    
    outfolder: output folder for log and err files        
    pdfs: folder where PDFs are to be found            
    penalty: species to put penalty on (e.g. Bi210) (optional) --> not implemented yet
    '''

    ## ---------------------------------

    # available values for each parameter
    options = {'CNO': ['fixed','lm', 'hm', 'fixed5'],
               'var': ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2'],
               'fit': ['ene', 'mv'],
               'inputs': ['all'] + [str(y) for y in range(2012,2018)],
               'penalty': ICC.keys() + ['pp/pep', 'none']
    }

    # check each parameter given by user
    for par in options:
        if not params[par] in options[par]:
            print '\nOptions for', par, ':', ', '.join(options[par]) + '\n'
            sys.exit(1)
    
    ## ---------------------------------

    ## init
    s = Submission(params['fit'], params['CNO'], params['var'], params['inputs'], params['pdfs'], params['penalty'])
    
    print # readability
    print '#######################################'
    print
    
    
    # submission file for CNAF
    s.subfile(params['outfolder'])
    
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
    
    if not len(userinput) in range(3,6):
        print
        print 'Examples:'
        print 'python generator.py CNO=fixed fit=mv var=npmts,nhits'
        print 'python generator.py fit=ene inputs=2012,2016 var=nhits CNO=fixed5'
        print 'python generator.py fit=ene var=nhits CNO=fixed5 inputs=2012,2016 pdfs=pdfs_TAUP2017'
        print
        sys.exit(1)

    ## options
    user = ['CNO', 'var', 'fit', 'inputs', 'pdfs','penalty'] # penalty not implemented yet
    opts = {}
    for opt in user:
        opts[opt] = 'none'

    for opt in user:
        for inp in sys.argv:
            if opt in inp:
                opts[opt] = inp.split('=')[1] if opt in ['fit','pdfs'] else inp.split('=')[1].split(',') # penalty can be a list; var is a list to loop on

    ## defaults
    defaults = {'pdfs': 'pdfs_TAUP2017',
                'inputs': ['all']
    }

    for par in defaults:
        if opts[par] == 'none': opts[par] = defaults[par]

    ## folder for given configuration (for submission files and output log file folder)
    outfolder = 'res-fit-' + opts['fit']
    if opts['inputs'] == 'all':
        outfolder += '-PeriodAll-'
    else:
        outfolder += '-' + '_'.join(opts['inputs']) # year by year
    
    outfolder += '-' + opts['pdfs']
        
    if os.path.exists(outfolder):
        print 'Folder', outfolder, 'already exists!!'
        print '#######################################'
        return
    else:
        os.mkdir(outfolder)

    ## input two years means range between those years
    if opts['inputs'][0][0] == '2':
        opts['inputs'] = [str(y) for y in range(int(opts['inputs'][0]), int(opts['inputs'][1]) + 1)]
    
    ## loop over variables and CNO and create a fit for each
    for CNO in opts['CNO']:
        for var in opts['var']:
            for inp in opts['inputs']:
                params = {'outfolder': outfolder, 'fit': opts['fit'], 'CNO': CNO, 'var': var, 'inputs': str(inp), 'pdfs': opts['pdfs'], 'penalty': opts['penalty']}
                generator(params)


if __name__ == '__main__':
    main()
