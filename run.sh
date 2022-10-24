#!/bin/bash
if [ $# -gt 1 ]
then
	printf "Invalid input.\nUsage:\n\t--> ./run.sh\nor, in order to solve a specific instance\n\t--> /run.sh path/to/instace.txt\n"
	exit -1
fi

if [[ $# -eq 1 ]] ; then
	python3 internals/solver.py $1
	exit 0
fi
python3 internals/solver.py


