#!/bin/bash -x

unset ESTATES_PRICE_MAX
unset ESTATES_MIN_AREA
./estates.py &> all.txt
mv stats.dat collected_stats.dat
export ESTATES_MIN_AREA=50
./estates.py &> all-above-50m2.txt
export ESTATES_PRICE_MAX=4000000
./estates.py &> above-50m2-up-to-4M.txt


