#!/usr/bin/env python3
import os
import glob
import csv
from collections import defaultdict

def group_files_by_location_year():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, 'extracted-data')
    target_dir = os.path.join(base_dir, 'grouped-data')
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Dictionary to store file handles for writing
    output_files = {}
    csv_writers = {}
    
    # Get all CSV files from source directory
    csv_files = glob.glob(os.path.join(source_dir, 'location-*-*.csv'))
    
    # Process each file
    for file_path in csv_files:
        try:
            file_name = os.path.basename(file_path)
            # Parse location and date from filename (location-X-YYYYMMDD.csv)
            parts = file_name.split('-')
            if len(parts) != 3:
                print(f"Skipping {file_name}: Invalid filename format")
                continue
                
            location = parts[1]
            date = parts[2].split('.')[0]  # Remove .csv
            year = date[:4]  # Extract year from YYYYMMDD
            
            # Create key for grouping
            group_key = f"location-{location}-{year}"
            output_path = os.path.join(target_dir, f"{group_key}.csv")
            
            # Try to open and read the source file with different encodings
            encodings_to_try = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            file_content = None
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as source_file:
                        # Check if file is empty
                        first_line = source_file.readline()
                        if not first_line.strip():
                            print(f"Skipping {file_name}: Empty file")
                            break
                            
                        # Reset file pointer and read all content
                        source_file.seek(0)
                        file_content = list(csv.reader(source_file))
                        break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error reading {file_name} with {encoding} encoding: {str(e)}")
                    continue
            
            if not file_content:
                print(f"Skipping {file_name}: Could not read file content")
                continue
            
            # Skip header row if exists and file is not empty
            if len(file_content) > 1:
                data_rows = file_content[1:]
            else:
                print(f"Skipping {file_name}: No data rows found")
                continue
            
            # Create or get the output file writer
            if group_key not in output_files:
                output_files[group_key] = open(output_path, 'a', newline='', encoding='utf-8')
                csv_writers[group_key] = csv.writer(output_files[group_key])
                print(f"Created/Opened file: {group_key}.csv")
            
            # Write all rows to the appropriate output file
            for row in data_rows:
                if any(row):  # Check if row contains any data
                    csv_writers[group_key].writerow(row)
                
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
            continue
    
    # Close all output files
    for file_handle in output_files.values():
        file_handle.close()
    
    print("\nGrouping complete!")
    print(f"Source directory: {source_dir}")
    print(f"Target directory: {target_dir}")
    print(f"Created {len(output_files)} grouped files")

if __name__ == "__main__":
    group_files_by_location_year() 