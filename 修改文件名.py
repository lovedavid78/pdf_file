import os
import re

# Define the folder path
folder_path = '/Users/fenghua/Library/CloudStorage/GoogleDrive-fenghua.email@gmail.com/我的云端硬盘/contract_uploaded/'

# Traverse the folder and process each .txt file
for file_name in os.listdir(folder_path):
    # Only process .txt files
    if file_name.endswith('.txt'):
        file_path = os.path.join(folder_path, file_name)

        # Open the .txt file and read its contents
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Check if the file has at least 3 lines
        if len(lines) >= 3:
            # Get the third line, stripping any leading/trailing whitespace
            new_file_name_part = lines[2].strip()

            # Extract the part in parentheses from the original file name
            original_parenthesis_part = re.search(r'\(.*\)', file_name)
            parenthesis_part = original_parenthesis_part.group(0) if original_parenthesis_part else ''

            # Construct the new file name, preserving the part in parentheses and the .txt extension
            new_file_name = f"{new_file_name_part}{parenthesis_part}.txt"

            # Define the full new file path
            new_file_path = os.path.join(folder_path, new_file_name)

            # Rename the file
            os.rename(file_path, new_file_path)
            print(f"Renamed file: '{file_name}' to '{new_file_name}'")
