import pandas as pd
import os

# Define paths relative to the project root
input_file = r' C:\Users\Praneet\project\dataset\recommendations.csv.csv'
output_file = r'C:\Users\Praneet\project\dataset\recommendations_small.csv'

if os.path.exists(input_file):
    print(f"Reading first 100,000 rows from {input_file}...")
    try:
        # Read only first 100k rows
        df = pd.read_csv(input_file, nrows=100000)
        # Save without index to keep format clean
        df.to_csv(output_file, index=False)
        print(f"Success! Created {output_file}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
else:
    print(f"Error: {input_file} not found. Please ensure it is in the 'dataset' folder.")
