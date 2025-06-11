import requests
import pandas as pd

# =====================================================================================
# Script: Project-Publication Matcher via CrossRef
# Author: Jan
# Date: June 2025
#
# Description:
# This script links research projects to related scientific publications using the
# CrossRef API. It matches project titles (and optionally funder names) to discover
# publications and establish a connection between projects and their published outputs.
#
# Inputs:
# - projects.csv: Metadata about research projects
# - project_funder_rel.csv: Project-to-funder relationships
# - funders_enriched.csv: Canonical funder data enriched with ROR metadata
#
# Outputs:
# - project_publications.csv: Metadata about discovered publications
# - publication_project_rel.csv: Mappings between projects and related publications
#
# Notes:
# - Only up to 5 publications per project are retrieved to reduce API load.
# - Basic heuristics are used to match funders (exact name or alias).
# - LIMIT parameter can restrict the number of processed projects.
# =====================================================================================

# -------------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------------
LIMIT = 10000  # Set to None to process all projects

# -------------------------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------------------------
PROJECTS_CSV = 'data/projects_data_csv/projects.csv'
FUNDERS_REL_CSV = 'data/projects_data_csv/project_funder_rel.csv'
FUNDERS_ENRICHED_CSV = 'data/projects_data_csv/funders_enriched.csv'
PUBLICATIONS_CSV = 'data/projects_data_csv/project_publications.csv'
RELATION_CSV = 'data/projects_data_csv/publication_project_rel.csv'

# -------------------------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------------------------
projects_df = pd.read_csv(PROJECTS_CSV, dtype={'callIdentifier': str}, low_memory=False)
funder_rel_df = pd.read_csv(FUNDERS_REL_CSV)
funders_df = pd.read_csv(FUNDERS_ENRICHED_CSV)

# -------------------------------------------------------------------------------------
# Helper Function: find_best_funder_match
# Description: Matches a given funder name to canonical funder data
# Matching logic:
#   1. Exact match with 'name'
#   2. Exact match with 'ror_name'
#   3. Partial match with aliases (semicolon-separated list)
# Returns the standardized funder name if matched, else None
# -------------------------------------------------------------------------------------
def find_best_funder_match(input_name):
    if pd.isna(input_name):
        return None

    # Match by original funder name
    match = funders_df[funders_df['name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']

    # Match by official ROR name
    match = funders_df[funders_df['ror_name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']

    # Match by alias
    for _, row in funders_df.iterrows():
        aliases = str(row['aliases']).lower().split(';')
        if input_name.lower() in [a.strip() for a in aliases]:
            return row['name']
    return None

# -------------------------------------------------------------------------------------
# Initialize containers
# -------------------------------------------------------------------------------------
publication_rows = []    # To hold unique publication metadata
relation_rows = []       # To link publications to projects

# Determine number of projects to process
total_projects = len(projects_df) if LIMIT is None else min(LIMIT, len(projects_df))
print(f"🔍 Starting publication search for {total_projects} projects...")

# -------------------------------------------------------------------------------------
# Main Loop: Search publications for each project using CrossRef API
# -------------------------------------------------------------------------------------
for idx, row in projects_df.head(LIMIT).iterrows():
    current = idx + 1
    project_id = row['id']
    title_query = row['title']

    # Get associated funder name (if any)
    funder_name = funder_rel_df.loc[funder_rel_df['project_id'] == project_id, 'funder_name'].values
    funder_name = funder_name[0] if len(funder_name) else None

    # Match funder to canonical name
    matched_funder = find_best_funder_match(funder_name) if funder_name else None

    # Build CrossRef query
    query = f'title:"{title_query}"'
    if matched_funder:
        query += f' funder-name:"{matched_funder}"'

    url = f'https://api.crossref.org/works?query.bibliographic={query}&rows=5'

    # Send request
    response = requests.get(url)

    if response.status_code == 200:
        items = response.json().get('message', {}).get('items', [])
        if items:
            print(f"✅ {len(items)} hits for project ID {project_id} ({current}/{total_projects})")
            for item in items:
                doi = item.get('DOI', '')
                title = item.get('title', [''])[0]
                journal = item.get('container-title', [''])[0] if item.get('container-title') else ''
                citation_count = item.get('is-referenced-by-count', 0)

                # Avoid duplicates by DOI
                if not any(pub['doi'] == doi for pub in publication_rows):
                    publication_rows.append({
                        "doi": doi,
                        "title": title,
                        "journal": journal,
                        "citation_count": citation_count
                    })

                # Link publication to project
                relation_rows.append({
                    "project_id": project_id,
                    "doi": doi
                })
        else:
            print(f"❌ No publications found for project {project_id} ({current}/{total_projects})")
    else:
        print(f"⚠️ Error for project {project_id}: HTTP {response.status_code} ({current}/{total_projects})")

# -------------------------------------------------------------------------------------
# Save results to CSV
# -------------------------------------------------------------------------------------
pd.DataFrame(publication_rows).to_csv(PUBLICATIONS_CSV, index=False)
pd.DataFrame(relation_rows).to_csv(RELATION_CSV, index=False)

print(f"\n📄 Saved {len(publication_rows)} publications to {PUBLICATIONS_CSV}")
print(f"🔗 Saved {len(relation_rows)} project-publication relations to {RELATION_CSV}")
