from neo4j import GraphDatabase
import csv



# Nur eine erste Idee, noch nicht getestet ob es funktioniert !!!
# lokaler neo4j server muss erst installiert werden 

# Beachte das die benötigten Dateien nicht komprimiert vorliegen dürfen - im fall erst lokal entzippen
# Aber nicht unkomprimiert auf den github pushen, die Dateien sind zu groß!







# Neo4j-Verbindung einrichten
uri = "bolt://localhost:7687"  # URL zu deiner Neo4j-Datenbank
username = "neo4j"  # Dein Neo4j-Benutzername
password = "password"  # Dein Neo4j-Passwort

# Verbindung zur Neo4j-Datenbank herstellen
driver = GraphDatabase.driver(uri, auth=(username, password))
session = driver.session()

def create_project_nodes(csv_file):
    """Lädt Projekte aus der CSV-Datei und erstellt Projekt-Knoten in Neo4j"""
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
            MERGE (p:Project {id: $id})
            SET p.title = $title,
                p.startDate = $startDate,
                p.endDate = $endDate,
                p.callIdentifier = $callIdentifier,
                p.keywords = $keywords,
                p.summary = $summary,
                p.totalCost = $totalCost,
                p.fundedAmount = $fundedAmount
            """
            session.run(query, 
                        id=row['id'],
                        title=row['title'],
                        startDate=row['startDate'],
                        endDate=row['endDate'],
                        callIdentifier=row['callIdentifier'],
                        keywords=row['keywords'],
                        summary=row['summary'],
                        totalCost=row['totalCost'],
                        fundedAmount=row['fundedAmount'])

def create_funder_nodes(csv_file):
    """Lädt Fördergeber aus der CSV-Datei und erstellt Funder-Knoten in Neo4j"""
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
            MERGE (f:Funder {name: $name})
            SET f.shortName = $shortName
            """
            session.run(query, name=row['name'], shortName=row['shortName'])

def create_country_nodes(csv_file):
    """Lädt Länder aus der CSV-Datei und erstellt Country-Knoten in Neo4j"""
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
            MERGE (c:Country {jurisdiction: $jurisdiction})
            """
            session.run(query, jurisdiction=row['jurisdiction'])

def create_project_funder_relationship(csv_file):
    """Lädt die Projekt-Fördergeber-Beziehungen und erstellt die Beziehungen in Neo4j"""
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
            MATCH (p:Project {id: $project_id})
            MATCH (f:Funder {name: $funder_name})
            MERGE (p)-[:FUNDED_BY]->(f)
            """
            session.run(query, project_id=row['project_id'], funder_name=row['funder_name'])

def create_project_country_relationship(csv_file):
    """Lädt die Projekt-Länder-Beziehungen und erstellt die Beziehungen in Neo4j"""
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
            MATCH (p:Project {id: $project_id})
            MATCH (c:Country {jurisdiction: $country})
            MERGE (p)-[:LOCATED_IN]->(c)
            """
            session.run(query, project_id=row['project_id'], country=row['country'])

# CSV-Dateipfade
projects_csv_file = 'data/projects_data_csv/projects.csv'
funders_csv_file = 'data/projects_data_csv/funders.csv'
countries_csv_file = 'data/projects_data_csv/countries.csv'
project_funder_rel_csv_file = 'data/projects_data_csv/project_funder_rel.csv'
project_country_rel_csv_file = 'data/projects_data_csv/project_country_rel.csv'

# Erstelle Knoten und Beziehungen in Neo4j
create_project_nodes(projects_csv_file)
create_funder_nodes(funders_csv_file)
create_country_nodes(countries_csv_file)
create_project_funder_relationship(project_funder_rel_csv_file)
create_project_country_relationship(project_country_rel_csv_file)

# Verbindung schließen
session.close()
driver.close()

print("Der Knowledge Graph wurde erfolgreich erstellt!")
