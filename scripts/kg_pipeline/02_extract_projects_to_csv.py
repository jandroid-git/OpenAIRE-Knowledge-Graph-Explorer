import json
import os
import csv
from tqdm import tqdm  # For displaying a progress bar during file processing

# =====================================================================================
# Script: JSON to CSV Converter for Project Data
# Author: Jan
# Date: February 2025
#
# Description:
# This script reads cleaned JSON files containing project data and transforms them
# into structured CSV files for further analysis or integration. It extracts project
# metadata, funders, countries, and their relationships, then writes them into
# separate CSV files.
#
# NOTE:
# - Input files must not be compressed (e.g., zipped). Unzip locally before use.
# =====================================================================================

# Directories for input (cleaned JSON) and output (CSV files)
original_data_dir = "data\\cleaned_projects_data_april2025"
output_dir = "data\\projects_data_csv"

# Safe extraction function: returns an empty string for None values
def safe(value):
    return value if value is not None else ""

# Collect all JSON files in the input directory
json_files = [f for f in os.listdir(original_data_dir) if f.endswith('.json')]

# Data containers for CSV output
projects = []
funders = {}
countries = {}
project_funder_rel = []
project_country_rel = []

# Prepare output CSV files
projects_csv = open(os.path.join(output_dir, 'projects.csv'), 'w', newline='', encoding='utf-8')
funders_csv = open(os.path.join(output_dir, 'funders.csv'), 'w', newline='', encoding='utf-8')
countries_csv = open(os.path.join(output_dir, 'countries.csv'), 'w', newline='', encoding='utf-8')
project_funder_rel_csv = open(os.path.join(output_dir, 'project_funder_rel.csv'), 'w', newline='', encoding='utf-8')
project_country_rel_csv = open(os.path.join(output_dir, 'project_country_rel.csv'), 'w', newline='', encoding='utf-8')

# Initialize CSV writers
projects_writer = csv.writer(projects_csv)
funders_writer = csv.writer(funders_csv)
countries_writer = csv.writer(countries_csv)
project_funder_writer = csv.writer(project_funder_rel_csv)
project_country_writer = csv.writer(project_country_rel_csv)

# Write CSV headers
projects_writer.writerow([
    'id', 'code', 'title', 'startDate', 'endDate', 'callIdentifier',
    'keywords', 'summary', 'totalCost', 'fundedAmount'
])
funders_writer.writerow(['name', 'shortName'])
countries_writer.writerow(['jurisdiction'])
project_funder_writer.writerow(['project_id', 'funder_name'])
project_country_writer.writerow(['project_id', 'country'])

# Process each JSON file with progress bar
for idx, file in enumerate(tqdm(json_files, desc="Processing JSON files", unit="file")):
    file_path = os.path.join(original_data_dir, file)

    try:
        # Load JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error loading file {file}: {e}")
        continue

    # Validate that data is a list of projects
    if isinstance(data, list):
        project_data_list = data
    else:
        print(f"File {file} does not contain a list of projects.")
        continue

    # Process each project in the JSON file
    for project_data in project_data_list:
        pid = safe(project_data.get("id"))
        code = safe(project_data.get("code"))
        title = safe(project_data.get("title"))
        start_date = safe(project_data.get("startDate"))
        end_date = safe(project_data.get("endDate"))
        call_identifier = safe(project_data.get("callIdentifier"))
        keywords = safe(project_data.get("keywords"))
        summary = safe(project_data.get("summary"))

        # Extract financial information
        granted_data = project_data.get("granted") or {}
        total_cost = safe(granted_data.get("totalCost"))
        funded_amount = safe(granted_data.get("fundedAmount"))

        # Write project record to CSV
        projects_writer.writerow([
            pid, code, title, start_date, end_date,
            call_identifier, keywords, summary,
            total_cost, funded_amount
        ])

        # Process funders
        for fund in (project_data.get("fundings") or []):
            fname = safe(fund.get("name"))
            fshort = safe(fund.get("shortName"))
            fjuris = safe(fund.get("jurisdiction"))

            # Add new funder if not already recorded
            if fname and fname not in funders:
                funders[fname] = {"shortName": fshort}

            # Link project to funder
            if fname:
                project_funder_rel.append([pid, fname])

            # Link project to country
            if fjuris:
                if fjuris not in countries:
                    countries[fjuris] = {}
                project_country_rel.append([pid, fjuris])

# Write funder records to CSV
for fund_name, fund_data in funders.items():
    fund_short = fund_data['shortName']
    funders_writer.writerow([fund_name, fund_short])

# Write unique countries to CSV
for country in countries:
    countries_writer.writerow([country])

# Write project-funder relationships to CSV
for rel in project_funder_rel:
    project_funder_writer.writerow(rel)

# Write project-country relationships to CSV
for rel in project_country_rel:
    project_country_writer.writerow(rel)

# Close all CSV files
projects_csv.close()
funders_csv.close()
countries_csv.close()
project_funder_rel_csv.close()
project_country_rel_csv.close()

print("CSV files have been successfully created!")
