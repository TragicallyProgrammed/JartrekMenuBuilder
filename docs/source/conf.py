# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'JartrekMenuBuilder'
copyright = '2022, Keystone Bingo'
author = 'Garrett Bowers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['autoapi.extension', 'sphinx.ext.napoleon']

# -- python Setup ------------------------------------------------------------
autoapi_type = 'python'
autoapi_dirs = ['../../src']
autoapi_root = 'python'

# -- javascript Setup ---------------------------------------------------------
# autoapi_type = 'javascript'
# autoapi_dirs = ['../../src/static/scripts']
# autoapi_root = 'javascript'

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'renku'
html_static_path = ['_static']
