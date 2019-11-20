# MCfits
Instructions on how to perform MC fits on CNAF

## Set up fitter

### CPU fitter

1) ``` cvs co offline/spectral-fitter ```
2) Change the following lines in ```lib/fitter.cc```
```
2134   arglist[0] = 50000; //Max number of calls
2135   arglist[1] = 0.001; // Tolerance (see MINUIT manual)
```

3)
```
cp MCfits/setup_taup.sh .
chmod +x setup_taup.sh
./setup_taup.sh
```
(will create local paths to PDFs, inputs, and set up the generator)

    
4) ```make```

Important to do ```make``` after ```./setup_taup.sh```, so that the fitter gets recompiled with the new MV species lists

(or do ```make clean``` and ```make``` just to be safe)

### GPU fitter

1) Follow the instructions in https://github.com/DingXuefeng/bx-GooStats

2) In ```src//MultiVariateInputManager.cc```:

In function ```MultiVariateInputManager::load_classifications_User()``` and ```MultiVariateInputManager::load_classifications_Rdist()```, add the line:

```multivariate_species_list[ "MCpup" ] =      0;```




## Generate submission

Example: ```python generator.py fit=mv CNO=fixed,lm,hm var=nhits,npmts```

Loop over given options and create a CNAF submission file for each combination of the fit. Creates a folder for future output log files and a ```.sh``` file for ```nohup bxsubmitter```. Uses ```creator.py``` and folder ```templates/```


## Details on how the fitter is run

#### Energy only fit

```./spectralfit pathfolder/input_file.root```<sup>**[1]**</sup> ```pp/final_nhits_pp pathfolder1/fitoptions.cfg```<sup>**[2]**</sup> ```pathfolder2/species_list.icc```<sup>**[3]**</sup> 

#### MV fit

```./spectralfit pathfolder/input_file.root pp/final_nhits_pp_0 pathfolder1/fitoptions.cfg pathfolder2/species_list.icc```

Use the ```species_taup.icc``` species list


## Files for the fitter

### [1] Input files

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/PeriodAll_FVpep_TFCMZ.root```

Year by year:

``` /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/pepmz ```

### [2] Fitoptions

#### Energy only fit

Folder [fitoptions](fitoptions) included in this repo.

#### MV fit

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/fitoptions_mv_201*.cfg```

Change the line that says:

```montecarlo_spectra_file = MCspectra_pp_FVpep_*_emin1_masked.root```

to:

``` montecarlo_spectra_file = pdfs_TAUP2017/MCspectra_pp_FVpep_*_emin1_masked.root```

where * = 2012, 2013 etc. or whatever path to PDFs you are using (folder below)

#### PDFs referenced in the cfg files

TAUP: ```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/pdfs_TAUP2017```

new QE: ```/p/project/cjikp20/jikp2007/PDFs_to_test/```

### [3] Species lists:

#### Multivariate fit

Folder:

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/bin/```

Files that **HAVE** to be in ```bin/``` folder in spectralfit, read automatically by the fitter:

```
multivariate_ps_species_list.icc
multivariate_rdist_species_list.icc
```

Input when running the fitter (see the "How to run" section): ``` species_list_taup.icc```

#### Energy only fit

```
species_list_ene.icc --> pep free, CNO penalty
species_list_pepcno_fixed.icc --> pep & CNO fixed
```

## Compare results

Simone's results on MV for PeriodAll:

https://borex.lngs.infn.it/docdb/0000/000013/002/MC_final_results_Phase2_v2.pdf

Simone's results year by year (probably energy only): slide 49


[table](simone_results.png)

CNO has to be fixed to 5.0 and pep to 2.8



## Read outputs

File: ```collect_species.py``` (from CNO reader)

Creates a table from log files in a given folder collecting fit results on different years for given species. 

File: ```table_simone.py```

Make the table to have the same look as tables in Simone's slides: transpose current table (so that year is column and not row) and put the means and the errors in one column with +-


## Clean

Use

```console
./clean_mcfits.sh
```

to quickly remove fitoptions, species lists and results. Use carefully!
