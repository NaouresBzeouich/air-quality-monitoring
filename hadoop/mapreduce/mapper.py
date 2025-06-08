#!/usr/bin/env python3
import sys
import csv

for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith("location_id"):  # Skip header/empty
        continue
    try:
        row = next(csv.reader([line]))
        if len(row) < 9:
            continue  # Skip malformed lines

        date = row[3][:10]  # Get YYYY-MM-DD
        parameter = row[6].strip().lower()
        value = float(row[8])
        
        if value != -999.0:
            print(f"{date}\t{parameter}\t{value}")
    except Exception as e:
        # Uncomment for debugging if needed:
        # print(f"ERROR: {e} on line: {line}", file=sys.stderr)
        continue
