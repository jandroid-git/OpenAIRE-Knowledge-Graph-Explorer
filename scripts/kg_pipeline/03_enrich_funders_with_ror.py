import pandas as pd
import json
from tqdm import tqdm

# ===================================================================
# Function: parse_json_field
# Purpose: Safely parse a field that may contain JSON-encoded data,
#          a list, or a string. Ensures the output is always a list,
#          simplifying downstream processing.
# Input:  field (str, list, or other)
# Output: list containing parsed elements or empty list if no valid data
# ===================================================================
def parse_json_field(field):
    try:
        # Attempt to parse the input as JSON
        parsed = json.loads(field)
        if isinstance(parsed, list):
            return parsed                     # Return if already a list
        elif isinstance(parsed, str):
            return [parsed]                  # Wrap string in list
        else:
            return [str(parsed)]             # Convert other types to string and wrap
    except:
        # If JSON parsing fails, handle based on original type
        if isinstance(field, list):
            return field                    # Return list as is
        elif isinstance(field, str):
            return [field]                  # Wrap string in list
        elif pd.isna(field):
            return []                       # Return empty list if NaN
        else:
            return [str(field)]             # Convert other types to string and wrap

# ===================================================================
# Load input CSV files:
# - funders.csv: contains funder names and short names.
# - ror_data.csv: detailed metadata from Research Organization Registry (ROR).
# ===================================================================
funders_df = pd.read_csv("data/projects_data_csv/funders.csv")
ror_df = pd.read_csv("data/ror_data/v1.66-2025-05-20-ror-data.csv")

# ===================================================================
# Create a lookup dictionary to map various name variants to the
# corresponding ROR data records.
# Variants include the main name, aliases, and acronyms.
# Keys are normalized (lowercased and stripped).
# ===================================================================
ror_lookup = {}

for _, row in ror_df.iterrows():
    # Collect all possible name variants for the current ROR record
    names = [row.get('name', '')]
    names += parse_json_field(row.get('aliases', '[]'))
    names += parse_json_field(row.get('acronyms', '[]'))

    for name in names:
        key = str(name).strip().lower()
        if key:  # Only add non-empty keys
            ror_lookup[key] = row

# ===================================================================
# Enrich the funders dataframe by matching funder names against the
# ROR lookup dictionary. If a match is found, relevant ROR metadata
# is extracted and added to the funder record.
# If no match is found, ROR-related fields remain empty.
# ===================================================================
enriched = []

for _, funder in tqdm(funders_df.iterrows(), total=len(funders_df), desc="Enriching funders"):
    funder_name = funder['name'].strip().lower()
    match = ror_lookup.get(funder_name, None)

    if match is not None:
        # Safely convert the 'established' year to an integer if possible
        established_raw = match.get('established', '')
        try:
            established = int(float(established_raw)) if established_raw != '' else ''
        except:
            established = ''

        # Build the enriched funder record combining original and ROR data
        row = {
            'name': funder['name'],
            'shortName': funder['shortName'],
            'ror_id': match['id'],
            'ror_name': match['name'],
            'types': match.get('types', ''),
            'status': match.get('status', ''),
            'aliases': match.get('aliases', ''),
            'labels': match.get('labels', ''),
            'acronyms': match.get('acronyms', ''),
            'wikipedia_url': match.get('wikipedia_url', ''),
            'links': match.get('links', ''),
            'established': established,
            # Access to nested data assumes dot notation flattened keys
            'lat': match.get('addresses[0].lat', ''),
            'lng': match.get('addresses[0].lng', ''),
            'city_name': match.get('addresses[0].geonames_city.name', '')
        }
    else:
        # If no ROR match found, initialize all ROR fields as empty strings
        row = {k: '' for k in [
            'ror_id', 'ror_name', 'types', 'status', 'aliases', 'labels', 'acronyms',
            'wikipedia_url', 'links', 'established',
            'lat', 'lng', 'city_name'
        ]}
        # Preserve the original funder name and shortName
        row.update({'name': funder['name'], 'shortName': funder['shortName']})

    enriched.append(row)

# ===================================================================
# Save the enriched funders data to a CSV file.
# Index is omitted to keep the file clean.
# ===================================================================
enriched_df = pd.DataFrame(enriched)
enriched_df.to_csv("data/projects_data_csv/funders_enriched.csv", index=False)
