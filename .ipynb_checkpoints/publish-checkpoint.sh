jupyter nbconvert README.ipynb --to markdown --TagRemovePreprocessor.remove_cell_tags='{"remove_cell"}'
sed -i 's\README_files\https://raw.githubusercontent.com/marnec/mpl_flow/master/README_files\g' README.md 
rm -r dist/
python3 setup.py sdist bdist_wheel
twine upload dist/* -u marnec -p PumaYPuma0
git add --all
