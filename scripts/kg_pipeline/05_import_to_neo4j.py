from neo4j import GraphDatabase
import csv
import logging
from tqdm import tqdm

# =====================================================================================
# Script: local neo4j Knowledge Graph creator script
# Author: Jan
# Date: March 2025
#
# Description:
# This script creates the Neo4j Knowledge Graph based on initial node and relationship
# CSV files using Cypher queries. It loads structured project, funder and country data,
# and builds corresponding graph structures.
#
# Inputs:
# - projects.csv: Project node metadata
# - funders_enriched.csv: Funder node metadata
# - countries.csv: Country node metadata (not yet implemented)
# - project_funder_rel.csv: Project-to-Funder relations
# - project_country_rel.csv: Project-to-Country relations
# - project_publications.csv: Publication metadata (for enrichment)
# - publication_project_rel.csv: Publication-to-Project relations
#
# Outputs:
# - Nodes and relationships written into local Neo4j database
#
# Notes:
# - You need to create the file 'neo4j_data/neo_access.txt' with your Neo4j password
# =====================================================================================


# -------------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------------

# Set up logging to display status messages during processing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Define Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"

# Load Neo4j password from local file (must be created manually)
access_file = "neo4j_data/neo_access.txt"
try:
    with open(access_file, "r", encoding="utf-8") as f:
        password = f.readline().strip()
except FileNotFoundError:
    logging.critical(f"❌ Access file not found: {access_file}")
    exit(1)

# Define CSV paths (adjust as needed)
projects_csv_file = 'data/projects_data_csv/projects.csv'
funders_csv_file = 'data/projects_data_csv/funders_enriched.csv'
countries_csv_file = 'data/projects_data_csv/countries.csv'
project_funder_rel_csv_file = 'data/projects_data_csv/project_funder_rel.csv'
project_country_rel_csv_file = 'data/projects_data_csv/project_country_rel.csv'
publication_csv_file = 'data/projects_data_csv/project_publications.csv'
pub_project_rel_csv_file = 'data/projects_data_csv/publication_project_rel.csv'

# Optional: limit number of rows to process for testing/performance
LIMIT_ENTRIES = 100000

# Create Neo4j driver for database access
driver = GraphDatabase.driver(uri, auth=(username, password))


# -------------------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------------------

def determine_batch_size(total_rows):
    """
    Returns an appropriate batch size based on the number of rows.
    Helps balance memory use and transaction efficiency.
    """
    if total_rows <= 50:
        return 10
    elif total_rows <= 200:
        return 25
    elif total_rows <= 1000:
        return 100
    elif total_rows <= 10000:
        return 500
    elif total_rows <= 100000:
        return 1000
    elif total_rows <= 1000000:
        return 5000
    else:
        return 10000

def batchify(iterable, batch_size):
    """
    Splits an iterable into batches of a given size.
    Useful for efficient bulk insertion into Neo4j.
    """
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def load_csv_and_run_batch(csv_file, query, param_fn, limit=None, show_progress=False):
    """
    Loads data from a CSV file, prepares query parameters, and executes Cypher
    write transactions in batches.

    Arguments:
    - csv_file: path to CSV file
    - query: Cypher query string
    - param_fn: function to map CSV row to Cypher parameters
    - limit: max number of rows to process
    - show_progress: whether to display tqdm progress bar
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = list(csv.DictReader(file))
            if limit:
                reader = reader[:limit]

            total = len(reader)
            batch_size = determine_batch_size(total)
            iterator = batchify(reader, batch_size)
            bar = tqdm(total=total, desc=f"Loading {csv_file}", unit="rows") if show_progress else None

            with driver.session() as session:
                for batch in iterator:
                    session.execute_write(lambda tx: [tx.run(query, **param_fn(row)) for row in batch])
                    if bar:
                        bar.update(len(batch))

            if bar:
                bar.close()

        logging.info(f"✅ Processed: {csv_file} (Limit: {limit}, Batch Size: {batch_size})")

    except FileNotFoundError:
        logging.error(f"❌ File not found: {csv_file}")
    except Exception as e:
        logging.error(f"❌ Error processing {csv_file}: {e}")


# -------------------------------------------------------------------------------------
# Node Creation Functions
# -------------------------------------------------------------------------------------

def create_project_nodes(csv_file, limit=None):
    """
    Creates Project nodes from the CSV file.
    Each project has metadata such as title, duration, keywords, costs, etc.
    """
    query = """
    MERGE (p:Project {id: $id})
    SET p.code = $code,
        p.title = $title,
        p.startDate = $startDate,
        p.endDate = $endDate,
        p.callIdentifier = $callIdentifier,
        p.keywords = $keywords,
        p.summary = $summary,
        p.totalCost = $totalCost,
        p.fundedAmount = $fundedAmount
    """
    def params(row):
        return {
            "id": row['id'],
            "code": row['code'],
            "title": row['title'],
            "startDate": row['startDate'],
            "endDate": row['endDate'],
            "callIdentifier": row['callIdentifier'],
            "keywords": row['keywords'],
            "summary": row['summary'],
            "totalCost": float(row['totalCost']) if row['totalCost'] else 0.0,
            "fundedAmount": float(row['fundedAmount']) if row['fundedAmount'] else 0.0
        }

    load_csv_and_run_batch(csv_file, query, params, limit, show_progress=True)

def create_funder_nodes(csv_file):
    """
    Creates Funder nodes based on enriched metadata.
    Includes location info, aliases, ROR IDs, etc.
    """
    query = """
    MERGE (f:Funder {name: $name})
    SET f.shortName = $shortName,
        f.ror_id = $ror_id,
        f.ror_name = $ror_name,
        f.types = $types,
        f.status = $status,
        f.aliases = $aliases,
        f.labels = $labels,
        f.acronyms = $acronyms,
        f.wikipedia_url = $wikipedia_url,
        f.links = $links,
        f.established = $established,
        f.lat = $lat,
        f.lng = $lng,
        f.city_name = $city_name
    """
    def params(row):
        return {
            "name": row['name'],
            "shortName": row.get('shortName', ''),
            "ror_id": row.get('ror_id', ''),
            "ror_name": row.get('ror_name', ''),
            "types": row.get('types', ''),
            "status": row.get('status', ''),
            "aliases": row.get('aliases', ''),
            "labels": row.get('labels', ''),
            "acronyms": row.get('acronyms', ''),
            "wikipedia_url": row.get('wikipedia_url', ''),
            "links": row.get('links', ''),
            "established": int(float(row['established'])) if row.get('established', '').strip() else None,
            "lat": float(row['lat']) if row.get('lat', '').strip() else None,
            "lng": float(row['lng']) if row.get('lng', '').strip() else None,
            "city_name": row.get('city_name', '')
        }

    load_csv_and_run_batch(csv_file, query, params, show_progress=True)

# -------------------------------------------------------------------------------------
# Node Creation: Countries
# -------------------------------------------------------------------------------------

def create_country_nodes(csv_file):
    """
    Create Country nodes from CSV data.
    Each country node has a 'jurisdiction' property used as a unique identifier.
    """
    query = "MERGE (c:Country {jurisdiction: $jurisdiction})"
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "jurisdiction": row['jurisdiction']
    }, show_progress=True)

# -------------------------------------------------------------------------------------
# Relationship Creation Functions
# -------------------------------------------------------------------------------------

def create_project_funder_relationship(csv_file, limit=None):
    """
    Create FUNDED_BY relationships between Project and Funder nodes.
    Requires matching by project ID and funder name.
    """
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (f:Funder {name: $funder_name})
    MERGE (p)-[:FUNDED_BY]->(f)
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "project_id": row['project_id'],
        "funder_name": row['funder_name']
    }, limit, show_progress=True)

def create_project_country_relationship(csv_file, limit=None):
    """
    Create LOCATED_IN relationships between Project and Country nodes.
    Matches by project ID and country jurisdiction.
    """
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (c:Country {jurisdiction: $country})
    MERGE (p)-[:LOCATED_IN]->(c)
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "project_id": row['project_id'],
        "country": row['country']
    }, limit, show_progress=True)

# -------------------------------------------------------------------------------------
# Node Creation: Publications
# -------------------------------------------------------------------------------------

def create_publication_nodes(csv_file):
    """
    Create Publication nodes from CSV data.
    Each publication has a DOI, title, journal, and citation count.
    """
    query = """
    MERGE (pub:Publication {doi: $doi})
    SET pub.title = $title,
        pub.journal = $journal,
        pub.citation_count = $citation_count
    """
    def params(row):
        return {
            "doi": row['doi'],
            "title": row.get('title', ''),
            "journal": row.get('journal', ''),
            "citation_count": int(row['citation_count']) if row.get('citation_count') else 0
        }
    load_csv_and_run_batch(csv_file, query, params, show_progress=True)

# -------------------------------------------------------------------------------------
# Relationship: Project ↔ Publication
# -------------------------------------------------------------------------------------

def create_project_publication_relationship(csv_file):
    """
    Create HAS_PUBLICATION relationships between Project and Publication nodes.
    Matches by project ID and publication DOI.
    """
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (pub:Publication {doi: $doi})
    MERGE (p)-[:HAS_PUBLICATION]->(pub)
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "project_id": row['project_id'],
        "doi": row['doi']
    }, show_progress=True)

# -------------------------------------------------------------------------------------
# Relationship: Funder ↔ Publication (via project)
# -------------------------------------------------------------------------------------

def create_funder_publication_relationship(publication_rel_csv, funder_rel_csv):
    """
    Create ACKNOWLEDGED_IN relationships between Funders and Publications.
    Uses project → funder and project → publication mappings to infer connections.
    """
    # Build mapping of project_id → funder_name
    funder_map = {}
    with open(funder_rel_csv, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            funder_map[row['project_id']] = row['funder_name']

    # Define Cypher query for linking funders to publications
    query = """
    MATCH (f:Funder {name: $funder_name})
    MATCH (pub:Publication {doi: $doi})
    MERGE (f)-[:ACKNOWLEDGED_IN]->(pub)
    """
    def params(row):
        return {
            "funder_name": funder_map.get(row['project_id'], ''),
            "doi": row['doi']
        }

    load_csv_and_run_batch(publication_rel_csv, query, params, show_progress=True)

# -------------------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    # Create node types
    create_project_nodes(projects_csv_file, limit=LIMIT_ENTRIES)
    create_funder_nodes(funders_csv_file)
    create_country_nodes(countries_csv_file)

    # Create relationships between nodes
    create_project_funder_relationship(project_funder_rel_csv_file, limit=LIMIT_ENTRIES)
    create_project_country_relationship(project_country_rel_csv_file, limit=LIMIT_ENTRIES)
    create_publication_nodes(publication_csv_file)
    create_project_publication_relationship(pub_project_rel_csv_file)
    create_funder_publication_relationship(pub_project_rel_csv_file, project_funder_rel_csv_file)

    # Clean up and close Neo4j connection
    driver.close()
    logging.info("✅ Knowledge Graph successfully created and extended!")
