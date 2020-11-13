#!/usr/bin/env bash
# based on
# http://www.willmcginnis.com/2016/02/29/automating-documentation-workflow-with-sphinx-and-github-pages/
# Run this script in the root

# build the docs
cd sphinx
make clean
make html
cd ..

# commit and push
git add -A
git commit -m "documentation updated"
git push origin master

# switch to gh-pages branch and pull docs
git checkout gh-pages
rm -rf ./docs
rm -rf ./tutorial
rm -rf _*
touch .nojekyll
git checkout master docs/html

# move docs to root and delete docs
mv ./docs/html/* ./
rm -rf ./docs

# push updated gh-pages
git add -A
git commit -m "documentation updated"
git push origin gh-pages

# switch back to master
git checkout master