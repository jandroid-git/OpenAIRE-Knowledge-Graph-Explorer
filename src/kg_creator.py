from neo4j import GraphDatabase
import csv
import logging
from tqdm import tqdm
import os

# === Konfiguration ===

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

uri = "bolt://localhost:7687"
username = "neo4j"

# Passwort aus Datei lesen
access_file = "neo4j_data/neo_access.txt"
try:
    with open(access_file, "r", encoding="utf-8") as f:
        password = f.readline().strip()
except FileNotFoundError:
    logging.critical(f"❌ Zugriffsdaten-Datei nicht gefunden: {access_file}")
    exit(1)

projects_csv_file = 'data/projects_data_csv/projects.csv'
funders_csv_file = 'data/projects_data_csv/funders.csv'
countries_csv_file = 'data/projects_data_csv/countries.csv'
project_funder_rel_csv_file = 'data/projects_data_csv/project_funder_rel.csv'
project_country_rel_csv_file = 'data/projects_data_csv/project_country_rel.csv'

LIMIT_ENTRIES = 100000  # oder None für alle

driver = GraphDatabase.driver(uri, auth=(username, password))

# === Hilfsfunktionen ===

def determine_batch_size(total_rows):
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
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def load_csv_and_run_batch(csv_file, query, param_fn, limit=None, show_progress=False):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = list(csv.DictReader(file))
            if limit:
                reader = reader[:limit]

            total = len(reader)
            batch_size = determine_batch_size(total)

            iterator = batchify(reader, batch_size)
            bar = tqdm(total=total, desc=f"Lade {csv_file}", unit="Zeile") if show_progress else None

            with driver.session() as session:
                for batch in iterator:
                    session.execute_write(lambda tx: [tx.run(query, **param_fn(row)) for row in batch])
                    if bar:
                        bar.update(len(batch))

            if bar:
                bar.close()

        logging.info(f"✅ Verarbeitet: {csv_file} (Limit: {limit}, Batch Size: {batch_size})")
    except FileNotFoundError:
        logging.error(f"❌ Datei nicht gefunden: {csv_file}")
    except Exception as e:
        logging.error(f"❌ Fehler bei Datei {csv_file}: {e}")

# === Importfunktionen ===

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
    load_csv_and_run_batch(csv_file, query, params, limit, show_progress=True)

def create_funder_nodes(csv_file):
    query = """
    MERGE (f:Funder {name: $name})
    SET f.shortName = $shortName
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "name": row['name'],
        "shortName": row['shortName']
    }, show_progress=True)

def create_country_nodes(csv_file):
    query = """
    MERGE (c:Country {jurisdiction: $jurisdiction})
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
        "jurisdiction": row['jurisdiction']
    }, show_progress=True)

def create_project_funder_relationship(csv_file, limit=None):
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
    query = """
    MATCH (p:Project {id: $project_id})
    MATCH (c:Country {jurisdiction: $country})
    MERGE (p)-[:LOCATED_IN]->(c)
    """
    load_csv_and_run_batch(csv_file, query, lambda row: {
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
