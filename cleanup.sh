#!/bin/sh
#
# This is cealnup script for cleaning make, tmp and other build files.
#
# Run it before uploading to hosting.

names="'*~' '*.pyc' '.*.swp'"

for name in $names
do
    echo "Removing files: ${name}"
    find ./ -name ${name} -type f -delete
done

echo "Done";
