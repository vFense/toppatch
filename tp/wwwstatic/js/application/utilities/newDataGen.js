define(
    ['jquery', 'backbone', 'test-json/patchLoader'],
    function ($, Backbone, patchList) {
        "use strict";

        var ipTable = _.shuffle(_.range(1, 254)),
            ipAvailable = 0,
            osList = [
                { name: 'Windows 7', short: "win7" },
                { name: 'Windows Server 2008', short: "win2k8" },
                { name: 'Windows Vista', short: "winV" },
                { name: 'Windows Server 2003', short: "win2k3" },
                { name: 'Windows XP', short: "winXP" }
            ],
            node,
            nodes,
            exports = {}
        exports.Model = Backbone.Model.extend({
            defaults: {
                "patch/need": [],
                "patch/done": [],
                "patch/fail": []
            },
            initialize: function () {
                this.set('ip', this.get('ip') || (function () {
                    var temp = "192.168.1." + ipTable[ipAvailable];
                    ipAvailable += 1;
                    return temp;
                }()));

                this.set('os', this.get('os') || _.shuffle(osList)[0]);

                var myPatches = patchList[this.get('os').short].patches,
                    pick = Math.ceil(Math.random() * myPatches.length);


                this.set("patch/need", _.first(myPatches, pick));
                this.set("patch/done", _.rest(myPatches, pick));
            }
        });
        exports.collection = new (Backbone.Collection.extend({
            model: exports.Model
        }))(
            // Initialize the collection with a
            // random length array of empty objects
            (function () {
                var i, q,
                    out = [],   // Our array
                    min = 5,    // Minimum length of array
                    max = 15;   // Maximum length of array
                for (i = 0, q = _.shuffle(_.range(min, max))[0]; i < q; i += 1) {
                    out.push({});
                }
                return out;
            }())
        );
        exports.View = Backbone.View.extend({
            initialize: function () {
                this.collection =  exports.collection;
            },
            beforeRender: $.noop,
            onRender: $.noop,
            render: function () {
                if (this.beforeRender !== $.noop) { this.beforeRender(); }

                this.$el.html('See the console log...');
                console.log(this.collection.toJSON());

                if (this.onRender !== $.noop) { this.onRender(); }
                return this;
            },
            renderModel: function (item) {}
        });

        return exports;
        /*  nodes.json
            [
                {
                    "ip": "192.168.1.2",
                    "os": "Windows 7",
                    "patches": {
                        "need": [
                            "KB0000001",
                            "KB0000002",
                            etc...
                        ],
                        "complete": [],
                        "failed": []
                    }
                },
                etc...
            ]
         */
    }
);