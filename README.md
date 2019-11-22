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


