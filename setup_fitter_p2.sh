# setup environment
source /p/project/cjikp20/jikp2013/software/setup.sh
source setup.sh

# compile googletest, GooFit
printf "~~~\nCompiling googletest and GooFit\n~~~\n"
bash compile.sh

# compile bx-GooStats
printf "~~~\nCompiling bx-GooStats\n~~~\n"
cd bx-GooStats
make

# Run your first fit
printf "~~~\nRunning first fit\n~~~\n"
./fitdata.sh

# After you finished installation, you can validation it. You should not see any failed test
printf "~~~\nValidating\n~~~\n"
./NLLcheck.sh
