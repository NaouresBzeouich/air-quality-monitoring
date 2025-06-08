#!/usr/bin/env python3
import os
import glob
import random
import shutil
from pathlib import Path

def create_light_dataset():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, 'grouped-data')
    target_dir = os.path.join(base_dir, 'grouped-light-data')
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Get all CSV files from source directory
    csv_files = glob.glob(os.path.join(source_dir, '*.csv'))
    
    # Calculate how many files to select (1/3 of total)
    num_files_to_select = len(csv_files) // 3
    
    # Randomly select files
    selected_files = random.sample(csv_files, num_files_to_select)
    
    # Copy selected files to target directory
    for file_path in selected_files:
        file_name = os.path.basename(file_path)
        target_path = os.path.join(target_dir, file_name)
        shutil.copy2(file_path, target_path)
        print(f"Copied {file_name} to light-data folder")
    
    print(f"\nCreated light dataset with {num_files_to_select} files")
    print(f"Source directory: {source_dir}")
    print(f"Target directory: {target_dir}")

if __name__ == "__main__":
    create_light_dataset() 