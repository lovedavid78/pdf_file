import os
import re
from dotenv import load_dotenv
#因为过长的文件名会自动截断,本程序的目的是批量重命名从北大法宝上下载下来文件夹中的所有法条 .txt 文件。
# 每个 .txt 文件的新名称将从文件中的第三行中提取全部的，然后将其与原始文件名中的括号部分组合在一起。
# 例如，如果文件名为 "file1 (123).txt"，第三行内容为 "New Name"，则文件将重命名为 "New Name (123).txt"。
# Define the folder path
load_dotenv()
folder_path = os.getenv("FOLDER_PATH")

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
