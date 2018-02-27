#!/bin/sh
if (($# < 2)); then
    echo "Usage: $0 <--type output.csv inputfile1.csv inputfile2.csv ...>"
    exit 1
fi

> $2
> total_input.csv

COUNT=0
for var in "$@"
do
	if (( $COUNT > 1))
	then
		echo "$var"
		cat $var >> total_input.csv
	fi
	COUNT=$((COUNT+1))
done

case $1 in
	"--beacon_phy" )
		echo "beacon_phy"
		cut -d , -f 4,6 total_input.csv > beacon_temp.csv
	   	sort -u beacon_temp.csv -o $2;;
	"--beacon_phychan" )
		echo "beacon_phychan"
		cut -d , -f 1,2,6 total_input.csv > beacon_temp.csv
		sort -u beacon_temp.csv -o $2;;
	"--channel" )
	    echo "channel"
	    cut -d , -f 2,3 total_input.csv > $2;;
esac

rm beacon_temp.csv