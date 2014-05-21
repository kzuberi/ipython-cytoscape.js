
from IPython.html import widgets, nbextensions
from IPython.display import display, Javascript
from IPython.utils.traitlets import Unicode, List
from IPython.core.display import Image
import json
from pkg_resources import resource_stream
from contextlib import closing
import copy
import base64


def init():
    with closing(resource_stream(__name__, 'cytowidgetview.js')) as js:
        display(Javascript(data=js.read()))


# configure default styles - these
# are converted to json and passed to browser
#
# key is a cytoscape.js selector, values are style properties
default_style = {'node': {
        'shape': 'data(shape)',
        'width': 'mapData(weight, 40, 80, 20, 60)',
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
        'width': 'mapData(strength, 70, 100, 2, 6)',
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

    def __init__(self):
        '''
        urge to put something here? don't forget the super call.
        oh let me just stub that in ...
        '''
        super(CytoWidget, self).__init__()


class Graph(object):
    def __init__(self, nodes_df, edges_df, style=default_style):
        self._nodes_df = nodes_df
        self._edges_df = edges_df
        self._widget = CytoWidget()
        self._widget.on_displayed(self._on_displayed)
        self._widget.on_msg(self._handle_message)
        self._widget.style = to_cystyle(style)
        self.png = None

    def _on_displayed(self, e):
        elements = self._get_elements()
        self._widget.elements = elements

    def _handle_message(self, widget, content):
        image = content['image']
        # should look like "data:image/<image type>;base64,<base64 encoded image>"
        self.png = base64.decodestring(image.split(',')[1])

    def show(self):
        display(self._widget)

    def _get_elements(self):
        node_data = self._nodes_df.to_json(orient='records')
        edge_data = self._edges_df.to_json(orient='records')
        elements = [node_data, edge_data]
        return elements

    def snapshot(self):
        content = {'msg_type': 'get_snapshot'}
        self.png = None
        self._widget.send(content)

    def show_snapshot(self):
        if self.png:
            display(Image(self.png))

    def get_snapshot(self):
        return self.png

    def _ipython_display_(self):
        display(self._widget)

