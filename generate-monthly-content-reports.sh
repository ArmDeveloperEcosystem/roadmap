#!/bin/bash
# Script to generate monthly content count reports from 06-01-2023 to 05-01-2025

START_YEAR=2023
START_MONTH=6
END_YEAR=2025
END_MONTH=5

YEAR=$START_YEAR
MONTH=$START_MONTH

while [ $YEAR -lt $END_YEAR ] || { [ $YEAR -eq $END_YEAR ] && [ $MONTH -le $END_MONTH ]; }; do
    # Format month and date as MM-01-YYYY
    DATE=$(printf "%02d-01-%d" $MONTH $YEAR)
    echo "Generating report for $DATE..."
    bash count-content.sh $DATE
    # Increment month/year
    if [ $MONTH -eq 12 ]; then
        MONTH=1
        YEAR=$((YEAR+1))
    else
        MONTH=$((MONTH+1))
    fi
done
