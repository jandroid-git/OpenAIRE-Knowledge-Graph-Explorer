import pandas as pd
import json
from tqdm import tqdm  # For progress tracking during funder enrichment

# =====================================================================================
# Script: Funders ROR Enrichment
# Author: Jan
# Date: May 2025
#
# Description:
# This script enriches a list of funding organizations by matching their names
# against metadata from the Research Organization Registry (ROR). It combines
# original funder data with authoritative ROR information such as aliases,
# acronyms, geolocation, and organizational metadata.
#
# Input:
# - funders.csv: CSV file containing funder names and short names.
# - ror_data.csv: ROR dataset (v1.66 or newer) containing detailed metadata.
#
# Output:
# - funders_enriched.csv: A CSV file combining original funder data with
#   enriched fields from the ROR registry.
# =====================================================================================

# -------------------------------------------------------------------------------------
# Function: parse_json_field
# Purpose: Parses a field that may be a JSON string, a list, or a scalar.
# Returns a list to unify data processing downstream.
# -------------------------------------------------------------------------------------
def parse_json_field(field):
    try:
        parsed = json.loads(field)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, str):
            return [parsed]
        else:
            return [str(parsed)]
    except:
        if isinstance(field, list):
            return field
        elif isinstance(field, str):
            return [field]
        elif pd.isna(field):
            return []
        else:
            return [str(field)]

# -------------------------------------------------------------------------------------
# Load source datasets
# -------------------------------------------------------------------------------------
funders_df = pd.read_csv("data/projects_data_csv/funders.csv")
ror_df = pd.read_csv("data/ror_data/v1.66-2025-05-20-ror-data.csv")

# -------------------------------------------------------------------------------------
# Build a lookup dictionary from ROR data
# Keys: normalized names, aliases, and acronyms
# Values: full ROR records
# -------------------------------------------------------------------------------------
ror_lookup = {}

for _, row in ror_df.iterrows():
    name_variants = [row.get('name', '')]
    name_variants += parse_json_field(row.get('aliases', '[]'))
    name_variants += parse_json_field(row.get('acronyms', '[]'))

    for name in name_variants:
        key = str(name).strip().lower()
        if key:
            ror_lookup[key] = row

# -------------------------------------------------------------------------------------
# Match and enrich each funder using the ROR lookup
# If a match is found, ROR metadata is extracted and appended
# -------------------------------------------------------------------------------------
enriched = []

for _, funder in tqdm(funders_df.iterrows(), total=len(funders_df), desc="Enriching funders"):
    funder_name = funder['name'].strip().lower()
    match = ror_lookup.get(funder_name, None)

    if match is not None:
        established_raw = match.get('established', '')
        try:
            established = int(float(established_raw)) if established_raw != '' else ''
        except:
            established = ''

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
            'lat': match.get('addresses[0].lat', ''),
            'lng': match.get('addresses[0].lng', ''),
            'city_name': match.get('addresses[0].geonames_city.name', '')
        }
    else:
        row = {k: '' for k in [
            'ror_id', 'ror_name', 'types', 'status', 'aliases', 'labels', 'acronyms',
            'wikipedia_url', 'links', 'established',
            'lat', 'lng', 'city_name'
        ]}
        row.update({'name': funder['name'], 'shortName': funder['shortName']})

    enriched.append(row)

# -------------------------------------------------------------------------------------
# Save enriched funder data to CSV
# -------------------------------------------------------------------------------------
enriched_df = pd.DataFrame(enriched)
enriched_df.to_csv("data/projects_data_csv/funders_enriched.csv", index=False)
