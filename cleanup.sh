#!/bin/sh
#
# This is cealnup script for cleaning make, tmp and other build files.
#
# Plz. Use it before move project to hosting place.

names="*~ *.pyc .*.swp"

for name in $names
do
    echo "Removing files: ${name}"
    find ./ -name ${name} -type f -delete;
done

echo "Done";
