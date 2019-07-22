# MCfits
Instructions on how to perform MC fits on CNAF

Example for MV fit for 2012 in the bottom

## Set up fitter

1) ``` cvs co offline/spectral-fitter ```
2) Change the following lines in ```lib/fitter.cc```
```
2134   arglist[0] = 50000; //Max number of calls
2135   arglist[1] = 0.001; // Tolerance (see MINUIT manual)
```

3) make

## How to run

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

Folder ```fitoptions``` included in this repo. Change the line that says:

```montecarlo_spectra_file = MCspectra_pp_FVpep_*_emin1_masked.root```

to:

``` montecarlo_spectra_file = pdfs_TAUP2017/MCspectra_pp_FVpep_*_emin1_masked.root```

where * = 2012, 2013 etc.

#### MV fit

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/fitoptions_mv_201*.cfg```

#### PDFs referenced in the cfg files

```/storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/pdfs_TAUP2017```

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


## Example

1. Fitoptions files

```
mkdir fitoptions_mv
cp /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/fitoptions_mv_201*.cfg fitoptions_mv/.
```

2. PDFs

``` cp -r /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/pdfs_TAUP2017 .``` (13M)

3. Edit ```fitoptions_mv/fitoptions_mv_2012.cfg```:

Line 68:

```  montecarlo_spectra_file = pdfs_TAUP2017/MCspectra_pp_FVpep_2012_emin1_masked.root ```

4. Species list

```
cp /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/bin/multivariate* bin/.
mkdir species_mv
cp /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_taup/fitter_TAUP/bin/species_list_taup.icc species_mv/.
```

5. Run command

```./spectralfit /storage/gpfs_data/borexino/users/penek/Simone_MC_31_Jan_2019/mc_fitter_cvs/offline/spectral-fitter/pepmz/Period2012_FVpep_TFCMZ.root pp/final_nhits_pp fitoptions_mv/fitoptions_mv_2012.cfg species_mv/species_list_taup.icc```

## Compare results

Simone's results:
https://borex.lngs.infn.it/docdb/0000/000013/002/MC_final_results_Phase2_v2.pdf

Slide 49

