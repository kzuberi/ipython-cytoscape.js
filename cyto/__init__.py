
import cyto


def load_ipython_extension(ipython):
    cyto.init()
    ipython.push(['cyto'])