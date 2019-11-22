import sys
from creator import * 

#----------------------------------------------------------
    
# available values for each parameter
options = {
    'ftype': ['cpu', 'gpu', 'cno'],
    'fit': ['ene', 'mv'],
    'inputs': ['Phase2', 'Phase3'] + [str(y) for y in range(2012,2020)],
    'tfc': ['MI', 'MZ'],
    'var': ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2'],

    'penalty': ICCpenalty.keys() + ['pileup', 'none'],
    'fixed': ICCfixed.keys() + ['none'],
    'met': ['hm', 'lm', 'none'], # metallicity for the pep constraint
    'shift': ['C11', 'Po210', 'none'],    

    'save': ['true', 'false'],
}
    
## defaults
defaults = {
    'tfc': 'MI',
    'var': ['nhits'],
    'pdfs': 'pdfs_TAUP2017',
    'emin': '92',
    'save': 'false',
}
    
## total options = options + the ones that do not have fixed choices
user = options.keys() + ['pdfs', 'emin', 'outfolder'] 

#----------------------------------------------------------

def generator(params):
    '''
        ftype ['cpu'|'gpu'|'cno']: CPU or GPU fitter.
            Setting 'cno' means GPU fitter with "CNO configuration"
            (no C14 and pp in the species). To remove pileup, simply do not put
            'penalty=pileup'

        fit ['ene'|'mv']: energy only or multivariate fit

        inputs (string): name of the period (e.g. Phase2) or a year (e.g. '2012')
            The inputs will be read from a folder 'input_files' (create a link in your folder)
            Giving "yyyy,YYYY" will create submissions for the range of years between yyyy and YYYY inclusive

        tfc ['MZ'|'MI']: type of TFC                         

        pdfs (string): path to MC PDFs

        var ['nhits' | 'npmts_dt1' | 'npmts_dt2']: fit variable

        emin (int): min energy of the fit
        
        penalty (list): list of species to be constrained in the fit
            Constraints are defined in the bottom in ICCpenalty
            IMPORTANT! with the current implementation, if pileup is not given
                        in this option, it means the fit is performed without
                        pileup as species at all

        fixed (list): list of species to be fixed in the fit
            Values are defined in the bottom in ICCfixed

        met ['hm'|'lm']: metallicity
            Used with option penalty or fixed for species the value for which
            depends on metallicity                      

        shift (list): list of species to apply shift to (C11, Po210)
        
        save [True|False]: save the fit output in .root and .pdf                      

        outfolder (string): output folder for the log files
            If not given, an output folder is created with a name based on the settings                                

    '''

    ## ---------------------------------


    # check each parameter given by user
    for par in options:
        # penalty is a list
        if par in ['penalty', 'shift', 'fixed']:
            flag = True # by default, we think it's an available option
            for parsp in params[par]:
                if not parsp in options[par]: flag = False # set to False if not available
        else:
            flag = params[par] in options[par]

        if not flag:
            print '\nOptions for', par, ':', ', '.join(options[par]) + '\n'
            sys.exit(1)
    
    ## ---------------------------------

    ## init
    s = Submission(params)
    
    print # readability
    print '#######################################'
    print
    
    
    # submission file for CNAF
    s.subfile()
    
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
        if opt in ['penalty', 'shift', 'fixed']:
            # for options that can be a list, penalty and shift
            opts[opt] = ['none']
        else:
            opts[opt] = 'none'

    # then read what user gave
    for opt in user:
        for inp in sys.argv:
            if opt in inp:
                opts[opt] = inp.split('=')[1] if opt in ['fit', 'pdfs', 'ftype', 'emin', 'save', 'met', 'tfc', 'outfolder'] else inp.split('=')[1].split(',') # penalty, fixed and shift can be a list; var is a list to loop on


    # assign defaults if nothing given
    for par in defaults:
        if opts[par] == 'none': opts[par] = defaults[par]

    ## folder for given configuration (for submission files and output log file folder)
    if opts['outfolder'] == 'none':
        outfolder = 'res-fit-' + opts['ftype'] + '-' +  opts['fit']
        outfolder += '-' + '_'.join(opts['inputs'])
    
        outfolder += '-' + opts['pdfs']
        outfolder += '-emin' + opts['emin']

        ## list like options
        for spop in ['shift','penalty','fixed']:
            if opts[spop] != ['none']:
                outfolder += '-' + spop + '_'.join(opts[spop])
        
        opts['outfolder'] = outfolder

        if os.path.exists(outfolder):
            print 'Folder', outfolder, 'already exists!!'
            print '#######################################'
            return
       
    if not os.path.exists(opts['outfolder']): os.mkdir(opts['outfolder'])

    ## input two years means range between those years
    if (len(opts['inputs'])) >= 2 and (opts['inputs'][0][0] == '2'):
        opts['inputs'] = [str(y) for y in range(int(opts['inputs'][0]), int(opts['inputs'][1]) + 1)]

    print
    print '~~ Your input:'
    print
    print opts

    # the parameters are the same as the user gave, but some have to be looped on, and not be lists in the input e.g. fit variable
    params = opts.copy()        

    ## loop over variables that have to be looped on 
    for var in opts['var']:
        for inp in opts['inputs']:
            params['var'] = var
            params['inputs'] = inp
            print
            print '~~~ This submission:'
            print
            print params
            print
            generator(params)


def wrong_inputs():
    '''A message to print if user input is wrong '''
    print
    print 'Examples:'
    print 'python generator.py inputs=Phase2 ftype=cno fit=mv var=nhits emin=140 pdfs=pdfs_new shift=C11 penalty=pileup,CNO'
    print 'python generator.py penalty=CNO,pileup inputs=Phase2 ftype=gpu fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=92 tfc=MZ outfolder=livia_checks'
    print 'python generator.py penalty=CNO,Ext_K40 inputs=Phase2 ftype=cno fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=140 tfc=MI'
    print
    print generator.__doc__
    print 'Options:'
    for op in options:
        print '\t', op, ':', ', '.join(options[op])
    print
    print 'Defaults:'
    for df in defaults:
        print '\t', df, ':', defaults[df]
    print
    sys.exit(1)


if __name__ == '__main__':
    main()
