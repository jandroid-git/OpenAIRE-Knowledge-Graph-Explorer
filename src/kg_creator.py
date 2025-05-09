from neo4j import GraphDatabase
import csv
import logging
from tqdm import tqdm  # <-- Neu
import os

# === Konfiguration ===

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

uri = "bolt://localhost:7687"
username = "neo4j"
password = os.getenv("LOCAL_DB_ACCESS_JAN")  # Nutzt GitHub Secret 

projects_csv_file = 'data/projects_data_csv/projects.csv'
funders_csv_file = 'data/projects_data_csv/funders.csv'
countries_csv_file = 'data/projects_data_csv/countries.csv'
project_funder_rel_csv_file = 'data/projects_data_csv/project_funder_rel.csv'
project_country_rel_csv_file = 'data/projects_data_csv/project_country_rel.csv'

LIMIT_ENTRIES = 10000  # oder None für alle

driver = GraphDatabase.driver(uri, auth=(username, password))

def load_csv_and_run_query(csv_file, query, param_fn, limit=None, show_progress=False):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = list(csv.DictReader(file))
            if limit is not None:
                reader = reader[:limit]

            iterator = tqdm(reader, desc=f"Lade {csv_file}", unit="Zeile") if show_progress else reader

            with driver.session() as session:
                for row in iterator:
                    session.run(query, **param_fn(row))

        logging.info(f"✅ Verarbeitet: {csv_file} (Limit: {limit})")
    except FileNotFoundError:
        logging.error(f"❌ Datei nicht gefunden: {csv_file}")
    except Exception as e:
        logging.error(f"❌ Fehler bei Datei {csv_file}: {e}")

def create_project_nodes(csv_file, limit=None):
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
    load_csv_and_run_query(csv_file, query, params, limit, show_progress=True)

def create_funder_nodes(csv_file):
    query = """
    MERGE (f:Funder {name: $name})
    SET f.shortName = $shortName
    """
    load_csv_and_run_query(csv_file, query, lambda row: {
        "name": row['name'],
        "shortName": row['shortName']
    }, show_progress=True)

def create_country_nodes(csv_file):
    query = """
    MERGE (c:Country {jurisdiction: $jurisdiction})
    """
    load_csv_and_run_query(csv_file, query, lambda row: {
        "jurisdiction": row['jurisdiction']
    }, show_progress=True)

def create_project_funder_relationship(csv_file, limit=None):
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (f:Funder {name: $funder_name})
    MERGE (p)-[:FUNDED_BY]->(f)
    """
    load_csv_and_run_query(csv_file, query, lambda row: {
        "project_id": row['project_id'],
        "funder_name": row['funder_name']
    }, limit, show_progress=True)

def create_project_country_relationship(csv_file, limit=None):
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (c:Country {jurisdiction: $country})
    MERGE (p)-[:LOCATED_IN]->(c)
    """
    load_csv_and_run_query(csv_file, query, lambda row: {
        "project_id": row['project_id'],
        "country": row['country']
    }, limit, show_progress=True)

# === Ausführung ===

if __name__ == "__main__":
    create_project_nodes(projects_csv_file, limit=LIMIT_ENTRIES)
    create_funder_nodes(funders_csv_file)
    create_country_nodes(countries_csv_file)
    create_project_funder_relationship(project_funder_rel_csv_file, limit=LIMIT_ENTRIES)
    create_project_country_relationship(project_country_rel_csv_file, limit=LIMIT_ENTRIES)
    driver.close()
    logging.info("✅ Der Knowledge Graph wurde erfolgreich erstellt!")