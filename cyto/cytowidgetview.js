
require.config({
    paths: {
        cytoscape: "http://cytoscape.github.io/cytoscape.js/api/cytoscape.js-latest/cytoscape.min",
    }
});


require(["widgets/js/widget", "cytoscape"], function(WidgetManager, cytoscape){

    var CytoWidgetView = IPython.DOMWidgetView.extend({
//        if we need the initialize function, remember to put in a call
//        to the super method. here's a reminder:
//        initialize: function() {
//            return CytoWidgetView.__super__.initialize.apply(this, arguments);
//        },

        render: function(){
            this.$el.css('height', '500px');
            this.$el.css('width', '500px');
            this.$el.css('position', 'relative');

            var that = this;

            this.$el.cytoscape({

                layout: {
                    name: 'circle',
                },

                zoomingEnabled: false,
                userZoomingEnabled: false,
                pan: { x: 0, y: 0 },
                panningEnabled: false,

                ready: function(evt){
                    // clear cytoscape container position cache
                    // to work around scrolling bug
                    var cy = this;
                    that.$el.closest("#notebook").scroll(function(){
                        cy._private.renderer.containerBB = null;
                    });
                },
            })

            return this;
        },

        update: function() {
            var cy = this.$el.cytoscape('get');

            var style = this.model.get('style');
            cy.style().resetToDefault().fromJson($.parseJSON(style));

            var layout = this.model.get('layout');
            cy.layout({name: layout});

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

            var elements = {nodes: nodes, edges: edges};

            cy.load(elements, function() {
                //console.log("cy load done");
            });

            return CytoWidgetView.__super__.update.apply(this);
        },

        on_msg: function(msg) {
            switch (msg.msg_type) {
                case 'get_snapshot':
                    var cy = this.$el.cytoscape('get');
                    var image = cy.png()
                    this.send({'msg_type': 'snapshot', 'image': image});
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
    WidgetManager.register_widget_view('CytoWidgetView', CytoWidgetView);
});