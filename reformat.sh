#! /bin/bash

if [ $# -eq 1 ]
then
    isort $1
    python3 -m black $1
    pylint $1
fi

if [ $# -eq 0 ]
then
    isort .
    python3 -m black .
fi