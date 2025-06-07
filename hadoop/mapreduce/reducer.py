#!/usr/bin/env python3
import sys
from collections import defaultdict

data = defaultdict(lambda: defaultdict(list))

for line in sys.stdin:
    parts = line.strip().split("\t")
    if len(parts) != 3:
        continue
    date, parameter, value = parts[0], parts[1], float(parts[2])
    data[date][parameter].append(value)

for date in data:
    daily_avg = 0
    count = 0
    print(f"Date: {date}")
    for param in data[date]:
        avg = sum(data[date][param]) / len(data[date][param])
        print(f"  {param} AVG: {avg:.2f}")
        daily_avg += avg
        count += 1
    if count:
        print(f"  >>> Overall AVG: {daily_avg/count:.2f}\n")
