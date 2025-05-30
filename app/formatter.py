import json
import csv

def to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def to_csv(data, filename):
    keys = data.keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerow(data)