import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))

print(sys.path)
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OpenAIRE-Knowledge-Graph-Explorer'
copyright = '2025, Jan Krings, Katerina Kostadinovska'
author = 'Jan Krings, Katerina Kostadinovska'
release = '2025-01-01'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  
]

templates_path = ['documentation\\spinx_docs\\_templates']
exclude_patterns = ['documentation\\spinx_docs\\_build', 'Thumbs.db', '.DS_Store']
html_static_path = ['documentation\\spinx_docs\\_static']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

