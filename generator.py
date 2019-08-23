import sys
from creator import * 

#----------------------------------------------------------
    
# available values for each parameter
options = {
    'CNO': ['fixed','lm', 'hm', 'fixed5'],
    'var': ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2'],
    'fit': ['ene', 'mv'],
    'inputs': ['all'] + [str(y) for y in range(2012,2018)],
    'penalty': ICC.keys() + ['pp/pep', 'none'], # penalty not implemented yet
    'fittype': ['cpu', 'gpu']
     
}
    
## defaults
defaults = {
    'pdfs': 'pdfs_TAUP2017',
    'inputs': ['all'], # has to be a list
    'var': 'nhits',
    'fittype': 'cpu'
}
    
## options for user
user = options.keys() + ['pdfs'] # pdfs is a path to a folder, has no fixed options

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
    fittype: cpu or gpu
    '''

    ## ---------------------------------


    # check each parameter given by user
    for par in options:
        if not params[par] in options[par]:
            print '\nOptions for', par, ':', ', '.join(options[par]) + '\n'
            sys.exit(1)
    
    ## ---------------------------------

    ## init
    s = Submission(params['fit'], params['CNO'], params['var'], params['inputs'], params['pdfs'], params['fittype'], params['penalty'])
    
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
   
    ## if simpy python generator.py is called, show all options
    if len(userinput) == 0:
        wrong_inputs()

    # first assign none
    opts = {}
    for opt in user:
        opts[opt] = 'none'

    # then read what user gave
    for opt in user:
        for inp in sys.argv:
            if opt in inp:
                opts[opt] = inp.split('=')[1] if opt in ['fit', 'pdfs', 'fittype'] else inp.split('=')[1].split(',') # penalty can be a list; var is a list to loop on


    # assign defaults if nothing given
    for par in defaults:
        if opts[par] == 'none': opts[par] = defaults[par]

    ## folder for given configuration (for submission files and output log file folder)
    outfolder = 'res-fit-' + opts['fit']
    if opts['inputs'] == 'all':
        outfolder += '-PeriodAll-'
    else:
        outfolder += '-' + '_'.join(opts['inputs']) # year by year
    
    outfolder += '-' + opts['pdfs']

    # note: fittype (cpu or gpu) is not in the name because one can't do both in one folder :) so no threat of overlapping results folder
        
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
                params = {'outfolder': outfolder, 'fit': opts['fit'], 'CNO': CNO, 'var': var, 'inputs': str(inp), 'pdfs': opts['pdfs'], 'penalty': opts['penalty'], 'fittype': opts['fittype']} # something smarter can be done here
                generator(params)


def wrong_inputs():
    '''A message to print if user input is wrong '''
    print
    print 'Parameters:'
    print ', '.join(user)
    print
    print 'Options:'
    for op in options:
        print '\t', op, ':', ', '.join(options[op])
    print 'For inputs, it\'s either "all" or "yyyy,YYYY" (range of years between yyyy and YYYY inclusive)'
    print 'Note: if fit=ene is used and inputs are years, pep is fixed to 2.8 (Simone yearly fits). Remove from code if not needed now'
    print
    print 'Defaults:'
    for df in defaults:
        print '\t', df, ':', defaults[df]
    print
    print 'Examples:'
    print 'python generator.py CNO=fixed fit=mv var=npmts,nhits'
    print 'python generator.py fit=ene inputs=2012,2016 var=nhits CNO=fixed5'
    print 'python generator.py fit=ene var=nhits CNO=fixed5 inputs=2012,2016 pdfs=pdfs_TAUP2017'
    print
    sys.exit(1)


if __name__ == '__main__':
    main()
