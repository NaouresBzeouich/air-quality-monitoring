#!/usr/bin/env python3
import os
import glob
import random
import shutil
from math import ceil

def split_grouped_data():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, 'grouped-data')
    
    # Create 5 target directories
    target_dirs = []
    for i in range(1, 16):
        target_dir = os.path.join(base_dir, f'split-data/split-{i}')
        os.makedirs(target_dir, exist_ok=True)
        target_dirs.append(target_dir)
    
    # Get all CSV files from grouped-data directory
    csv_files = glob.glob(os.path.join(source_dir, '*.csv'))
    
    if not csv_files:
        print("No CSV files found in grouped-data directory!")
        return
    
    # Shuffle the files randomly
    random.shuffle(csv_files)
    
    # Calculate how many files per split (round up to ensure all files are distributed)
    files_per_split = ceil(len(csv_files) / 5)
    
    # Distribute files across the 5 directories
    for i, file_path in enumerate(csv_files):
        # Calculate which split this file should go to
        target_split = i // files_per_split
        if target_split >= 5:  # Ensure we don't exceed our 5 splits
            target_split = 4
            
        file_name = os.path.basename(file_path)
        target_path = os.path.join(target_dirs[target_split], file_name)
        
        try:
            # Copy the file to its target directory
            shutil.copy2(file_path, target_path)
            print(f"Copied {file_name} to split-data-{target_split + 1}")
        except Exception as e:
            print(f"Error copying {file_name}: {str(e)}")
    
    # Print summary
    print("\nSplit complete!")
    for i, target_dir in enumerate(target_dirs, 1):
        files_in_split = len(glob.glob(os.path.join(target_dir, '*.csv')))
        print(f"split-data-{i}: {files_in_split} files")
    
    print(f"\nTotal files processed: {len(csv_files)}")
    print(f"Source directory: {source_dir}")
    print("Target directories:")
    for i in range(1, 6):
        print(f"  - {os.path.join(base_dir, f'split-data-{i}')}")

if __name__ == "__main__":
    split_grouped_data() 