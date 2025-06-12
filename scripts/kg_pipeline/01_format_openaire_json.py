import os

# =====================================================================================
# Script: JSON File Formatter for Project Data
# Author: Jan
# Date: February 2025
#
# Description:
# This script processes raw `.json` files stored in a specified input directory.
# It performs basic cleanup and formatting tasks, such as trimming whitespace and
# ensuring that JSON objects are wrapped in an array (`[ ]`) with commas between them.
#
# NOTE:
# - The source JSON files must not be compressed. If they are zipped, unzip them locally first.
# =====================================================================================

# Define the path to the folder containing the original (raw) project data files from the OpenAIRE KG fileforamt - json
input_folder = r"data/original_openAIRE_data/original_projects_data_april2025"

# Define the path to the folder where cleaned and formatted files will be saved
output_folder = r"data/cleaned_projects_data_april2025"

# Ensure the output directory exists; create it if it does not
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate over each file in the input directory
for file_name in os.listdir(input_folder):
    # Process only files with the .json extension
    if file_name.endswith('.json'):
        # Construct full file paths for reading and writing
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)

        try:
            # Open the input JSON file and read all lines using UTF-8 encoding
            with open(input_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Strip trailing whitespace and newline characters from each line
            lines = [line.rstrip() for line in lines]

            # Open the output file for writing cleaned content
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write("[\n")  # Begin the JSON array

                # Loop through each line to format as a proper JSON array
                for i, line in enumerate(lines):
                    if line.startswith("{"):
                        # Add a comma if the next line is another object
                        if i < len(lines) - 1 and lines[i + 1].startswith("{"):
                            file.write(line + ",\n")
                        else:
                            file.write(line + "\n")
                    else:
                        # Write non-object lines unchanged
                        file.write(line + "\n")

                file.write("]")  # Close the JSON array

            # Log successful processing of the file
            print(f"Successfully processed and saved file: {file_name}")

        except Exception as e:
            # Log any errors that occur during processing
            print(f"Error processing file {file_name}: {e}")
