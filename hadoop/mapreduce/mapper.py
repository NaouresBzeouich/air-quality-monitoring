#!/usr/bin/env python3
import sys
import csv
from datetime import datetime

for line in sys.stdin:
    if line.startswith("location_id") or not line.strip():
        continue
    row = list(csv.reader([line]))[0]
    try:
        date = row[3][:10]  # Get YYYY-MM-DD
        parameter = row[6]
        value = float(row[8])
        if value != -999.0:  # Clean bad values
            print(f"{date}\t{parameter}\t{value}")
    except:
        continue
