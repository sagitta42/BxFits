# MCfits
Instructions on how to perform MC fits on CNAF

## Set up fitter

1) ``` cvs co offline/spectral-fitter ```
2) Change the following lines in ```lib/fitter.cc```
```
2106   arglist[0] = 50000; //Max number of calls
2107   arglist[1] = 0.001; // Tolerance (see MINUIT manual)
```

3) make

## Fitter files

1) Species lists: ```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/bin/*.icc```
2) PDFs: ```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/pdfs_TAUP2017```
3) Input files: ```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/PeriodAll_FVpep_TFCMZ.root```
4) Fitoptions: included in this repo. Change the line with
```montecarlo_spectra_file = MCspectra_pp_FVpep_*_emin1_masked.root```
to
``` montecarlo_spectra_file = pdfs_TAUP2017/MCspectra_pp_FVpep_*_emin1_masked.root```
where * = 2012, 2013 etc.

## How to run

```./spectralfit pathfolder/input_file.root pp/final_nhits_pp_0 pathfolder1/fitoptions.cfg pathfolder2/species_list.icc```
