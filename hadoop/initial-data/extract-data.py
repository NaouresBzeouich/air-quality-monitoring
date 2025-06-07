import os
import gzip
import shutil

# Define the input and output directories
input_dir = "data"
output_dir = "extracted-data"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Walk through all subdirectories of input_dir
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".csv.gz"):
            gz_path = os.path.join(root, file)
            csv_filename = file[:-3]  # remove .gz
            output_path = os.path.join(output_dir, csv_filename)

            # Decompress the .gz file to .csv in output_dir
            with gzip.open(gz_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            print(f"Extracted: {csv_filename}")
