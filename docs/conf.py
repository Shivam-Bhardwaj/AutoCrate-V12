# Configuration file for the Sphinx documentation builder.
# AutoCrate API Documentation Configuration

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'AutoCrate'
copyright = f'{datetime.now().year}, AutoCrate AI Development Team'
author = 'AI Development Showcase'
release = '12.0.6'
version = '12.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx_rtd_theme',
    'myst_parser',
]

# Add support for Markdown files
source_suffix = {
    '.rst': None,
    '.md': None,
}

# Auto-generate API documentation
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Templates path
templates_path = ['_templates']

# List of patterns to ignore when looking for source files
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom CSS
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# Logo and favicon
html_logo = '_static/autocrate_logo.png'
html_favicon = '_static/favicon.ico'

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': r'''
\usepackage{charter}
\usepackage[defaultsans]{lato}
\usepackage{inconsolata}
''',
}

latex_documents = [
    ('index', 'AutoCrate.tex', 'AutoCrate Documentation',
     'AI Development Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    ('index', 'autocrate', 'AutoCrate Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    ('index', 'AutoCrate', 'AutoCrate Documentation',
     author, 'AutoCrate', 'AI-Assisted Engineering Software Development Showcase.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# Todo extension
todo_include_todos = True

# Coverage extension
coverage_show_missing_items = True

# MathJax configuration
mathjax3_config = {
    'tex': {
        'inlineMath': [['$', '$'], ['\\(', '\\)']],
        'displayMath': [['$$', '$$'], ['\\[', '\\]']],
        'packages': ['base', 'ams', 'noerrors', 'noundefined', 'autoload'],
    },
    'options': {
        'ignoreHtmlClass': 'tex2jax_ignore',
        'processHtmlClass': 'tex2jax_process'
    }
}

# Custom roles
def setup(app):
    app.add_css_file('custom.css')
    
    # Add custom roles for ASTM standards
    from docutils.parsers.rst import directives
    from sphinx.util.docutils import SphinxRole
    
    class ASTMRole(SphinxRole):
        def run(self):
            from docutils import nodes
            text = self.text
            node = nodes.literal(text, text)
            node['classes'].append('astm-standard')
            return [node], []
    
    app.add_role('astm', ASTMRole())

# Suppress warnings for missing references
suppress_warnings = ['ref.citation']