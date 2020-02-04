import sys
import itertools
from creator import * 

#----------------------------------------------------------
# format {species: value}, to fix a certain species in the species list
# to a given value (part of the scan). Special feature: c11mean
SCAN = {'pep': np.arange(0, 6, 0.1),
        'c11mean': range(15,29)
        }       
#----------------------------------------------------------
    
# available values for each parameter
options = {
    'ftype': ['cpu', 'gpu', 'cno'],
    'fit': ['ene', 'mv'],
    'inputs': ['Phase2', 'Phase3'] + range(2012,2020),
    'tfc': ['MI', 'MZ'],
    'var': ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2'],

    'penalty': ICCpenalty.keys() + ['pileup', 'none'],
    'met': ['hm', 'lm', 'none'], # metallicity for the pep constraint
    'shift': ['C11', 'Po210', 'none'],    

    'save': ['true', 'false'],
}

options['fixed'] = options['penalty']
#options['scan'] = SCAN.keys() 
    
## defaults
defaults = {
    'ftype': 'gpu',
    'tfc': 'MI',
    'var': 'nhits',
    'pdfs': 'MCfits/pdfs_TAUP2017',
    'input_path': '/p/project/cjikp20/jikp2007/fitter_input/v3.1.0/files',
    'emin': '92',
    'save': 'false',
}
    
## total options = options + the ones that do not have fixed choices
user = options.keys() + ['pdfs', 'input_path', 'emin', 'outfolder'] + ['scan']
   

## parameters that are lists in the submission
par_list = ['penalty', 'shift', 'fixed']
## parameters that will be looped on (so also lists)
par_loop = ['inputs', 'emin']
# things to split by comma
splt_comma = par_list + par_loop

#----------------------------------------------------------

## nonte: for generator(), params['inputs'] is one string
## in main() it's a list, and will be looped on
## however, in the generator() docstring it says "list"
## just because this is what i print out for the user
## it's a bit confusing
def generator(params):
    '''
        ftype ['cpu'|'gpu'|'cno']: CPU or GPU fitter.
            Setting 'cno' means GPU fitter with "CNO configuration"
            (no C14 and pp in the species). To remove pileup, simply do not put
            'penalty=pileup'

        fit ['ene'|'mv']: energy only or multivariate fit

        inputs (list): names of the period (e.g. Phase2) or a year (e.g. '2012')
             If multiple inputs are be given, e.g. ['Phase2', 'Phase3'], multiple
                submissions will be generated.
             In case years are given, a range of years between the given ones
                       will be generated, e.g. ['2012','2016'] will create
                       submissions for years 2012 to 2016 inclusive

        tfc ['MZ'|'MI']: type of TFC. Default: MI 

        input_path (string): path to fitter inputs. Default: path to v3.1.0 inputs in JURECA
        pdfs (string): path to MC PDFs. Default: MCfits/pdfs_TAUP2017 (included in the repo)

        var ['nhits' | 'npmts_dt1' | 'npmts_dt2']: fit variable. Default: nhits

        emin (int): min energy of the fit. Default: 92
        
        penalty (list): list of species to be constrained in the fit
            Constraints are defined in the bottom in ICCpenalty

        fixed (list): list of species to be fixed in the fit
            Values are defined in the bottom in ICCfixed

        scan (string): species to perform scan on (must be in SCAN dictionary above)
            
        met ['hm'|'lm']: metallicity
            Used with option penalty or fixed for species the value for which
            depends on metallicity                      

        shift (list): list of species to apply shift to (C11, Po210)

        save [True|False]: save the fit output in .root and .pdf                      

        outfolder (string): output folder for the log files
            If not given, an output folder is created with a name based on the settings
            Default: false                            
    
  Examples:

    python generator.py inputs=Phase2 ftype=cno fit=mv var=nhits emin=140 pdfs=pdfs_new shift=C11 penalty=pileup,CNO

    python generator.py penalty=CNO,pileup inputs=Phase2 ftype=gpu fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=92 tfc=MZ outfolder=livia_checks

    python generator.py penalty=CNO,Ext_K40 inputs=2012,2016 ftype=cno fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=140 tfc=MI

    python generator.py penalty=pileup,CNO met=hm inputs=Phase2 fit=mv scan=pep outfolder=test_dir_pep

    '''

    ## ---------------------------------


    # check each parameter given by user
    for par in options:
        # parameters that are lists and have only some allowed options
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
    
    print # readability
    
    # submission file for CNAF
    s.subfile()



def main():
    userinput = sys.argv[1:]
   
    ## if simpy python generator.py is called, show all options
    if len(userinput) == 0:
        wrong_inputs()


    # first assign none
    opts = {}
    for opt in user:
        if opt in splt_comma:
            # for options that can be a list, penalty and shift
            opts[opt] = ['none']
        else:
            opts[opt] = 'none'

    # then read what user gave
    for opt in user:
        for inp in sys.argv:
            if opt in inp.split('=')[0]:
                # penalty, fixed and shift can be a list; inputs is a list to loop on
                opts[opt] = inp.split('=')[1].split(',') if opt in splt_comma else inp.split('=')[1]
#                print opt, opts[opt]

    # assign defaults if nothing given
    for par in defaults:
        if opts[par] == 'none':
            opts[par] = defaults[par]
        elif opts[par] == ['none']:
            opts[par] = [defaults[par]]

    ## folder for given configuration (for submission files and output log file folder)
    if opts['outfolder'] == 'none':
        outfolder = 'res-fit-' + opts['ftype'] + '-' +  opts['fit']
        outfolder += '-' + '_'.join(opts['inputs'])
    
        outfolder += '-' + opts['pdfs'].split('/')[-1]
        outfolder += '-emin' + opts['emin']

        ## list like options
        for spop in par_list:
            if opts[spop] != ['none']:
                outfolder += '-' + spop + '_'.join(opts[spop])
        
        opts['outfolder'] = outfolder

        if os.path.exists(outfolder):
            print
            print 'Folder', outfolder, 'already exists!!'
            print '#######################################'
            return
    
    if not os.path.exists(opts['outfolder']): os.mkdir(opts['outfolder'])

    ## inputs that loop to make separate submissions: create ranges
    for par in par_loop:
        if not opts[par] == ['none']: opts[par] = make_range(opts[par])


        
    print '######################'
    print '~~ Your input:'
    print opts
    print '######################'

    # the parameters are the same as the user gave, but some have to be looped on, and not be lists in the input e.g. fit variable
    params = opts.copy()        

    ## loop over the parameters that define separate submissions

    # list of lists of values for parameters to loop on to create a separate Submission
    loop_iter = [opts[key] for key in par_loop]
    # scan range for species
    if opts['scan'] != 'none':
        loop_iter.append(SCAN[opts['scan']])

    # loop over all combos
    for combo in itertools.product(*loop_iter):
        # assign current combination
        for i in range(len(par_loop)):
            params[par_loop[i]] = combo[i]
        # assign scan value    
        if opts['scan'] != 'none': params['scan'] = {opts['scan']: combo[-1]}

        print
        print '~~~ This submission:'
        print
        print params
        print
        generator(params)

    print


def wrong_inputs():
    '''A message to print if user input is wrong '''
    print
    print generator.__doc__
    print
    print 'Short list of parameters:'
    print '\t' + ', '.join(user)
    print
    print 'Options:'
    for op in options:
        print '\t', op, ':', ', '.join(str(x) for x in options[op])
    print
    print 'Defaults:'
    for df in defaults:
        print '\t', df, ':', defaults[df]
    print
    sys.exit(1)


def make_range(lst):
    if lst[0].isdigit():
        return range(int(lst[0]), int(lst[-1]) + 1)
    # if it's something like Phase2
    return lst



if __name__ == '__main__':
    main()
