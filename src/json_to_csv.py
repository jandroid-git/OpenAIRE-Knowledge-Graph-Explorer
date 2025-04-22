import json
import os
import csv
from tqdm import tqdm  # Importiere die tqdm-Bibliothek

#Beachte das die benötigten Dateien nicht komprimiert vorliegen dürfen - im fall erst lokal entzippen





# Verzeichnis für Originaldaten und Zielordner für CSV-Dateien
original_data_dir = 'data\\cleaned_projects_data_april2025'
output_dir = 'data\\projects_data_csv'

# Sicherheitsfunktion für den Umgang mit 'None'-Werten
def safe(value):
    return value if value is not None else ""

# Dateien aus dem Original-Datenverzeichnis laden und parsen
json_files = [f for f in os.listdir(original_data_dir) if f.endswith('.json')]

# Listen und Dictionaries zum Speichern der Daten
projects = []
funders = {}
countries = {}
project_funder_rel = []
project_country_rel = []

# CSV-Dateien vorbereiten
projects_csv = open(os.path.join(output_dir, 'projects.csv'), 'w', newline='', encoding='utf-8')
funders_csv = open(os.path.join(output_dir, 'funders.csv'), 'w', newline='', encoding='utf-8')
countries_csv = open(os.path.join(output_dir, 'countries.csv'), 'w', newline='', encoding='utf-8')
project_funder_rel_csv = open(os.path.join(output_dir, 'project_funder_rel.csv'), 'w', newline='', encoding='utf-8')
project_country_rel_csv = open(os.path.join(output_dir, 'project_country_rel.csv'), 'w', newline='', encoding='utf-8')

# CSV-Writer erstellen
projects_writer = csv.writer(projects_csv)
funders_writer = csv.writer(funders_csv)
countries_writer = csv.writer(countries_csv)
project_funder_writer = csv.writer(project_funder_rel_csv)
project_country_writer = csv.writer(project_country_rel_csv)

# CSV-Header schreiben
projects_writer.writerow(['id', 'code', 'title', 'startDate', 'endDate', 'callIdentifier', 'keywords', 'summary', 'totalCost', 'fundedAmount'])
funders_writer.writerow(['name', 'shortName'])
countries_writer.writerow(['jurisdiction'])
project_funder_writer.writerow(['project_id', 'funder_name'])
project_country_writer.writerow(['project_id', 'country'])

# Fortschrittsanzeige hinzufügen
for idx, file in enumerate(tqdm(json_files, desc="Bearbeite JSON-Dateien", unit="Datei")):
    file_path = os.path.join(original_data_dir, file)

    try:
        # JSON-Datei laden
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Laden der Datei {file}: {e}")
        continue

    # Überprüfen, ob die JSON-Daten eine Liste sind
    if isinstance(data, list):  # Falls die Daten eine Liste von Projekten sind
        project_data_list = data
    else:
        print(f"Die Datei {file} enthält keine Liste, sondern ein einzelnes Objekt.")
        continue

    # Durch jedes Projekt in der Liste gehen
    for project_data in project_data_list:
        # Projektinformationen extrahieren
        pid = safe(project_data.get("id"))
        code = safe(project_data.get("code"))
        title = safe(project_data.get("title"))
        start_date = safe(project_data.get("startDate"))
        end_date = safe(project_data.get("endDate"))
        call_identifier = safe(project_data.get("callIdentifier"))
        keywords = safe(project_data.get("keywords"))
        summary = safe(project_data.get("summary"))

        # Sicherstellen, dass "granted" nicht None ist
        granted_data = project_data.get("granted")
        if granted_data is None:
            granted_data = {}

        # Wenn "granted" vorhanden ist, dann auf totalCost und fundedAmount zugreifen
        total_cost = safe(granted_data.get("totalCost"))
        funded_amount = safe(granted_data.get("fundedAmount"))

        # Projekt in die CSV-Datei schreiben
        projects_writer.writerow([pid, code, title, start_date, end_date, call_identifier, keywords, summary, total_cost, funded_amount])

        # Sicherstellen, dass 'fundings' immer eine Liste ist
        for fund in (project_data.get("fundings") or []):  # Wenn 'fundings' None ist, verwende eine leere Liste
            fname = safe(fund.get("name"))
            fshort = safe(fund.get("shortName"))
            fjuris = safe(fund.get("jurisdiction"))

            # Funder-Knoten erstellen, falls noch nicht vorhanden
            if fname and fname not in funders:
                funders[fname] = {"shortName": fshort}
            
            # Projekt-Funder-Beziehung
            if fname:
                project_funder_rel.append([pid, fname])

            # Länder-Knoten und Beziehung
            if fjuris:
                if fjuris not in countries:
                    countries[fjuris] = {}
                project_country_rel.append([pid, fjuris])

# Funder-Daten in die CSV-Datei schreiben
for fund_name, fund_data in funders.items():
    fund_short = fund_data['shortName']
    funders_writer.writerow([fund_name, fund_short])

# Länder-Daten in die CSV-Datei schreiben
for country in countries:
    countries_writer.writerow([country])

# Projekt-Funder-Beziehungen in die CSV-Datei schreiben
for rel in project_funder_rel:
    project_funder_writer.writerow(rel)

# Projekt-Länder-Beziehungen in die CSV-Datei schreiben
for rel in project_country_rel:
    project_country_writer.writerow(rel)

# CSV-Dateien schließen
projects_csv.close()
funders_csv.close()
countries_csv.close()
project_funder_rel_csv.close()
project_country_rel_csv.close()

print("CSV-Dateien wurden erfolgreich erstellt!")
