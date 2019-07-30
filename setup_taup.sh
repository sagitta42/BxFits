## INPUTS
ln -s MCfits/input_files .
## FITOPTIONS
# PDFs will be referenced locally in fitoptions
ln -s MCfits/pdfs_TAUP2017 .
ln -s MCfits/pdfs_years_simone .
## SPECIES LISTS FOR MV
cp -i MCfits/bin/* bin/.
## generator
cp MCfits/generator.py .
cp MCfits/creator.py .
ln -s MCfits/templates .
