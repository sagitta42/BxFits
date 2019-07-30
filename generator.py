import sys
from creator import * 

#----------------------------------------------------------

def generator(outfolder, fit, CNO, var, inputs, pdfs, penalty):
    '''
    outfolder: output folder for log and err files        
    fit: type of fit (ene, mv)            
    CNO: fit condition (fixed, lm, hm)
    var: energy variable (nhits, npmts, npmts_dt1, npmts_dt2)
    inputs: period to fit (all, YYYY)
    pdfs: folder where PDFs are to be found            
    penalty: species to put penalty on (e.g. Bi210) (optional) --> not implemented yet
    '''

    ## ---------------------------------
    ## technical checks

    CNOoptions = ['fixed','lm', 'hm', 'fixed5']
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

    inputoptions = ['all'] + [str(y) for y in range(2012,2018)]        
    if not inputs in inputoptions:
        print '\nOptions for inputs:', ', '.join(fitoptions) + '\n'
        return
    
    for pen in penalty:
        if not ((pen in ICC) or (pen == 'pp/pep') or penalty == 'none'):
            print '\nOptions for penalty:', ','.join(ICC.keys())
            return


    ## ---------------------------------

    ## init
    s = Submission(fit, CNO, var, inputs, pdfs, penalty)
    
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

    ## default for PDFs is TAUP
    if opts['pdfs'] == 'none': opts['pdfs'] = 'pdfs_TAUP2017'        

    ## folder for given configuration (for submission files and output log file folder)
    outfolder = 'res-fit-' + opts['fit']
    if opts['inputs'] == 'none':
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
    ## no input by default means PeriodAll
    if opts['inputs'] == 'none':
        opts['inputs'] = ['all']           

    
    ## loop over variables and CNO and create a fit for each
    for CNO in opts['CNO']:
        for var in opts['var']:
            for inp in opts['inputs']:
                params = [outfolder, opts['fit'], CNO, var, str(inp), opts['pdfs'], opts['penalty']]
#                print params
                generator(*params)


if __name__ == '__main__':
    main()
