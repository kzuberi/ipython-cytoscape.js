
from __future__ import absolute_import

from IPython.html import widgets, nbextensions
from IPython.display import display, Javascript, HTML
from IPython.utils.traitlets import Unicode, List
from IPython.core.display import Image
import json
from pkg_resources import resource_stream
from contextlib import closing
import copy
import base64
import pandas as pd


def init():
    with closing(resource_stream(__name__, 'cytowidgetview.js')) as js:
        display(Javascript(data=(js.read()).decode('utf8')))


# configure default styles - these
# are converted to json and passed to browser
#
# key is a cytoscape.js selector, values are style properties
default_style = {'node': {
        'shape': 'data(shape)',
        'width': 'mapData(weight, 0, 100, 20, 60)',
        'height': 'mapData(weight, 0, 100, 20, 60)',
        'content': 'data(name)',
        'text-valign': 'center',
        'text-outline-width': 2,
        'text-outline-color': 'data(color)',
        'background-color': 'data(color)',
        'color': '#fff',
    },

    ':selected': {
        'border-width': 3,
        'border-color': '#333',
    },

    'edge': {
        'width': 'mapData(strength, 0, 100, 2, 6)',
        'target-arrow-shape': 'triangle',
        'source-arrow-shape': 'circle',
        'line-color': 'data(color)',
        'source-arrow-color': 'data(color)',
        'target-arrow-color': 'data(color)',
    },

    'edge.questionable': {
        'line-style': 'dotted',
        'target-arrow-shape': 'diamond',
    },

    '.faded': {
        'opacity': 0.25,
        'text-opacity': 0
    }
}


def style_factory():
    '''
    would be great to come up with a collection
    of attractive built-in styles to use and customize

    for now, just a default
    '''

    return copy.deepcopy(default_style)


def to_cystyle(style):
    '''
    cytoscape likes a list of objects with a pair of keys,
    'selector' and 'css'.
    '''


    stylish_list = []
    for selector, css in style.items():
        stylish_list.append({'selector': selector, 'css': css})

    return json.dumps(stylish_list)


class CytoWidget(widgets.DOMWidget):
    _view_name = Unicode('CytoWidgetView', sync=True)
    elements = List(Unicode, sync=True)
    style = Unicode('', sync=True)
    layout = Unicode('circle', sync=True)

    def __init__(self):
        '''
        urge to put something here? don't forget the super call.
        oh let me just stub that in ...
        '''
        super(CytoWidget, self).__init__()


class Network(object):
    def __init__(self, nodes=None, edges=None, style=default_style, layout='circle'):

        if nodes is None and edges is not None:
            nodes = self._nodes_from_edges(edges)

        self._nodes = nodes
        self._edges = edges
        self._widget = CytoWidget()
        self._widget.on_displayed(self._on_displayed)
        self._widget.on_msg(self._handle_message)
        self._widget.style = to_cystyle(style)
        self._widget.layout = layout
        self.png = None
        self.state = None

    def _on_displayed(self, e):
        elements = self._get_elements()
        self._widget.elements = elements

    def _handle_message(self, widget, content):
        if content['msg_type'] == 'snapshot':
            image = content['image']
            # should look like "data:image/<image type>;base64,<base64 encoded image>"
            self.png = base64.decodestring(image.split(',')[1].encode('ascii'))
            if content['on_return'] == 'save':
                filename = content['filename']
                f = open(filename, 'w')
                f.write(self.png)
                f.close()
            elif content['on_return'] == 'display':
                self.show_snapshot()

        elif content['msg_type'] == 'json':
            self.state = content['json']
            self._cache_state()
        else:
            print("unexpected message type", content['msg_type'])

    def show(self):
        display(self._widget)

    def _get_elements(self):
        node_data = self._nodes.to_json(orient='records')
        edge_data = self._edges.to_json(orient='records')
        elements = [node_data, edge_data]
        return elements

    def snapshot(self, filename = None):

        content = {'msg_type': 'get_snapshot'}

        if filename:
            content['on_return'] = 'save'
            content['filename'] = filename
        else:
            content['on_return'] = 'display'

        self.png = None
        self._widget.send(content)

    def show_snapshot(self):
        if self.png:
            display(Image(self.png))

    def save_state(self):
        content = {'msg_type': 'save_state'}
        self.state = None
        self._widget.send(content)

    def _ipython_display_(self):
        display(self._widget)

    def _cache_state(self):
        cache_element = "<div id='cyto_state' style='display: none;'>%s</div>" % self.state
        display(HTML(cache_element))

    def _nodes_from_edges(self, edges):
        nodes = pd.DataFrame(pd.concat([edges['source'], edges['target']]), columns=['id'])
        nodes.drop_duplicates(inplace=True)
        nodes['name'] = nodes['id']

        return nodes