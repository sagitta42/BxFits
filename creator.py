import sys
import os
import shutil
import numpy as np

class Submission():
    def __init__(self, params):
        '''
        For the description of params go to generator.py function generator()
        '''

        self.fittype = params['ftype'] 
        self.fitcno = False
        ftyp = self.fittype # for filenames

        # fit type CNO is just a GPU fit with extra CNO settings
        # (right now only means comment out C14 and pp, NOT pileup,
        # because were running tests with Livia)
        if self.fittype == 'cno':
            self.fitcno = True
            self.fittype = 'gpu'

        # fitting TFC strict sample to determine C11 shift
        self.fittfc = False
        if self.fittype == 'tfc':
            self.fittfc = True
            self.fittype = 'gpu'

        # Oemer: tag should be same as full just diff. histo
        self.fit = params['fit'] # mv, ene (full spectrum), tag
#        self.fpdf = params['fpdf'] # pdfs analytical or MC
        self.inputs = str(params['inputs'])
        self.tfc = params['tfc']
        self.input_path = params['input_path']
        self.pdfs = params['pdfs'] # path or "ana"
        self.var = params['var'] # is a list always
        self.emin = str(params['emin'])
        self.emax = str(params['emax'])
        ene = 900 if 'npmts' in self.var else 950
        if self.emax == 'none':
            self.emax = str(ene)
        self.rdmin = str(params['rdmin'])
        self.rdmax = str(params['rdmax'])
        self.rdbin = str(params['rdbin'])
        self.psmin = str(params['psmin'])
        self.psmax = str(params['psmax'])
        self.c11shift = str(params['c11sh'])
        
        # needed for the case when penalty or fixed is set for species that depend on metallicity
        self.met = params['met']                            
        # check if metallicity given 
        allsp = []
        for tp in ['penalty', 'fixed', 'ulim']:
            allsp += [ sp.split(':')[0] for sp in params[tp] ]
        for sp in allsp:
            if sp in METSP and self.met == 'none':
                print
                print 'Species', sp, 'requires metallicity! Use met=hm or met=lm\n'
                sys.exit(1)

        # penalty, fixed and ulim name parts for icc and log file before we extract values
        penicc = '' if params['penalty'] == ['none'] else '_penalty' + '-'.join(sp.replace(':','_') for sp in params['penalty'])
        fixicc = '_fixed' + '-'.join(sp.replace(':','_') for sp in params['fixed']) if params['fixed'] != ['none'] else ''
        ulimicc = '_ulim' + '-'.join(sp.replace(':', '_') for sp in params['ulim']) if params['ulim'] != ['none'] else ''

        # one dictionary for all: penalty, fixed and ulim, to use increating icc
        # values for penalty and fixed are in a dictionary in the bottom
        self.penfix = {}
        for key in ['penalty', 'fixed', 'ulim']:
            for i in range(len(params[key])):
                sp = params[key][i]
                if not sp == 'none':
                    # extract value if given
                    if ':' in sp:
                        spec, val = sp.split(':')
                        params[key][i] = spec
                        if spec in METSP:
                            ICCpenalty[spec]['mean'][self.met] = float(val)
                        else:
                            ICCpenalty[spec]['mean'] = float(val)
                        print spec, '->', val
                    # add to global dict
                    self.penfix[params[key][i]] = key # will be empty if all are none

        # pen, fix and ulim separately: for names, and for pileup which is in the cfg
        self.penalty = params['penalty'] # to be constrained (list)
        self.fixed = params['fixed'] # to be fixed (list)
        self.ulim = params['ulim'] # to set upper limit (list)

    
        # dictionary {species: value} or 'none'
        # special features: c11mean and c11shift
        self.scan = params['scan'] 
        self.scansp = 'none'
        if not self.scan == 'none':
            self.scansp = self.scan.keys()[0]
            # ignore c11mean and c11shift
            if not 'c11' in self.scansp:
                self.penfix[self.scansp] = 'fixed'
            if self.scansp == 'c11shift':
                self.c11shift = self.scan['c11shift']

        self.shift = params['shift']

        self.save = params['save']
        self.outfolder = params['outfolder']

      
        ## parts for cfg and log filenames
        eminname = '-emin' + self.emin
        emaxname = '-emax' + self.emax
        rdminname = '-rdmin' + self.rdmin
        rdmaxname = '-rdmax' + self.rdmax
        rdbinname = '-rdbin' + self.rdbin
        c11name = '' if self.pdfs == 'ana' else '-c11shift' + self.c11shift

        ## fitoptions filename
        # pileup penalty changes cfg
        pencfg = '-pileup' if 'pileup' in self.penalty else ''
        # shift
        shiftcfg = '' if self.shift == ['none'] else '_' + '-'.join(self.shift) + '-shift'
        # scan of c11shift
        scancfg = '_scan'  + self.scansp + str(self.scan[self.scansp]) if self.scansp == 'c11shift' else ''
        self.cfgname = 'fitoptions/fitoptions_' + ftyp + '-' + self.fit + '-' + self.inputs + self.tfc + '-' + self.pdfs.split('/')[-1] + '-' + self.var + eminname + emaxname + rdminname + rdmaxname + rdbinname + c11name + pencfg + shiftcfg + scancfg + '.cfg' # e.g. fitoptions_mv-all-pdfs_TAUP2017-nhits.cfg

        ## species list filename
        # in case penalty depends on metallicity
        penmet = '-' + self.met if self.met != 'none' else '' 
        scanicc = '' if self.scansp in ['none', 'c11shift'] else '_scan'  + self.scansp + str(self.scan[self.scansp])
        self.iccname = 'species_list/species-fit-' + ftyp + '-' + self.fit + eminname + emaxname + penicc + penmet + fixicc + ulimicc + scanicc + '.icc'
        # log file name 
        self.outfile = 'fit-' + ftyp + '-' + self.fit + '-' + self.pdfs.split('/')[-1] + '-' + 'Period' + self.inputs + self.tfc + '-' + self.var + eminname + emaxname + rdminname + rdmaxname + rdbinname + c11name + penicc + fixicc + 'met_' + self.met + shiftcfg + scanicc + scancfg + ulimicc
        
    
    def cfgfile(self):
        '''
        Create a fitoptions file corresponding to the given configuration (if needed)
        '''
        
        ## name of the cfg file
        print 'Fitoptions:', self.cfgname
        
        ## if file already exists, do nothing
        ## changed: the save option means have to do again
#        if os.path.exists(self.cfgname) and not self.save:
#            return
            
        ## otherwise generate from a template
        cfglines = open('BxFits/templates/fitoptions.cfg').readlines()
        cfglines = [ln.rstrip('\r\n') for ln in cfglines]

        # line 3: fit variable --> in case of npmts_dtX is just npmts
        cfglines[2] = 'fit_variable = ' + self.var.split('_')[0]
        # line 5: PDFS analytical or MC
        spdf = 'analytical' if self.pdfs == 'ana' else 'montecarlo'
        cfglines[4] = 'spectra_pdfs = ' + spdf
        
        # line 11: fit variable MC
        cfglines[10] = 'fit_variable_MC = ' + self.var

        # line 12: MC ext bkg
        ebg = 'true' if self.pdfs == 'ana' else 'false'
        cfglines[11] = 'MC_ext_bkg = ' + ebg

        # line 13: geometric correction
        if self.pdfs == 'ana':
            cfglines[12] = comment(cfglines[12])

        # line 36: multivariate or energy only fit
        boolsub = 'false' if self.fit == 'ene' else 'true'
        cfglines[35] = 'c11_subtracted = ' + boolsub

        # line 38: alpha response function
        alph = 'true' if self.pdfs == 'ana' else 'mc'
        cfglines[37] = 'use_alpha_response_function = ' + alph

        # line 68: PDF path
        # e.g. MCspectra_FVpep_Period_2012_unmasked.root
        # TAUP and new PDFs have different format
        mcname = 'MCspectra_pp_FVpep_' + self.inputs + '_emin1_masked.root' if 'TAUP' in self.pdfs else 'MCspectra_FVpep_Period_' + self.inputs + '_unmasked.root'
        # e.g. MCspectra_FVpep_Period_Phase2_unmasked.root

        # line 68: MC PDFs
        if self.pdfs == 'ana':
            cfglines[67] = comment(cfglines[67])
        else:
            cfglines[67] = 'montecarlo_spectra_file = ' + self.pdfs + '/' + mcname

        # line 80: remaining Pb214
        # Pb214 not implemented in the GPU fitter
        if self.fittype == 'gpu': cfglines[79] = "use_remaining_pb214 = false" # default is true

        # line 82: minimum energy
        cfglines[81] = 'minimum_energy = ' + self.emin

        # line 83: maximum energy
#        ene = 900 if 'npmts' in self.var else 950
        cfglines[82] = 'maximum_energy = ' + self.emax

        # line 88: save fit result or not
        cfglines[87] = 'save_fit_results = ' + self.save

        if self.save == 'true':
            # line 89: fit results output filename
            cfglines[88] = 'fit_results_output = ' + self.outfolder + '/' + 'fit_results_' + self.outfile + '.root'
            # line 90: plot filename
            cfglines[89] = 'plot_filename = ' + self.outfolder + '/' + 'plot_' + self.outfile + '.root'

        # line 91: ps: only in mv
        bl = 'true' if self.fit == 'mv' else 'false'
        cfglines[90] = 'multivariate_ps_fit = ' + bl

        # line 92, 93: PS range
        cfglines[91] = 'multivariate_ps_fit_min = ' + self.psmin
        cfglines[92] = 'multivariate_ps_fit_max = ' + self.psmax

        # line 96: rdist: only in mv
        cfglines[95] = 'multivariate_rdist_fit = ' + bl

        # line 97 and 98: RD min and max
        cfglines[96] = 'multivariate_rdist_fit_min = ' + self.rdmin
        cfglines[97] = 'multivariate_rdist_fit_max = ' + self.rdmax
        cfglines[98] = 'multivariate_rdist_fit_bins = ' + self.rdbin

        # line 101: complem.: only in mv
        compbl = 'true' if self.fit == 'mv' else 'false'
        cfglines[100] = 'complementary_histo_fit = ' + compbl

        # line 102: compl. fit variable
        cfglines[101] = 'complementary_histo_name = pp/final_' + self.var + '_pp_1'

        # line 111: dark noise convo
        dn = 'true' if self.pdfs == 'ana' else 'false'
        cfglines[110] = 'convolve_dark_noise = ' + dn

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

        if self.pdfs == 'ana':
            cfglines.append('fiducial_mass = 0')
            cfglines.append('force_dn_after_mask = false')
            cfglines.append('fcher_free = false')

            ## comment out MC pileup stuff
            for i in range(118,132): cfglines[i] = comment(cfglines[i])

        ## C11 shift            
        else:                                     
            if "TAUP" in self.pdfs:
                cfglines.append('freeMCshiftC11 = false')
                cfglines.append('freeMCshiftC11step = 0')
            else:
                cfglines.append('freeMCshiftC11 = true')
                cfglines.append('freeMCshiftC11step = 0')
        
                cfglines.append('freeMCshiftC11min = {0}'.format(self.c11shift))
                cfglines.append('freeMCshiftC11max = {0}'.format(self.c11shift))
                    
            

#        if self.fitcno:
#            # comment out pileup (lines 124 - 128)
#            for l in range(123,128): cfglines[l] = '#' + cfglines[l]                                     
        
        # line 103: dark noise: only in analytical fit, not MC fit
        if self.pdfs == 'ana':
            cfglines[102] = 'dark_noise_window = win' + self.var[-1]

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
            print '\tcreator.py: iccfile : already exists'
            return
            
        ## otherwise generate from a template
        

        icclines = open('BxFits/templates/species_list.icc').readlines()

        # line 15: pileup, comment out if we do not want to use pileup
        if not 'pileup' in self.penalty:
            icclines[14] = comment(icclines[14], '//')

        # line 25: C11 mean
        if self.scansp == 'c11mean':
            icclines[24] = '{{ "C11",          -1,   kMagenta,kSolid,  2,    {0},    "free",  0.,  100. }},\n'.format(float(self.scan['c11mean']))

        # line 31: Pb214
        if self.fittype == 'gpu':
            # comment out because not implemented in the GPU fitter
            icclines[30] = comment(icclines[30], '//')

        # CNO configuration species
        if self.fitcno:
            # C14 (l 13) and pp (l 16) are out (not pileup!)
            for i in [12, 15]:
                icclines[i] = comment(icclines[i], '//')

        # TFC fit: only C11            
        if self.fittfc:
            # comment out everything except C11 and C11_2
            nonc11 = np.setdiff1d(range(12, 34), [24,25])
            for i in nonc11:
                icclines[i] = comment(icclines[i], '//')

        # energy only fit (full spectrum): Po210_2 (l 22), C11_2 (l 26), C10_2 (l 28) and He6_2 (l 30) have to go
        # fitting the tagged spectrum: the non "_2" species should go: PO210 (l 21), C11 (l 25)
        clines = {'tag': [20, 24], 'ene': [21, 25, 27, 28], 'mv': []}
        for i in clines[self.fit]:
                icclines[i] = comment(icclines[i], '//')

        # fits for C11shift determination
        if int(self.emin) >= 300:
            # comment out Po210 (lines 21 and 22)
            for i in [20,21]:
                icclines[i] = comment(icclines[i], '//')

        # set penalties, fixed and upper limit if given
        for pensp in self.penfix:
            print pensp
        # pileup penalty is in cfg not icc
            if pensp in ['pileup', 'c11shift']: continue

            # species to scan, if given
            if pensp in self.scan:
                mean = self.scan[pensp] 
                sig = 0
            else:
                mean = ICCpenalty[pensp]['mean']   
                sig = ICCpenalty[pensp]['sigma']
                iccsp = pensp
                # species for which penalty depends on metallicity
                if pensp in METSP:
                    mean = mean[self.met] 
                    sig = sig[self.met]
                # cue to fitter to use upper limit instead of penalty
                if self.penfix[pensp] == 'ulim':
                    sig = - sig
                    self.penfix[pensp] = 'penalty'

            if pensp in NEUTRINOS:
                iccsp = 'nu({0})'.format(pensp)


            line_num = ICCpenalty[pensp]['line']
            # format in the icc file
            icclines[line_num] = '{{ "{0}",        -1,   {1}, kSolid,  2,    {2},    "{4}",  {2},  {3} }},\n'.format(iccsp, ICCpenalty[pensp]['color'], mean, sig, self.penfix[pensp])
            print icclines[line_num]
       

        ## save file
        # one species list for all fits
        outfile = open(self.iccname, 'w')
        outfile.writelines(icclines)
        outfile.close()
        print '\tcreator.py: iccfile : generated'



    def subfile(self, nfile):
        '''
        Create submission/exe .sh file if does not exist
        If yes, append the fit to the existing one
        '''

        print 'Future log file:', self.outfile        

        ## input file
        # files on Jureca are different
#        cy = '_c19' if self.fittype == 'gpu' else '' 
        cy = '' if 'TAUP' in self.pdfs else '_c19'
        # e.g. Period2012_FVpep_TFCMI_c19.root
        inputfile = self.input_path + '/Period' + self.inputs + '_FVpep_TFC' + self.tfc + cy + '.root'

        ## CNAF: submission file with bsub, Jureca: file with sbatch commands
        outname = self.outfolder + '_submission.sh' # one file to rule them all, run interactively
        # to print bin bash or not
        out = open(outname, 'a') 

        extra = {'mv': '_0', 'tag': '_1', 'ene': ''}
#        extra = '_0' if self.fit == 'mv' else ''

        # CNAF submission
        if self.fittype == 'cpu':

            print >> out, 'bsub -q borexino_physics',\
                '-e', self.outfolder + '/' + self.outfile + '.err',\
                '-o', self.outfolder + '/' + self.outfile + '.log',\
                './spectralfit', inputfile, 'pp/final_' + self.var + '_pp' + extra[self.fit],\
                self.cfgname, self.iccname

            print 'Fit file:', outname

        # Jureca submission
        elif self.fittype == 'gpu':
            ## fit file
            fitname = self.outfolder + '/fit_' + self.outfile + '.sh'
            fitfile = open(fitname, 'w')
            print >> fitfile, '#!/bin/bash'
            print >> fitfile, './borexino', inputfile,\
                'pp/final_' + self.var + '_pp' + extra[self.fit],\
                self.cfgname, self.iccname, ' | tee', self.outfolder + '/' + self.outfile + '.log'
            fitfile.close()
            make_executable(fitname)
            print 'Fit file:', fitname

            ## sbatch file        
            # our file
            sbatchname = self.outfolder + '/sbatch_' + str(nfile) + '.sh'

            # if file doesn't exist, create
            if not os.path.exists(sbatchname):
                # template
                shutil.copy('BxFits/templates/sbatch_submission_template.sh', sbatchname)
                make_executable(sbatchname)
                # add to top file that sbatches all the sbatch files
                print >> out, 'sbatch', sbatchname

            # our submission
            sbfile = open(sbatchname, 'a')
            print >> sbfile, 'srun ./' + fitname
            sbfile.close()
            print 'Sbatch file:', sbatchname


        out.close()



def make_executable(path):
    ''' chmod +x the file'''
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)




# line number is line - 1 (i.e. line 1 is 0)        
ICCpenalty = {
    'Bi210': {'line': 22,
              'color': 'kSpring',
              'mean': 11.7,
              'sigma': 1.6
             },
    'pep': {'line': 17,
            'color': 'kCyan',
            'mean': {'hm': 2.74, 'lm': 2.78},
            'sigma': {'hm': 0.04, 'lm': 0.04}
            },
    'CNO': {'line': 18,
            'color': 'kCyan',
            'mean': {'hm': 4.92, 'lm': 3.52, 'zero': 0} ,
            'sigma': {'hm': 0.56, 'lm': 0.37, 'zero': 0}
            },
    'Ext_K40': {'line': 33,
                'color': 'kAzure',
                'mean': 0.15,
                'sigma': 0 # it's never penalty, only fixed
            }
}

# neutrinos -> format nu(xx)
NEUTRINOS = ['pp', 'pep', 'CNO', 'Be7']
# species for which penalty depends on metallicity
METSP = []
for sp in ICCpenalty:
    if type(ICCpenalty[sp]['mean']) == dict: METSP.append(sp)


#PPPEP = {'hm': [47.76, 0.84], 'lm': [47.5, 0.8]}

## pileup penalty
PUPPEN = {
        'Phase2': [2.1, 0.04],
        'All': [2.1, 0.04],
        '2012': [2.6, 0.03],
        '2013': [2.2, 0.03],
        '2014': [2.0, 0.03],
        '2015': [3.2, 0.03],
        '2016': [1.4, 0.03]
}



# helper function
def comment(line, sym='#'):
    return sym + line
