#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "ipython-cytoscape.js",
    version = "0.2a1",
    description = "Cytoscape.js network visualization widget for the IPython Notebook",
    author = "Khalid Zuberi",
    author_email = "kzuberi@gmail.com",
    packages = ["cyto",],
    package_data = {'': ['*.css', '*.js',]},
    zip_safe = True,
    install_requires = ['IPython>=2.0', 'pandas>=0.12',],
)
