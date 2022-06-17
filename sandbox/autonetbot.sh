#!/bin/bash
START=1
END=$(("$4"))
for ((i=START; i<=END; i++))
do
    { echo "$1"; echo "$2"; echo "$3"; } | python3 netbot.py 
done
