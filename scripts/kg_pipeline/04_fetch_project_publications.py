import requests
import pandas as pd

# ===================================================================
# Configuration parameters
# LIMIT: Maximum number of projects to process. Set to None to process all.
# ===================================================================
LIMIT = 1000

# ===================================================================
# Input CSV file paths
# - projects.csv: contains project details
# - project_funder_rel.csv: mapping of projects to funders
# - funders_enriched.csv: funder metadata enriched with external info
# ===================================================================
PROJECTS_CSV = 'data/projects_data_csv/projects.csv'
FUNDERS_REL_CSV = 'data/projects_data_csv/project_funder_rel.csv'
FUNDERS_ENRICHED_CSV = 'data/projects_data_csv/funders_enriched.csv'

# ===================================================================
# Output CSV file paths
# - project_publications.csv: extracted publications matching projects
# - publication_project_rel.csv: relations between projects and publications
# ===================================================================
PUBLICATIONS_CSV = 'data/projects_data_csv/project_publications.csv'
RELATION_CSV = 'data/projects_data_csv/publication_project_rel.csv'

# ===================================================================
# Load input datasets into pandas DataFrames
# 'callIdentifier' is read as string explicitly to preserve formatting
# low_memory=False disables internal dtype guessing for better consistency
# ===================================================================
projects_df = pd.read_csv(PROJECTS_CSV, dtype={'callIdentifier': str}, low_memory=False)
funder_rel_df = pd.read_csv(FUNDERS_REL_CSV)
funders_df = pd.read_csv(FUNDERS_ENRICHED_CSV)

# ===================================================================
# Helper function: find_best_funder_match
# Purpose: Given a funder name string, attempts to find the best match
#          in the enriched funders dataset.
# Matching is done in order:
#   1. Exact match with 'name' field
#   2. Exact match with 'ror_name' field
#   3. Partial match in 'aliases' field (semicolon-separated)
# Returns: the canonical funder name if matched, else None
# ===================================================================
def find_best_funder_match(input_name):
    if pd.isna(input_name):
        return None
    # Check direct name match (case insensitive)
    match = funders_df[funders_df['name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']
    # Check match against ROR official name
    match = funders_df[funders_df['ror_name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']
    # Check in aliases list (split on ';')
    for _, row in funders_df.iterrows():
        aliases = str(row['aliases']).lower().split(';')
        if input_name.lower() in [a.strip() for a in aliases]:
            return row['name']
    return None

# ===================================================================
# Containers to accumulate publication records and relations
# ===================================================================
publication_rows = []
relation_rows = []

# Calculate the total number of projects to process based on LIMIT
total_projects = len(projects_df) if LIMIT is None else min(LIMIT, len(projects_df))
print(f"🔍 Starting publication search for {total_projects} projects...")

# ===================================================================
# Main processing loop over projects (limited by LIMIT)
# For each project:
# - Retrieve the project ID and title
# - Lookup the funder name associated with the project
# - Match the funder name to a canonical funder in enriched data
# - Build a query string for the CrossRef API to find publications
#   related to the project title and optionally the funder name
# - Fetch up to 5 publications from CrossRef matching the query
# - Store publication metadata and link it to the project ID
# - Provide progress output and error handling
# ===================================================================
for idx, row in projects_df.head(LIMIT).iterrows():
    current = idx + 1  # 1-based progress counter
    project_id = row['id']
    title_query = row['title']

    # Find associated funder name for the current project
    funder_name = funder_rel_df.loc[funder_rel_df['project_id'] == project_id, 'funder_name'].values
    funder_name = funder_name[0] if len(funder_name) else None

    # Attempt to find canonical funder match
    matched_funder = find_best_funder_match(funder_name) if funder_name else None

    # Construct the CrossRef API query string
    query = f'title:"{title_query}"'
    if matched_funder:
        query += f' funder-name:"{matched_funder}"'

    # Perform API request to CrossRef to fetch publication data
    url = f'https://api.crossref.org/works?query.bibliographic={query}&rows=5'
    response = requests.get(url)

    if response.status_code == 200:
        items = response.json()['message']['items']
        if items:
            print(f"✅ {len(items)} hits for project ID {project_id} ({current}/{total_projects})")
            for item in items:
                doi = item.get('DOI', '')
                title = item.get('title', [''])[0]
                journal = item.get('container-title', [''])[0] if item.get('container-title') else ''
                citation_count = item.get('is-referenced-by-count', 0)

                # Add publication if not already added (based on DOI)
                if not any(pub['doi'] == doi for pub in publication_rows):
                    publication_rows.append({
                        "doi": doi,
                        "title": title,
                        "journal": journal,
                        "citation_count": citation_count
                    })

                # Record the relation between project and publication DOI
                relation_rows.append({
                    "project_id": project_id,
                    "doi": doi
                })
        else:
            print(f"❌ No publications found for project {project_id} ({current}/{total_projects})")
    else:
        print(f"⚠️ Error for project {project_id}: HTTP {response.status_code} ({current}/{total_projects})")

# ===================================================================
# Save collected publication and relation data to CSV files
# ===================================================================
pd.DataFrame(publication_rows).to_csv(PUBLICATIONS_CSV, index=False)
pd.DataFrame(relation_rows).to_csv(RELATION_CSV, index=False)

print(f"\n Saved {len(publication_rows)} publications to {PUBLICATIONS_CSV}")
print(f" Saved {len(relation_rows)} project-publication relations to {RELATION_CSV}")
