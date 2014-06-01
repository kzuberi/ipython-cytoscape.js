IPython-Cytoscape.js
====================

An interactive network visualization widget for the IPython Notebook based on the
`Cytoscape.js <http://cytoscape.github.io/cytoscape.js/>`_ JavaScript library.

Features
--------

* Create network visualizations from interactions specified in
  `Pandas <http://pandas.pydata.org/>`_ DataFrames
* Control visual features like graph layout, node & edge
  colors, node shapes, etc
* Interact with graph by selecting & moving nodes, panning & zooming the view
* Convert graph to a png image for static display or inclusion in
  other documents
* Save the graph to the notebook allowing the graph to be displayed in nbviewer
  including manual layout tweaks without an ipython backend, and still be interacted
  with by the viewer

Installation
------------

Currently in pre-release development, install from `github source <https://github.com/kzuberi/ipython-cytoscape.js>`_.

.. code-block:: bash

    $ pip install git+git://github.com/kzuberi/ipython-cytoscape.js#egg=ipython-cytoscape.js

Usage
------

Load extension in a notebook

.. code-block:: python

    %load_ext cyto

Specify interactions and create a graph

.. code-block:: python

    import pandas as pd
    nodes = pd.read_csv('/path/to/nodes.csv')
    edges = pd.read_csv('/path/to/edges.csv')

    graph = cyto.graph(nodes, edges, layout='circle')

Click and drag nodes as needed, save result to a png

.. code-block:: python

    graph.snapshot()
    graph.show_snapshot()

Save current widget state to notebook

.. code-block:: python

    graph.save_state()


