cd ..
python setup.py develop
cd sphinx
sphinx-apidoc -f -o source/ ../nutsflow/
make.bat html