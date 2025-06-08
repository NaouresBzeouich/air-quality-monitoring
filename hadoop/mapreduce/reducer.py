#!/usr/bin/env python3
import sys
from collections import defaultdict

# Structure: data[date][parameter] = list of values
data = defaultdict(lambda: defaultdict(list))

for line in sys.stdin:
    parts = line.strip().split("\t")
    if len(parts) != 3:
        continue
    date, parameter, value_str = parts
    try:
        value = float(value_str)
        data[date][parameter].append(value)
    except ValueError:
        continue  # Ignore bad float conversion

# Sort by date for readability
for date in sorted(data.keys()):
    daily_avg = 0
    count = 0
    print(f"Date: {date}")
    for param in sorted(data[date].keys()):
        values = data[date][param]
        if values:
            avg = sum(values) / len(values)
            print(f"  {param} AVG: {avg:.2f}")
            daily_avg += avg
            count += 1
    if count:
        print(f"  >>> Overall AVG: {daily_avg / count:.2f}\n")
