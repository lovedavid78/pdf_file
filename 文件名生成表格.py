import os
import re
import pandas as pd

# Define the folder path
folder_path = '/Users/fenghua/Library/CloudStorage/GoogleDrive-fenghua.email@gmail.com/我的云端硬盘/contract_uploaded/'

# Regex to match the pattern inside the parentheses (FBM-CLI.2.29300)
pattern = re.compile(r'\((\w+)-(\w+)\.(\d+)\.(\d+)\)')

# List to hold extracted data
data = []

# Traverse the folder and extract data from each file name
for file_name in os.listdir(folder_path):
    # Remove the file extension
    file_name_no_ext = os.path.splitext(file_name)[0]

    # Remove the content inside parentheses from the file name
    file_name_cleaned = re.sub(r'\(.*?\)', '', file_name_no_ext).strip()

    # Match the pattern inside the parentheses
    match = pattern.search(file_name)

    if match:
        # Append the extracted groups and the cleaned file name (without parentheses content) to the data list
        data.append(list(match.groups()) + [file_name_cleaned])

# Create a DataFrame from the extracted data
df = pd.DataFrame(data, columns=['FBM', 'CLI', '2', '29300', 'File Name'])

# Save the DataFrame to a CSV file with utf-8-sig encoding for proper display in Excel
output_path = '/Users/fenghua/Library/CloudStorage/GoogleDrive-fenghua.email@gmail.com/我的云端硬盘/extracted_file_data.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Data has been saved to '{output_path}'")
