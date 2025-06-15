## Step one: Download the data
- To start the project, you need to donwload the data local. The raw data is available as a ZIP archive and is very large - therefore it cannot be saved in the GitHub repository. Please download them yourself. Link: https://zenodo.org/records/14851262. Then unzipped the folder into data/original_projects_data_april2025/


## Step two: JSON Cleaning & Wrapping 
- Clean and prepare raw JSON files from Zenodo so they can be properly parsed later as arrays of objects.

- Why we need this 
    - The original JSON dumps may contain many individual JSON objects concatenated without commas or array brackets. This can lead to invalid JSON that breaks standard parsers. Our script:

        1) Wraps each file’s content in [...] to form an array.

        2) Automatically adds commas between objects.

        3) Strips trailing whitespace to ensure clean formatting.

- Script Configuration 
    input_folder = r"data\original_projects_data_april2025"
    output_folder = r"data\cleaned_projects_data_april2025"
    - Reads .json files from the original folder.
    - Writes cleaned versions into cleaned_projects_data_april2025 (created automatically).

- How to run ?
    - python src/format_json.py


## Step three: Convert Cleaned JSON to Structured CSV Files 
- Transform cleaned JSON project files into structured CSV tables for use in downstream scripts and Neo4j import.

- Why this matters
    - CSV is easier for bulk-loading, relational analysis, and visualizations. This script src/02_extract_projects_to_csv.py 
        - extracts project metada (ID, title, dates, cost, etc.)
        - records funder details (name, shortName) and avoids duplicates
        - records country jurisdictions and deduplicates
        - builds link tables: 
            - Project -> Funder (many-to-many)
            - Project -> Country (many-to-many)
- After running this code with python src/json_to_csv.py, it will automatically make clean csv data frame in data\projects_data_csv

## Step four: Link Projects with Publications via CrossRef
- This script enriches your dataset by discovering scientific publications related to OpenAIRE projects using the CrossRef API and linking them. You will need to download the data from: https://zenodo.org/records/15475023

- Why we need this
    - Links ongoing project impact via publication counts and citations
    - Helps quantify project impact via publication counts and citations
    - Enables deeper network analysis and visualization by connecting Project -> Publishers/Funders

- How it works
    1) Load input CSVs 
    2) Match funder names to canonical ROR names using: 
        - Exact match on "name"
        - Exact match on "ror_name"
        - Partial match via aliases field
    3) Loop over each project (up to LIMIT)
        - Query crossref with project title (and funder filter, if matched)
        - Take up to 5 hits
        - Extract DOI, title, journal, citation count.
        - Skip duplicate DOIs
        - Store publication metadata and project-publication link
    4) Write CSV outputs

- Run the script using python src/03_enrich_funders_with_ror.py

## Step five: Build Local Knowledge Graph in Neo4j
- This script imports structured CSV data into a local Neo4j database, creating a knowledge graph with nodes and relationships for Projects, Funders, Countries, and Publications.

- How it works 
    - Install neo4j (local) https://neo4j.com/download/ 
    - Set up neo4j password in neo4j_data/neo_access.txt (local)
    - The script connects to Neo4j via bolt://localhost:7687 (default Bolt protocol), reads CSVs, and imports the data 
    - Set the LIMIT_ENTRIES variable in the script to control how many projects get processed.
- Why this matters
    - Converts flat CSV tables into a rich graph structure
    - Enables graph-based queries (w.g., find all projects funded by Funder X with publications in Journal Y)
    - Supports future graph augmentations, e.g., adding methods, researchers, or institutions

- How to run
    - ensure Neo4j is running and password is set in neo4j_data/neo_acces.txt and then run the script using python src/05_import_to_neo4j.py


# Dashboard Overview
- To gain a clearer understanding of our dataset, we built an interactive dashboard featuring 12 visualizations (limited:10000 projects) that cover the following core insights: 
    - Basic metrics:
        - Number of projects per year
        - Average and total funding per year
        - Number of publications per project/year
        - Number of publications per country
    - Funder Analysis:
        - Top funders by number of projects and funding volume
        - Average funding per funder
    - Projects Characteristics:
        - Project duration vs. funding scatter plot
        - Distribution of citation counts
        - Comparison of top project by publication count

- The dashboard is built using Streamlit, powered by Python scripts that: 
    1) Read CSVs generated from preprocessed JSON files (projects, publications, funders, countries, relationships)
    2) Aggregate data- grouping and summarizing key metrics (countrs, sums, averages)
    3) Visualize results using seaborn/matplotlib for easy interpretation
    4) Render plots in a web IU where users can explore trends interactively
- To launch the dashboard, run the following in your terminal:
streamlit run src/dashboard.py
Then open the displayed URL (usually http://localhost:8501) in your browser.


