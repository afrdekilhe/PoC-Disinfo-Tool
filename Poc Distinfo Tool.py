import json
import re
import pandas as pd
import os
from IPython.display import display

# Construct the full path to the JSON file
file_path = os.path.join('https://github.com/afrdekilhe/PoC-Disinfo-Tool/blob/main/dataset_rafale.json')

# Load the JSON data
with open(file_path, 'r') as f:
    data = json.load(f)

# Extract screen names
screen_names = [item['author']['screen_name'] for item in data]

# Identify suspicious handles
suspicious_handles = [name for name in screen_names if re.fullmatch(r'[a-zA-Z]+\d+', name)]

# Count occurrences
handle_counts = pd.Series(suspicious_handles).value_counts().reset_index()
handle_counts.columns = ['screen_name', 'count']

# Create a list of dictionaries with suspicious handle data and metadata
suspicious_data_with_metadata = []
for item in data:
    screen_name = item['author']['screen_name']
    if screen_name in suspicious_handles:
        suspicious_data_with_metadata.append({
            'screen_name': screen_name,
            'date': item['author'].get('date'),  # Using .get() for potentially missing keys
            'description': item['author'].get('description'),
            'geolocation': item['author'].get('geolocation')
        })

# Create a DataFrame from the collected data
suspicious_df = pd.DataFrame(suspicious_data_with_metadata)

# Merge with counts to get the final table
final_table = pd.merge(suspicious_df, handle_counts, on='screen_name')

# Remove exact duplicates
final_table = final_table.drop_duplicates()

# Sort the table by count in descending order
final_table_sorted = final_table.sort_values(by='count', ascending=False)

# Display the sorted table
print("Suspicious Handles with Metadata (Sorted by Count):")
display(final_table_sorted)

# Define the output CSV file path
output_csv_path = '/content/suspicious_handles_with_metadata_no_duplicates.csv'

# Save the DataFrame to a CSV file
final_table.to_csv(output_csv_path, index=False)

print(f"\nTable saved to {output_csv_path}")
