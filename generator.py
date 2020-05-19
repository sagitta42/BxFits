import sys
import itertools
from creator import * 

#----------------------------------------------------------
# format {species: value}, to fix a certain species in the species list
# to a given value (part of the scan). Special feature: c11mean
SCAN = {'pep': np.arange(0, 6.2, 0.2),
        'c11mean': range(15,29),
#        'CNO': np.arange(0, 15, 0.5),
        'Bi210': np.arange(0,20,0.5),
#        'c11shift': range(7,8), # fixed to 7.0
        'c11shift': np.arange(0, 16.5, 0.5),
        'CNO': np.arange(0, 2.0, 0.5)
#        'CNO': np.arange(0, 10.5, 0.5)
        }       
#----------------------------------------------------------
    
# available values for each parameter
options = {
    'arch': ['cpu','gpu'],
    'ftype': ['full', 'cno', 'tfc'], # cno and tfc are type of gpu; 
    'fit': ['ene', 'mv', 'tag'],
#    'fpdf': ['mc', 'ana'],
    'inputs': ['All', 'Phase2', 'Phase3', 'Phase3Strict', 'Phase3Large'] + range(2012,2020),
    'tfc': ['MI', 'MZ'],
    'var': ['nhits', 'npmts', 'npmts_dt1', 'npmts_dt2'],

    'penalty': ICCpenalty.keys() + ['pileup', 'none', 'pp-pep'],
    'met': ['hm', 'lm', 'zero', 'none'], # metallicity for the pep or CNO constraint
    'shift': ['C11', 'Po210', 'none'],    

    'save': ['true', 'false'],
}

options['fixed'] = options['penalty'] # species to be fixed
options['ulim'] = options['penalty'] # species for upper limit
#options['scan'] = SCAN.keys() 
    
## defaults
defaults = {
    'arch': 'gpu',
    'ftype': 'cno',
#    'fpdf': 'mc',
    'tfc': 'MI',
    'var': 'nhits',
    'pdfs': 'BxFits/pdfs_TAUP2017',
    'input_path': '/p/project/cjikp20/jikp2007/fitter_input/v4.0.0/files',
#    'input_path': '/p/project/cjikp20/jikp2007/fitter_input/v3.1.0/files',
    'rdmin': 500,
    'rdmax': 900,
    'rdbin': 16,
    'psmin': 400,
    'psmax': 650,
    'c11sh': 7.0, # recent studies show 5-6
    'save': 'false',
    'nbatch': 0,
}
    
## total options = options + the ones that do not have fixed choices
user = options.keys() + ['pdfs', 'input_path', 'outfolder', 'nbatch'] +\
       ['emin', 'emax', 'rdmin',\
           'rdmax',\
           'rdbin', 'psmin', 'psmax', 'c11sh'] +\
       ['scan']
   

## parameters that are lists in the submission
par_list = ['penalty', 'shift', 'fixed', 'ulim']
## parameters that will be looped on (so also lists)
par_loop = ['inputs', 'emin', 'emax', 'rdmin',\
            'rdmax',\
            'rdbin', 'psmin', 'psmax',\
           'c11sh', 'tfc','var']
# things to split by comma
splt_comma = par_list + par_loop

#----------------------------------------------------------

# global batch counter
bcount = 0


## nonte: for generator(), params['inputs'] is one string
## in main() it's a list, and will be looped on
## however, in the generator() docstring it says "list"
## just because this is what i print out for the user
## it's a bit confusing
def generator(params_gen):
    '''
        arc ['cpu'|'gpu']: architecture, CPU (CNAF) or GPU (Jureca) fitter

        ftype ['full'|'cno'|'tfc']: "type" of the fit
            'full': our standard energy range (from around 85),
                including all the species
            'cno': "CNO configuration" i.e. no pp, C14 and pileup
            'tfc': configuration for fitting a single shape (C11) to
                strict TFC sample to determine C11 shift

        fit ['ene'|'mv']: energy only or multivariate fit

        inputs (string): name of the period (e.g. Phase2) or a year (e.g. '2012')
             If multiple inputs are be given, e.g. ['Phase2', 'Phase3'], multiple
                submissions will be generated.
             In case years are given, a range of years between the given ones
                       will be generated, e.g. ['2012','2016'] will create
                       submissions for years 2012 to 2016 inclusive

        tfc ['MZ'|'MI']: type of TFC. Default: MI 

        input_path (string): path to fitter inputs. Default: path to v3.1.0 inputs in JURECA
        input_path (string): path to fitter inputs. Default: path to v3.1.0 inputs in JURECA
        pdfs (string): "ana" for analytical fit, or path to MC PDFs for MC fit. Default: BxFits/pdfs_TAUP2017 (included in the repo)

        var ['nhits' | 'npmts_dt1' | 'npmts_dt2']: fit variable. Default: nhits

        emin (int): min energy of the fit. Default: 92
        emax (int): min energy of the fit. Default: 'none' (means 900 for npmts and 950 for nhits)
            If two values are given, e.g. [140,150], submissions for a range of values
                with min 140 max 150 and step 2 will be generated

        rdmin (int): min range of RD histo. Default: 500                    
        rdmax (int): max range of RD histo. Default: 900. If 0, will be equal to Emax                    
        rdbin (int): bin width of RD histo. Default: 16
        psmin (int): min range of PS histo. Default: 400                    
        psmax (int): max range of PS histo. Default: 650                    
            If multiple values are given, multiple submissions for given values
                will be generated
        
        penalty (string): species to be constrained in the fit
        fixed (string): species to be fixed in the fit
        ulim (string): species to put upper limit on in the fit
            Values are defined in the bottom in ICCpenalty
            Available species and values are defined in the bottom in ICCpenalty
            Possible to give the exact value instead of the default one
            Format example: Bi210:11.7,pep:2.99                          
            When no values are given, e.g. Bi210,pep , default values from ICCpenalty are used                          

        scan (string): species to perform scan on
            Must be in SCAN dictionary above, defining species and range of values
            
        met ['hm'|'lm']: metallicity
            Used with option penalty or fixed for species the value for which
            depends on metallicity                      

        shift (string): species to apply free shift to (C11, Po210)
        c11sh (float): value to fix C11 shift in MC fit. Default: 7.0

        save [True|False]: save the fit output in .root and .pdf                      

        outfolder (string): output folder for the log files
            If not given, an output folder is created with a name based on the settings
            Default: false                           
        nbatch: number of fits in one Jureca job. Default: 1                            
    
  Examples:

    python generator.py inputs=Phase2 ftype=cno fit=mv var=nhits emin=140 pdfs=pdfs_new shift=C11 penalty=pileup,CNO

    python generator.py penalty=CNO,pileup inputs=Phase2 ftype=gpu fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=92 tfc=MZ outfolder=livia_checks

    python generator.py penalty=CNO,Ext_K40 inputs=2012,2016 ftype=cno fit=mv met=hm var=nhits pdfs=pdfs_TAUP2017 emin=140 tfc=MI

    python generator.py penalty=pileup,CNO met=hm inputs=Phase2 fit=mv scan=pep outfolder=test_dir_pep

    '''

    global bcount

    ## ---------------------------------

    params = copy.deepcopy(params_gen)

    # check each parameter given by user
    for par in options:
        # parameters that are lists and have only some allowed options
        if par in ['penalty', 'shift', 'fixed', 'ulim']:
            flag = True # by default, we think it's an available option
            for parsp in params[par]:
                if not parsp.split(':')[0] in options[par]: flag = False # set to False if not available
#                if not parsp in options[par]: flag = False # set to False if not available
        else:
            flag = params[par] in options[par]

        if not flag:
            print '\nOptions for', par, ':', ', '.join(str(p) for p in options[par]) + '\n'
            sys.exit(1)


    ## ---------------------------------

    ## init

    s = Submission(params)
    
    
    
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
    
    ## submission file for CNAF
    # according to the counter of submissions and number of submissions in one batch, tell the subfile to which sbatch file it belongs
    nb = int(params['nbatch'])
    nfile = bcount / nb  if nb else -1
    s.subfile(nfile)
    # update number of fits
    bcount+=1



def setup_gen(userinput=None):
    if userinput == None:
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
        for inp in userinput:
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
        emin_part = opts['emin'][0] if len(opts['emin']) == 1 else 'to'.join(opts['emin'])
        emax_part = opts['emax'][0] if len(opts['emax']) == 1 else 'to'.join(opts['emax'])
        outfolder += '-emin' + emin_part
        outfolder += '-emax' + emax_part

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
#    for par in par_loop:
#        if not opts[par] == ['none']:
#            # for emin and emax, make a range
#            if par in ['emin', 'psmin', 'psmax']:
#                opts[par] = make_range(opts[par], int, 2)
#            elif par == 'emax':
#                opts[par] = make_range(opts[par], int, 16)
#            elif par == 'c11sh':
#                opts[par] = make_range(opts[par], float, 0.5)
#            else:
#                opts[par


       
    print        
    print '######################'
    print 'Your input:'
    print opts
    print '######################'
    # the parameters are the same as the user gave, but some have to be looped on, and not be lists in the input e.g. fit variable

    ## loop over the parameters that define separate submissions

    # list of lists of values for parameters to loop on to create a separate Submission
    loop_iter = [opts[key] for key in par_loop]
    # scan range for species
    if opts['scan'] != 'none':
        loop_iter.append(SCAN[opts['scan']])

    # loop over all combos
    for combo in itertools.product(*loop_iter):
        print combo
        params = copy.deepcopy(opts)
        print params
        # assign current combination
        for i in range(len(par_loop)):
            params[par_loop[i]] = combo[i]
        # assign scan value    
#        if opts['scan'] != 'none': params['scan'] = {opts['scan']: combo[-1]}
        if opts['scan'] != 'none':
            scline = '{0}:{1}:0'.format(opts['scan'], str(combo[-1]))
            if params['fixed'] != ['none']:
                params['fixed'].append(scline)
            else:
                params['fixed'] = [scline]


        # readability
        print '\n#######################################\n'
        print 'This submission:'
        print
        print params
        print
        generator(params)
#        print params
#        print opts
    
    # final submission file
    make_executable(opts['outfolder'] + '_submission.sh')
    print '---------------'
    print 'Submission for all sbatch:', opts['outfolder'] + '_submission.sh'
    print '---------------'

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
    print '\t', 'scan:', ', '.join(SCAN.keys())
    print
    print 'Defaults:'
    for df in defaults:
        print '\t', df, ':', defaults[df]
    print
    sys.exit(1)


def make_range(lst, tp=int, step=1):
#    if lst[0].isdigit():
    # -1 to account for the case if only one value is given
    return np.arange(tp(lst[0]), tp(lst[-1]) + step, step)
#    return range(int(lst[0]), int(lst[-1]) + 1)
    # if it's something like Phase2
#    return lst



if __name__ == '__main__':
    setup_gen()
