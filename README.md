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

### Species lists:

**Multivariate** fit:
```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/bin/*.icc```:

HAVE to be in bin/ folder in spectralfit, read automatically by the fitter:

```
multivariate_ps_species_list.icc
multivariate_rdist_species_list.icc
```

Input by hand when running the fitter (see the "How to run" section)

``` species_list_taup.icc --> input by hand ```

**Energy only** fit:

```
species_list_ene.icc --> pep free, CNO penalty
species_list_pepcno_fixed.icc --> pep & CNO fixed
```

### PDFs
```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/pdfs_TAUP2017```

### Input files
```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/PeriodAll_FVpep_TFCMZ.root```

### Fitoptions

**Energy only** fit:
Folder ```fitoptions``` included in this repo. Change the line that says:
```montecarlo_spectra_file = MCspectra_pp_FVpep_*_emin1_masked.root```
to:
``` montecarlo_spectra_file = pdfs_TAUP2017/MCspectra_pp_FVpep_*_emin1_masked.root```
where * = 2012, 2013 etc.

**MV** fit:

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/fitoptions_mv_201*.cfg```

## How to run

Energy only fit:

```./spectralfit pathfolder/input_file.root pp/final_nhits_pp pathfolder1/fitoptions.cfg pathfolder2/species_list.icc```

MV fit:

```./spectralfit pathfolder/input_file.root pp/final_nhits_pp_0 pathfolder1/fitoptions.cfg pathfolder2/species_list.icc```

