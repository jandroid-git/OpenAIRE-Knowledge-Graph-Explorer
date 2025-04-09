# TODO LISTE  
_Last update: 09.04.2025 ~Jan_

---
## **Main Idea**  
Webanwendung – Interaktive Weltkarte zur Darstellung globaler Entwicklungen in der **KI-Forschung**.

Datenquelle: **OpenAIRE API**.

---

## **Core Features – Hauptkarte**

### **Visualisierungsart (Choroplethenkarte)**

#### **Filter – Multiple Choice:**
- Anzahl der Publikationen  
- Anzahl der Projekte  
- Anzahl der Institutionen/Autoren aktiv in der KI-Forschung  

#### **Filter – Single Choice:**
- Wachstumsentwicklung im Betrachtungszeitraum von Jahr X bis Jahr Y

### **Filterpanel**
- Zeitspanne  
- Projekttyp (z.B. alle, privat, national, EU, etc.)

### **Weitere Überlegungen (abhängig von Projektzeitraum)**  
- Sub-Forschungsbereiche (z.B. NLP, GenAI, Computer Vision) als zusätzliche Filteroption
- OnClick auf ein Land: Anzeige des Rankings der Anzahl veröffentlichter Projekte nach Autor/Institution und Darstellung der zeitlichen Entwicklung von Jahr X bis Jahr Y in Graphen
- Visualisierung von Forschungskooperationen:  
  (Verbindungslinien zwischen Ländern, die je nach Kooperationsintensität variieren)
- Weitere Forschungsfelder einbinden
- **Update-Funktion**:  
  OpenAIRE API-Anfrage für alle gewählten Forschungsfelder, die JSON-Daten neuerer Datensätze als die letzten in der Datenbank enthalten. Extraktion und Anfügen an die existierenden Tabellen, gefolgt von einem **Daten-Refresh** in der Anwendung.

---

## **OPEN TODOs** (chronologisch)

- Gesamt-Abfrage aller JSON-Datensätze zu Projekten mit KI-Kontext  
- Extraktion und Zusammenführung dieser JSON-Daten in **SQLite** oder **MySQL** Tabellen
- Grundkonstrukt der interaktiven Webanwendung erstellen (HTML, CSS, JavaScript)
- Implementierung der Landkartenvisualisierung (mit Leaflet, Choroplethenkarte?)
- Implementierung dynamischer Filter und Regler – Verknüpfung mit Datenbankabfragen (API erstellen) und Aktualisierung der Länderkarte
- Design der Webanwendung (Design und UI/UX verbessern)
- **How to host?** Ausführliche Dokumentation und Vereinfachung der Projektaufsetzung sowie Bereitstellung der Anwendung

---

## **Progress**

### **In Development**

#### **Jan**
- Test-API-Abfrage von ca. 1000 Projektdaten und Zusammenführung in eine CSV-Datei
- Prüfung der Datenqualität und Projekttauglichkeit anhand der Test-Abfrage CSV

#### **Katerina**
*(noch keine Einträge)*

### **Done**
- Dokumentation & Projektplanung abgeschlossen  
- Entscheidung über relevante Informationen getroffen:  
  - Welche Forschungsfelder sollen dargestellt werden?  
  - Welche statistischen Maße sind sinnvoll?  
  - Festlegung der Features und Funktionalitäten  
- API-Dokumentation und Tutorials studiert  
  (Stand: 01.04.2025)

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
