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

means that the name of the column will be 'Period', and the way the value for that column is read is "split the filename by underscore and take the second part". See example output in the bottom in the Examples section.

Using this table it's very easy to make plots with python

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('examples/fits2012-2019_species.out', sep = ' ')
df.plot(x = 'Period', y = 'Bi210', yerr = 'Bi210Error')
plt.savefig('examples/bi210rate.png')
```

(```plot_example.py```)





## Part 3: Create comparison tables

Use

```console
python table_comparison.py foldername
```

It will create a file ```foldername_comparison.csv``` that you can open with Spreadsheet. The results from each log file in the folder will be put side by side for comparison


If the species is not present in the log file (for example, here it's Po210 shift), a NaN value will be assigned. That means, in the table file it will be an empty space. If you open this file with a Spreadsheet program, it will be an empty cell. The default separator is space. If you want, you can change it to comma in the code.



## Examples to try out 

### Collet species

To create a table


```console
$ python collect_species.py examples/fits2012-2019
  Period  nu(Be7)  nu(pep)  Bi210   C11  Kr85   Po210  Ext_Bi214  ...  Kr85Error  Po210Error  Po210_2Error Po210shiftError  nu(Be7)Error  nu(pep)Error    ExpSub    ExpTag
4   2012     49.2     3.37   23.4  1.78  11.1  717.50       1.61  ...        4.3        2.70           2.9           0.041           2.8          0.72  10931.80  10074.20
6   2013     50.4     4.93   14.6  1.51   9.3  160.10       2.67  ...        4.0        1.50           1.8           0.110           2.9          0.76  10737.80   6624.08
0   2014     49.4     2.82   14.0  1.25   7.7  105.10       3.38  ...        3.4        1.10           1.4           0.130           2.5          0.60  14021.80   8045.30
3   2015     52.4     3.33    9.5  1.59   8.3   80.30       1.86  ...        3.5        1.00           1.3           0.170           2.6          0.65  12898.70   8145.44
5   2016     45.3     3.14    8.9  1.53  17.6   55.00       3.15  ...        4.1        1.10           1.3           0.230           2.9          0.73  10837.60   6266.81
1   2017     52.7     3.92    5.7  1.26   8.4   54.00       4.69  ...        3.8        1.00           1.2           0.220           2.7          0.66  13139.10   8261.60
2   2018     49.5     3.62    9.9  1.51   7.7   49.03       5.17  ...        3.6        0.98           1.1           0.240           2.6          0.66  14190.00   9299.89
7   2019     47.0     4.02    7.8  1.02  15.7   49.20       5.40  ...        5.5        1.60           1.8           0.350           4.1          0.95   5851.96   3776.53

[8 rows x 30 columns]
--> examples/fits2012-2019_species.out
```

To make a plot

```console
python plot_example.py
```

Will create ```examples/bi210rate.png```


### Table comparison

Create a csv with comparison

```console
python table_comparison.py examples/Ext_K40free

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
```

Later you can open it with Spreadsheet and make a table like in the example ```examples/Ext_K40free_comparison.pdf```


### Extra info

"Zara PDFs" (up to May 2019, used for Davide GM results): ``/p/project/cjikp20/jikp2007/PDFs_to_test''

"Giulio PDFs" (up to Dec 2019): ``/p/project/cjikp20/jikp2015/MC_fit_bx_nusol/root''                                                        
