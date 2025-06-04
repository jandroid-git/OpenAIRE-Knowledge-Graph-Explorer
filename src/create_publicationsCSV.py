import requests
import pandas as pd

# === Parameter ===
LIMIT = 1000  # Anzahl der Projekte zum Verarbeiten; setze auf None für alle

# === Eingabedateien ===
PROJECTS_CSV = 'data/projects_data_csv/projects.csv'
FUNDERS_REL_CSV = 'data/projects_data_csv/project_funder_rel.csv'
FUNDERS_ENRICHED_CSV = 'data/projects_data_csv/funders_enriched.csv'

# === Ausgabedateien ===
PUBLICATIONS_CSV = 'data/projects_data_csv/project_publications.csv'
RELATION_CSV = 'data/projects_data_csv/publication_project_rel.csv'

# === Einlesen ===
projects_df = pd.read_csv(PROJECTS_CSV, dtype={'callIdentifier': str}, low_memory=False)
funder_rel_df = pd.read_csv(FUNDERS_REL_CSV)
funders_df = pd.read_csv(FUNDERS_ENRICHED_CSV)

# === Hilfsfunktion: Funder-Matching ===
def find_best_funder_match(input_name):
    if pd.isna(input_name):
        return None
    # 1. name
    match = funders_df[funders_df['name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']
    # 2. ror_name
    match = funders_df[funders_df['ror_name'].str.lower() == input_name.lower()]
    if not match.empty:
        return match.iloc[0]['name']
    # 3. aliases (mit Split auf ; getrennte Liste)
    for _, row in funders_df.iterrows():
        aliases = str(row['aliases']).lower().split(';')
        if input_name.lower() in [a.strip() for a in aliases]:
            return row['name']
    return None

# === Ergebnis-Container ===
publication_rows = []
relation_rows = []

total_projects = len(projects_df) if LIMIT is None else min(LIMIT, len(projects_df))
print(f"🔍 Starte Publikationssuche für {total_projects} Projekte...")

# === Hauptlogik ===
for idx, row in projects_df.head(LIMIT).iterrows():
    current = idx + 1  # aktueller Zähler (1-basiert)
    project_id = row['id']
    title_query = row['title']

    # Bestimme Funder für das Projekt
    funder_name = funder_rel_df.loc[funder_rel_df['project_id'] == project_id, 'funder_name'].values
    funder_name = funder_name[0] if len(funder_name) else None
    matched_funder = find_best_funder_match(funder_name) if funder_name else None

    # Query zusammenbauen
    query = f'title:"{title_query}"'
    if matched_funder:
        query += f' funder-name:"{matched_funder}"'

    # API-Abfrage
    url = f'https://api.crossref.org/works?query.bibliographic={query}&rows=5'
    response = requests.get(url)

    if response.status_code == 200:
        items = response.json()['message']['items']
        if items:
            print(f"✅ {len(items)} Treffer für Projekt-ID {project_id} ({current}/{total_projects})")
            for item in items:
                doi = item.get('DOI', '')
                title = item.get('title', [''])[0]
                journal = item.get('container-title', [''])[0] if item.get('container-title') else ''
                citation_count = item.get('is-referenced-by-count', 0)

                # Publikation erfassen (einmal pro DOI)
                if not any(pub['doi'] == doi for pub in publication_rows):
                    publication_rows.append({
                        "doi": doi,
                        "title": title,
                        "journal": journal,
                        "citation_count": citation_count
                    })

                # Relation erfassen
                relation_rows.append({
                    "project_id": project_id,
                    "doi": doi
                })
        else:
            print(f"❌ Keine Publikationen für Projekt {project_id} ({current}/{total_projects})")
    else:
        print(f"⚠️ Fehler für Projekt {project_id}: HTTP {response.status_code} ({current}/{total_projects})")


# === Speichern ===
pd.DataFrame(publication_rows).to_csv(PUBLICATIONS_CSV, index=False)
pd.DataFrame(relation_rows).to_csv(RELATION_CSV, index=False)

print(f"\n📄 {len(publication_rows)} Publikationen gespeichert in {PUBLICATIONS_CSV}")
print(f"🔗 {len(relation_rows)} Projekt-Publikations-Relationen gespeichert in {RELATION_CSV}")
