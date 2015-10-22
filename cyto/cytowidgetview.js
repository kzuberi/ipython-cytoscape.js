
require.config({
    paths: {
        cytoscape: "http://cytoscape.github.io/cytoscape.js/api/cytoscape.js-latest/cytoscape.min",
    }
});

require(["cytoscape"], function(cytoscape) {
    // if there is a widget state saved in the page, use to
    // initialize a graph. May be able to support display on
    // viewer pages without the backend.
    $.each($("#cyto_state"), function(){
        console.log("found a cyto_state %o", this);
        var json_state = $.parseJSON($(this).text());

        // change layout to use saved positions
        json_state['layout'] = {'name': 'preset'};

        $(this).after("<div id='cyto_graph' style='height: 500px; width: 500px; position: relative'></div>");
        $("#cyto_graph").cytoscape(json_state);
    });

});

//require(["widgets/js/widget", "cytoscape"], function(widget, cytoscape){
require(["nbextensions/widgets/widgets/js/widget",
         "nbextensions/widgets/widgets/js/manager",
         "cytoscape"],
         function(widget, manager, cytoscape){

    var CytoWidgetView = widget.DOMWidgetView.extend({
//        if we need the initialize function, remember to put in a call
//        to the super method. here's a reminder:
//        initialize: function() {
//            return CytoWidgetView.__super__.initialize.apply(this, arguments);
//        },

        render: function(){
            // for some reason setting up cytoscape in this render
            // function doesn't work anymore, moved the work to update()
            this.model.on('change:elements', this.value_changed, this);
            return this;
        },

        value_changed: function() {
          console.log("in value_changed()");
        },

        update: function() {

          this.$el.css('height', '500px');
          this.$el.css('width', '500px');
          this.$el.css('position', 'relative');

          // since cy.load() is deprecated, and cy.add()
          // requires a different format, setup the elements
          // when creating the cytocape instance, and
          // figure out how to deal with updates later
          var elements = this.model.get('elements');
          var node_data = $.parseJSON(elements[0]);
          var edge_data = $.parseJSON(elements[1]);

          var nodes = [];
          for (var i=0; i<node_data.length; i++) {
              nodes.push({data: node_data[i]});
          }

          var edges = [];
          for (var i=0; i<edge_data.length; i++) {
              edges.push({data: edge_data[i]});
          }

          var elems = {nodes: nodes, edges: edges};
          // console.log("elements", JSON.stringify(elems));

          var that = this;

          this.$el.cytoscape({
            elements: elems,

              layout: {
                  name: 'circle',
                  fit: true,
              },

              zoomingEnabled: true,
              userZoomingEnabled: false,
              pan: { x: 0, y: 0 },
              panningEnabled: true,
              userPanningEnabled: false,

              ready: function(evt){
                  // clear cytoscape container position cache
                  // to work around scrolling bug
                  var cy = this;
                  that.$el.closest("#notebook").scroll(function(){
                      cy._private.renderer.containerBB = null;
                  });
              },
          })

          var cy = this.$el.cytoscape('get');

          var layout = this.model.get('layout');
          cy.layout({name: layout, fit: true});

          var style = this.model.get('style');
          cy.style().resetToDefault().fromJson($.parseJSON(style)).update();

          return CytoWidgetView.__super__.update.apply(this);
        },

        on_msg: function(msg) {
            switch (msg.msg_type) {
                case 'get_snapshot':
                    var cy = this.$el.cytoscape('get');
                    var image = cy.png()
                    var return_msg = {'msg_type': 'snapshot', 'image': image};

                    // pass on_return back
                    if (msg.on_return == 'display') {
                        return_msg['on_return'] = 'display';
                    }
                    else if (msg.on_return == 'save') {
                        return_msg['on_return'] = 'save';
                        return_msg['filename'] = msg.filename;
                    }

                    this.send(return_msg);
                    break;
                case 'save_state':
                    var cy = this.$el.cytoscape('get');
                    var json = JSON.stringify(cy.json());
                    this.send({'msg_type': 'json', 'json': json});
                    break;
                default:
                    console.log("unexpected msg_type", msg.msg_type);
            }
        }

    });

    // register widget
    manager.WidgetManager.register_widget_view('CytoWidgetView', CytoWidgetView);
});
