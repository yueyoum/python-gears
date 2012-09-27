#!/bin/bash

# run this script to deploy the latest code

location=/data/project
folder_name=python_gears

cd "$location"

# download code from bitbucket
wget -q https://bitbucket.org/my_sting/python-gears/get/tip.tar.bz2

# unpack
tar jxf tip.tar.bz2
source_folder=`ls | grep my_sting-python-gears`

# copy
cp -r $source_folder/* $folder_name

# clear
rm tip.tar.bz2
rm -rf $source_folder

echo
echo "Don't forget to modify:"
echo "gmail password in settings_base.py"
echo "mysql root password in settings_prod.py"

exit 0