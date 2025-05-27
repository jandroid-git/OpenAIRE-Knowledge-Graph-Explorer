import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from tqdm import tqdm  # Fortschrittsbalken-Modul

# Ordner für gespeicherte Bilder erstellen, falls er noch nicht existiert
output_folder = 'assets'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# CSV-Datei für 'country' laden
file_path_country = 'data/projects_data_csv/project_country_rel.csv'
data_country = pd.read_csv(file_path_country)

# Häufigkeit der Länderkürzel in der Spalte 'country' zählen
country_counts = data_country['country'].value_counts()

# Fortschrittsbalken für den ersten Schritt (Country-Analyse)
for _ in tqdm(range(1), desc="Erstelle Diagramm für Länderkürzel"):
    # Horizontales Balkendiagramm für Länderkürzel erstellen mit dunkelgrüner Farbe
    plt.figure(figsize=(10, 6))
    ax = country_counts.plot(kind='barh', color='#006400')  # Dunkelgrün
    plt.title('Anzahl der Forschungsprojekte nach Land')
    plt.xlabel('Anzahl der Datensätze')
    plt.ylabel('Länderkürzel')
    ax.get_xaxis().set_visible(False)  # X-Achse ausblenden
    for spine in ax.spines.values():  # Rahmen entfernen
        spine.set_visible(False)
    for i, value in enumerate(country_counts):  # Häufigkeit über Balken anzeigen
        ax.text(value + 0.3, i, str(value), va='center', fontsize=10, color='black')  # Abstand erhöht
    plt.tight_layout()  # Layout anpassen

    # Plot für Land speichern
    plt.savefig(os.path.join(output_folder, 'projects_by_country.png'))
    plt.close()

# CSV-Datei für 'funder' laden
file_path_funder = 'data/projects_data_csv/project_funder_rel.csv'
data_funder = pd.read_csv(file_path_funder)

# Häufigkeit der Förderer in der Spalte 'funder_name' zählen
funder_counts = data_funder['funder_name'].value_counts()

# Nur die Top 20 Förderer anzeigen
top_20_funder_counts = funder_counts.head(20)

# Fortschrittsbalken für den zweiten Schritt (Funder-Analyse)
for _ in tqdm(range(1), desc="Erstelle Diagramm für Förderer"):
    # Horizontales Balkendiagramm für die Top 20 Förderer erstellen mit dunkelgrüner Farbe
    plt.figure(figsize=(10, 6))
    ax = top_20_funder_counts.plot(kind='barh', color='#006400')  # Dunkelgrün
    plt.title('Anzahl der Forschungsprojekte nach Förderer (Top 20)')
    plt.xlabel('Anzahl der Datensätze')
    plt.ylabel('Förderer')
    ax.get_xaxis().set_visible(False)  # X-Achse ausblenden
    for spine in ax.spines.values():  # Rahmen entfernen
        spine.set_visible(False)
    for i, value in enumerate(top_20_funder_counts):  # Häufigkeit über Balken anzeigen
        ax.text(value + 0.3, i, str(value), va='center', fontsize=10, color='black')  # Abstand erhöht
    plt.tight_layout()  # Layout anpassen

    # Plot für Förderer speichern
    plt.savefig(os.path.join(output_folder, 'projects_by_funder_top_20.png'))
    plt.close()

# CSV-Datei für 'projects' laden
file_path_projects = 'data/projects_data_csv/projects.csv'
data_projects = pd.read_csv(file_path_projects)

# Deskriptive Statistik für numerische Spalten
print("Deskriptive Statistik für numerische Spalten:")
print(data_projects[['totalCost', 'fundedAmount']].describe())

# Fortschrittsbalken für Verteilung der Daten (TotalCost und FundedAmount)
for _ in tqdm(range(1), desc="Erstelle Diagramm für Verteilungen"):
    # Visualisierung der Verteilung von 'totalCost' und 'fundedAmount'
    plt.figure(figsize=(12, 6))

    # Transformation der Daten, um den dominierenden Bereich zu verringern
    sns.histplot(data_projects['totalCost'], kde=True, color='darkgreen', bins=50)
    plt.title('Verteilung der Gesamtkosten (totalCost)')
    plt.xlabel('Gesamtkosten')
    plt.ylabel('Häufigkeit')

    # Gebe an, dass die beiden Verteilungen nebeneinander sein sollen
    plt.figure(figsize=(12, 6))
    sns.histplot(data_projects['fundedAmount'], kde=True, color='darkblue', bins=50)
    plt.title('Verteilung des Förderbetrags (fundedAmount)')
    plt.xlabel('Förderbetrag')
    plt.ylabel('Häufigkeit')

    plt.tight_layout()

    # Verteilungsdiagramm speichern
    plt.savefig(os.path.join(output_folder, 'distribution_totalCost_fundedAmount.png'))
    plt.close()

# Häufigkeit der Werte in den kategorischen Spalten 'callIdentifier' und 'keywords'
call_identifier_counts = data_projects['callIdentifier'].value_counts().head(20) 
keywords_counts = data_projects['keywords'].value_counts().head(20)  # Die 20 häufigsten Keywords

# Fortschrittsbalken für CallIdentifier und Keywords
for _ in tqdm(range(1), desc="Erstelle Diagramme für CallIdentifiers und Keywords"):
    # Visualisierung der Häufigkeit von 'callIdentifier'
    plt.figure(figsize=(12, 6))  # größere Figur für bessere Lesbarkeit
    sns.barplot(x=call_identifier_counts.index, y=call_identifier_counts.values, color='seagreen')
    plt.title('Häufigkeit der verschiedenen "callIdentifier"')
    plt.xlabel('callIdentifier')
    plt.ylabel('Häufigkeit')
    plt.xticks(rotation=45, ha='right')  # X-Achsen-Beschriftung rotieren
    plt.tight_layout()

    # 'callIdentifier' Plot speichern
    plt.savefig(os.path.join(output_folder, 'callIdentifier_frequency.png'))
    plt.close()

    # Visualisierung der 20 häufigsten 'keywords'
    plt.figure(figsize=(12, 6))  # größere Figur für bessere Lesbarkeit
    sns.barplot(x=keywords_counts.index, y=keywords_counts.values, color='darkorange')
    plt.title('Top 20 häufigste Keywords')
    plt.xlabel('Keywords')
    plt.ylabel('Häufigkeit')
    plt.xticks(rotation=45, ha='right')  # X-Achsen-Beschriftung rotieren

    # Platz unten erhöhen für besser sichtbare X-Achsen-Beschriftung
    plt.subplots_adjust(bottom=0.8)

    plt.tight_layout()

    # 'keywords' Plot speichern
    plt.savefig(os.path.join(output_folder, 'keywords_top_20.png'))
    plt.close()


# Zeitliche Analyse: Start- und Enddatum der Projekte
# Zunächst die Spalten in Datetime konvertieren
data_projects['startDate'] = pd.to_datetime(data_projects['startDate'], errors='coerce')
data_projects['endDate'] = pd.to_datetime(data_projects['endDate'], errors='coerce')

# Projekte nach Jahr gruppieren
data_projects['startYear'] = data_projects['startDate'].dt.year
projects_by_year = data_projects['startYear'].value_counts().sort_index()

# Fortschrittsbalken für die zeitliche Analyse
for _ in tqdm(range(1), desc="Erstelle Diagramm für Projekte nach Jahr"):
    # Visualisierung der Anzahl der Projekte pro Jahr
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=projects_by_year.index, y=projects_by_year.values, color='purple', marker='o')
    plt.title('Anzahl der Projekte nach Startjahr')
    plt.xlabel('Startjahr')
    plt.ylabel('Anzahl der Projekte')
    plt.tight_layout()

    # Projekte pro Jahr Plot speichern
    plt.savefig(os.path.join(output_folder, 'projects_by_year.png'))
    plt.close()

# Durchschnittlicher Förderbetrag pro Jahr
avg_funded_amount_by_year = data_projects.groupby('startYear')['fundedAmount'].mean()

for _ in tqdm(range(1), desc="Erstelle Diagramm für durchschnittlichen Förderbetrag"):
    # Visualisierung des durchschnittlichen Förderbetrags pro Jahr
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=avg_funded_amount_by_year.index, y=avg_funded_amount_by_year.values, color='red', marker='o')
    plt.title('Durchschnittlicher Förderbetrag pro Jahr')
    plt.xlabel('Startjahr')
    plt.ylabel('Durchschnittlicher Förderbetrag')
    plt.tight_layout()

    # Durchschnittlicher Förderbetrag pro Jahr Plot speichern
    plt.savefig(os.path.join(output_folder, 'avg_funded_amount_by_year.png'))
    plt.close()


# ============================================
# Neue Analyse 1: Top 10 Funder nach Fördersumme
# ============================================
merged_funding = pd.merge(data_funder, data_projects[['id', 'fundedAmount']], left_on='project_id', right_on='id', how='left')
funding_sum_by_funder = merged_funding.groupby('funder_name')['fundedAmount'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=funding_sum_by_funder.values, y=funding_sum_by_funder.index, color='teal')
plt.title('Top 10 Förderer nach Gesamtsumme der Förderungen')
plt.xlabel('Gesamte Fördermittel (€)')
plt.ylabel('Förderer')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'top10_funder_by_fundedAmount.png'))
plt.close()

# ============================================
# Neue Analyse 2: Durchschnittlicher Förderbetrag pro Funder
# ============================================
avg_funding_by_funder = merged_funding.groupby('funder_name')['fundedAmount'].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=avg_funding_by_funder.values, y=avg_funding_by_funder.index, color='steelblue')
plt.title('Durchschnittlicher Förderbetrag pro Förderer (Top 10)')
plt.xlabel('Durchschnittliche Förderung (€)')
plt.ylabel('Förderer')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'avg_funded_per_funder.png'))
plt.close()

# ============================================
# Neue Analyse 3: Projektdauer vs Förderbetrag
# ============================================
# Berechne Projektdauer in Tagen
data_projects['project_duration_days'] = (data_projects['endDate'] - data_projects['startDate']).dt.days

# Filtere ungültige Werte
valid_duration = data_projects[(data_projects['project_duration_days'] > 0) & (data_projects['fundedAmount'] > 0)]

plt.figure(figsize=(10, 6))
sns.scatterplot(data=valid_duration, x='project_duration_days', y='fundedAmount', alpha=0.5)
plt.title('Zusammenhang zwischen Projektdauer und Förderbetrag')
plt.xlabel('Projektdauer (Tage)')
plt.ylabel('Förderbetrag (€)')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'scatter_duration_vs_funding.png'))
plt.close()


