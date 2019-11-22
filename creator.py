import os
import numpy as np

class Submission():
    def __init__(self, params):
        '''
        params: dictionary with different parameters from user input

        ftype ['cpu'|'gpu'|'cno']: CPU or GPU fitter.
            Setting 'cno' means GPU fitter with "CNO configuration"
            (no C14 and pp in the species). To remove pileup, simply do not put
            'penalty=pileup'
        fit ['ene'|'mv']: energy only or multivariate fit
        inputs (string): name of the period (e.g. Phase2) or a year (e.g. '2012')
            The inputs will be read from a folder 'input_files' (create a link in your folder)
        tfc ['MZ'|'MI']: type of TFC                         
        pdfs (string): path to MC PDFs
        var ['nhits' | 'npmts_dt1' | 'npmts_dt2']: fit variable
        emin (int): min energy of the fit
        
        penalty (list): list of species to be constrained in the fit
            Constraints are defined in the bottom in ICCpenalty
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
        
        self.fittype = params['ftype'] 
        self.fitcno = False
        ftyp = self.fittype # for filenames
        # fit type CNO is just a GPU fit with extra CNO settings
        if self.fittype == 'cno':
            self.fitcno = True
            self.fittype = 'gpu'
        
        self.fit = params['fit'] 
        self.inputs = params['inputs'] 
        self.tfc = params['tfc']
        self.pdfs = params['pdfs']
        self.var = params['var'] # is a list always
        self.emin = params['emin']
        
        self.penalty = params['penalty'] # to be constrained (list)
        self.fixed = params['fixed']
        self.met = params['met']
        self.shift = params['shift']

        self.save = params['save']
        self.outfolder = params['outfolder']

        
        ## fitoptions filename
        # pileup penalty changes cfg
        pencfg = '-pileup' if 'pileup' in self.penalty else ''
        # shift
        shiftcfg = '' if self.shift == ['none'] else '_' + '-'.join(self.shift) + '-shift'
        self.cfgname = 'fitoptions/fitoptions_' + ftyp + '-' + self.fit + '-' + self.inputs + self.tfc + '-' + self.pdfs + '-' + self.var + '-emin' + self.emin + pencfg + shiftcfg + '.cfg' # e.g. fitoptions_mv-all-pdfs_TAUP2017-nhits.cfg

        ## species list filename
        # penalty
        penicc = '' if self.penalty == ['none'] else '_' + '-'.join(self.penalty) + '-penalty'
        # in case penalty depends on metallicity
        penmet = '-' + self.met if self.met != 'none' else '' 
        fixicc = '-'.join(self.fixed) + '-fixed' if self.fixed != ['none'] else ''
        self.iccname = 'species_list/species-fit-' + ftyp + '-' + self.fit + penicc + penmet + fixicc + '.icc'
        # log file name 
        self.outfile = 'fit-' + ftyp + '-' + self.fit + '-' + self.pdfs + '-' + 'Period' + self.inputs + self.tfc + '-' + self.var + '-emin' + self.emin + penicc + '-' + fixicc + 'met_' + self.met + shiftcfg
        
    
    def cfgfile(self):
        '''
        Create a fitoptions file corresponding to the given configuration (if needed)
        '''
        
        ## name of the cfg file
        print 'Fitoptions:', self.cfgname
        
        ## if file already exists, do nothing
        if os.path.exists(self.cfgname):
            return
            
        ## otherwise generate from a template
        cfglines = open('MCfits/templates/fitoptions_MCfit.cfg').readlines()
        cfglines = [ln.rstrip('\r\n') for ln in cfglines]

        # line 3: fit variable --> in case of npmts_dtX is just npmts
        cfglines[2] = 'fit_variable = ' + self.var.split('_')[0]
        
        # line 11: fit variable MC
        cfglines[10] = 'fit_variable_MC = ' + self.var

        # line 12: MC ext bkg
        cfglines[11] = 'MC_ext_bkg = true' # Davide check

        # boolean for MV fit
        bl = 'true' if self.fit == 'mv' else 'false'
        
        # line 36: multivariate or energy only fit
        cfglines[35] = 'c11_subtracted = ' + bl

        # line 68: PDF path
        # e.g. MCspectra_FVpep_Period_2012_unmasked.root
        # TAUP and new PDFs have different format
        mcname = 'MCspectra_pp_FVpep_' + self.inputs + '_emin1_masked.root' if 'TAUP' in self.pdfs else 'MCspectra_FVpep_Period_' + self.inputs + '_unmasked.root'
            
        cfglines[67] = 'montecarlo_spectra_file = ' + self.pdfs + '/' + mcname

        # line 80: remaining Pb214
        # Pb214 not implemented in the GPU fitter
        if self.fittype == 'gpu': cfglines[79] = "use_remaining_pb214 = false" # default is true

        # line 82: minimum energy
        cfglines[81] = 'minimum_energy = ' + self.emin

        # line 88: save fit result or not
        cfglines[87] = 'save_fit_results = ' + self.save

        if self.save == 'true':
            # line 89: fit results output filename
            cfglines[88] = 'fit_results_output = ' + self.outfolder + '/' + 'fit_results_' + self.outfile + '.root'
            # line 90: plot filename
            cfglines[89] = 'plot_filename = ' + self.outfolder + '/' + 'plot_' + self.outfile + '.root'

        # line 91: ps: only in mv
        cfglines[90] = 'multivariate_ps_fit = ' + bl

        # line 96: rdist: only in mv
        cfglines[95] = 'multivariate_rdist_fit = ' + bl

        # line 101: complem.: only in mv
        cfglines[100] = 'complementary_histo_fit = ' + bl

        # line 102: compl. fit variable
        cfglines[101] = 'complementary_histo_name = pp/final_' + self.var + '_pp_1'

        # line 127 and 128: pileup constraint (in species list is set to free, constraint is here)
        if 'pileup' in self.penalty:
            cfglines[126] = 'pileup_penalty_mean = ' + str(PUPPEN[self.inputs][0])
            cfglines[127] = 'pileup_penalty_sigma = ' + str(PUPPEN[self.inputs][1])
        else:
            # no pileup at all (also in species list)
            for l in range(123,128): cfglines[l] = '#' + cfglines[l]                                     

        if self.shift != ['none']:
            # add shift on Po210 and C11
            for sh in self.shift:
                cfglines.append('freeMCshift' + sh + ' = true')
                
#        if self.fitcno:
#            # comment out pileup (lines 124 - 128)
#            for l in range(123,128): cfglines[l] = '#' + cfglines[l]                                     
        
        # line 103: dark noise: only in analytical fit, not MC fit
#        cfglines[102] = 'dark_noise_window = win' + self.var[-1] + '\n'

        # line 112 pp/pep constraint
#        if 'ppDpep' in self.penalty:
#            cfglines[111] = 'apply_pp/pep_constrain = true\n'
#            cfglines[112] = 'mean(Rpp/Rpep) = ' + str(PPPEP[self.metal][0]) + '\n'
#            cfglines[113] = 'sigma(Rpp/Rpep) = ' + str(PPPEP[self.metal][1]) + '\n'


        ## save file
        cfglines = [ln + '\n' for ln in cfglines]
        outfile = open(self.cfgname, 'w')
        outfile.writelines(cfglines)
        outfile.close()
        print '\tcreator.py: cfgfile : generated'


    def iccfile(self):
        '''
        Create a species list corresponding to the given configuration (if needed)
        '''

        print 'Species list:', self.iccname

        ## if file already exists, do nothing            
        if os.path.exists(self.iccname):
            return
            
        ## otherwise generate from a template
        icclines = open('MCfits/templates/species_list.icc').readlines()

        # line 15: pileup, comment out if we do not want to use pileup
        if not 'pileup' in self.penalty:
            icclines[14] = comment(icclines[14])

        # line 31: Pb214
        if self.fittype == 'gpu':
            # comment out because not implemented in the GPU fitter
            icclines[30] = comment(icclines[30])

        # CNO configuration species
        if self.fitcno:
            # C14 (l 13) and pp (l 16) are out (not pileup!)
            for i in [12, 15]:
                icclines[i] = comment(icclines[i])

        # energy only fit: Po210_2 (l 22), C11_2 (l 26), C10_2 (l 28) and He6_2 (l 30) have to go
        if self.fit == 'ene':
            for i in [21, 25, 27, 29]:
                icclines[i] = comment(icclines[i])

        # set penalties if given
        if self.penalty != ['none']:
            for pensp in self.penalty:
                # pileup penalty is in cfg not icc
                if pensp == 'pileup': continue

                line_num, line = ICCpenalty[pensp]
                # species for which penalty depends on metallicity
                if pensp in ['pp','pep', 'CNO']:
                    icclines[line_num] = line[self.met]
                # other species
                else:
                    icclines[line_num] = line

                icclines[line_num] += ',\n'
       
        # set fixed if given
        if self.fixed != ['none']:
            for fixsp in self.fixed:
                # get line number from penalty dict
                line_num = ICCpenalty[fixsp][0]
                # get line from fixed dict
                line = ICCfixed[fixsp]
                # species for which penalty depends on metallicity
                if fixsp in ['pp','pep', 'CNO']:
                    icclines[line_num] = line[self.met]
                # other species
                else:
                    icclines[line_num] = line

                icclines[line_num] += ',\n'

        ## save file
        # one species list for all fits
        outfile = open(self.iccname, 'w')
        outfile.writelines(icclines)
        outfile.close()
        print '\tcreator.py: iccfile : generated'



    def subfile(self):
        '''
        Create submission/exe .sh file if does not exist
        If yes, append the fit to the existing one
        '''

        ## input file
        # files on Jureca are different
        cy = '_c19' if self.fittype == 'gpu' else '' 
        # e.g. Period2012_FVpep_TFCMI_c19.root
        inputfile = 'input_files/Period' + self.inputs + '_FVpep_TFC' + self.tfc + cy + '.root'

        ## submission file
        outname = self.outfolder + '_submission.sh'
        # to print bin bash or not
        binbool = os.path.exists(outname)
        out = open(outname, 'a') # append

        extra = '_0' if self.fit == 'mv' else ''

        # CNAF submission
        if self.fittype == 'cpu':

            print >> out, 'bsub -q borexino_physics',\
                '-e', self.outfolder + '/' + self.outfile + '.err',\
                '-o', self.outfolder + '/' + self.outfile + '.log',\
                './spectralfit', inputfile, 'pp/final_' + self.var + '_pp' + extra,\
                self.cfgname, self.iccname

        elif self.fittype == 'gpu':
            if not binbool: print >> out, '#!/bin/bash'
            print >> out, './borexino', inputfile,\
                'pp/final_' + self.var + '_pp' + extra,\
                self.cfgname, self.iccname, ' | tee', self.outfolder + '/' + self.outfile + '.log'
            out.close()
            make_executable(outname)

        print 'Fit:', outname
        print 'Future log file:', self.outfile


def make_executable(path):
    ''' chmod +x the file'''
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)




# species: [line number, line] for normal species
# species: {metallicity : [line number, line]} for the ones depending on metallicity
# species : line number for the ones that only get fixed and never constrained        
# line number is line - 1 (i.e. line 1 is 0)        
ICCpenalty = {
    'Bi210': [22, '{ "Bi210",        -1,   kSpring, kSolid,  2,    11.84,    "penalty",  11.84,  1.59 }'], # addition for systematics
#    'Kr85': [29, '{ "Kr85",         -1,   kBlue,   kSolid,  2,    6.8,     "penalty", -999.,  110. }\n'],
#    'pp': [17, {'hz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    131.1,   "penalty",  131.1., 1.4 },\n', 'lz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    132.2,   "penalty",  132.2,  1.4 },\n'}],
    
    'pep': [17,\
    {'hm': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.74,   "penalty", 2.74,  0.04 }',
     'lm': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.78,   "penalty", 2.78,  0.04 }'}],
    
    'CNO': [28,\
    {'hm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    4.92,   "penalty", 4.92,  0.56 }',
     'lm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    3.52,   "penalty", 3.52,  0.37 }'}],

    'Ext_K40': [33]

}

ICCfixed = {
#    'fixed': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    0.,   "fixed", 0.,  50. },\n',
#    'fixed5': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.,   "fixed", 5.,  50. },\n',
            
    'Ext_K40':  '{ "Ext_K40",      -1,   kAzure,  kSolid,  2,    0.15,   "fixed",  0.,  10. }',

    'CNO': {'hm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    4.92,   "fixed", 4.92,  0.56 }',
    'lm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    3.52,   "fixed", 3.52,  0.37 }'}
#    'pep': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.8,   "fixed", 2.8,  10. },'
}

# i forgot what this was
#RND = {'Bi210': [10,2], 'C14': [3456000, 172800]}

#PPPEP = {'hm': [47.76, 0.84], 'lm': [47.5, 0.8]}

## pileup penalty
PUPPEN = {'Phase2': [2.1, 0.04],
        '2012': [2.6, 0.03],
        '2013': [2.2, 0.03],
        '2014': [2.0, 0.03],
        '2015': [3.2, 0.03],
        '2016': [1.4, 0.03]
}


# helper function
def comment(line):
    return '//' + line
