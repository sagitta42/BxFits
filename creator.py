import os
from math import ceil
import numpy as np
import random as rnd
rnd.seed(1)

class Submission():
    def __init__(self, fit, CNO, var, penalty):
        '''
        CNO (str): fit condition (fixed, lm, hm)
        var (str): energy variable (nhits, npmts, npmts_dt1, npmts_dt2)
        penalty (list): species to be constrained (pp/pep)
        '''
        
        self.fit = fit # energy only or full mv
        self.cno = CNO
        self.var = var # is a list always
#        self.penalty = penalty # to be constrained
        
        ## corr. fitoptions and species lists filenames
 #       if self.penalty[0] == 'pp/pep': self.penalty[0] = 'ppDpep'
 #       pen = '' if self.penalty == 'none' else '_' + '-'.join(self.penalty) + '-penalty'
 #       penmet = '-' + self.metal if 'pp' in ''.join(self.penalty) else '' # pp/pep constraint depends on metallicity

        # if penalty is pp/pep, it's in fitoptions, but not species list
#        pencfg = pen + penmet if self.penalty[0] == 'ppDpep' else ''
        pencfg = '' # no penalty options for now
        self.cfgname = 'fitoptions/fitoptions_' + fit + '_' + var + pencfg + '.cfg'
#        penicc = pen + penmet if self.penalty[0] != 'ppDpep' else ''
        penicc = '' # no penalty for now
        self.iccname = 'species_list/species_' + CNO + penicc + '.icc'
        
        self.outfile = 'fit_' + fit + '_CNO'+ CNO + '_' + var
        
    
    def cfgfile(self):
        ''' Create a fitoptions file corresponding to the given configuration (if needed) '''
            ## name of the cfg file
        print 'Fitoptions:', self.cfgname
        
        ## if file already exists, do nothing
        if os.path.exists(self.cfgname):
            return
            
        ## otherwise generate from a template
        cfglines = open('templates/fitoptions_MCfit.cfg').readlines()
        cfglines = [ln.rstrip('\r\n') for ln in cfglines]

        end = ''
#        end = '\n'
        
        # line 3: fit variable --> always npmts? not npmts_dt1 or dt2?
        cfglines[2] = 'fit_variable = ' + self.var + end
        
        # line 11: fit variable MC
        cfglines[10] = 'fit_variable_MC = ' + self.var + end

        bl = 'true' if self.fit == 'mv' else 'false'
        
        # line 36: multivariate or energy only fit
        cfglines[35] = 'c11_subtracted = ' + bl + end

        # line 91: ps: only in mv
        cfglines[90] = 'multivariate_ps_fit = ' + bl + end

        # line 96: rdist: only in mv
        cfglines[95] = 'multivariate_rdist_fit = ' + bl + end

        # line 101: complem.: only in mv
        cfglines[100] = 'complementary_histo_fit = ' + bl + end

        # line 103: dark noise: only in analytical fit, not MC fit
#        cfglines[102] = 'dark_noise_window = win' + self.var[-1] + '\n'

        # line 112 pp/pep constraint
#        if self.penalty[0] == 'ppDpep':
#            cfglines[111] = 'apply_pp/pep_constrain = true\n'
#            cfglines[112] = 'mean(Rpp/Rpep) = ' + str(PPPEP[self.metal][0]) + '\n'
#            cfglines[113] = 'sigma(Rpp/Rpep) = ' + str(PPPEP[self.metal][1]) + '\n'


        
        ## save file
        print cfglines[2]
        cfglines = [ln + '\n' for ln in cfglines]
        outfile = open(self.cfgname, 'w')
        outfile.writelines(cfglines)
        outfile.close()
        print '\tcreator.py: cfgfile : generated'


    def iccfile(self):
        ''' Create a species list corresponding to the given configuration (if needed) '''
        print 'Species list:', self.iccname
        ## if file already exists, do nothing
            
        if os.path.exists(self.iccname):
            return
            
        ## otherwise generate from a template
        icclines = open('templates/species_list_taup.icc').readlines()

        # line 24: cno fixed or free; or constrained to lm/hm
        icclines[23] = CNOICC[self.cno]

#        # extra: free (default) or penalty
#        if self.penalty != 'none':
#            for pensp in self.penalty:
#                if pensp == 'ppDpep': continue
#                line_num, line = ICC[pensp]
#                if pensp in ['pp','pep']:
#                    icclines[line_num] = line[self.metal]
#                else:
#                    icclines[line_num] = line
        
        ## save file
        # one species list for all fits
        outfile = open(self.iccname, 'w')
        outfile.writelines(icclines)
        outfile.close()
        print '\tcreator.py: iccfile : generated'



    def subfile(self, outfolder):
        ''' Create CNAF submission file if does not exist; if yes, append
        name of the submission file is outfolder_submission.sh, where outfolder is the folder for the output log files
        '''

        inputfile = '/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/PeriodAll_FVpep_TFCMZ.root'

        out = open(outfolder + '_submission.sh', 'a') # append

        extra = '_0' if self.fit == 'mv' else ''

        print >> out, 'bsub -q borexino_physics',\
            '-e', outfolder + '/' + self.outfile + '.err',\
            '-o', outfolder + '/' + self.outfile + '.log',\
            './spectralfit', inputfile, 'pp/final_' + self.var + '_pp' + extra,\
            self.cfgname, self.iccname


def make_executable(path):
    ''' chmod +x the file'''
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


CNOICC = {
    'fixed': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    0.,   "fixed", 0.,  50. },\n',

    'free': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.36,   "free", 0.,  50. },\n',
    'hm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    4.92,   "penalty", 4.92,  0.56 },\n',
    'lm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    3.52,   "penalty", 3.52,  0.37 },\n'
}

# penalty: line number is line - 1 (i.e. line 1 is 0)
ICC = {
    'Bi210': [27, '{ "Bi210",        -1,   kSpring, kSolid,  2,    17.5,    "penalty",  17.5,  2.0 },\n'],
    'C14': [13, '{ "C14",          -1,   kViolet, kSolid,  2,    3.456e+6, "penalty", 3.456e+6, 17.28e+4 },\n'],
    'Kr85': [29, '{ "Kr85",         -1,   kBlue,   kSolid,  2,    6.8,     "penalty", -999.,  110. }\n'],
    'pp': [17, {'hz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    131.1,   "penalty",  131.1., 1.4 },\n', 'lz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    132.2,   "penalty",  132.2,  1.4 },\n'}],
    'pep': [19, {'hz': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.74,   "penalty", 2.74,  0.04 },\n', 'lz': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.78,   "penalty", 2.78,  0.04 },\n'}]
}

RND = {'Bi210': [10,2], 'C14': [3456000, 172800]}

PPPEP = {'hm': [47.76, 0.84], 'lm': [47.5, 0.8]}
