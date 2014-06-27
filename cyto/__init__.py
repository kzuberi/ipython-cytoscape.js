from __future__ import absolute_import
from . import cyto

def load_ipython_extension(ipython):
    cyto.init()
    ipython.push(['cyto'])