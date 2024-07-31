import csv
import json

# Increase the field size limit
csv.field_size_limit(1000000000)  # Adjust this value as needed

def csv_to_json_streaming(csv_file_path, json_file_path, chunk_size=1000):
    with open(csv_file_path, 'r') as csv_file, open(json_file_path, 'w') as json_file:
        csv_reader = csv.DictReader(csv_file)
        json_file.write('[\n')
        for i, row in enumerate(csv_reader):
            if i > 0:
                json_file.write(',\n')
            json.dump(row, json_file)
            if i % chunk_size == 0:
                json_file.flush()
        json_file.write('\n]')

# Usage
csv_to_json_streaming('F:\\DeepThought\\tests\\ESS Logs 05072024.csv', 'F:\\DeepThought\\tests\\ESS Logs 05072024.json')

