# TODO LISTE

## Jan

- Ziel und grundlegendes Vorgehen (Concept Map / Dokumentation / Datenstruktur) - auf Englisch
- Installationsanleitung inkl. Abhängigkeiten (setup.py, requirements.txt, etc.) + Datenstruktur, wie GitHub aufgebaut
- Workflows, Datenfluss, Dokumentationstools wählen (Sphinx vs. MkDocs)
- Templates?

## Katerina

- API ansteuern können, Anfragen speichern (z.B. in JSON-Dateien?)
  - API Limits? 60 Requests ausreichend? Wenn nicht, welche nächsten Schritte?
  - Script zum Request (als Showcase für den Förstner)
  - Anfrage transformieren, oder ist JSON ausreichend?

OpenAIRE-Knowledge-Graph-Explorer/
├── src/                        # Source code directory (Python modules)
│   └── python_module.py        # Example Python module with functions
│
├── tests/                      # Test directory for unimplemented tests
│   └── test_example.py         # Example test file (can be written using pytest or unittest)
│
├── documentation/              # Sphinx Documentation directory
│   ├── sphinx_docs/            # Sphinx documentation files
│   │   ├── _build/             # Generated documentation (HTML output)
│   │   ├── _static/            # Static files (images, CSS, etc.)
│   │   ├── _templates/         # Templates for Sphinx
│   │   ├── conf.py             # Sphinx configuration file
│   │   ├── index.rst           # Main documentation file (Table of Contents)
│   │   ├── python_module.rst   # Documentation setting file for the example python module
│   └── requirements.txt        # Dependencies (Sphinx and other libraries)
│
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup script for installing the package
├── README.md                   # Project overview and usage
└── LICENSE                     # Project license