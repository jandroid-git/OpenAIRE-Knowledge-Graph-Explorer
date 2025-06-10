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
# This script creates the neo4j Knowledeg Graph based on the initial created node csv files and theire corespondnng csv relationship files using Cypher.
#
# NOTE:
# 
# =====================================================================================


# === Configuration and Setup ===

# Configure logging for informative console output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Neo4j connection parameters
uri = "bolt://localhost:7687"
username = "neo4j"

# Read Neo4j password from file - this subfolder and file has to be created by yourself and stores the privat password for your local neo4j database
access_file = "neo4j_data/neo_access.txt"
try:
    with open(access_file, "r", encoding="utf-8") as f:
        password = f.readline().strip()
except FileNotFoundError:
    logging.critical(f"❌ Access file not found: {access_file}")
    exit(1)

# CSV input file paths for nodes and relationships
projects_csv_file = 'data/projects_data_csv/projects.csv'
funders_csv_file = 'data/projects_data_csv/funders_enriched.csv'
countries_csv_file = 'data/projects_data_csv/countries.csv'
project_funder_rel_csv_file = 'data/projects_data_csv/project_funder_rel.csv'
project_country_rel_csv_file = 'data/projects_data_csv/project_country_rel.csv'
publication_csv_file = 'data/projects_data_csv/project_publications.csv'
pub_project_rel_csv_file = 'data/projects_data_csv/publication_project_rel.csv'

# Limit number of rows processed (None = all)
LIMIT_ENTRIES = 10000

# Initialize Neo4j driver for database sessions
driver = GraphDatabase.driver(uri, auth=(username, password))

# === Helper Functions ===

def determine_batch_size(total_rows):
    """
    Determine an appropriate batch size based on the total number of rows.
    This helps balance memory usage and performance.
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
    Yield successive batches of size batch_size from iterable.
    """
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def load_csv_and_run_batch(csv_file, query, param_fn, limit=None, show_progress=False):
    """
    Generic function to load a CSV file, read data rows, and execute
    a given Cypher query in batches on Neo4j.
    
    Parameters:
    - csv_file: path to the CSV file
    - query: Cypher query string with parameters
    - param_fn: function that maps a CSV row dict to query parameters
    - limit: optional max number of rows to process
    - show_progress: whether to display a tqdm progress bar
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
                    # Execute write transactions for each batch
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

# === Node Creation Functions ===

def create_project_nodes(csv_file, limit=None):
    """
    Create Project nodes from CSV data.
    Properties: id, code, title, start/end dates, call identifier,
                keywords, summary, total cost, funded amount
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
    Create Funder nodes from enriched CSV data.
    Properties include name, shortName, ROR identifiers, aliases, location info, etc.
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

def create_country_nodes(csv_file):
    """
    Create Country nodes with 'jurisdiction' property.
    """
    query = "MERGE (c:Country {jurisdiction: $jurisdiction})"
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "jurisdiction": row['jurisdiction']
    }, show_progress=True)

# === Relationship Creation Functions ===

def create_project_funder_relationship(csv_file, limit=None):
    """
    Create FUNDED_BY relationships between Project and Funder nodes.
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

def create_publication_nodes(csv_file):
    """
    Create Publication nodes with DOI, title, journal, and citation count.
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

def create_project_publication_relationship(csv_file):
    """
    Create HAS_PUBLICATION relationships between Project and Publication nodes.
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

def create_funder_publication_relationship(publication_rel_csv, funder_rel_csv):
    """
    Create ACKNOWLEDGED_IN relationships between Funders and Publications
    based on the mapping of projects to funders and projects to publications.
    """
    # Build a mapping from project_id to funder_name for quick lookup
    funder_map = {}
    with open(funder_rel_csv, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            funder_map[row['project_id']] = row['funder_name']

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

# === Main Execution ===

if __name__ == "__main__":
    # Create nodes
    create_project_nodes(projects_csv_file, limit=LIMIT_ENTRIES)
    create_funder_nodes(funders_csv_file)
    create_country_nodes(countries_csv_file)

    # Create relationships
    create_project_funder_relationship(project_funder_rel_csv_file, limit=LIMIT_ENTRIES)
    create_project_country_relationship(project_country_rel_csv_file, limit=LIMIT_ENTRIES)
    create_publication_nodes(publication_csv_file)
    create_project_publication_relationship(pub_project_rel_csv_file)
    create_funder_publication_relationship(pub_project_rel_csv_file, project_funder_rel_csv_file)

    # Close Neo4j driver connection
    driver.close()
    logging.info("✅ Knowledge Graph successfully created and extended!")
