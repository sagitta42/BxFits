import sys
import os
import shutil
import numpy as np
import copy # for deep copy of dict

class Submission():
    def __init__(self, params_gen):
        '''
        For the description of params go to generator.py function generator()
        '''

        params = copy.deepcopy(params_gen)
        
        self.arch = params['arch'] # cpu or gpu 
        self.fittype = params['ftype'] # full, cno or tfc

        # Oemer: tag should be same as full just diff. histo
        self.fit = params['fit'] # mv, ene (full spectrum), tag
#        self.fpdf = params['fpdf'] # pdfs analytical or MC
        self.inputs = str(params['inputs'])
        self.tfc = params['tfc']
        self.input_path = params['input_path']
        self.pdfs = params['pdfs'] # path or "ana"
        self.var = params['var'] # is a list always

        # default emin for Npmts and Nhits
        self.emin = str(params['emin'])
        if self.emin == 'none':
            ene = 85 if 'npmts' in self.var else 92
            self.emin = str(ene)

        # default emax for Npmts and Nhits
        self.emax = str(params['emax'])
        if self.emax == 'none':
            ene = 900 if 'npmts' in self.var else 950
            self.emax = str(ene)
        
        self.rdmin = str(params['rdmin'])
        self.rdmax = self.emax if params['rdmax'] == 0 else str(params['rdmax'])
#        self.rdmax = str(params['rdmax'])
        self.rdbin = str(params['rdbin'])
        self.psmin = str(params['psmin'])
        self.psmax = str(params['psmax'])
#        self.c11shift = str(params['c11sh'])
        
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


        # one dictionary for all: penalty, fixed and ulim, to use increating icc
        # values for penalty and fixed are in a dictionary in the bottom
        self.penfix = {}
        for key in ['penalty', 'fixed', 'ulim']:
            for i in range(len(params[key])):
                sp = params[key][i]
                if not sp == 'none':
                    # extract value if given
                    if ':' in sp:
                        spec, val, sig = sp.split(':')
                        params[key][i] = spec
                        if spec in METSP:
                            ICCpenalty[spec]['mean'][self.met] = float(val)
                            ICCpenalty[spec]['sigma'][self.met] = float(sig)
                        else:
                            ICCpenalty[spec]['mean'] = float(val)
                            ICCpenalty[spec]['sigma'] = float(sig)
                        print spec, '->', val
                    # add to global dict
                    self.penfix[params[key][i]] = key # will be empty if all are none

        # to accomodate Bi now
        ulimicc = '_ulim' + '-'.join(sp + '_' + str(ICCpenalty[sp]['mean']) for sp in params['ulim']) if params['ulim'] != ['none'] else ''
        penicc = '_pen' + '-'.join(sp if ((sp in METSP) or (sp not in ICCpenalty)) else sp + '_' + str(ICCpenalty[sp]['mean']) for sp in params['penalty']) if params['penalty'] != ['none'] else ''
        fixicc = '_fixed' + '-'.join(sp + '_' + str(ICCpenalty[sp]['mean'][self.met]) if sp in METSP else sp + '_' + str(ICCpenalty[sp]['mean']) for sp in params['fixed']) if params['fixed'] != ['none'] else ''
#        fixicc = '_fixed' + '-'.join(sp if ((sp in METSP) or (sp not in ICCpenalty)) else sp + '_' + str(ICCpenalty[sp]['mean']) for sp in params['fixed']) if params['fixed'] != ['none'] else ''
#        fixicc = '_fixed' + '-'.join(sp + '_' + str(ICCpenalty[sp]['mean']) for sp in params['fixed']) if params['fixed'] != ['none'] else ''
#        fixicc = '_fixed' + '-'.join(sp.replace(':','_') for sp in params['fixed']) if params['fixed'] != ['none'] else ''
#        ulimicc = '_ulim' + '-'.join(sp.replace(':', '_') for sp in params['ulim']) if params['ulim'] != ['none'] else ''
        # penalty, fixed and ulim name parts for icc and log file before we extract values
#        penicc = '' if params['penalty'] == ['none'] else '_penalty' + '-'.join(sp.replace(':','_') for sp in params['penalty'])

        # pen, fix and ulim separately: for names, and for pileup which is in the cfg
        self.penalty = params['penalty'] # to be constrained (list)
        self.fixed = params['fixed'] # to be fixed (list)
        self.ulim = params['ulim'] # to set upper limit (list)

        self.shift = params['shift']
        dct = {}
        if self.shift != ['none']:
            for sh in self.shift:
                if ':' in sh:
                    sp,val = sh.split(':')
                    dct[sp] = val
                    print sp, 'shift ->', dct[sp]
                else:
                    dct[sh] = 'free'
                    print sh, 'shift ->', dct[sh]
        self.shift = dct
    
        # dictionary {species: value} or 'none'
        # special features: c11mean and c11shift
#        self.scan = params['scan'] 
#        self.scansp = 'none'
#        if not self.scan == 'none':
#            self.scansp = self.scan.keys()[0]
#            # ignore c11mean and c11shift
#            if not 'c11' in self.scansp:
#                self.penfix[self.scansp] = 'fixed'
#            if self.scansp == 'c11shift':
#                self.shift['C11'] = self.scan['c11shift']
#                self.c11shift = self.scan['c11shift']



        self.save = params['save']
        self.outfolder = params['outfolder']

      
        ## parts for cfg and log filenames
        eminname = '-emin' + self.emin
        emaxname = '-emax' + self.emax
        rdminname = '-rdmin' + self.rdmin
        rdmaxname = '-rdmax' + self.rdmax
        rdbinname = '-rdbin' + self.rdbin
        psminname = '-psmin' + self.psmin
        psmaxname = '-psmax' + self.psmax
#        c11name = '' if self.pdfs == 'ana' or 'C11' in self.shift else '-c11shift' + self.c11shift

        ## fitoptions filename
        # pileup penalty changes cfg
        pencfg = '-pileup' if 'pileup' in self.penalty else ''
        if 'pp-pep' in self.penalty: pencfg += '_pp-pep-' + self.met 
        # shift
        shiftcfg = '' if self.shift == {} else '-shift' + '_'.join(sh + '-' + self.shift[sh] for sh in self.shift)
        # scan of c11shift
#        scancfg = '_scan'  + self.scansp + str(self.scan[self.scansp]) if self.scansp == 'c11shift' else ''
        self.cfgname = 'fitoptions/fitoptions_' + self.arch + '-' + self.fittype + '-' + self.fit + '-' + self.inputs + self.tfc + '-' + self.pdfs.split('/')[-1] + '-' + self.var + eminname + emaxname + rdminname + rdmaxname + rdbinname + psminname + psmaxname + pencfg + shiftcfg + '.cfg' # e.g. fitoptions_mv-all-pdfs_TAUP2017-nhits.cfg

        ## species list filename
        # in case penalty depends on metallicity
        penmet = '-' + self.met if self.met != 'none' else '' 
#        scanicc = '' if self.scansp in ['none', 'c11shift'] else '_scan'  + self.scansp + str(self.scan[self.scansp])
        self.iccname = 'species_list/species-fit-' + self.arch + '-' + self.fittype + '-' + self.fit + eminname + emaxname + penicc + penmet + fixicc + ulimicc + '.icc'
        # log file name 
        self.outfile = 'fit-' + self.arch + '-' + self.fittype + '-' + self.fit + '-' + self.pdfs.split('/')[-1] + '-' + 'Period' + self.inputs + self.tfc + '-' + self.var + eminname + emaxname + rdminname + rdmaxname + rdbinname + psminname + psmaxname + penicc + fixicc + 'met_' + self.met + shiftcfg + ulimicc
        
    
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
        # previous way of fitting: apply_mask = false in the cfg, and using masked PDFs
        # current way: apply_mask = true in cfg, and using unmasked PDFs
        taup = False
        for word in ['TAUP', 'v1.0.0', 'v100']: taup = taup or (word in self.pdfs)
        if taup:
            # change apply mask to false because there are no unmasked TAUP PDFs
            cfglines[7] = 'applying mask = false'
            mcname = 'MCspectra_pp_FVpep_{0}_emin1_masked.root'.format(self.inputs)
        else:
        # e.g. MCspectra_FVpep_Period_Phase2_unmasked.root
            mcname = 'MCspectra_FVpep_Period_{0}_unmasked.root'.format(self.inputs)

        # line 68: MC PDFs
        if self.pdfs == 'ana':
            cfglines[67] = comment(cfglines[67])
        else:
            cfglines[67] = 'montecarlo_spectra_file = ' + self.pdfs + '/' + mcname

        # line 80: remaining Pb214
        # Pb214 not implemented in the GPU fitter; apparently also not in CPU?..
#        if self.arch == 'gpu':
        cfglines[79] = "use_remaining_pb214 = false" # default is true

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
        cfglines[97] = 'multivariate_rdist_fit_max = ' + self.rdmax # cannot be larger than emax -> decided to synch
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
            cfglines[126] = 'pileup_penalty_mean = {0}'.format(PUPPEN[self.inputs][0])
            cfglines[127] = 'pileup_penalty_sigma = {0}'.format(PUPPEN[self.inputs][1])
#        else:
#            # no pileup at all (also in species list)
#            for l in range(123,128): cfglines[l] = '#' + cfglines[l]                                     

        for sh in ['Po210','C11']:
            # if it's in the shift, it's either free of fixed
            if sh in self.shift:
                if self.shift[sh] == 'free':
                    cfglines.append('freeMCshift' + sh + ' = true')
                else:
                    cfglines.append('freeMCshift{0} = true'.format(sh))
                    cfglines.append('freeMCshift{0}step = 0'.format(sh))
                    cfglines.append('freeMCshift{0}min = {1}'.format(sh, self.shift[sh]))
                    cfglines.append('freeMCshift{0}max = {1}'.format(sh, self.shift[sh]))
            # if not, it's fixed to zero
            else:
                cfglines.append('freeMCshift{0} = false'.format(sh))
                cfglines.append('freeMCshift{0}step = 0'.format(sh))
                    

        if self.pdfs == 'ana':
            cfglines.append('fiducial_mass = 0')
            cfglines.append('force_dn_after_mask = false')
            cfglines.append('fcher_free = false')

            ## comment out MC pileup stuff
            for i in range(118,132): cfglines[i] = comment(cfglines[i])


        if self.fittype == 'cno':
            # comment out pileup (lines 124 - 128) and C14 stuff (119-122)
            for l in range(118,128): cfglines[l] = '#' + cfglines[l]                                     
        
        # line 103: dark noise: only in analytical fit, not MC fit
        if self.pdfs == 'ana':
            cfglines[102] = 'dark_noise_window = win' + self.var[-1]

        # line 112 pp/pep constraint
        if 'pp-pep' in self.penalty:
            cfglines.append('apply_pp/pep_constrain = true')
            cfglines.append('mean(Rpp/Rpep) = {0}'.format(PPPEP[self.met][0]))
            cfglines.append('sigma(Rpp/Rpep) = {0}'.format(PPPEP[self.met][1]))


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
        
        # line 15: pileup, comment out if it's not in penalty (means not using at all) 
#        if not 'pileup' in self.penalty:
        # line 15: comment out pileup if doing Ana fit (only convo available right now)
        if self.pdfs == 'ana':
            icclines[14] = comment(icclines[14], '//')

        # line 21, 22: Po210 guess
        guess = 60 if 'Phase3' in self.inputs else 300
        icclines[20] = '{{ "Po210",        -1,   kOrange, kSolid,  2,    {0}.,   "free",  0.01,3000. }},\n'.format(guess)
        icclines[21] = '{{ "Po210_2",        -1,   kOrange, kSolid,  2,    {0}.,   "free",  0.01,3000. }},\n'.format(guess)

        # line 25: C11 mean
#        if self.scansp == 'c11mean':
#            icclines[24] = '{{ "C11",          -1,   kMagenta,kSolid,  2,    {0},    "free",  0.,  100. }},\n'.format(float(self.scan['c11mean']))

        # line 31: Pb214
#        if self.arch == 'gpu':
        # comment out because not implemented in the GPU fitter; apparently also not in CPU fitter?
        icclines[30] = comment(icclines[30], '//')

        # CNO configuration species
        if self.fittype == 'cno':
            # C14 (l 13), pileup (l 15) and pp (l 16) are out 
            for i in [12, 14, 15]:
                icclines[i] = comment(icclines[i], '//')

        # TFC fit: only C11            
        if self.fittype == 'tfc':
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
            # these penalties or fixed are in cfg not icc
            if pensp in ['pileup', 'c11shift', 'pp-pep']: continue

            # species to scan, if given
#            iccsp = pensp
#            if pensp in self.scan:
#                mean = self.scan[pensp] 
#                sig = 0
#            else:
            mean = ICCpenalty[pensp]['mean']   
            sig = ICCpenalty[pensp]['sigma']
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
        if ('v1.0.0' in self.input_path) or ('v100' in self.input_path):
            # e.g. pepFV_TFCMainz/PeriodAll_FVpep_TFCMZ.root
            inputfile = 'pepFV_TFC{0}/Period{1}_FVpep_TFC{2}.root'.format({'MZ': 'Mainz', 'MI': 'Milano'}[self.tfc], self.inputs, self.tfc)
        else:
            # e.g. Period2012_FVpep_TFCMI_c19.root
            inputfile = 'Period{0}_FVpep_TFC{1}_c19.root'.format(self.inputs, self.tfc)

        inputfile = self.input_path + '/' + inputfile

        ## fit file (for a single fit)
        fitname = self.outfolder + '/fit_' + self.outfile + '.sh'
        fitfile = open(fitname, 'w')
        extra = {'mv': '_0', 'tag': '_1', 'ene': ''}
        print >> fitfile, '#!/bin/bash'
        print >> fitfile, './borexino', inputfile,\
            'pp/final_' + self.var + '_pp' + extra[self.fit],\
            self.cfgname, self.iccname, ' | tee', self.outfolder + '/' + self.outfile + '.log'
        fitfile.close()
        make_executable(fitname)
        print 'Fit file:', fitname

        ## CNAF: submission file with condor, Jureca: file with sbatch commands
        # one file to rule them all, and launch all the submissions 
        outname = self.outfolder + '_submission.sh' 
        # to print bin bash or not (?)
        out = open(outname, 'a') 

            
        ## CNAF submission
        if self.arch == 'cpu':
            ## old bsub format
#            print >> out, 'bsub -q borexino_physics',\
#                '-e', self.outfolder + '/' + self.outfile + '.err',\
#                '-o', self.outfolder + '/' + self.outfile + '.log',\
#                './spectralfit', inputfile, 'pp/final_' + self.var + '_pp' + extra[self.fit],\
#                self.cfgname, self.iccname

            ## file with the fit(s)
            if nfile == -1:
                fitsubname = self.outfolder + '/fitsub_' + self.outfile + '.sh'
            else:
                fitsubname = self.outfolder + '/fitsub_' + str(nfile) + '.sh'

            # if file doesn't exist, create
            if not os.path.exists(fitsubname):
                print 'creating fitsub', fitsubname
                fitsub = open(fitsubname, 'w')
                print >> fitsub, '#!/bin/bash'
                print >> fitsub, 'source /storage/gpfs_data/borexino/users/dingbx/Software/root_v6.18.04.Linux-centos7-x86_64-gcc4.8/bin/thisroot.sh'
                print >> fitsub, 'source /storage/gpfs_data/borexino/users/dingbx/bx-GooStats-v6.3.2/setup.sh'
                # our directory
                curdir = os.getcwd()
                print >> fitsub, 'cd', curdir
                fitsub.close()
                make_executable(fitsubname)

            # add our fit    
            fitsub = open(fitsubname, 'a')
            print >> fitsub, './' + fitname
            fitsub.close()
            print 'Fit sub file:', fitsubname

            ## condor file that submits the file with the fit(s)
            condorname = '.'.join(fitsubname.split('.')[:-1]) + '.sub'
            # if file doesn't exist, create
            if not os.path.exists(condorname):
                clines = open('BxFits/templates/condor_template.sub').readlines()
                # executable
                clines[1] = 'executable = ' + fitsubname + '\n'
                # out and err files
                corename = os.path.splitext(fitsubname)[0]
                clines[2] = 'output = ' + corename + '.out\n'
                clines[3] = 'error = ' + corename  + '.err\n'
                condor = open(condorname,'w')
                condor.writelines(clines)
                make_executable(condorname)

                # add to top submission file
                print >> out, 'condor_submit -spool -name sn-01.cr.cnaf.infn.it ' + condorname
                print >> out, 'sleep 60'



        # Jureca submission
        elif self.arch == 'gpu':

            ## sbatch file        
            # our file
            if nfile == -1:
                sbatchname = self.outfolder + '/sbatch_' + self.outfile + '.sh'
            else:
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
 #             'mean': 12.5,  # Phase3Large
#              'sigma': 1.1,
              'mean': 10.8, # Phase3Strict
              'sigma': 1.3 # 1.6
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

# penalty on pp/pep ratio for Phase-II CNO analysis
PPPEP = {'hm': [47.76, 0.84], 'lm': [47.5, 0.8]}
METSP.append('pp-pep')

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
