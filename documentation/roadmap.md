# TODO LISTE  
_Last update: 04.04.2025 ~Jan_

---

## Main Idea  
Interaktive Weltkarte zur Darstellung und Analyse globaler Entwicklungen in der KI-Forschung, basierend auf **OpenAIRE-Daten**.

---

## Core Features – Hauptkarte

### Visualisierungsart (Choroplethen)

**Multiple Choice Filter:**
- Anzahl Publikationen  
- Anzahl Projekte  
- Anzahl Institutionen aktiv in KI-Forschung  

**Single Choice Filter:**
- Wachstumsentwicklung im Betrachtungszeitraum X bis Y

### Filterpanel
- Zeitspanne  
- Projekttyp (z. B. alle, privat, national, EU, etc.)

### Weitere Überlegungen (wenn Projektzeit es erlaubt)
- Filterpanel nach Forschungsbereich (z. B. NLP, GenAI, Computer Vision)
- OnClick auf Land: Top-Projekte & Institutionen, Graphen zur zeitlichen Entwicklung von Jahr X bis Y
- Darstellung von Forschungskooperationen  
  (Verbindungslinien zwischen Ländern, Größenordnung abhängig von Kooperationsintensität)

---

## OPEN TODOs (chronologisch)
- Datenqualität der API prüfen (Vollständigkeit, Datenbereinigung?)  
- Pipeline skizzieren:  
  - Wie API-Daten extrahieren?  
  - In nutzbares Format transformieren  
  - Speicherung & Abfrageformat für einfache Maßzahlen (measures)  
- Datenvisualisierung:  
  - Welche Umgebung? Welche Interaktivität möglich?  
  - Visualisierung per Landkarte, Zeitfilter, etc.?  
  - TechStack?  
- Verknüpfung mit Länder-Visualisierung (GeoJSON?)

---

## Progress

### In Development

#### Jan
- Erste API-Testabfragen

#### Katerina
*(noch keine Einträge)*

### Done
- Dokumentation & Projektplanung
- Welche Informationen sind verwertbar?  
  - Welche Forschungsfelder wollen wir darstellen?  
  - Welche statistischen Maße (measures) sind sinnvoll?  
  - Festlegung der Features
- API-Dokumentation & Tutorials lesen  
~Jan, 01.04.2025

---

## Projektstruktur

```bash
OpenAIRE-Knowledge-Graph-Explorer/
├── src/                        # Source Code (Python Module)
│   └── python_module.py        # Beispielmodul
│
├── tests/                      # Tests (pytest / unittest)
│   └── test_example.py         
│
├── documentation/              # Sphinx Dokumentation
│   ├── sphinx_docs/
│   │   ├── _build/             # Generierte Doku (HTML)
│   │   ├── _static/            # Statische Inhalte (Bilder, CSS)
│   │   ├── _templates/         # Sphinx-Templates
│   │   ├── conf.py             # Konfiguration
│   │   ├── index.rst           # Hauptseite
│   │   └── python_module.rst   # Moduldoku
│   └── requirements.txt        # Abhängigkeiten (Sphinx etc.)
│
├── requirements.txt            # Python-Abhängigkeiten
├── setup.py                    # Setup-Skript
├── README.md                   # Projektübersicht & Usage
└── LICENSE                     # Lizenz
