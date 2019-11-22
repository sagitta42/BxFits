# MCfits

Generating and analysing custom MC fits

Part 0: Set up this machinery

Part 1: Generate submission

Part 2: Collect fit results

Part 3: Create comparison tables

## Part 0: Set up this machinery

Go to your fit folder e.g.

```console
cd /p/project/cjikp20/jikp2008/2019-11-11-cno/bx-GooStats-release/bx-GooStats
```

Check out this repo

```console
git clone https://github.com/sagitta42/MCfits.git
```

Link the generator files to the fit directory

```console
ln -s MCfits/creator.py .
ln -s MCfits/generator.py .
```

Note: linking is good for when there is an update. Then you can simply do

```console
git pull
```

In the ```MCfits/``` folder, and it will be updated, unlike if you make a copy.



## Part 1: Generate submission

In your fit folder, do

```console
python generator.py
```

And you will see the available options for the fit generation like fit type, TFC, variable etc.




## Part 2: Collect fit results

Usage

```console
python collect_species.py foldername
```

Will create a file ```foldername_species.out``` with a table of results collected from the log files in the given folder

On top of the file (line 8), one can select the species one wants to collect

```python
COLUMNS = ['nu(Be7)', 'nu(pep)', 'Bi210', 'C11', 'Kr85', 'Po210',\
    'Ext_Bi214', 'Ext_K40', 'Ext_Tl208', 'Po210shift', 'C11shift', 'chi2/ndof',\
    'C11_2', 'Po210_2']
```

If you don't need all of them, you can select only specific ones. 

At line 23, you can define what will be your "special column". The value of this column is not read from the log file, but from the name of the log file. On line 69 is the command that does this reading. For example,

```python
special_col = 'Period'
# data_Phase3_EO_22C11_TAUP_MI_Nov.log
spec = filename.split('_')[1] # Phase3
```

means that the name of the column will be 'Period', and the way the value for that column is read is "split the filename by underscore and take the second part".

Example output:


```console
python collect_species.py Ext_K40free
   Period nu(Be7) nu(pep) Bi210    C11  Kr85   Po210 Ext_Bi214 Ext_K40  ... Ext_Tl208Error Kr85Error Po210Error Po210_2Error Po210shiftError nu(Be7)Error nu(pep)Error   ExpSub   ExpTag
0  Phase2    49.1     1.4   8.8  1.796   4.2  249.59      1.82    0.94  ...           0.16       2.2       0.78          1.0             NaN          1.2          1.4  53621.1  36107.7
1  Phase2    47.3     0.7  16.3   1.99  10.0  244.66      1.87    1.33  ...           0.15       2.4       0.77         1.00             NaN          1.3          1.7  53621.1  36107.7
2  Phase2    47.7     3.2  18.4   1.90   6.9  265.94      1.93    1.89  ...           0.16       2.7       0.75          1.0             NaN          1.2          2.3  57770.6  31958.2
4  Phase2    49.1     1.4   8.7  1.798   3.9  249.09      1.82    0.95  ...           0.16       2.1       0.78          1.0             NaN          1.2          1.3  53621.1  36107.7
5  Phase2    47.3     1.9  12.8  1.819   7.6  248.35      1.82    1.06  ...           0.16       1.9       0.75         0.99             NaN          1.1          1.4  53621.1  36107.7
3  Phase3    45.0    2.95  18.7   1.79  12.7   50.83      4.23    0.00  ...           0.27       2.1       0.58         0.67             NaN          1.5         0.47  39584.1  24980.7

[6 rows x 30 columns]
--> Ext_K40free_species.out
```

If the species is not present in the log file (for example, here it's Po210 shift), a NaN value will be assigned. That means, in the table file it will be an empty space. If you open this file with a Spreadsheet program, it will be an empty cell. The default separator is space. If you want, you can change it to comma in the code.


## Part 3: Create comparison tables

Use

```console
python table_comparison.py foldername
```

It will create a file ```foldername_comparison.csv``` that you can open with Spreadsheet. The results from each log file in the folder will be put side by side for comparison


Example output:

```console
$ python table_comparison.py Ext_K40free

~~~ fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-penalty-met_hm.log

           fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-penalty-met_hm         
                                                                               Mean    Error
Period                                                 Phase2                            NaN
nu(Be7)                                                  49.1                            1.2
nu(pep)                                                   1.4                            1.4
Bi210                                                     8.8                            8.3
C11                                                     1.796                          0.097
Kr85                                                      4.2                            2.2
Po210                                                  249.59                           0.78
Ext_Bi214                                                1.82                            0.3
Ext_K40                                                  0.94                           0.62
Ext_Tl208                                                3.41                           0.16
Po210shift                                                NaN                            NaN
C11shift                                                  NaN                            NaN
chi2/ndof                                              1.2449                            NaN
C11_2                                                   64.29                           0.59
Po210_2                                                 306.6                              1
C11avg                                                26.9442                        1.47608
Po210avg                                              272.531                        1.23105

~~~ fit-cno-mv-pdfs_new-PeriodPhase2MI-nhits-emin140_CNO-penalty-met_hm.log

...

~~~ fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MZ-nhits-emin92_CNO-pileup-penalty-met_hm.log

...

~~~ fit-cno-mv-pdfs_new-PeriodPhase3MI-nhits-emin140_CNO-penalty-met_hm.log

...

~~~ fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-pileup-penalty-met_hm.log

...         

~~~ fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin92_CNO-pileup-penalty-met_hm.log

...

----------------
-> Ext_K40free_comparison.csv
