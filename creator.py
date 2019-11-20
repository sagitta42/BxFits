import os
import numpy as np

class Submission():
    def __init__(self, params):
        '''
        params: dictionary with different parameters from user input

        fit (str): fit style (ene or mv)                   
        CNO (str): fit condition (fixed, lm, hm)
        var (str): energy variable (nhits, npmts, npmts_dt1, npmts_dt2)
        emin (int): min energy of the fit
        inputs (list): min and max year for inputs ([int, int]) (PeriodAll if none)                   
        pdfs (str): folder to look for PDFs                       
        ftype: cpu or gpu
        penalty (list): species to be constrained (pp/pep)
        shift (list): what shift to apply (Po and C11)                        
        '''
        
        self.fit = params['fit'] # energy only or full mv
        self.cno = params['CNO']
        self.var = params['var'] # is a list always
        self.inputs = params['inputs'] # 'all' or string for year 
        self.pdfs = params['pdfs']
        self.fittype = params['ftype'] # cpu or gpu; cno = gpu with cno config
        self.fitcno = False
        if self.fittype == 'cno':
            self.fitcno = True
            self.fittype = 'gpu'
        self.emin = params['emin']
        self.save = params['save']
        self.outfolder = params['outfolder']

        self.penalty = params['penalty'] # to be constrained (list)
        self.met = params['met']
        self.shift = params['shift']
        
        ## fitoptions filename
 #       if self.penalty[0] == 'pp/pep': self.penalty[0] = 'ppDpep'
        pen = '' if self.penalty == ['none'] else '_' + '-'.join(self.penalty) + '-penalty'
        penmet = '-' + self.met if 'pep' in ''.join(self.penalty) else '' # pep and pp/pep constraints depend on metallicity

        # if penalty is pp/pep, it's in fitoptions, but not species list
#        pencfg = pen + penmet if self.penalty[0] == 'ppDpep' else ''
        pencfg = '' # no penalty options for pp/pep for now
        shiftcfg = '' if self.shift == ['none'] else '_' + '-'.join(self.shift) + '-shift'
        self.cfgname = 'fitoptions/fitoptions_' + self.fit + '-' + self.inputs + '-' + self.pdfs + '-' + self.var + '-emin' + self.emin + pencfg + shiftcfg + '.cfg' # e.g. fitoptions_mv-all-pdfs_TAUP2017-nhits.cfg

        ## species list filename
        penicc = pen + penmet if self.penalty[0] != 'ppDpep' else ''
#        penicc = '' # no penalty for now
        self.iccname = 'species_list/species-fit-' + self.fit + 'CNO-' + self.cno + penicc + '.icc'
        # log file name 
        self.outfile = 'fit-' + self.fit + 'Period' + self.inputs + '-CNO'+ self.cno + '-' + self.var
        
    
    def cfgfile(self):
        ''' Create a fitoptions file corresponding to the given configuration (if needed) '''
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

        bl = 'true' if self.fit == 'mv' else 'false'
        
        # line 36: multivariate or energy only fit
        cfglines[35] = 'c11_subtracted = ' + bl

        # line 68: PDF path
        # e.g. MCspectra_FVpep_Period_2012_unmasked.root
        mcname = {'cpu': 'MCspectra_pp_FVpep_' + self.inputs + '_emin1_masked.root',
            'gpu': 'MCspectra_FVpep_Period_' + self.inputs + '_unmasked.root'} # on JURECA
        cfglines[67] = 'montecarlo_spectra_file = ' + self.pdfs + '/' + mcname[self.fittype]

        # line 80: remaining Pb214
        # Pb214 not implemented in the GPU fitter
        if self.fittype == 'gpu': cfglines[79] = "use_remaining_pb214 = false" # default is true

        # line 82: minimum energy
        cfglines[81] = 'minimum_energy = ' + self.emin

        # line 88: save fit result or not
        cfglines[87] = 'save_fit_results = ' + self.save

        if self.save == 'true':
            # line 89: fit results output filename
            cfglines[88] = 'fit_results_output = ' + self.outfolder + '/' + 'fit_results.root'
            # line 90: plot filename
            cfglines[89] = 'plot_filename = ' + self.outfolder + '/' + 'plot.root'

        # line 91: ps: only in mv
        cfglines[90] = 'multivariate_ps_fit = ' + bl

        # line 96: rdist: only in mv
        cfglines[95] = 'multivariate_rdist_fit = ' + bl

        # line 101: complem.: only in mv
        cfglines[100] = 'complementary_histo_fit = ' + bl

        # line 102: compl. fit variable
        cfglines[101] = 'complementary_histo_name = pp/final_' + self.var + '_pp_1'

        # line 127 and 128: pileup constraint in CPU fit
        if self.fittype == 'cpu':
            # in CPU fit, the constraint is in fitoptions
            cfglines[126] = 'pileup_penalty_mean = ' + str(PUPPEN[self.inputs][0])
            cfglines[127] = 'pileup_penalty_sigma = ' + str(PUPPEN[self.inputs][1])
        elif self.fittype == 'gpu' and self.shift != ['none']:
            # add shift on Po210 and C11
            for sh in self.shift:
                cfglines.append('freeMCshift' + sh + ' = true')
#            extralines = ['freeMCshiftPo210 = true',\
#                         'freeMCscalePo210 = true',\
#                         'freeMCshiftC11 = true',\
#                         'freeMCscaleC11 = true']

#            cfglines += extralines                         

        if self.fitcno:
            # comment out pileup (lines 124 - 128)
            for l in range(123,128): cfglines[l] = '#' + cfglines[l]                                     
        
        # question: should the pileup_penalty* lines in fitoptions be removed for the GPU fit? or will they be ignored?
        
        # in GPU fit, pileup penalty is in species list


        # line 103: dark noise: only in analytical fit, not MC fit
#        cfglines[102] = 'dark_noise_window = win' + self.var[-1] + '\n'

        # line 112 pp/pep constraint
#        if self.penalty[0] == 'ppDpep':
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
        ''' Create a species list corresponding to the given configuration (if needed) '''
        print 'Species list:', self.iccname
        ## if file already exists, do nothing
            
        if os.path.exists(self.iccname):
            return
            
        ## otherwise generate from a template
        extra = '_cno' if self.fitcno else '' # for cno configuration fits
        icclines = open('MCfits/templates/species_list_' + self.fit + extra + '.icc').readlines()

        # line 18: pile up species in GPU fitter
        # not used now in the CNO config
#        if self.fittype == 'gpu':
#            icclines[17] = '{ "MCpup", -1,   kViolet, kDashed, 2,     ' + str(PUPPEN[self.inputs][0]) + ', "penalty",  ' + str(PUPPEN[self.inputs][0]) + ',  ' + str(PUPPEN[self.inputs][1]) + ' }'

        # line 23 pep: fixed if ene Simone yearly fits, in principle is not a must
        if self.fittype == 'cpu' and self.fit == 'ene' and self.inputs[0] == '2':
            icclines[22] = '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.8,   "fixed", 2.8,  10. },\n'

        # line 24: cno fixed or free; or constrained to lm/hm
        icclines[23] = CNOICC[self.cno]


        # set penalties if given
        if self.penalty != ['none']:
            for pensp in self.penalty:
                if pensp == 'ppDpep': continue
                line_num, line = ICC[pensp]
                if pensp in ['pp','pep']:
                    icclines[line_num] = line[self.met]
                else:
                    icclines[line_num] = line
        
        ## save file
        # one species list for all fits
        outfile = open(self.iccname, 'w')
        outfile.writelines(icclines)
        outfile.close()
        print '\tcreator.py: iccfile : generated'



    def subfile(self):#, outfolder):
        ''' Create CNAF submission file if does not exist; if yes, append
        name of the submission file is outfolder_submission.sh, where outfolder is the folder for the output log files
        '''

        pr = 'All' if self.inputs == 'all' else self.inputs
        tfc = 'MI_c19' if self.fittype == 'gpu' else 'MZ' # files on Jureca are different
        # e.g. Period2012_FVpep_TFCMI_c19.root
        inputfile = 'input_files/Period' + pr + '_FVpep_TFC' + tfc + '.root'

        out = open(self.outfolder + '_submission.sh', 'a') # append

        extra = '_0' if self.fit == 'mv' else ''

        # CNAF submission
        if self.fittype == 'cpu':

            print >> out, 'bsub -q borexino_physics',\
                '-e', self.outfolder + '/' + self.outfile + '.err',\
                '-o', self.outfolder + '/' + self.outfile + '.log',\
                './spectralfit', inputfile, 'pp/final_' + self.var + '_pp' + extra,\
                self.cfgname, self.iccname

        elif self.fittype == 'gpu':
            print >> out, '#!/bin/bash'
            print >> out, './borexino', inputfile,\
                'pp/final_' + self.var + '_pp' + extra,\
                self.cfgname, self.iccname, '| tee', self.outfolder + '/' + self.outfile + '.log'
            out.close()
            make_executable(self.outfolder + '_submission.sh')


def make_executable(path):
    ''' chmod +x the file'''
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


CNOICC = {
#    'fixed': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    0.,   "fixed", 0.,  50. },\n',
#    'fixed5': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.,   "fixed", 5.,  50. },\n',

    'free': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.36,   "free", 0.,  50. },\n',
    'hm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    4.92,   "fixed", 4.92,  0.56 },\n',
    'lm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    3.52,   "fixed", 3.52,  0.37 },\n'
}

# penalty: line number is line - 1 (i.e. line 1 is 0)
ICC = {
#    'Bi210': [29, '{ "Bi210",        -1,   kSpring, kSolid,  2,    11.84,    "penalty",  11.84,  1.4 },\n'],
    'Bi210': [29, '{ "Bi210",        -1,   kSpring, kSolid,  2,    11.84,    "penalty",  11.84,  1.59 },\n'], # addition for systematics
#    'Bi210': [27, '{ "Bi210",        -1,   kSpring, kSolid,  2,    17.5,    "penalty",  17.5,  2.0 },\n'],
#    'C14': [13, '{ "C14",          -1,   kViolet, kSolid,  2,    3.456e+6, "penalty", 3.456e+6, 17.28e+4 },\n'],
#    'Kr85': [29, '{ "Kr85",         -1,   kBlue,   kSolid,  2,    6.8,     "penalty", -999.,  110. }\n'],
#    'pp': [17, {'hz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    131.1,   "penalty",  131.1., 1.4 },\n', 'lz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    132.2,   "penalty",  132.2,  1.4 },\n'}],
    'pep': [22, {'hm': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.74,   "penalty", 2.74,  0.04 },\n', 'lm': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.78,   "penalty", 2.78,  0.04 },\n'}],
    'CNO': [23, {'hm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    4.92,   "penalty", 4.92,  0.56 },\n', 'lm': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    3.52,   "penalty", 3.52,  0.37 },\n'}]
}

RND = {'Bi210': [10,2], 'C14': [3456000, 172800]}

PPPEP = {'hm': [47.76, 0.84], 'lm': [47.5, 0.8]}

## pileup penalty
PUPPEN = {'all': [2.1, 0.04],
        '2012': [2.6, 0.03],
        '2013': [2.2, 0.03],
        '2014': [2.0, 0.03],
        '2015': [3.2, 0.03],
        '2016': [1.4, 0.03],
}
